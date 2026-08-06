---
title: "쿠버네티스 requests와 limits — 예약석과 천장은 다르다"
date: 2026-08-07
category: 트러블슈팅
tags: ["Kubernetes", "requests", "limits", "OOMKilled", "스로틀링", "QoS"]
summary: "왜 둘 다 있고, 왜 다르게 잡으라는 걸까요. requests는 스케줄러의 예약, limits는 런타임의 천장 — 이 구분에서 OOMKilled와 스로틀링의 정체까지 풀립니다."
---

> **한 줄 요약:** **requests는 예약석**(스케줄러가 "이만큼 빈 노드"를 찾는 기준), **limits는 천장**(런타임이 "여기까지만"을 집행하는 상한)입니다. 예약보다 덜 쓰는 건 자유, 천장을 치면 — **CPU는 감속(스로틀), 메모리는 즉사(OOMKilled 137)**. 이 비대칭이 설정 요령의 전부예요.

[[diagram:requests-limits]]

## 왜 두 개인가 — 극장 비유

Pod를 극장 관객이라 합시다.

- **requests** = **예매한 좌석 수.** 극장(노드)은 예매 합계가 좌석 수를 넘지 않게만 입장시킵니다. 스케줄러가 보는 건 **이 숫자뿐** — 실제로 얼마나 쓰는지가 아니라, 얼마나 예약했는지로 배치를 결정해요.
- **limits** = **한 사람이 최대로 차지할 수 있는 좌석 수.** 옆자리가 비면 팔걸이 넘어 넓게 앉아도 되는데(버스트), 이 천장까지만.

둘을 나눈 이유가 여기 있습니다 — **배치는 보수적으로(예약 기준), 실행은 유연하게(빈 자원 활용).** 하나로 합치면 이 유연성이 사라지죠.

## 천장을 치면: CPU와 메모리의 결정적 차이

**CPU limits 도달 → 스로틀링(감속).** CPU는 압축 가능한 자원이라, 천장을 치면 커널이 그 컨테이너를 **잠깐씩 멈춰가며** 할당량 안에 가둡니다. 죽지는 않는데 **느려집니다** — p95가 이유 없이 튀는데 CPU 사용률 그래프는 멀쩡해 보이는 미스터리의 단골 범인. 사용률이 아니라 **스로틀 지표**(`container_cpu_cfs_throttled_*`)를 봐야 잡힙니다.

**메모리 limits 도달 → OOMKilled(즉사).** 메모리는 뺏을 수 없는 자원이라 감속이 불가능 — 천장을 치는 순간 컨테이너가 죽습니다. CrashLoopBackOff 글의 **Exit Code 137**, OOM Killer 글의 cgroup 버전이 바로 이겁니다. describe에서 `Last State: OOMKilled`가 그 사망진단서고요.

이 비대칭에서 실무 정석이 나옵니다.

```yaml
resources:
  requests:
    cpu: 250m        # 예약 — 평상시 사용량 기준
    memory: 512Mi
  limits:
    memory: 512Mi    # 메모리: requests = limits (즉사 예방이 최우선)
    # cpu limits는 생략 — 스로틀링 미스터리를 피하고 버스트 허용
```

- **메모리는 requests=limits**로: 예약만큼은 확실히 보장받고, 천장 초과 즉사의 변수를 없앱니다.
- **CPU limits는 생략(또는 넉넉히)**이 요즘 통설: 남는 CPU를 쓰는 건 공짜 성능이고, 필요하면 스로틀 대신 이웃의 requests가 보장선을 지켜줍니다. (멀티테넌트처럼 공평성이 계약인 환경은 예외.)

## requests가 만드는 두 번째 문제: Pending과 과예약

requests는 스케줄링의 화폐라서, 잘못 잡으면 두 방향으로 사고가 납니다.

- **너무 크게** → 노드가 실제론 한가한데 "예약 합계가 꽉 차서" 새 Pod가 **Pending**(kubectl 글의 describe Events에 `Insufficient cpu`). 극장이 텅 비었는데 예매가 매진인 상황 — 오토스케일링 비용도 이 허수 기준으로 불어납니다.
- **너무 작게** → 배치는 잘 되는데 다 같이 진짜로 쓰기 시작하면 노드가 붐빕니다. 이때 누굴 먼저 쫓아내는가가 **QoS 등급** — requests=limits면 Guaranteed(마지막까지 보호), 아니면 Burstable, 둘 다 없으면 BestEffort(1순위 퇴출). 메모리 requests=limits 권장에는 이 보호 등급 확보의 의미도 있습니다.

적정값은 관측에서 나옵니다 — `kubectl top pod`로 실제 사용량을 보고, **requests는 평상시 사용량 근처, 메모리 limits는 피크+여유**로. 감이 아니라 지표로 (평가 루프 글의 그 원칙이 리소스에도).

## 진단 치트시트

```
Pod가 Pending            → describe Events: Insufficient cpu/memory → requests 과예약 점검
137 / OOMKilled          → 메모리 limits 도달 → 피크 관측 후 상향 (누수면 코드 — 우상향 판별법)
느린데 CPU는 한가해 보임   → 스로틀 지표 확인 → cpu limits 제거/상향
노드는 한가한데 배치 안 됨 → kubectl describe node: Allocated resources (예약 합계) 확인
```

## 한 줄 정리

**requests = 스케줄러의 예약, limits = 런타임의 천장.** 천장의 결과는 CPU 감속 / 메모리 즉사로 다르니 — **메모리는 requests=limits, CPU limits는 신중하게(대개 생략).** 그리고 숫자는 감이 아니라 `kubectl top`과 스로틀 지표가 정해줍니다.
