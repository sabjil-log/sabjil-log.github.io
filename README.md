# 삽질노트 — 무인 자동 블로그

마크다운만 넣으면 → 스타일 입은 HTML로 빌드 → GitHub Pages가 루트에서 그대로 서빙.
GitHub에는 **빌드 단계가 없어서**(완성된 HTML만 올림) 깨질 게 없습니다.

## 폴더 구조
```
blog/
├── build.py                 # 생성기 (설정은 파일 상단 SITE / CATEGORIES 만 고치면 됨)
├── publish.sh               # 빌드 + 커밋 + 푸시 한 방
├── posts/                   # ← 여기에 글(.md)만 쌓임. 원본.
│   └── 2026-07-09-...md
├── index.html  p/  c/  assets/   # ← 자동 생성물(루트). GitHub Pages가 서빙. 손대지 말 것.

```

## 처음 한 번만 (익명 세팅)

1. **가명 전용 이메일** 하나 만들기 (기존 신원과 안 엮인 걸로).
2. 그 이메일로 **새 GitHub 계정** 생성 → 사용자명이 곧 블로그 주소가 되니 가명으로.
3. 저장소 만들기: 이름을 `<사용자명>.github.io` 로. (예: `sabjil-log.github.io`)
4. 이 폴더 내용을 그 저장소에 push.
5. `<사용자명>.github.io` 저장소는 push만 하면 **자동 발행**됩니다(Pages 설정 불필요).
6. 1~2분 뒤 `https://<사용자명>.github.io/` 로 접속 → 끝.

> 익명성 핵심: 커밋 작성자 정보도 가명으로.
> `git config user.name "가명"` / `git config user.email "가명이메일"` 을 이 저장소에 설정하세요.
> 실명·회사 이메일로 커밋하면 커밋 로그에 그대로 남습니다.

## 매일 (무인 루프)

글 하나 = `posts/YYYY-MM-DD-슬러그.md` 파일 하나. 아래 형식만 지키면 됩니다.

```markdown
---
title: "제목"
date: 2026-07-10
category: 리눅스        # 트러블슈팅 / 리눅스 / 클라우드 / 네트워크 / 보안 / AI/LLM
tags: [태그1, 태그2]
summary: "목록에 뜨는 한 줄 요약"
---

본문 마크다운...
```

그다음:
```bash
./publish.sh "add: 오늘 글 제목"
```
→ 빌드 → 커밋 → 푸시. 몇십 초 뒤 사이트에 반영됩니다.

**Claude가 대신 밀어주게 하려면**(진짜 무인): 그 저장소 하나에만 권한 있는
fine-grained PAT(Contents: Read and write, 만료일 지정)을 발급해서 넘겨주면,
Claude가 매일 글 생성 → 푸시까지 처리합니다. 토큰은 그 저장소 밖으론 아무것도 못 건드립니다.

## 이름/저자 바꾸기
`build.py` 상단 `SITE` 딕셔너리의 `handle`, `title`, `tagline`, `author` 만 고치고 `./publish.sh` 하면 끝.
