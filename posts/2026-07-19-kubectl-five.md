---
title: "kubectl 디버깅은 다섯 명령으로 끝난다 — logs, describe, exec, get -o, port-forward"
date: 2026-07-19
category: 리눅스
tags: ["kubectl", "Kubernetes", "디버깅", "Pod", "트러블슈팅"]
summary: "쿠버 문제의 9할은 다섯 명령의 조합으로 잡힙니다. 각각이 '무엇을 보는 창'인지, 어떤 순서로 꺼내는지 정리했어요."
---

> **한 줄 요약:** 쿠버네티스 디버깅의 기본 장비는 다섯 개입니다 — **logs(앱의 말), describe(쿠버의 말), exec(현장 진입), get -o yaml(설계도 원본), port-forward(직통 전화).** 순서는 대개 이 나열 그대로예요.

## 왜 다섯 개인가

문제가 생기면 확인할 것은 결국 넷입니다. 앱이 뭐라고 하는가, 쿠버네티스가 뭐라고 하는가, 현장(컨테이너 안)은 어떤가, 설정은 내 의도대로인가. 다섯 명령이 정확히 이 창들이에요. 하나씩 —

## ① logs — 앱의 말부터

```bash
kubectl logs myapp-xxx                    # 현재 컨테이너의 stdout/stderr
kubectl logs myapp-xxx --previous         # ★ 직전에 죽은 컨테이너의 유언
kubectl logs myapp-xxx -f --tail=100      # 실시간 + 마지막 100줄부터
kubectl logs myapp-xxx -c sidecar         # Pod에 컨테이너가 여럿이면 지정
kubectl logs -l app=myapp --tail=20       # 레이블로 여러 Pod 한꺼번에
```

CrashLoop 상황이면 무조건 `--previous`부터 — 지금 컨테이너는 방금 태어나서 아무것도 모릅니다.

## ② describe — 쿠버네티스의 말

앱 로그가 비었거나 Pod가 아예 안 뜨면(Pending, ImagePullBackOff), 앱이 아니라 **쿠버네티스 쪽 사정**입니다.

```bash
kubectl describe pod myapp-xxx
```

볼 곳은 두 군데: **Last State/Exit Code**(137이면 OOM — 그 글의 그것), 그리고 맨 아래 **Events**. 이미지 못 받음, 볼륨 마운트 실패, 스케줄 불가(리소스 부족), 프로브 실패가 전부 Events에 시간순으로 적혀 있어요. describe는 Pod만이 아니라 무엇에든 됩니다 — `describe node`로 노드의 리소스 압박, `describe svc`로 서비스 상태도 봅니다.

## ③ exec — 현장 진입

로그와 이벤트로 부족하면 안에 들어가서 봅니다.

```bash
kubectl exec -it myapp-xxx -- sh              # 쉘 진입 (bash 없으면 sh)
kubectl exec myapp-xxx -- env | sort          # 주입된 환경변수 확인
kubectl exec myapp-xxx -- cat /app/config.yml # 설정이 진짜 반영됐나
kubectl exec myapp-xxx -- nc -vz db-svc 5432  # Pod 입장에서 DB가 보이나
```

특히 마지막 것 — **"그 Pod의 눈으로" 네트워크를 확인**하는 게 핵심입니다. 내 노트북에서 되는 것과 Pod에서 되는 것은 완전히 다른 얘기예요(DNS, 네트워크폴리시). 요즘 경량 이미지는 쉘/nc조차 없는데, 그럴 땐 `kubectl debug`로 도구 든 임시 컨테이너를 붙이는 방법이 있습니다.

## ④ get -o yaml — 설계도 원본 대조

"분명 설정했는데 왜 반영이 안 되지?"의 답은 **지금 클러스터에 실제로 적용된 원본**에 있습니다.

```bash
kubectl get pod myapp-xxx -o yaml             # 내 매니페스트가 아니라 '실제 상태'
kubectl get deploy myapp -o yaml | grep -A3 image:   # 진짜 배포된 이미지 태그는?
kubectl get pod myapp-xxx -o jsonpath='{.spec.containers[0].resources}'  # 리밋만 콕
```

내 로컬 YAML 파일과 클러스터의 `-o yaml`이 다른 경우가 생각보다 많습니다 — 적용을 깜빡했거나, 다른 파이프라인이 덮어썼거나. **의도(내 파일)와 현실(-o yaml)의 diff**가 곧 원인인 사건이 수두룩해요.

## ⑤ port-forward — 중간 단계 다 빼고 직통

Ingress → Service → Pod 어디가 문제인지 모를 때, **Pod에 직접 전화**를 걸어봅니다.

```bash
kubectl port-forward pod/myapp-xxx 8080:8080
# 내 노트북에서: curl localhost:8080/health

kubectl port-forward svc/myapp 8080:80        # Service 단계까지 포함해 테스트
```

Pod 직통은 되는데 Service 경유는 안 된다? → Service의 selector/포트 문제. Service는 되는데 Ingress는 안 된다? → Ingress 설정. **직통 전화로 구간을 반씩 잘라내는** 이분탐색이죠 — 계층 진단 글의 그 사고방식이 쿠버 안에서 반복되는 겁니다.

## 조합 루틴 — 증상별 첫 수

```
Pod가 안 뜸 (Pending/ImagePull...)  → ② describe (Events)
떴다가 죽음 (CrashLoop)             → ① logs --previous → ② Exit Code
떠 있는데 이상 동작                  → ① logs -f → ③ exec (설정·env·연결)
설정이 반영 안 된 느낌               → ④ get -o yaml 로 의도 vs 현실 diff
연결이 안 됨 (어디선가)              → ⑤ port-forward 이분탐색 + ③ nc
```

## 한 줄 정리

**logs(앱) → describe(쿠버) → exec(현장) → get -o yaml(설계도) → port-forward(직통).** 다섯 창을 순서대로 열면 쿠버 문제의 9할은 어느 창엔가 얼굴을 비춥니다. 화려한 도구 전에 이 다섯을 손에 익히세요.
