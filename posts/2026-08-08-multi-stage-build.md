---
title: "1.2GB 이미지가 80MB가 되기까지 — 멀티스테이지 빌드"
date: 2026-08-08
category: 트러블슈팅
tags: ["Docker", "multi-stage", "이미지 경량화", "빌드", "보안"]
summary: "빌드 도구는 짐 싸는 데만 필요하고 여행엔 필요 없습니다. 공장(빌드 스테이지)과 매장(런타임 스테이지)을 분리하는 멀티스테이지의 원리와 함정."
---

> **한 줄 요약:** 이미지가 무거운 이유는 대부분 **빌드에만 필요했던 것들**(컴파일러, 헤더, node_modules, 소스)이 결과물과 함께 실려 있어서입니다. 멀티스테이지는 **공장 스테이지에서 만들고, 매장 스테이지엔 완성품만 COPY**하는 것 — 용량과 공격 표면이 같이 줄어요.

[[diagram:multi-stage]]

## 왜 이렇게 무거워졌나

```dockerfile
FROM node:20
COPY . .
RUN npm install && npm run build
CMD ["node", "dist/server.js"]
```

이 평범한 Dockerfile의 최종 이미지에는 — 실행에 필요한 `dist/` 말고도 **node_modules 전체(devDependencies 포함), 소스 원본, npm 캐시, 그리고 base 이미지의 빌드 도구들**이 전부 들어 있습니다. 레이어 캐시 글에서 봤듯 이미지는 겹겹의 필름이라, `RUN rm -rf`로 나중에 지워도 **아래 필름에는 남아** 용량이 안 줄어요. 애초에 **안 싣는 것**만이 답입니다.

컴파일 언어(Go, Java)는 더 극단적입니다 — 결과물은 바이너리/jar 하나인데, 그걸 만들려고 SDK 전체를 실은 채 배포하는 셈이니까요.

## 멀티스테이지: 공장과 매장

Dockerfile 하나에 `FROM`을 여러 번 — 각 FROM이 독립된 스테이지고, **최종 이미지는 마지막 스테이지만** 남습니다.

```dockerfile
# ── 스테이지 1: 공장 (이름을 붙인다) ──
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci                      # 캐시 글의 그 순서 최적화 그대로
COPY . .
RUN npm run build && npm prune --omit=dev   # 실행용 의존성만 남기기

# ── 스테이지 2: 매장 (가볍고 깨끗하게) ──
FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist              # ★ 공장에서 완성품만 반입
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json .
USER node
CMD ["node", "dist/server.js"]
```

핵심은 `COPY --from=builder` 한 줄 — **다른 스테이지의 파일시스템에서 필요한 것만 집어오는** 문법입니다. 공장의 컴파일러·소스·캐시는 최종 이미지에 존재한 적조차 없게 되죠.

Go라면 결과가 더 극적입니다.

```dockerfile
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app ./cmd/server

FROM gcr.io/distroless/static     # 쉘도 패키지 매니저도 없는 초경량 베이스
COPY --from=builder /app /app
ENTRYPOINT ["/app"]
```

golang 베이스 800MB+ → 최종 **수십 MB**. 이게 제목의 그 다이어트입니다.

## 용량만이 아니다 — 보안과 속도

- **공격 표면 축소.** 최종 이미지에 컴파일러·쉘·curl이 없으면, 뚫린 뒤에 공격자가 쓸 연장도 없습니다(배스천을 빈 껍데기로 두는 그 논리). 취약점 스캐너 경고 수가 뚝 떨어지는 부수 효과는 컴플라이언스 대응에서 실질적인 시간 절약이고요.
- **배포 속도.** 이미지 크기는 곧 pull 시간 — 오토스케일링으로 새 노드가 뜰 때, 80MB와 1.2GB는 첫 응답까지의 시간이 다릅니다. NAT 글에서 본 "이미지 pull이 NAT를 지나며 GB당 과금"까지 생각하면 돈 문제이기도 하죠.

## 함정과 요령 넷

**① 매장 베이스 선택.** `slim`(최소 데비안)이 무난한 기본값, `distroless`는 더 작고 안전하지만 **쉘이 없어 `kubectl exec`류 현장 진입이 안 됩니다** — 그 글에서 언급한 `kubectl debug`(임시 컨테이너)가 전제돼야 해요. alpine은 작지만 musl 호환성 이슈가 언어에 따라 있으니 "작다"만 보고 고르지 마세요.

**② 런타임 의존성 실수.** 공장에서 다 만들었다고 매장에 아무것도 없으면 안 되는 경우 — 예를 들어 이미지 처리 앱은 매장에도 해당 공유 라이브러리가 필요합니다. "로컬(공장 풀셋)에선 되는데 배포하면 라이브러리 없다고 죽어요"가 이 함정의 증상.

**③ 캐시와의 합주.** 스테이지 분리는 레이어 캐시 글의 순서 원칙과 곱연산입니다 — 공장 스테이지 안에서도 `package.json 먼저 COPY → npm ci → 소스 COPY` 순서를 지켜야 의존성 캐시가 삽니다. CI에서는 이전 이미지를 캐시 소스로 지정하는 옵션(`--cache-from` 계열)까지 챙기면 빌드 시간도 다이어트돼요.

**④ 빌드 시크릿.** 공장에서 사설 저장소 토큰이 필요할 때 `COPY .npmrc` / `ENV TOKEN=...`은 레이어에 박제됩니다(Secret 글의 그 사고). `RUN --mount=type=secret`으로 **빌드 순간에만 주입**하는 게 정석 — 멀티스테이지라 최종엔 안 남는다 해도, 공장 스테이지 캐시가 레지스트리에 올라가는 구성이면 새는 경로가 됩니다.

## 확인

```bash
docker images myapp                      # before/after 용량
docker history myapp:latest | head       # 최종 이미지에 뭐가 실렸나 (레이어별)
docker run --rm myapp ls /usr/bin | wc -l   # 매장에 연장이 얼마나 남았나 (distroless면 이것도 안 됨 — 그게 정상)
```

## 한 줄 정리

**빌드에 필요한 것과 실행에 필요한 것은 다릅니다.** 공장(builder)에서 만들고 매장(slim/distroless)엔 `COPY --from`으로 완성품만 — 용량·pull 시간·공격 표면·스캐너 경고가 한 번에 줄어요. 단, 매장의 런타임 의존성과 현장 진입 수단(kubectl debug)은 미리 챙기고요.
