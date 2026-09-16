---
title: "HTTP 헤더 실무편 — Host, X-Forwarded-For, Cache-Control 세 개면 사고의 8할"
date: 2026-09-16
category: 네트워크
tags: ["HTTP", "헤더", "X-Forwarded-For", "Cache-Control", "Host", "프록시"]
summary: "LB·CDN·프록시 뒤에서 앱이 이상하게 구는 이유는 대개 헤더 세 개 중 하나입니다. 각각이 어디서 붙고 어디서 사라지는지 따라가 봅니다."
---

> **한 줄 요약:** 요청이 CDN → LB → 프록시 → 앱을 지나는 동안 헤더가 **붙고, 바뀌고, 사라집니다.** 실무 사고의 대부분은 세 헤더 — **Host**(어느 사이트로 온 요청인가), **X-Forwarded-For**(진짜 클라이언트는 누구인가), **Cache-Control**(누가 얼마나 캐시해도 되나) — 에서 나고, 진단은 `curl -v`로 각 층에서 헤더를 찍어보는 겁니다.

[[diagram:http-headers]]

## Host — 한 IP에 여러 사이트가 사는 법

서버 한 대(IP 하나)가 `api.example.com`과 `admin.example.com`을 함께 서빙할 수 있는 이유가 Host 헤더입니다. 브라우저가 요청에 "나는 api.example.com에 왔다"를 적어 보내고, 웹서버/LB가 그걸 보고 분기하죠(ALB 글의 호스트 기반 라우팅이 이것). DNS 글에서 "IP는 맞는데 안 열린다"의 다음 층이 여기예요.

사고 유형:
- **IP로 직접 접속하면 기본(첫 번째) 사이트가 뜸** — 정상입니다. Host가 없으니 기본값. `curl -H "Host: api.example.com" http://10.0.3.15/`로 테스트해야 진짜 검증.
- **프록시가 Host를 자기 것으로 바꿔 전달** — nginx의 `proxy_set_header Host $host;`가 빠지면 뒷단 앱이 `localhost:8080`을 Host로 받아 리다이렉트 URL·쿠키 도메인이 깨집니다. "로그인 후 localhost로 튕겨요"의 단골 원인.

## X-Forwarded-For — 진짜 클라이언트는 누구인가

ALB 글에서 예고한 그 문제. L7 프록시는 연결을 새로 맺으니 앱이 보는 발신 IP는 **프록시의 IP**입니다. 진짜 클라이언트 IP는 프록시가 `X-Forwarded-For`(XFF)에 **덧붙여** 넘기죠.

```
X-Forwarded-For: 203.0.113.9, 10.0.1.20, 10.0.2.5
                  ↑클라이언트   ↑CDN       ↑LB       (지나온 순서대로 오른쪽에 추가)
```

세 가지를 알아야 안전합니다.

**① 맨 왼쪽이 항상 진짜는 아니다.** 클라이언트가 **직접 XFF 헤더를 위조해 보낼 수 있습니다.** 그러면 맨 왼쪽은 공격자가 적은 가짜 IP. 신뢰할 수 있는 건 **내가 아는 프록시가 추가한 값**뿐 — 즉 "오른쪽에서부터, 신뢰하는 프록시 홉 수만큼 세어 그 직전 값"이 진짜입니다. nginx의 `set_real_ip_from`(신뢰 대역) + `real_ip_recursive on`이 정확히 이 계산을 해줍니다.

**② IP 기반 통제는 이 값을 써야 한다.** 레이트리밋, 국가 차단, 관리자 IP 허용목록이 프록시 IP를 보면 — 전 사용자가 한 IP로 보여 한 명이 막히면 전부 막힙니다. WAF 글의 레이트리밋도 XFF 기준으로 동작해야 하고요.

**③ 로그 포맷에 반영.** 액세스 로그에 XFF(신뢰 계산 후)가 없으면 로그 중앙화 글의 모든 분석이 "전부 LB IP"로 무의미해집니다.

## Cache-Control — 누가 얼마나 기억해도 되나

응답 헤더로, **브라우저와 중간 캐시(CDN)에게 내리는 지시**입니다. CDN 캐시 글의 그 "유통기한"을 실제로 적는 자리.

```
Cache-Control: public, max-age=31536000, immutable   ← 해시 파일명 정적 자원: 1년, 재검증 불필요
Cache-Control: no-cache                              ← HTML: 캐시해도 되지만 매번 서버에 확인
Cache-Control: private, no-store                     ← 개인 데이터 API: 어디에도 저장 금지
```

사고 유형:
- **개인화 응답에 public** — "다른 사용자의 마이페이지가 보여요"라는 최악의 사고. CDN이 A의 응답을 캐시해 B에게 줍니다. 인증이 필요한 응답은 `private` 또는 `no-store`가 기본값이어야 하고, CDN 쪽에서도 쿠키/Authorization 있는 요청은 캐시 제외.
- **`Vary` 누락** — 같은 URL이 언어·기기별로 다른 응답을 주는데 `Vary: Accept-Language`가 없으면 첫 사용자 언어로 전부 캐시됩니다.
- **no-cache ≠ no-store** — 이름이 반직관적입니다. `no-cache`는 "저장은 하되 쓰기 전에 확인", `no-store`는 "저장 자체 금지". 민감 데이터는 후자.

## 진단: 층마다 헤더 찍기

curl 글의 방식 그대로, **각 층에 직접** 붙어 헤더를 비교합니다.

```bash
curl -sI https://api.example.com/x            # CDN/LB 경유 — 사용자가 보는 것
curl -sI -H "Host: api.example.com" http://LB-내부IP/x       # LB 직접
curl -sI -H "Host: api.example.com" http://10.0.3.15:8080/x # 앱 직접
# → 어느 층에서 Cache-Control이 바뀌고, XFF가 붙고, Host가 사라지는지 비교
```

앱이 받는 실제 헤더를 봐야 할 때는 요청을 그대로 되돌려주는 디버그 엔드포인트(헤더 덤프)를 하나 두는 게 좋습니다 — 단, 운영에선 내부 IP에만 열기(감사 로그 글의 그 감각).

## 덤: 자주 만나는 나머지

- **`X-Forwarded-Proto`** — 프록시에서 TLS를 풀었으니 앱은 http로 받지만, 원래는 https였다는 표시. 이게 없으면 앱이 http로 리다이렉트 URL을 만들어 **무한 리다이렉트 루프**가 납니다.
- **`X-Request-ID` / `traceparent`** — 로그 중앙화 글의 trace_id. 가장 앞단(CDN/LB)에서 발급하고 모든 층이 그대로 전달.
- **`Connection`, `Content-Length`/`Transfer-Encoding`** — 스트리밍(SSE 글)에서 중간 장비가 버퍼링하는 원인이 이 근처에 있습니다.

## 한 줄 정리

**Host는 어느 사이트, XFF는 진짜 누구(단, 신뢰 홉 계산 필수), Cache-Control은 누가 기억해도 되나.** 프록시 뒤에서 이상하면 `curl -sI`로 층마다 헤더를 찍어 비교하세요 — 사라진 Host, 위조 가능한 XFF, 개인 응답의 public 캐시가 사고의 8할입니다.
