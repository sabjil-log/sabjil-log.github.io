---
title: "CrashLoopBackOff — 쿠버네티스가 '재시도 중'이라고 말하는 방식"
date: 2026-07-13
category: 트러블슈팅
tags: ["Kubernetes", "CrashLoopBackOff", "kubectl", "Pod", "디버깅"]
summary: "CrashLoopBackOff는 병명이 아니라 증상입니다. '컨테이너가 죽어서 점점 천천히 재시도 중'이라는 뜻 — 진짜 원인 찾는 순서를 정리했어요."
---

> **한 줄 요약:** CrashLoopBackOff는 에러의 **원인이 아니라 상태**입니다. "컨테이너가 시작하자마자 죽어서, 쿠버네티스가 **점점 간격을 늘려가며 재시도 중**"이라는 뜻이에요. 원인은 따로 찾아야 하고, 찾는 순서가 있습니다.

## 이 상태의 정체

```bash
kubectl get pods
# NAME        READY   STATUS             RESTARTS   AGE
# myapp-xxx   0/1     CrashLoopBackOff   7          10m
```

비유하면 이렇습니다. 시동이 꺼지는 차를 계속 다시 걸어보는 건데, 매번 바로 꺼지니까 **"좀 기다렸다 다시 걸어보자"** 하며 대기 시간을 10초 → 20초 → 40초… 점점 늘리는(BackOff) 상태. `RESTARTS` 숫자가 그 재시도 횟수입니다. 차가 왜 꺼지는지는 이 상태명이 말해주지 않아요 — 우리가 봐야 합니다.

## 1순위 — 죽기 직전에 뭐라고 했나

가장 많은 정보는 컨테이너의 **마지막 유언(로그)**에 있습니다. 핵심은 `--previous` — 지금 도는(방금 재시작된) 컨테이너 말고 **직전에 죽은** 컨테이너의 로그를 봐야 해요.

```bash
kubectl logs myapp-xxx --previous
# 앱의 스택트레이스, "config not found", "connection refused" 등
# 십중팔구 여기서 답이 나옵니다
```

앱이 로그를 남길 새도 없이 죽으면 출력이 비어 있을 수 있습니다. 그럼 2순위로.

## 2순위 — 쿠버네티스가 본 사망 정황

```bash
kubectl describe pod myapp-xxx
```

여기서 볼 곳은 두 군데입니다.

- **Last State / Exit Code:**
  - `Exit Code: 1` — 앱이 스스로 에러로 종료 (설정 오류, 예외)
  - `Exit Code: 137` — **외부에서 죽임 당함.** `Reason: OOMKilled` 면 메모리 한도 초과가 범인
  - `Exit Code: 127` / `Error: executable not found` — 명령어/엔트리포인트 오타
- **Events (하단):** 이미지 풀 실패, 볼륨/ConfigMap 마운트 실패, 프로브 실패가 여기 찍힙니다.

## 범인 톱4와 각각의 대처

**① 설정/시크릿 누락** — 로그에 "env not set", "config not found". ConfigMap/Secret 이름 오타, 키 누락이 대부분.

```bash
kubectl get configmap,secret            # 참조하는 게 실제로 존재하는지
kubectl exec -it myapp-xxx -- env | sort   # (잠깐 떠있는 사이) 주입된 env 확인
```

**② OOMKilled (137)** — 메모리 limit이 앱의 실제 사용량보다 작음. limit을 올리거나 앱 메모리를 줄입니다. JVM처럼 힙 옵션이 별도인 런타임은 limit과 힙 설정을 **같이** 맞춰야 해요.

**③ liveness 프로브가 성급함** — 앱은 정상 기동 중인데 헬스체크가 너무 일찍/빡빡하게 찔러서 쿠버네티스가 "죽었네" 하고 재시작시키는 경우. describe의 Events에 `Liveness probe failed`가 반복되면 이 케이스입니다. `initialDelaySeconds`를 앱 기동 시간보다 넉넉히 주거나 `startupProbe`를 도입하세요. 로드밸런서 헬스체크 3대장과 같은 원리가 Pod 안에서도 벌어지는 셈이죠.

**④ 의존 서비스 미준비** — DB가 아직 안 떠서 connection refused로 사망 → 재시작 → 또 사망. 앱에 재시도 로직을 넣거나 initContainer로 의존성 대기를 거는 게 정석입니다.

## 그래도 모르겠으면 — 시동 끄고 타보기

컨테이너가 계속 죽으니 안에 들어가 볼 수가 없죠. 그럴 땐 **엔트리포인트를 잠재우고** 쉘로 들어가 손으로 실행해봅니다.

```bash
kubectl run debug --rm -it --image=<같은이미지> --command -- sleep 3600
kubectl exec -it debug -- sh
# 안에서 원래 명령을 직접 실행 → 에러를 눈으로 확인
```

## 한 줄 정리

CrashLoopBackOff를 보면 반사적으로 이 순서: **`logs --previous` (유언) → `describe` (Exit Code·Events) → 톱4 대조 (설정·OOM 137·프로브·의존성)**. 상태명에 겁먹지 마세요 — 그건 그냥 "재시도 중"이라는 뜻입니다.
