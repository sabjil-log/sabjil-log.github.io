---
title: "systemd 서비스가 자꾸 죽을 때 — journalctl로 원인 찾는 순서"
date: 2026-07-13
category: 리눅스
tags: ["systemd", "journalctl", "systemctl", "서비스", "디버깅"]
summary: "서비스가 죽었다는 사실은 알겠는데 왜 죽었는지 모르겠다면, 볼 곳은 정해져 있습니다. status → journalctl -u → 원인별 대처 순서를 정리했어요."
---

> **한 줄 요약:** 서비스가 죽으면 **`systemctl status`로 사망 요약 → `journalctl -u 서비스명`으로 유언 전문** 순서로 봅니다. 죽는 이유의 대부분은 **앱 에러 / OOM / 의존성·권한 / 재시작 한도 초과** 넷 중 하나예요.

## 상황

```bash
systemctl status myapp
# ● myapp.service - My Application
#    Active: failed (Result: exit-code) since ...
#    Process: 1234 ExecStart=/usr/bin/myapp (code=exited, status=1/FAILURE)
```

`failed`까진 알겠는데, 그래서 **왜**? 쿠버네티스의 CrashLoopBackOff와 똑같은 상황이 맨 리눅스에서 벌어진 겁니다. 접근법도 똑같아요 — 유언부터.

## 1단계 — status는 요약본이다

`systemctl status`는 사망진단서 요약입니다. 여기서 세 가지만 챙기세요.

- **Result:** `exit-code`(스스로 에러 종료) / `signal`(죽임 당함) / `timeout`(기동 시간 초과)
- **status=1/FAILURE** 같은 종료 코드
- 하단에 딸려 나오는 **최근 로그 몇 줄** — 운 좋으면 여기서 끝

## 2단계 — journalctl로 유언 전문 보기

systemd는 서비스의 stdout/stderr를 전부 저널에 담아둡니다. 죽기 직전 로그 전문은 여기에 있어요.

```bash
journalctl -u myapp -e              # 해당 서비스 로그, 끝부분으로 바로 이동
journalctl -u myapp --since "10 min ago"   # 최근 10분만
journalctl -u myapp -f              # 실시간 추적 (재시작해보며 관찰할 때)
journalctl -u myapp -p err          # 에러 레벨 이상만 필터
```

부팅 단위로 끊어 보는 것도 유용합니다. "재부팅하고부터 안 돼요"라면:

```bash
journalctl -u myapp -b              # 이번 부팅 이후만
journalctl -u myapp -b -1           # 직전 부팅에서의 로그
```

## 3단계 — 원인 톱4 대조

**① 앱 자체 에러 (exit-code)** — 로그에 스택트레이스, "config not found", "port already in use". 앱 문제이므로 앱 쪽에서 해결. 포트 점유는 `ss -tlnp | grep :포트` 로 선점자를 확인합니다.

**② OOM으로 죽음 (signal=KILL)** — 로그가 뚝 끊기고 `signal=KILL`이면 커널의 OOM Killer를 의심하세요.

```bash
journalctl -k --since "1 hour ago" | grep -i "out of memory"
# "Killed process 1234 (myapp)" 이 보이면 확진
```

서비스 유닛에 `MemoryMax=` 가 걸려 있는지도 확인 (`systemctl cat myapp`). cgroup 한도에 걸려 죽는 경우도 흔합니다.

**③ 의존성·권한 문제** — 부팅 직후에만 죽는다면, 네트워크나 DB가 준비되기 전에 시작해서일 가능성. 유닛 파일의 `After=network-online.target` 같은 순서 지정을 점검하세요. `status=203/EXEC` 은 실행 파일 경로·권한 오류, `status=217/USER` 는 유닛에 지정한 계정이 없는 것 — 종료 코드가 곧 힌트입니다.

**④ 재시작 한도 초과** — `Restart=always`인데도 안 살아난다면:

```bash
systemctl status myapp | grep -i "start-limit"
# "Start request repeated too quickly" → 짧은 시간에 너무 많이 죽어서 systemd가 포기한 것
```

이건 별개의 원인이 아니라 **①~③이 반복된 결과**입니다. 원인 고친 뒤 `systemctl reset-failed myapp && systemctl start myapp` 으로 리셋하고 살리세요.

## 재현하며 잡기

원인이 손에 안 잡히면, 터미널 두 개를 씁니다.

```bash
# 터미널 1: 실시간 관찰
journalctl -u myapp -f

# 터미널 2: 재시작 시도
systemctl restart myapp
```

죽는 순간이 눈앞에서 재생되니, 마지막 줄이 곧 답입니다. 그래도 로그가 아예 안 남는다면 서비스로서가 아니라 **손으로 직접 실행**(`sudo -u 서비스계정 /usr/bin/myapp`)해보세요 — 환경변수·권한 차이가 그 자리에서 드러납니다.

## 한 줄 정리

**status(요약) → `journalctl -u`(전문) → 톱4 대조(앱 에러 / OOM / 의존성·권한 / start-limit)**. 그리고 안 잡히면 `-f`로 죽는 장면을 직접 목격하세요. 서비스는 말없이 죽지 않습니다 — 저널에 다 적어놓고 죽어요.
