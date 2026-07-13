---
title: "컨테이너에서 localhost가 안 통하는 이유 — 도커 네트워크의 착각"
date: 2026-07-14
category: 트러블슈팅
tags: ["Docker", "localhost", "네트워크", "bridge", "host.docker.internal"]
summary: "컨테이너 안의 localhost는 호스트가 아니라 컨테이너 자신입니다. '각자 다른 집'이라는 그림 하나만 잡히면 연결 문제의 대부분이 풀려요."
---

> **한 줄 요약:** 컨테이너 안에서 `localhost`는 **호스트 머신이 아니라 컨테이너 자기 자신**입니다. 컨테이너마다 자기만의 네트워크 공간(집)을 갖기 때문 — 호스트나 옆 컨테이너로 가려면 **다른 주소**로 불러야 해요.

## 증상 3종 세트

- 컨테이너 안 앱이 호스트에 띄운 DB(`localhost:5432`)에 연결 실패
- 컨테이너 A에서 컨테이너 B를 `localhost:8080`으로 호출했더니 connection refused
- 반대로, 컨테이너에서 서버를 띄웠는데 호스트 브라우저에서 `localhost`로 안 열림

전부 원인이 같습니다 — **localhost가 가리키는 곳이 서로 다르다**는 걸 놓친 거예요.

## 비유: 아파트의 각 세대

도커의 기본 네트워크(bridge)에서 컨테이너는 **각자 현관문과 주소가 있는 세대**입니다. 호스트는 그 아파트 건물이고요.

- 컨테이너 안에서 `localhost` = **우리 집 안** (자기 자신)
- 옆 컨테이너 = **옆집** — 옆집 주소(컨테이너 이름)로 불러야 함
- 호스트 = **건물 관리실** — 별도의 주소가 필요함

우리 집에서 "여기요(localhost)!"라고 외쳐봐야 옆집이나 관리실에는 안 들립니다.

## 케이스별 해법

**① 컨테이너 → 호스트의 서비스**

```bash
# Mac/Windows (Docker Desktop): 예약된 이름 사용
psql -h host.docker.internal -p 5432

# Linux: 기본으론 이 이름이 없음 → 실행 시 매핑 추가
docker run --add-host=host.docker.internal:host-gateway myapp
```

한 가지 더 — 호스트 쪽 서비스가 `127.0.0.1`에만 바인딩돼 있으면 컨테이너에서 못 붙습니다. `0.0.0.0`으로 듣게 하세요. (헬스체크 글에서 본 그 바인딩 문제와 같은 뿌리입니다.)

**② 컨테이너 → 컨테이너**

localhost가 아니라 **컨테이너 이름**으로 부릅니다. 단, 같은 사용자 정의 네트워크에 있어야 이름 해석이 됩니다.

```bash
docker network create mynet
docker run -d --name db  --network mynet postgres
docker run -d --name app --network mynet myapp
# app 안에서: psql -h db -p 5432   ← "db"라는 이름이 곧 주소
```

docker-compose를 쓰면 서비스들이 자동으로 한 네트워크에 묶여서, **서비스 이름이 곧 호스트명**이 됩니다. compose 파일의 `db:` 서비스는 그냥 `db`로 부르면 돼요.

**③ 호스트 → 컨테이너**

컨테이너의 포트는 기본적으로 아파트 담장 안입니다. `-p`로 **포트를 건물 외벽에 내놔야** 호스트에서 접근됩니다.

```bash
docker run -d -p 8080:80 nginx
# 호스트에서: curl localhost:8080  → 컨테이너의 80으로 전달
# -p 를 안 했으면 호스트에서 접근 불가가 정상
```

## 확인하는 법

```bash
docker network ls                               # 네트워크 목록
docker inspect app --format '{{json .NetworkSettings.Networks}}' | python3 -m json.tool
# 어느 네트워크 소속인지, IP가 뭔지

docker exec -it app sh -c "getent hosts db"    # 컨테이너 안에서 이름이 풀리는지
docker exec -it app sh -c "nc -vz db 5432"     # 옆집 포트가 열려 있는지
```

②가 안 될 때 십중팔구는 **두 컨테이너가 다른 네트워크에 있는** 경우입니다. inspect로 소속부터 확인하세요.

## 예외: --network host

`docker run --network host` 를 쓰면 컨테이너가 자기 집을 포기하고 **호스트의 네트워크를 그대로** 씁니다. 이때는 localhost가 정말 호스트를 가리켜요. 담장이 없어져 편하지만 포트 충돌·격리 상실이 따라오고, Linux에서만 온전히 동작합니다. "왜 어떤 서버에선 localhost가 되지?"의 범인이 대개 이 모드예요.

## 한 줄 정리

컨테이너의 localhost는 **자기 자신**입니다. 호스트는 `host.docker.internal`, 옆 컨테이너는 **같은 네트워크 + 컨테이너 이름**, 호스트에서 컨테이너는 `-p` 포트 공개 — 이 세 주소 체계만 잡으면 도커 연결 문제의 8할이 사라집니다.
