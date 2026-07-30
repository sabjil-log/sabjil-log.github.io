---
title: "죽였는데 포트가 안 풀린다 — Address already in use 3분 수사"
date: 2026-07-30
category: 트러블슈팅
tags: ["lsof", "포트", "Address already in use", "ss", "프로세스"]
summary: "분명 프로세스를 죽였는데 재시작하면 Address already in use. 범인은 셋 중 하나입니다 — 살아있는 자식, TIME_WAIT, 또는 엉뚱한 점유자."
---

> **한 줄 요약:** "죽였는데 포트가 안 풀린다"의 범인은 거의 항상 셋 중 하나입니다 — **① 부모만 죽고 살아남은 자식 프로세스, ② TIME_WAIT 잔상, ③ 애초에 딴 놈이 쓰고 있었음.** `ss -tlnp` 한 줄이면 셋을 즉시 가릅니다.

[[diagram:port-holders]]

## 상황

```bash
$ kill 12345 && ./run_server.sh
Error: listen EADDRINUSE: address already in use :::8080
```

방금 죽였는데요? 여기서 `kill -9`를 난사하거나 재부팅으로 도망가는 대신, 3분 수사를 합니다.

## 수사 1단계 — 지금 누가 잡고 있나

```bash
sudo ss -tlnp | grep :8080
# LISTEN 0 511 *:8080  users:(("node",pid=12401,fd=23))
```

**pid가 나온다 = 살아있는 누군가가 잡고 있다.** 게임 끝, 그 pid를 조사하면 됩니다. (구형 서버라면 `sudo lsof -i :8080` 도 같은 답을 줍니다.)

아무것도 안 나오는데 EADDRINUSE라면? 리스닝은 없는데 소켓 잔상이 남은 것 — 3단계(TIME_WAIT)로.

## 수사 2단계 — 그 pid의 정체

**케이스 A: 죽인 것과 같은 이름, 다른 pid — 자식이 살아남았다.**

가장 흔한 범인입니다. Node 클러스터, gunicorn/uWSGI 워커, `&`로 띄운 셸 스크립트의 자식 — **부모를 죽여도 자식은 죽지 않습니다.** 오히려 고아가 되어 init에 입양된 채 포트를 물고 버텨요.

```bash
ps -ef --forest | grep -A3 node     # 가족 관계도로 확인
# 해법: 프로세스 그룹째 죽이기
kill -- -$(ps -o pgid= -p 12401 | tr -d ' ')
# 또는 패턴으로 일괄
pkill -f "node server.js"
```

근본 대책은 **systemd로 띄우는 것** — `KillMode=control-group`(기본값)이 서비스의 자식들까지 한 cgroup으로 묶어 정리해줍니다. "kill 했는데 안 죽어요"류 문제의 절반이 systemd 이관으로 사라져요.

**케이스 B: 처음 보는 프로세스 — 애초에 선점자가 따로 있었다.**

내 앱이 죽은 이유 자체가 이놈 때문이었을 수 있습니다. 도커 프록시(`docker-proxy`)가 자주 등장하는 용의자 — 어떤 컨테이너가 `-p 8080`으로 그 포트를 물고 있는 거죠.

```bash
docker ps --format '{{.Names}}\t{{.Ports}}' | grep 8080
```

**케이스 C: pid는 없는데 안 열린다 — TIME_WAIT/FIN_WAIT 잔상.**

```bash
ss -tan | grep :8080 | awk '{print $1}' | sort | uniq -c
#   87 TIME-WAIT     ← 리스닝은 없고 잔상만
```

TIME_WAIT 글에서 본 그 "치우는 중 테이블"입니다. 몇 분 기다리면 풀리지만, 서버 재시작이 잦은 개발 환경에서 매번 기다릴 순 없죠. 정석 해법은 기다림이 아니라 **서버 코드에서 `SO_REUSEADDR`** — "치우는 중인 테이블이라도 내가 다시 앉겠다"는 소켓 옵션입니다.

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # bind 전에!
s.bind(("0.0.0.0", 8080))
```

대부분의 웹 프레임워크·서버(nginx, gunicorn, Node)는 기본으로 켜져 있어서, 이게 문제가 되는 건 주로 **직접 짠 소켓 코드**입니다. 반대로 말하면 — 내가 만든 데몬이 재시작 때마다 EADDRINUSE라면 십중팔구 이 옵션 누락이에요.

## 손버릇으로 만들 원라이너

```bash
# 이 포트, 지금 상황이 어떻게 되나 (리스닝+잔상 한 번에)
sudo ss -tanp | grep :8080

# 잡고 있는 놈을 찾아 바로 죽이기 (개발 환경 한정)
sudo fuser -k 8080/tcp
```

`fuser -k`는 편하지만 **무엇을 죽이는지 안 보여주고 죽입니다** — 운영 서버에선 반드시 ss/lsof로 정체 확인 후 처리하세요. C 케이스(잔상)에는 죽일 프로세스 자체가 없으니 효과도 없고요.

## 한 줄 정리

EADDRINUSE는 `ss -tlnp`로 시작합니다. **pid 있음 → 자식 생존(그룹째 kill, systemd 이관) 또는 선점자(도커 확인) / pid 없음 → TIME_WAIT 잔상(SO_REUSEADDR).** kill -9 난사와 재부팅은 수사를 포기하는 것 — 3분이면 범인이 나옵니다.
