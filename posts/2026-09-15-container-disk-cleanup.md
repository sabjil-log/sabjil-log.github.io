---
title: "컨테이너가 노드 디스크를 다 먹었다 — 이미지·로그·오버레이 청소법"
date: 2026-09-15
category: 트러블슈팅
tags: ["Docker", "디스크", "prune", "오버레이", "로그", "Kubernetes"]
summary: "노드 디스크 90% 알람의 범인은 대개 컨테이너 층에 있습니다. 어디가 먹는지 재는 법과, 지워도 되는 것/안 되는 것을 가르는 청소 순서."
---

> **한 줄 요약:** 컨테이너 호스트의 디스크는 **옛 이미지, 죽은 컨테이너, 컨테이너 stdout 로그, 빌드 캐시**가 조용히 먹습니다. `docker system df`로 어디가 얼마인지 재고, **로그 상한 설정 + 정기 prune**을 걸어두면 이 알람은 사라집니다. 단, 볼륨은 데이터라 함부로 prune하지 마세요.

[[diagram:container-disk]]

## 어디가 먹는지 재기부터

```bash
docker system df -v            # 이미지 / 컨테이너 / 볼륨 / 빌드 캐시 — 항목별 용량과 회수 가능량
du -sh /var/lib/docker/*  2>/dev/null | sort -h      # 실제 디렉토리 기준
du -sh /var/lib/docker/containers/*/*-json.log | sort -h | tail   # 컨테이너별 로그
```

전형적 분포: 이미지가 수십 GB(태그 바꿔 배포할 때마다 옛 이미지가 남음), 특정 컨테이너의 json 로그가 수 GB(로그 상한 미설정), 빌드 캐시가 수 GB(CI 노드). "지웠는데 안 줄어요"의 파일 삭제 글 현상이 여기서도 나오니, `df`와 `du`가 어긋나면 그 글의 `lsof +L1`도 병행하세요.

## 청소 순서 — 안전한 것부터

**① 컨테이너 로그 (가장 흔한 범인).** 도커의 기본 로깅 드라이버는 stdout을 json 파일로 **무제한** 쌓습니다. 응급은 truncate, 근본은 상한 설정.

```bash
# 응급: 특정 컨테이너 로그 비우기 (파일 삭제 글의 그 방식 — 삭제 아님)
sudo truncate -s 0 /var/lib/docker/containers/<ID>/<ID>-json.log

# 근본: /etc/docker/daemon.json — 모든 컨테이너 기본 상한
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "50m", "max-file": "3" }
}
# → systemctl restart docker (기존 컨테이너는 재생성돼야 적용)
```

로그 중앙화 글의 구조라면 로컬은 이 상한만 두고 수집기가 걷어가니 근본 해결이 됩니다.

**② 멈춘 컨테이너·태그 없는 이미지·미사용 네트워크.**
```bash
docker system prune            # 멈춘 컨테이너 + dangling 이미지 + 미사용 네트워크 (볼륨 제외)
docker image prune -a          # 실행 중인 컨테이너가 안 쓰는 이미지 전부 — 다음 배포 시 다시 pull
```
`-a`는 강력합니다 — 롤백용으로 쥐고 있던 이전 버전 이미지도 지우니, 레지스트리에서 다시 받을 수 있는지(그리고 NAT 요금·pull 시간이 감당되는지) 확인 후에.

**③ 빌드 캐시.** CI 노드에서 커집니다.
```bash
docker builder prune --filter until=168h    # 일주일 안 쓴 캐시만
```
레이어 캐시 글에서 빌드 속도의 핵심이라 했으니, **전부 지우면 다음 빌드가 느려집니다.** until 필터로 오래된 것만.

**④ 볼륨 — 여기서 멈추세요.**
```bash
docker volume ls -f dangling=true    # 어떤 컨테이너도 안 쓰는 볼륨 목록 — 지우기 전에 이름 확인
```
`docker volume prune`은 **데이터 삭제**입니다. 도커 볼륨 글의 그 `down -v` 사고와 같은 급. dangling 볼륨이라도 "정지된 DB 컨테이너의 데이터"일 수 있으니, 목록을 보고 **이름을 확인한 뒤 개별 삭제**가 원칙이에요.

## 쿠버네티스 노드라면

kubelet이 **가비지 컬렉션**을 자동으로 합니다 — 디스크 사용률 임계(기본 85%)를 넘으면 미사용 이미지를 지우고, 더 심하면 Pod를 퇴출(eviction)시킵니다. "노드가 갑자기 Pod를 쫓아냈다"(DiskPressure)의 정체가 이것.

```bash
kubectl describe node <노드> | grep -A5 Conditions     # DiskPressure 여부
kubectl get events --field-selector reason=Evicted     # 퇴출 이력
```

노드에 직접 들어가 `docker prune`하는 건 kubelet과 충돌할 수 있으니(containerd 환경이면 `crictl rmi --prune`), 정석은 **kubelet의 GC 임계값 조정 + 로그 상한(컨테이너 런타임 설정) + 노드 디스크 크기 산정**입니다. 그리고 Pod가 emptyDir이나 로컬 경로에 대용량을 쓰고 있다면 그건 워크로드 설계 문제 — requests/limits 글의 `ephemeral-storage` 제한이 이 계열의 안전판이에요.

## 재발 방지 세트

```
□ daemon.json 로그 상한 (max-size / max-file)
□ 주간 cron: docker system prune -f + builder prune --filter until=168h  (볼륨 제외!)
□ 디스크 사용률 알람 80% (알람 설계 글의 시한폭탄 예외 항목)
□ 노드 디스크 산정 시 "이미지 3세대 + 로그 상한 × 컨테이너 수" 반영
□ 이미지 다이어트 (멀티스테이지) — 원인의 크기 자체를 줄이기
```

## 한 줄 정리

`docker system df`로 재고, **로그 → 멈춘 컨테이너/옛 이미지 → 빌드 캐시** 순으로 지우되 **볼륨은 목록 보고 개별로.** 근본은 로그 상한 + 정기 prune + 알람이고, 쿠버 노드는 kubelet GC와 싸우지 말고 임계값을 조정하세요.
