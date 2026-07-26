---
title: "[그림 한 장] 쿠버네티스 Service와 Ingress — 트래픽이 Pod까지 가는 길"
date: 2026-07-21
category: 네트워크
tags: ["Kubernetes", "Service", "Ingress", "ClusterIP", "시각화"]
summary: "Ingress는 도메인·경로를 보는 정문 안내판, Service는 갈아타는 Pod들의 고정 전화번호. 움직이는 그림 한 장으로 트래픽의 전체 여정을 담았어요."
---

> **한 줄 요약:** Pod는 수시로 죽고 다시 태어나며 IP가 바뀝니다. **Service는 그 변덕스러운 Pod들 앞의 고정 전화번호**(+로드밸런싱), **Ingress는 도메인·경로를 읽고 알맞은 Service로 안내하는 정문 안내판**입니다. 아래 그림에서 초록 점(요청)의 여정을 따라가 보세요.

## 전체 여정 — 움직이는 그림

<div class="viz">
<svg viewBox="0 0 660 250" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="18" class="vz-cap">인터넷 → Ingress → Service → Pod : 초록 점이 실제 요청의 경로</text>
  <!-- nodes -->
  <rect x="10" y="95" width="90" height="46" rx="10" class="vz-box"/>
  <text x="55" y="114" text-anchor="middle" class="vz-label">사용자</text>
  <text x="55" y="128" text-anchor="middle" class="vz-sub">api.shop.com/cart</text>

  <rect x="150" y="95" width="110" height="46" rx="10" class="vz-box-hi"/>
  <text x="205" y="114" text-anchor="middle" class="vz-label">Ingress</text>
  <text x="205" y="128" text-anchor="middle" class="vz-sub">호스트·경로 라우팅</text>

  <rect x="320" y="40" width="110" height="42" rx="10" class="vz-box-hi"/>
  <text x="375" y="57" text-anchor="middle" class="vz-label">Service: cart</text>
  <text x="375" y="71" text-anchor="middle" class="vz-sub">ClusterIP 고정</text>

  <rect x="320" y="160" width="110" height="42" rx="10" class="vz-box"/>
  <text x="375" y="177" text-anchor="middle" class="vz-label">Service: pay</text>
  <text x="375" y="191" text-anchor="middle" class="vz-sub">/pay 는 이쪽</text>

  <rect x="500" y="14" width="130" height="34" rx="10" class="vz-box"/>
  <text x="565" y="35" text-anchor="middle" class="vz-label">Pod cart-a</text>
  <rect x="500" y="58" width="130" height="34" rx="10" class="vz-box"/>
  <text x="565" y="79" text-anchor="middle" class="vz-label">Pod cart-b</text>
  <rect x="500" y="102" width="130" height="34" rx="10" class="vz-box" stroke-dasharray="4 3"/>
  <text x="565" y="123" text-anchor="middle" class="vz-sub">cart-c (재생성 중…)</text>

  <!-- edges -->
  <path d="M100,118 L150,118" class="vz-line-hi"/>
  <path d="M260,112 C 295,100 295,72 320,64" class="vz-line-hi"/>
  <path d="M260,124 C 295,140 295,172 320,180" class="vz-line"/>
  <path d="M430,55 C 470,48 470,33 500,31" class="vz-line-hi"/>
  <path d="M430,66 C 470,70 470,75 500,75" class="vz-line-hi"/>

  <!-- moving request: user→ingress→cart svc→pod a -->
  <circle r="4.5" class="vz-dot">
    <animateMotion dur="4s" repeatCount="indefinite"
      path="M100,118 L150,118 L260,112 C 295,100 295,72 320,64 L430,58 C 470,50 470,33 500,31"/>
  </circle>
  <!-- second request load-balanced to pod b -->
  <circle r="4.5" class="vz-dot" opacity="0.75">
    <animateMotion dur="4s" begin="2s" repeatCount="indefinite"
      path="M100,118 L150,118 L260,112 C 295,100 295,72 320,64 L430,64 C 470,70 470,75 500,75"/>
  </circle>
  <text x="375" y="235" text-anchor="middle" class="vz-cap">같은 Service로 온 요청이 살아있는 Pod들로 번갈아 분배됩니다 (cart-c는 죽어도 무영향)</text>
</svg>
</div>

그림에서 봐야 할 세 가지 —

1. **Ingress가 갈림길**: `/cart`는 cart Service로, `/pay`는 pay Service로. 도메인·경로를 **읽고** 분기합니다(ALB의 L7 라우팅과 같은 일을 클러스터 안에서 하는 것).
2. **Service가 완충지대**: 요청은 Pod의 IP를 모릅니다. Service의 고정 주소로만 가고, Service가 그 순간 살아있는 Pod에게 분배해요.
3. **Pod 하나가 죽어도(점선 상자) 여정은 무사**: Service가 죽은 Pod를 분배 대상에서 빼버리니까요.

## 왜 Service가 필요한가 — 30초 논리

Pod의 IP로 직접 통신한다고 해봅시다. Pod가 재시작하면(CrashLoop, 배포, 스케일링) IP가 바뀝니다 → 클라이언트가 들고 있던 주소는 사망 → 매번 새 주소를 알아내야 함. **전화번호가 매일 바뀌는 가게**랑 거래하는 셈이죠.

Service는 여기에 **대표번호**를 답으로 내놓습니다. `cart` Service를 만들면 고정 가상 IP(ClusterIP)와 DNS 이름(`cart`)이 생기고, 레이블이 맞는 Pod들을 **자동으로 추적**하며 트래픽을 나눠줍니다. 도커 컨테이너끼리 이름으로 부르던 그 편리함의 클러스터 버전입니다.

```yaml
apiVersion: v1
kind: Service
metadata: { name: cart }
spec:
  selector: { app: cart }     # 이 레이블을 단 Pod들이 분배 대상
  ports: [{ port: 80, targetPort: 8080 }]
```

## Service의 세 단계 노출 범위

<div class="viz">
<svg viewBox="0 0 660 150" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="30" width="195" height="90" rx="10" class="vz-box"/>
  <text x="107" y="55" text-anchor="middle" class="vz-label">ClusterIP</text>
  <text x="107" y="75" text-anchor="middle" class="vz-sub">클러스터 안에서만</text>
  <text x="107" y="90" text-anchor="middle" class="vz-sub">내부 서비스 간 통신 (기본값)</text>

  <rect x="232" y="30" width="195" height="90" rx="10" class="vz-box"/>
  <text x="329" y="55" text-anchor="middle" class="vz-label">NodePort</text>
  <text x="329" y="75" text-anchor="middle" class="vz-sub">모든 노드의 3만번대 포트로</text>
  <text x="329" y="90" text-anchor="middle" class="vz-sub">간이 외부 노출 (테스트용)</text>

  <rect x="454" y="30" width="195" height="90" rx="10" class="vz-box-hi"/>
  <text x="551" y="55" text-anchor="middle" class="vz-label">LoadBalancer</text>
  <text x="551" y="75" text-anchor="middle" class="vz-sub">클라우드 LB 자동 생성</text>
  <text x="551" y="90" text-anchor="middle" class="vz-sub">프로덕션 외부 노출</text>

  <path d="M205,75 L232,75" class="vz-line"/>
  <path d="M427,75 L454,75" class="vz-line"/>
  <text x="330" y="140" text-anchor="middle" class="vz-cap">오른쪽으로 갈수록 바깥에 많이 노출 — 필요한 만큼만 여세요</text>
</svg>
</div>

## 그럼 Ingress는 왜 또 필요한가

Service마다 LoadBalancer 타입을 쓰면 **서비스 수만큼 클라우드 LB가** 생깁니다 — LB는 공짜가 아니죠(비용 글 참조). Ingress는 **LB 하나를 정문으로 두고**, 그 뒤에서 호스트·경로 규칙으로 여러 Service에 나눠주는 계층입니다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
spec:
  rules:
  - host: api.shop.com
    http:
      paths:
      - path: /cart
        pathType: Prefix
        backend: { service: { name: cart, port: { number: 80 } } }
      - path: /pay
        pathType: Prefix
        backend: { service: { name: pay, port: { number: 80 } } }
```

주의 하나 — Ingress 리소스는 **규칙(안내판)일 뿐**, 실제로 일하는 건 Ingress Controller(nginx 등)입니다. 컨트롤러가 설치 안 된 클러스터에서 Ingress만 만들고 "왜 안 되지" 하는 게 단골 사고예요.

## 안 될 때 — 이분탐색 복습

kubectl 글의 port-forward 이분탐색이 정확히 이 그림 위에서 돕니다: **Pod 직통 OK? → Service 경유 OK? → Ingress 경유 OK?** 어느 구간에서 끊기는지 = 그림에서 어느 화살표가 죽었는지. Service 단계에서 끊기면 십중팔구 selector 레이블 오타입니다(`kubectl get endpoints cart` 가 비어 있으면 확진).

## 한 줄 정리

**Pod는 변덕, Service는 고정 대표번호, Ingress는 정문 안내판.** 그림의 초록 점 여정 — 정문에서 경로 읽고, 대표번호로 가고, 살아있는 Pod가 받는다 — 이 세 단계가 쿠버 네트워킹의 뼈대입니다.
