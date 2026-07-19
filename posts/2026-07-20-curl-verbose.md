---
title: "curl -v 출력, 한 줄씩 읽는 법 — 어디서 막혔는지 혼자 말해준다"
date: 2026-07-20
category: 네트워크
tags: ["curl", "TLS", "HTTP", "DNS", "트러블슈팅"]
summary: "curl -v는 DNS→TCP→TLS→HTTP 네 단계를 순서대로 중계해주는 실황 방송입니다. 어느 줄에서 멈췄는지가 곧 진단 결과예요."
---

> **한 줄 요약:** `curl -v`의 출력은 접속의 네 단계 — **DNS 해석 → TCP 연결 → TLS 악수 → HTTP 대화** — 를 순서대로 보여주는 실황 중계입니다. **출력이 어느 줄에서 멈추거나 에러를 내는지**가 곧 "몇 층에서 막혔는지"의 답이에요.

## 왜 이걸 읽을 줄 알아야 하나

계층 진단 글에서 dig, nc, tcpdump를 각각 썼는데, 사실 HTTPS 접속 문제라면 **curl -v 한 방**이 네 단계를 전부 순서대로 시연해줍니다. 읽는 법만 알면 별도 도구 없이 진단의 절반이 끝나요.

## 출력 해부 — 정상 케이스

```
$ curl -v https://example.com/health
* Host example.com:443 was resolved.            ← [1] DNS: 이름→IP 성공
* Connected to example.com (93.184.216.34) port 443   ← [2] TCP: 연결 성공
* TLS handshake, ...                             ← [3] TLS: 악수 진행
* SSL certificate verify ok.                     ←     인증서 검증 통과
> GET /health HTTP/1.1                           ← [4] HTTP: > 는 내가 보낸 것
> Host: example.com
< HTTP/1.1 200 OK                                ←     < 는 서버가 보낸 것
< content-type: application/json
```

기호 세 개만 기억하세요 — **`*` 는 연결 과정 중계, `>` 는 내 요청, `<` 는 서버 응답.** `>` 가 보였다는 건 3층까지 전부 통과했다는 뜻입니다.

## 어디서 멈췄나 = 누가 범인인가

**[1]에서 멈춤 — `Could not resolve host`**
DNS 문제. 오타, 사설 DNS 미설정, /etc/resolv.conf. → `dig 도메인` 으로 이어서 확인.

**[2]에서 멈춤 — 두 가지 얼굴**
```
* connect to 93.184.216.34 port 443 failed: Connection refused   ← 즉시 거절
* connect to ... failed: Connection timed out                    ← 하염없이 침묵
```
이 구분이 중요합니다. **refused = 도착은 했는데 그 포트에 아무도 없음**(RST — tcpdump 글의 패턴②, 앱 다운/포트 오류). **timeout = 패킷이 어딘가에서 증발**(패턴①/③, 방화벽·NACL·라우팅). refused면 서버 쪽 `ss -tlnp`, timeout이면 방화벽부터.

**[3]에서 멈춤 — TLS 계열 에러**
```
* SSL certificate problem: certificate has expired         ← 인증서 만료
* SSL: no alternative certificate subject name matches ... ← 도메인 불일치 (다른 도메인 인증서)
* error:0A00010B ... wrong version number                  ← HTTPS로 접속했는데 상대는 평문 HTTP
```
셋 다 메시지가 답을 그대로 말해줍니다. 마지막 것은 특히 자주 봅니다 — 포트는 열려 있는데 그 포트가 TLS를 안 하는 경우(예: 8080에 https://로 접속). 인증서 자체를 자세히 보려면:

```bash
curl -vI https://example.com 2>&1 | grep -A5 "Server certificate"
# 만료일(expire date), 발급 대상(subject)이 바로 나옴
```

**[4]에서 문제 — 연결은 됐고, 이제 앱의 영역**
```
< HTTP/1.1 301 Moved Permanently        ← 리다이렉트: -L 붙여 따라가 보기
< HTTP/1.1 401 / 403                    ← 인증·권한
< HTTP/1.1 502 Bad Gateway              ← LB/프록시 뒤의 백엔드가 죽음 — 헬스체크 글로
< HTTP/1.1 504 Gateway Timeout          ← 백엔드가 너무 느림
```
여기부터는 네트워크 무죄, 앱·백엔드 수사로 전환합니다.

## 자주 쓰는 조합 옵션

```bash
curl -v -m 5 https://...          # 타임아웃 5초 — timeout 진단을 5초 만에
curl -vL https://...              # 리다이렉트 추적 (301/302 체인 전체가 보임)
curl -v --resolve example.com:443:10.0.3.15 https://example.com/
#   ↑ DNS 무시하고 특정 서버로 강제 — "LB 뒤 3번 서버만 이상한가?" 검증에 최고
curl -sw 'dns:%{time_namelookup} tcp:%{time_connect} tls:%{time_appconnect} total:%{time_total}\n' -o /dev/null https://...
#   ↑ 단계별 소요시간 — "느린데 어디가 느린지"를 숫자로
```

특히 `--resolve`는 LB 환경의 보물입니다 — 도메인은 그대로 두고(인증서 검증 유지) 대상 서버만 바꿔 찍어볼 수 있어요.

## 한 줄 정리

curl -v는 **DNS→TCP→TLS→HTTP 4단 실황 중계**입니다. 멈춘 줄이 곧 범인의 층이고, refused와 timeout의 구분, TLS 에러 문구, 상태코드까지 — 출력을 읽을 줄 알면 진단 도구 하나로 계층 절반을 커버합니다.
