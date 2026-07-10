# -*- coding: utf-8 -*-
"""
queue.md 에서 토픽 N개를 꺼내 → Anthropic API 로 '가르치듯' 블로그 글 생성 →
posts/ 에 저장하고, 소비한 토픽은 queue.md 에서 제거한다.
GitHub Actions(새벽 크론)에서 build.py 앞에 실행된다.

환경변수:
  ANTHROPIC_API_KEY   (필수, 저장소 Secret)
  POSTS_PER_DAY       (선택, 기본 3 — 한 달 뒤 1 로 바꾸면 됨)
  MODEL               (선택, 기본 claude-sonnet-5)
"""
import os, re, json, datetime, glob
import anthropic

ROOT = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(ROOT, "queue.md")
POSTS = os.path.join(ROOT, "posts")
N = int(os.environ.get("POSTS_PER_DAY", "3"))
MODEL = os.environ.get("MODEL", "claude-sonnet-5")
CATEGORIES = ["트러블슈팅", "리눅스", "클라우드", "네트워크", "보안", "AI/LLM"]

SYSTEM = """너는 실무 엔지니어를 위한 한국어 기술 블로그의 필자다.
독자는 주니어~중급 개발자/인프라 담당자. 목표는 '남에게 쉽게 가르치듯' 설명하는 것.

반드시 아래 형식과 규칙을 지켜라:
- 구조: (1) 인용구로 시작하는 '한 줄 요약(TL;DR)'  (2) 겪는 증상/맥락  (3) 진짜 원인을 '쉬운 비유'로  (4) 확인하는 법(가능하면 바로 복붙 가능한 명령어/코드)  (5) 해결책  (6) '한 줄 정리'
- 명령어·코드는 반드시 정확해야 한다. 확실하지 않으면 지어내지 말고 개념 설명으로 대체.
- 과장/광고 문구 금지. 담백하고 정확하게.
- 코드 블록은 언어를 명시한 fenced code(```bash 등).
- 마크다운 본문만. 최상단 제목(#)은 쓰지 마라(제목은 별도 필드로 준다).
- 분량: 본문 마크다운 기준 대략 500~1000자 + 필요한 코드.

출력은 오직 아래 JSON 하나. 그 외 텍스트/설명/코드펜스 금지:
{
  "title": "제목(간결, 후킹)",
  "slug": "english-kebab-case-slug",
  "category": "다음 중 하나: 트러블슈팅|리눅스|클라우드|네트워크|보안|AI/LLM",
  "tags": ["태그", "3~5개"],
  "summary": "목록에 뜨는 한 줄 요약",
  "body_markdown": "인용구 TL;DR로 시작하는 본문 마크다운"
}"""

def read_queue():
    if not os.path.exists(QUEUE):
        return [], []
    lines = open(QUEUE, encoding="utf-8").read().splitlines()
    topics, keep_idx = [], []
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*-\s+(.*)$", ln)
        if m and m.group(1).strip():
            topics.append((i, m.group(1).strip()))
    return lines, topics

def slugify(s, fallback):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or fallback

def gen(client, topic):
    hint = ""
    if "::" in topic:
        topic, cat = [t.strip() for t in topic.split("::", 1)]
        hint = f"\n(카테고리 힌트: {cat})"
    msg = client.messages.create(
        model=MODEL, max_tokens=2000,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"다음 주제로 글 하나를 써라: {topic}{hint}"}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    data = json.loads(text)
    if data.get("category") not in CATEGORIES:
        data["category"] = "트러블슈팅"
    return data

def main():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY 없음")
    lines, topics = read_queue()
    if not topics:
        print("queue 비어있음 — 생성 건너뜀")
        return
    client = anthropic.Anthropic(api_key=key)
    today = datetime.date.today().isoformat()
    existing = set(os.path.basename(p) for p in glob.glob(os.path.join(POSTS, "*.md")))
    used_line_idx, made = [], 0

    for idx, topic in topics[:N]:
        try:
            d = gen(client, topic)
        except Exception as e:
            print(f"실패(건너뜀): {topic[:30]} … {e}")
            continue
        slug = slugify(d.get("slug"), f"post-{made+1}")
        fname = f"{today}-{slug}.md"
        n = 2
        while fname in existing:
            fname = f"{today}-{slug}-{n}.md"; n += 1
        existing.add(fname)
        fm = {
            "title": d["title"], "date": today, "category": d["category"],
            "tags": d.get("tags", []), "summary": d.get("summary", ""),
        }
        front = "---\n" + "".join(
            (f'{k}: {json.dumps(v, ensure_ascii=False)}\n' if k in ("tags",)
             else f'{k}: "{v}"\n' if k in ("title", "summary") else f"{k}: {v}\n")
            for k, v in fm.items()) + "---\n\n"
        open(os.path.join(POSTS, fname), "w", encoding="utf-8").write(front + d["body_markdown"].strip() + "\n")
        used_line_idx.append(idx); made += 1
        print(f"생성: {fname}")

    # 소비한 토픽 줄 제거
    if used_line_idx:
        keep = [ln for i, ln in enumerate(lines) if i not in set(used_line_idx)]
        open(QUEUE, "w", encoding="utf-8").write("\n".join(keep).rstrip() + "\n")
    print(f"총 {made}개 생성, 남은 큐 갱신 완료")

if __name__ == "__main__":
    main()
