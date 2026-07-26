---
title: "[그림 한 장] RAG 파이프라인 전체 — 문서가 답변이 되기까지"
date: 2026-07-21
category: AI/LLM
tags: ["RAG", "파이프라인", "임베딩", "리랭커", "시각화"]
summary: "청킹, 임베딩, 벡터검색, 리랭커, 근거 프롬프트 — 시리즈로 하나씩 다뤘던 부품을 움직이는 그림 한 장으로 조립했습니다. 이 그림이 곧 시리즈의 지도예요."
---

> **한 줄 요약:** RAG는 두 개의 흐름입니다 — 미리 해두는 **적재(문서→조각→벡터→창고)**와, 질문마다 도는 **검색(질문→후보 50→정예 5→근거와 함께 LLM)**. 아래 그림의 회색 점(적재)과 초록 점(질문)을 따라가면, 시리즈에서 다룬 모든 부품이 제자리에 보입니다.

## 전체 그림 — 두 개의 흐름

<div class="viz">
<svg viewBox="0 0 660 320" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="16" class="vz-cap">위 트랙(회색 점): 미리 적재 · 아래 트랙(초록 점): 질문마다 실행</text>

  <!-- ingestion track -->
  <rect x="10" y="40" width="90" height="46" rx="10" class="vz-box"/>
  <text x="55" y="59" text-anchor="middle" class="vz-label">문서</text>
  <text x="55" y="73" text-anchor="middle" class="vz-sub">위키·규정·매뉴얼</text>

  <rect x="140" y="40" width="100" height="46" rx="10" class="vz-box"/>
  <text x="190" y="59" text-anchor="middle" class="vz-label">청킹</text>
  <text x="190" y="73" text-anchor="middle" class="vz-sub">완결된 생각 단위</text>

  <rect x="280" y="40" width="100" height="46" rx="10" class="vz-box"/>
  <text x="330" y="59" text-anchor="middle" class="vz-label">임베딩</text>
  <text x="330" y="73" text-anchor="middle" class="vz-sub">뜻 → 벡터</text>

  <rect x="420" y="40" width="120" height="46" rx="10" class="vz-box-hi"/>
  <text x="480" y="59" text-anchor="middle" class="vz-label">벡터 DB</text>
  <text x="480" y="73" text-anchor="middle" class="vz-sub">ANN 인덱스 창고</text>

  <path d="M100,63 L140,63" class="vz-line"/>
  <path d="M240,63 L280,63" class="vz-line"/>
  <path d="M380,63 L420,63" class="vz-line"/>
  <circle r="4" fill="var(--faint)">
    <animateMotion dur="4.5s" repeatCount="indefinite" path="M100,63 L140,63 L240,63 L280,63 L380,63 L420,63"/>
  </circle>

  <!-- query track -->
  <rect x="10" y="170" width="90" height="46" rx="10" class="vz-box"/>
  <text x="55" y="189" text-anchor="middle" class="vz-label">질문</text>
  <text x="55" y="203" text-anchor="middle" class="vz-sub">"환불 수수료는?"</text>

  <rect x="140" y="170" width="100" height="46" rx="10" class="vz-box"/>
  <text x="190" y="189" text-anchor="middle" class="vz-label">임베딩</text>
  <text x="190" y="203" text-anchor="middle" class="vz-sub">같은 좌표계로</text>

  <rect x="280" y="170" width="100" height="46" rx="10" class="vz-box"/>
  <text x="330" y="189" text-anchor="middle" class="vz-label">1차 검색</text>
  <text x="330" y="203" text-anchor="middle" class="vz-sub">서류전형 top-50</text>

  <rect x="420" y="170" width="100" height="46" rx="10" class="vz-box"/>
  <text x="470" y="189" text-anchor="middle" class="vz-label">리랭커</text>
  <text x="470" y="203" text-anchor="middle" class="vz-sub">면접 → top-5</text>

  <rect x="555" y="164" width="95" height="58" rx="10" class="vz-box-hi"/>
  <text x="602" y="186" text-anchor="middle" class="vz-label">LLM</text>
  <text x="602" y="200" text-anchor="middle" class="vz-sub">근거만 보고 답변</text>
  <text x="602" y="212" text-anchor="middle" class="vz-sub">없으면 "모름"</text>

  <path d="M100,193 L140,193" class="vz-line-hi"/>
  <path d="M240,193 L280,193" class="vz-line-hi"/>
  <path d="M380,193 L420,193" class="vz-line-hi"/>
  <path d="M520,193 L555,193" class="vz-line-hi"/>
  <!-- vector DB feeds search -->
  <path d="M480,86 L480,150 C 480,162 460,166 430,170" class="vz-line" stroke-dasharray="4 3"/>
  <path d="M460,86 C 420,120 370,145 335,170" class="vz-line" stroke-dasharray="4 3"/>

  <circle r="4.5" class="vz-dot">
    <animateMotion dur="5s" repeatCount="indefinite" path="M100,193 L140,193 L240,193 L280,193 L380,193 L420,193 L520,193 L555,193"/>
  </circle>
  <!-- candidates shrinking: many small dots at search, few at rerank -->
  <circle r="3" class="vz-dot" opacity="0.35"><animateMotion dur="5s" begin="0.3s" repeatCount="indefinite" path="M280,208 L380,208 L420,208"/></circle>
  <circle r="3" class="vz-dot" opacity="0.35"><animateMotion dur="5s" begin="0.6s" repeatCount="indefinite" path="M280,180 L380,180 L420,180"/></circle>

  <text x="330" y="255" text-anchor="middle" class="vz-cap">점선: 창고(벡터 DB)가 1차 검색에 후보를 공급 · 후보 50 → 리랭커에서 5로 압축</text>
  <text x="330" y="300" text-anchor="middle" class="vz-cap">품질 문제가 생기면 — 어느 상자에서 새는지부터 찾는 게 RAG 디버깅입니다 (아래 표)</text>
</svg>
</div>

## 각 상자 = 시리즈의 한 편

이 그림은 사실 지난 글들의 목차입니다. 상자마다 무슨 일이 벌어지고, 뭘 조심해야 하는지 —

| 상자 | 하는 일 | 실패하면 생기는 증상 | 깊이 판 글 |
|---|---|---|---|
| 청킹 | 완결된 생각 단위로 자르기 | 잡음 섞임 / 문맥 끊김 | 청크 크기와 오버랩 |
| 임베딩 | 뜻을 벡터 좌표로 | 유사어를 못 묶음 | 코사인 유사도 |
| 벡터 DB | ANN으로 초고속 후보 공급 | 있는 문서가 후보에 안 듦 | 벡터 DB와 ANN |
| 1차 검색 | 넉넉하게 top-50 | k가 작으면 정답이 탈락 | 리랭커 (1차의 한계) |
| 리랭커 | 질문과 쌍으로 재채점 | 비슷한 오답이 상위 점령 | 리랭커 |
| LLM+근거 | 근거만 보고, 없으면 모른다 | 그럴듯한 지어내기 | 근거 지시와 환각 |

## 이 그림으로 디버깅하는 법

"답이 이상해요"는 진단이 아닙니다. 그림 위에서 **어느 상자가 새는지**를 좁혀야죠.

```
1. 정답이 문서에 존재하는가?           → 없으면 RAG 문제가 아님 (문서 문제)
2. 정답 청크가 top-50 안에 있는가?     → 없으면: 청킹 or 임베딩 or ANN 다이얼(k, ef)
3. top-50엔 있는데 top-5엔 없는가?    → 리랭커 문제 (모델 교체·후보 수 조정)
4. top-5엔 있는데 답이 틀리는가?      → 프롬프트 문제 (근거 지시·인용 강제)
```

포인트는 순서입니다 — 다들 4번(프롬프트)부터 만지는데, 실무 문제의 다수는 **2번(검색 재현율)**에 삽니다. 중간 산출물(top-50, top-5 목록)을 눈으로 볼 수 있게 로깅해두는 것, 그게 RAG 운영의 절반이에요.

## 두 트랙의 온도 차이도 기억하세요

- **위 트랙(적재)은 배치**: 문서가 바뀔 때만 돌면 됩니다. 여기서 공들인 청킹 품질이 아래 트랙 전체의 상한선을 정해요.
- **아래 트랙(질문)은 실시간**: 매 질문마다 도니 지연·비용이 여기 붙습니다. 1차는 넉넉히(빠르니까), 리랭커는 후보에만(느리니까) — 그 2단 구조의 이유죠.

## 한 줄 정리

RAG는 **적재 트랙(자르고→벡터로→창고에)**과 **질문 트랙(넓게 찾고→좁게 추리고→근거만 보고 답)**의 조립품입니다. 이 그림을 지도로 — 품질 문제는 상자 단위로 좁히고, 프롬프트보다 검색 재현율부터 의심하세요.
