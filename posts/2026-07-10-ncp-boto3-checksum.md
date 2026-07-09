---
title: "NCP Object Storage에 boto3 물릴 때 터지는 함정 — 체크섬과 서명"
date: 2026-07-10
category: 클라우드
tags: ["NCP", "Object Storage", "boto3", "S3", "체크섬"]
summary: "S3 호환이라 boto3가 그냥 될 줄 알았는데 업로드가 실패한다면, 최신 SDK의 기본 체크섬 헤더와 서명 방식이 원인일 때가 많습니다."
---

> **한 줄 요약:** NCP Object Storage는 **S3 API 호환**이지만 100% 똑같진 않습니다. 최신 boto3가 기본으로 붙이는 **체크섬 헤더**와 **서명 방식(SigV4)** 설정만 맞춰주면 대부분 해결돼요.

## 증상

`endpoint_url`만 NCP로 바꾸면 될 줄 알았는데, `put_object`나 멀티파트 업로드에서 알 수 없는 에러가 납니다. `HeadBucket`은 되는데 업로드만 실패하기도 하고, 서명이 안 맞는다는 오류가 뜨기도 하죠. 코드는 AWS에서 멀쩡히 돌던 그대로인데요.

## 왜 그런가 — "호환"의 함정

S3 호환 스토리지는 S3의 **핵심 규격**을 따르지만, AWS가 새로 추가하는 최신 동작까지 전부 따라가진 못합니다. 특히 최근 boto3/AWS SDK는 업로드할 때 **무결성 체크섬 헤더(CRC32 등)를 기본으로 자동 첨부**하기 시작했는데, 호환 스토리지가 이 최신 헤더를 아직 그대로 처리하지 못하면 요청이 거부됩니다. "표준어는 통하는데 신조어는 못 알아듣는" 상황이에요.

## 해결 — 클라이언트 설정 맞추기

핵심은 두 가지입니다. **서명 방식을 SigV4로 고정**하고, **자동 체크섬을 요청할 때만 붙이도록** 낮춰줍니다.

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="https://kr.object.ncloudstorage.com",   # NCP 엔드포인트
    region_name="kr-standard",
    aws_access_key_id="...",
    aws_secret_access_key="...",
    config=Config(
        signature_version="s3v4",          # 서명 방식 고정
        s3={"addressing_style": "path"},   # path-style로 (버킷.도메인 대신 도메인/버킷)
    ),
)
```

그래도 업로드 때 체크섬 관련 오류가 남으면, 최신 SDK의 자동 체크섬 동작을 낮춥니다. (botocore 버전에 따라 방식이 다르니 버전을 먼저 확인하세요.)

```python
# 예: 요청 시에만 체크섬을 계산하도록 환경변수로 조정
# AWS_REQUEST_CHECKSUM_CALCULATION=when_required
# AWS_RESPONSE_CHECKSUM_VALIDATION=when_required
```

값이 안 먹으면 botocore를 호환이 검증된 버전으로 **핀 고정**하는 것도 현실적인 우회책입니다.

## 확인하는 법

무엇이 오가는지 보면 원인이 빨리 잡힙니다.

```python
import boto3
boto3.set_stream_logger("botocore", level="DEBUG")   # 요청 헤더/서명 전부 출력
```

로그에서 `x-amz-checksum-*` 헤더가 붙는지, 서명 버전이 `AWS4`(=SigV4)인지 확인하세요. 그리고 CLI로 단순 검증:

```bash
aws --endpoint-url https://kr.object.ncloudstorage.com s3 ls
```

## 한 줄 정리

"S3 호환 = boto3 그냥 됨"이 아닙니다. **SigV4 고정 + path-style + 자동 체크섬 조정**, 그리고 안 될 땐 **DEBUG 로그로 오가는 헤더 확인**. 대부분 이 선에서 정리됩니다.
