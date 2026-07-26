---
title: "[그림 한 장] 요청 한 번의 VPC 여정 — 클릭에서 응답까지 무슨 일이 벌어지나"
date: 2026-07-21
category: 클라우드
tags: ["VPC", "로드밸런서", "ACG", "NAT", "아키텍처", "시각화"]
summary: "사용자가 버튼을 누른 순간부터 응답이 돌아오기까지 — DNS, LB, 방화벽, private 서브넷, DB, NAT이 각자 무슨 일을 하는지 움직이는 그림 하나에 담았습니다."
---

> **한 줄 요약:** 버튼 클릭 한 번에 요청은 **DNS → 로드밸런서(public) → 방화벽(ACG) → WAS(private) → DB**를 지나 되돌아오고, 서버가 밖에 나갈 땐 **NAT**이라는 뒷문을 씁니다. 그동안 따로 다뤘던 부품들을 그림 한 장에 조립했어요 — 초록 점(요청/응답)과 주황 점(아웃바운드)을 따라가 보세요.

## 전체 그림 — 움직이는 여정

<div class="viz">
<svg viewBox="0 0 660 300" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="16" class="vz-cap">초록 점: 사용자 요청→응답 왕복 · 주황 점: 서버가 외부 API로 나가는 길(NAT)</text>

  <!-- VPC boundary -->
  <rect x="150" y="28" width="500" height="258" rx="14" fill="none" stroke="var(--faint)" stroke-dasharray="6 4" stroke-width="1.2"/>
  <text x="160" y="44" class="vz-cap">VPC 10.0.0.0/16</text>

  <!-- public subnet -->
  <rect x="165" y="52" width="200" height="222" rx="10" fill="none" stroke="var(--line)" stroke-width="1.2"/>
  <text x="175" y="67" class="vz-cap">public 서브넷 (IGW 경로 있음)</text>
  <!-- private subnet -->
  <rect x="385" y="52" width="250" height="222" rx="10" fill="none" stroke="var(--line)" stroke-width="1.2"/>
  <text x="395" y="67" class="vz-cap">private 서브넷 (인터넷 직통 없음)</text>

  <!-- user -->
  <rect x="10" y="120" width="90" height="46" rx="10" class="vz-box"/>
  <text x="55" y="139" text-anchor="middle" class="vz-label">사용자</text>
  <text x="55" y="153" text-anchor="middle" class="vz-sub">shop.com 클릭</text>

  <!-- LB -->
  <rect x="185" y="112" width="120" height="52" rx="10" class="vz-box-hi"/>
  <text x="245" y="132" text-anchor="middle" class="vz-label">Load Balancer</text>
  <text x="245" y="147" text-anchor="middle" class="vz-sub">TLS 종료 · 헬스체크</text>

  <!-- NAT -->
  <rect x="195" y="205" width="100" height="46" rx="10" class="vz-box"/>
  <text x="245" y="224" text-anchor="middle" class="vz-label">NAT GW</text>
  <text x="245" y="238" text-anchor="middle" class="vz-sub">나가기 전용 문</text>

  <!-- WAS -->
  <rect x="405" y="112" width="105" height="52" rx="10" class="vz-box-hi"/>
  <text x="457" y="132" text-anchor="middle" class="vz-label">WAS</text>
  <text x="457" y="147" text-anchor="middle" class="vz-sub">ACG: LB에서만 8080</text>

  <!-- DB -->
  <rect x="530" y="112" width="95" height="52" rx="10" class="vz-box"/>
  <text x="577" y="132" text-anchor="middle" class="vz-label">DB</text>
  <text x="577" y="147" text-anchor="middle" class="vz-sub">ACG: WAS만 5432</text>

  <!-- external API -->
  <rect x="10" y="205" width="90" height="46" rx="10" class="vz-box"/>
  <text x="55" y="224" text-anchor="middle" class="vz-label">외부 API</text>
  <text x="55" y="238" text-anchor="middle" class="vz-sub">결제사 등</text>

  <!-- edges: request path -->
  <path d="M100,138 L185,138" class="vz-line-hi"/>
  <path d="M305,138 L405,138" class="vz-line-hi"/>
  <path d="M510,138 L530,138" class="vz-line-hi"/>
  <!-- outbound path WAS→NAT→ext -->
  <path d="M405,155 C 340,175 300,200 295,222" class="vz-line"/>
  <path d="M195,228 L100,228" class="vz-line"/>

  <!-- request dot: round trip -->
  <circle r="4.5" class="vz-dot">
    <animateMotion dur="6s" repeatCount="indefinite"
      path="M100,138 L185,138 L305,138 L405,138 L510,138 L530,138 L510,138 L405,138 L305,138 L185,138 L100,138"/>
  </circle>
  <!-- outbound dot -->
  <circle r="4" class="vz-dot2">
    <animateMotion dur="5s" begin="1.2s" repeatCount="indefinite"
      path="M420,158 C 350,180 300,205 295,225 L195,228 L100,228 L195,228 L295,225"/>
  </circle>

  <text x="330" y="296" text-anchor="middle" class="vz-cap">DB는 인터넷과 어떤 직선도 없다는 것 — 이 그림에서 가장 중요한 '없는 선'</text>
</svg>
</div>

## 여정을 단계별로 — 각 부품이 하는 일

**① DNS (그림 밖 0단계):** `shop.com` → LB의 주소. 사용자는 서버가 아니라 **항상 LB를** 바라봅니다.

**② LB (public 서브넷):** 유일하게 인터넷을 정면으로 만나는 부품. TLS를 여기서 풀고(인증서 관리 일원화), 헬스체크로 살아있는 WAS만 골라 넘깁니다. L7 분기가 필요하면 ALB — 그 선택 기준은 ALB vs NLB 글에.

**③ ACG 통과:** WAS의 방문 경비는 "LB의 ACG에서 오는 8080만" 허용. IP가 아니라 **역할(ACG 체이닝)**로 열려 있어서 LB가 몇 대로 늘든 규칙은 그대로입니다.

**④ WAS (private 서브넷):** 인터넷으로 가는 라우팅 경로 자체가 없는 층. 공격자가 WAS 주소를 알아내도 **직접 닿을 길이 없습니다.**

**⑤ DB:** 한 겹 더 깊이. "WAS의 ACG에서 오는 5432만". 그림에서 DB와 인터넷 사이에 **선이 하나도 없다**는 것 — 이 아키텍처의 존재 이유입니다.

**⑥ 응답 왕복:** 온 길을 그대로 되돌아갑니다. ACG는 스테이트풀이라 응답 규칙은 따로 필요 없죠(NACL을 조였다면 임시 포트 — 그 총정리 글).

**⑦ 주황 점, 뒷문:** WAS가 결제사 API를 부를 땐 NAT을 경유해 **NAT의 공인 IP로** 나갑니다. 나가는 건 되지만 밖에서 이 문으로 들어올 수는 없고(장부 구조), 지나가는 GB마다 요금이 붙는다는 것까지 — NAT 글의 그 얘기입니다.

## 이 그림으로 장애를 읽는 법

이제 장애 증상을 그림 위의 "끊긴 화살표"로 번역할 수 있습니다.

```
사이트 전체 안 열림          → ①~② 구간: DNS(dig) / LB 상태
간헐적 502·UNHEALTHY        → ②~③ 구간: 헬스체크 3대장 (포트·경로·방화벽)
WAS는 뜨는데 기능 오류       → ④~⑤ 구간: WAS→DB (Pod의 눈으로 nc 5432)
결제·외부 연동만 실패        → ⑦ 구간: NAT 라우팅, 외부사 허용목록에 NAT IP인지
```

진단 도구 배치도 그대로예요 — 구간을 반씩 자르는 이분탐색(curl --resolve, port-forward의 사고방식), 애매하면 그 지점에서 tcpdump.

## 한 줄 정리

좋은 VPC 설계는 그림에 **선이 적은** 설계입니다 — 인터넷을 만나는 건 LB뿐, DB는 어떤 직선도 없음, 나가는 길은 NAT 하나. 이 그림을 머리에 넣어두면, 장애는 "어느 화살표가 끊겼나"라는 좌표 문제가 됩니다.
