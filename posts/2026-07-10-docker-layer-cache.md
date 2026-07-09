---
title: "도커 빌드가 매번 느린 이유 — 이미지 레이어와 캐시, Dockerfile 순서의 비밀"
date: 2026-07-10
category: 트러블슈팅
tags: ["Docker", "이미지레이어", "빌드캐시", "Dockerfile"]
summary: "도커 이미지는 층층이 쌓인 레이어입니다. 이 구조를 알면 Dockerfile 한 줄 순서만 바꿔도 빌드가 몇 배 빨라져요."
---

> **한 줄 요약:** 도커 이미지는 **층층이 쌓인 레이어**입니다. 빌드는 바뀐 층부터 다시 만들기 때문에, **잘 안 바뀌는 걸 아래에, 자주 바뀌는 걸 위에** 두면 캐시가 살아나 빌드가 확 빨라집니다.

## 이런 적 있으신가요

코드 한 줄 고쳤을 뿐인데 `docker build`가 라이브러리를 처음부터 다시 깝니다. 매번 몇 분씩. "아무것도 안 바뀐 부분인데 왜 또 받지?" 싶죠. 원인은 **레이어 순서**입니다.

## 비유: 투명 필름을 겹치는 것

이미지는 투명 필름(레이어)을 아래부터 위로 겹쳐 만든 그림입니다. Dockerfile의 명령 한 줄이 필름 한 장이에요.

- `FROM` → 바탕 필름
- `RUN apt install ...` → 그 위에 한 장
- `COPY . .` → 또 그 위에 한 장

도커는 빌드할 때 **어떤 필름부터 바뀌었는지** 봅니다. 바뀐 필름과 **그 위의 모든 필름**은 다시 그리고, 그 아래는 **캐시**를 재사용합니다.

## 그래서 순서가 전부다

문제는 이런 Dockerfile입니다.

```dockerfile
FROM python:3.12-slim
COPY . .                      # 코드가 여기서 통째로 들어옴
RUN pip install -r requirements.txt
```

코드를 한 줄만 고쳐도 `COPY . .` 필름이 바뀌고, **그 위의 `pip install`도 무효화**됩니다. 그래서 매번 라이브러리를 새로 깔죠.

순서만 바꾸면 해결됩니다.

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .        # 의존성 목록만 먼저
RUN pip install -r requirements.txt   # 목록이 안 바뀌면 이 층은 캐시!
COPY . .                       # 자주 바뀌는 코드는 맨 마지막
```

이제 `requirements.txt`가 그대로면 `pip install` 층은 캐시가 유지되고, 코드만 다시 복사됩니다. 빌드가 몇 분 → 몇 초로 줄어요.

## 확인하는 법

빌드 로그에서 `CACHED` 표시를 보면 어느 층이 재사용됐는지 바로 압니다.

```bash
docker build -t myapp .
#  => [2/4] COPY requirements.txt .        CACHED
#  => [3/4] RUN pip install -r ...         CACHED   ← 이게 목표
#  => [4/4] COPY . .

docker history myapp           # 레이어별 크기와 명령 확인
```

## 팁 하나 더

`RUN` 을 여러 줄로 쪼개면 그만큼 필름이 늘어 이미지가 커집니다. 관련 명령은 `&&` 로 묶고, 캐시 정리까지 한 층에서 끝내세요.

```dockerfile
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
```

## 한 줄 정리

도커 이미지는 겹겹의 필름이고, 빌드는 **바뀐 층부터 위로** 다시 그립니다. **안 바뀌는 것(의존성)은 아래, 자주 바뀌는 것(코드)은 위** — 이 순서 하나로 빌드 속도가 갈립니다.
