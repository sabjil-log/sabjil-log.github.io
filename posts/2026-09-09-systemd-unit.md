---
title: "systemd 유닛 파일 읽는 법 — Type, After, Restart가 하는 일"
date: 2026-09-09
category: 리눅스
tags: ["systemd", "유닛", "서비스", "Restart", "의존성"]
summary: "서비스가 안 뜨거나 계속 재시작하는 이유의 대부분은 유닛 파일 세 줄에 있습니다. Type·After·Restart를 읽으면 원인이 보여요."
---

> **한 줄 요약:** 유닛 파일에서 사고가 나는 곳은 사실상 세 줄입니다 — **Type=**(언제 "떴다"고 볼 건가), **After=/Requires=**(뭘 기다릴 건가), **Restart=**(죽으면 어떻게 할 건가). 이 셋의 조합이 "안 뜬다 / 뜬 척한다 / 무한 재시작"을 만듭니다.

[[diagram:systemd-unit]]

## 유닛 파일의 골격

```ini
[Unit]                      # ← 정체성과 의존성
Description=My API server
After=network-online.target
Wants=network-online.target

[Service]                   # ← 어떻게 실행하고 관리할지
Type=simple
User=app
WorkingDirectory=/srv/api
Environment=PORT=8080
ExecStart=/srv/api/venv/bin/python -m app
Restart=on-failure
RestartSec=5
LimitNOFILE=65535

[Install]                   # ← 언제 자동 시작할지
WantedBy=multi-user.target
```

세 섹션의 역할이 명확합니다 — `[Unit]`은 관계, `[Service]`는 실행, `[Install]`은 부팅 시 활성화(그래서 `systemctl enable`이 이 섹션을 읽습니다). 확인은 항상 실물로:

```bash
systemctl cat myapi          # 유닛 + override 전부 합친 최종본 ← 진실
systemctl show myapi | grep -E "^(Type|Restart|After|ExecStart|LimitNOFILE)="
```

`cat`이 중요합니다 — `/etc/systemd/system/myapi.service.d/*.conf` 같은 override가 있으면 원본만 봐서는 실제 설정을 알 수 없어요(fd 글에서 `systemctl edit`로 LimitNOFILE 넣던 그 방식).

## Type= — "떴다"의 정의

여기서 제일 많이 틀립니다. systemd는 Type에 따라 **언제 시작 성공으로 판단할지**를 다르게 봅니다.

- **`simple`** (기본) — ExecStart 프로세스를 띄우는 즉시 "떴다"로 간주. 앱이 아직 포트를 안 열었어도 성공 처리됩니다. 그래서 **의존 서비스가 너무 일찍 시작**하는 문제가 생기죠.
- **`exec`** — 실행 파일이 성공적으로 실행된 것까지 확인. simple보다 살짝 엄격.
- **`forking`** — 데몬이 스스로 백그라운드로 빠지는(fork) 전통적 방식. 부모가 종료되면 성공. `PIDFile=`을 함께 씁니다. **이 타입인데 앱이 fork를 안 하면** systemd가 영원히 기다리다 타임아웃 — "start 명령이 90초 걸리고 실패"의 단골 원인.
- **`notify`** — 앱이 "나 준비됐어"를 systemd에 직접 알림. 준비 완료 시점이 정확해서 의존성 순서가 진짜로 지켜집니다(nginx, postgres 등이 지원).
- **`oneshot`** — 실행하고 끝나는 작업(마이그레이션, 초기화). 끝나도 "죽었다"고 안 봅니다. `RemainAfterExit=yes`를 붙이면 종료 후에도 active 상태 유지.

**진단 감각:** 앱은 잘 도는데 `systemctl start`가 멈춰 있으면 → Type 불일치(대개 forking 오지정). 반대로 앱이 준비되기 전에 뒤따르는 서비스가 시작해 실패하면 → simple을 쓰고 있는데 notify가 필요한 상황.

## After= / Requires= / Wants= — 순서와 필수 여부는 별개다

혼동 포인트: **After는 순서만, Requires는 필수 여부만** 뜻합니다.

```ini
After=postgresql.service      # 순서: DB 유닛 시작 후에 나를 시작 (성공 여부는 안 봄)
Requires=postgresql.service   # 필수: DB가 실패하면 나도 중지 (순서는 안 정함)
Wants=postgresql.service      # 권장: 있으면 좋지만 실패해도 나는 계속
```

그래서 실무에서는 **After + Wants(또는 Requires)를 짝으로** 씁니다. 하나만 쓰면 "순서는 맞는데 DB 죽어도 계속 뜬다" 또는 "필수인데 순서가 뒤엉킨다"가 됩니다.

**네트워크 함정 하나:** `After=network.target`은 "네트워크 스택이 올라옴"이지 **IP가 붙었음이 아닙니다.** 시작 시 특정 IP에 바인딩하는 앱이 부팅 직후에만 실패한다면, `network-online.target`을 After+Wants로 쓰세요(그리고 그 타깃이 실제로 enable돼 있는지 확인). port-in-use 글의 바인딩 문제가 부팅 타이밍으로 나타나는 케이스입니다.

## Restart= — 죽으면 어떻게

```ini
Restart=no             # 기본 — 안 살림
Restart=on-failure     # 0이 아닌 종료·시그널사·타임아웃에만 재시작 ← 서비스의 정석
Restart=always         # 정상 종료(exit 0)도 재시작 — 무한 루프 위험
RestartSec=5           # 재시작 전 대기
StartLimitIntervalSec=60
StartLimitBurst=3      # 60초에 3번 넘게 실패하면 포기하고 failed로
```

마지막 두 줄이 실무의 안전판입니다. 이게 없으면 **설정이 틀린 서비스가 초당 수십 번 재시작**하며 로그와 CPU를 태웁니다 — CrashLoopBackOff 글의 백오프를 systemd에서 직접 설정하는 셈이죠. 반대로 `start-limit-hit`으로 서비스가 멈춰 있으면 원인을 고친 뒤 `systemctl reset-failed myapi`로 카운터를 지워야 다시 시작됩니다("고쳤는데 왜 안 떠요?"의 답).

## 진단 3콤보

```bash
systemctl status myapi          # 요약 + Result·종료코드 (journalctl 글의 그 지점)
journalctl -u myapi -n 50       # 유언 전문
systemctl cat myapi             # 설정의 진실 (override 포함)
```

종료코드가 힌트를 줍니다 — `203/EXEC`(ExecStart 경로·권한), `217/USER`(User= 계정 없음), `signal=KILL`이면 dmesg로 OOM 확인. 그리고 `Environment=`로 준 변수는 셸을 안 거치니 `$HOME` 같은 확장이 안 되고, 여러 개면 `EnvironmentFile=`로 빼는 게 깔끔합니다 — cron 환경 글의 "빈 주방" 원칙이 systemd에도 그대로 적용돼요.

## 한 줄 정리

유닛 파일은 **Type(떴다의 정의) · After+Wants(순서와 필수) · Restart+StartLimit(죽었을 때)** 세 줄로 읽습니다. start가 멈추면 Type, 부팅 직후만 실패하면 network-online, 무한 재시작이면 StartLimit — 그리고 진실은 항상 `systemctl cat`에 있습니다.
