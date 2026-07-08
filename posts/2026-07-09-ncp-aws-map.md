---
title: "NCP와 AWS, 같은 걸 다르게 부른다 — 헷갈리는 서비스 이름 지도"
date: 2026-07-09
category: 클라우드
tags: [NCP, AWS, VPC, ACG, 멀티클라우드]
summary: "개념은 거의 1:1인데 이름만 달라서 헤맵니다. 핵심 매핑만 외우면 두 클라우드 문서가 같은 언어로 읽혀요."
---

> **한 줄 요약:** NCP와 AWS는 개념이 거의 1:1로 대응합니다. 이름만 다를 뿐이에요. 매핑 지도를 한 번 외워두면, 한쪽 문서를 읽던 감각 그대로 다른 쪽을 읽을 수 있습니다.

## 왜 헷갈리나

같은 요리를 나라마다 다른 이름으로 파는 것과 같습니다. 재료(개념)는 똑같은데 메뉴판 글씨만 달라서, 처음엔 전혀 다른 음식처럼 보이죠. "인스턴스 방화벽"을 AWS는 Security Group, NCP는 ACG라고 부르는 식입니다.

## 핵심 매핑 지도

| 개념 | AWS | NCP |
|---|---|---|
| 가상 네트워크 | VPC | VPC |
| 서브넷 | Subnet | Subnet |
| 인스턴스 방화벽 | Security Group | ACG (Access Control Group) |
| 서브넷 방화벽 | Network ACL | Network ACL |
| 로드밸런서 | ELB / ALB / NLB | Load Balancer (ALB / NLB) |
| 오브젝트 스토리지 | S3 | Object Storage (S3 호환) |
| 블록 스토리지 | EBS | Block Storage |
| 관리형 RDB | RDS | Cloud DB (for MySQL/PostgreSQL 등) |
| 서버리스 함수 | Lambda | Cloud Functions |
| 모니터링 | CloudWatch | Cloud Insight |
| 키 관리 | KMS | Key Management Service (KMS) |
| 비밀 관리 | Secrets Manager | Secret Manager |
| 계정/권한 | IAM | Sub Account / IAM |
| DNS | Route 53 | Global DNS |
| CDN | CloudFront | CDN+ / Global CDN |

이 표만 손에 쥐고 있으면, "AWS에서 이거 하던 건데 NCP선 뭐지?" 할 때 바로 목적지를 찾습니다.

## 함정: 이름은 닮았는데 동작이 다른 것들

지도만 외우면 방심하기 쉬운데, **동작이 미묘하게 다른 짝**이 있습니다.

- **방화벽의 상태성:** 인스턴스 방화벽(Security Group / ACG)은 **스테이트풀** — 나간 요청의 응답은 규칙 없이 자동으로 돌아옵니다. 반면 **Network ACL은 양쪽 다 스테이트리스** — 인바운드만 열고 아웃바운드(리턴) 포트를 안 열면 응답이 막힙니다. 헬스체크·SSH가 "붙는 듯 안 붙는" 전형적 원인이에요.
- **S3 호환의 함정:** NCP Object Storage는 S3 API 호환이지만 100%는 아닙니다. 서명 방식(s3v4)·일부 체크섬 헤더 처리에서 차이가 있어, 최신 SDK(예: boto3 신버전)의 기본값이 그대로 안 먹을 때가 있어요. 클라이언트 설정을 호환 모드로 맞춰줘야 합니다.
- **부르는 단위가 다를 때:** 같은 "관리형 DB"라도 지원 엔진·버전·백업 정책 세부는 벤더마다 다릅니다. 개념은 같아도 **스펙은 반드시 각 문서에서 재확인**하세요.

## 한 줄 정리

개념 지도(왼쪽 열)를 외우면 두 클라우드가 같은 언어로 읽힙니다. 단, **이름이 같아도 상태성·호환성 같은 동작 차이**는 따로 확인 — 특히 스테이트리스 NACL이 사람 잡습니다.
