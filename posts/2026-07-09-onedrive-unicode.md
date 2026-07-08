---
title: "맥·윈도우 섞인 팀에서 OneDrive가 파일을 자꾸 두 개로 만드는 이유"
date: 2026-07-09
category: 트러블슈팅
tags: [OneDrive, 유니코드, 맥, 동기화]
summary: "이름이 똑같아 보여도 맥과 윈도우가 한글 이름을 다르게 저장해서 생기는 문제. 눈이 아니라 바이트로 봐야 답이 나옵니다."
---

> **한 줄 요약:** 파일 이름이 똑같아 보여도, 맥과 윈도우가 한글 이름을 *다른 방식으로 저장*하기 때문입니다. 사람 눈엔 같은데 컴퓨터 눈엔 다른 파일이에요.

## 이런 적 있으신가요

맥 쓰는 디자이너가 `제안서.pptx`를 올렸는데, 윈도우 쓰는 팀원한테는 `제안서.pptx`랑 `제안서.pptx`가 **두 개** 보입니다. 이름은 글자 하나 안 다른데요. 누가 하나 지우면 다른 사람 파일이 사라지고, 동기화는 계속 충돌 나고… 딱 미치는 상황이죠.

## 범인은 "유니코드 정규화"

핵심만 말하면, **한글 글자 하나를 저장하는 방법이 두 가지**라서 그렇습니다. `한`이라는 글자를 예로 들어볼게요.

- **방법 A (NFC):** `한` 하나로 통째로 저장 — 윈도우가 쓰는 방식
- **방법 B (NFD):** `ㅎ` + `ㅏ` + `ㄴ` 자음·모음을 따로따로 저장 — 맥이 쓰는 방식

화면엔 둘 다 똑같이 `한`으로 보입니다. 하지만 실제 바이트는 완전히 다릅니다. 마치 **"1"을 아라비아 숫자 `1`로 쓰느냐, 로마 숫자 `Ⅰ`로 쓰느냐**의 차이 같은 거예요. 읽는 사람은 같은 1이지만 기계는 다른 문자로 봅니다. OneDrive 입장에선 "다른" 두 파일이니 착실하게 둘 다 보관합니다.

## 왜 하필 맥이 문제냐

맥 파일 시스템(APFS/HFS+)이 파일 이름을 **분해된 형태(NFD)로 저장**하는 습관이 있어서입니다. 반대로 윈도우·대부분의 웹서비스·리눅스는 **합쳐진 형태(NFC)**를 표준으로 씁니다. 그래서 맥에서 만든 한글 파일이 다른 환경으로 넘어갈 때 어긋남이 터져요. (영어 파일명은 분해될 게 없어서 안 생깁니다. 한글·한자처럼 조합형 글자에서만 나타나요.)

## 진짜인지 확인하는 법

`한`은 눈으로 한 글자지만, NFC면 코드포인트 1개, NFD면 3개(ㅎ, ㅏ, ㄴ)입니다. 글자 수만 세보면 바로 드러나요.

파이썬 — 이름 하나 찍어보기:

```python
import unicodedata

name = "한"
print(len(name))                                # NFC면 1, NFD면 3
print([hex(ord(c)) for c in name])              # NFD면 자모가 따로 보임
print(unicodedata.is_normalized("NFC", name))   # False면 NFD 상태
```

PowerShell(윈도우) — 폴더에서 NFD 파일명만 골라내기:

```powershell
Get-ChildItem | Where-Object {
  $_.Name -ne $_.Name.Normalize([Text.NormalizationForm]::FormC)
} | Select-Object Name
```

맥/리눅스 터미널 — 이름 길이 비교:

```bash
for f in *; do
  python3 -c "import sys,unicodedata as u; n=sys.argv[1]; print(len(n), len(u.normalize('NFC',n)), n)" "$f"
done
# 앞 두 숫자가 다른 줄이 NFD 파일
```

## 해결책

**1. 업로드 전에 폴더 전체를 NFC로 일괄 변환** — 가장 확실합니다.

```python
import os, unicodedata

target = "."  # 정규화할 폴더
for name in os.listdir(target):
    nfc = unicodedata.normalize("NFC", name)
    if nfc != name:
        os.rename(os.path.join(target, name), os.path.join(target, nfc))
        print(f"renamed: {name} -> {nfc}")
```

> ⚠️ 돌리기 전에 백업. 이미 NFC 복제본이 함께 있으면 이름 충돌이 나니, 복제본부터 정리하고 실행하세요.

**2. 한글 파일명을 아예 피한다.** 팀 규칙으로 `proposal_260709.pptx`처럼 영문+날짜로 통일하면 문제 자체가 사라집니다. 근본 회피책이죠.

**3. 이미 생긴 복제본은 최신본 확인 후 하나로 병합**하고 위 규칙으로 재발을 막습니다. 지울 땐 어느 쪽이 최신 수정본인지 꼭 확인하세요 — 엉뚱한 걸 지우면 남의 작업이 날아갑니다.

## 한 줄 정리

**"같은 이름인데 왜 두 개지?"** 싶으면 십중팔구 맥의 NFD와 윈도우의 NFC가 싸우는 겁니다. 이름을 눈이 아니라 **바이트로** 보면 답이 나옵니다.
