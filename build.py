# -*- coding: utf-8 -*-
"""
삽질노트 - 초경량 정적 블로그 생성기
사용법:  python3 build.py
- posts/YYYY-MM-DD-slug.md  (front matter + 마크다운) 를 읽어
- docs/ 아래 완성된 HTML 을 생성한다. GitHub Pages 는 docs/ 를 그대로 서빙만 하면 됨.
의존성:  markdown, pygments, pyyaml
"""
import os, re, html, glob, datetime, shutil
from string import Template
import yaml
import markdown as md
from pygments.formatters import HtmlFormatter

# ─────────────────────────── 설정 (여기만 고치면 됨) ───────────────────────────
SITE = {
    "handle": "sabjil-log",                   # 프롬프트에 뜨는 핸들 (영문 권장)
    "title": "삽질노트",                        # 블로그 이름
    "tagline": "삽질해서 배운 걸, 남은 안 삽질하게. — 매일 하나씩 정리하는 실무 노트",
    "author": "익명의 엔지니어",                 # ← 가명으로 바꾸세요
    "footer": "© 삽질노트 · 가명 운영",
    "url": "https://sabjil-log.github.io",     # 절대 URL (canonical/sitemap용)
    # 검색엔진 소유확인 (값 받으면 여기에 붙여넣기 — content 값만)
    "google_verification": "",                 # 구글 서치 콘솔
    "naver_verification": "2c95f84cd3549a43e184fe5fb9dbc7fb47f2a312",                  # 네이버 서치어드바이저
}
# 카테고리: 표시이름 → URL 슬러그
CATEGORIES = {
    "트러블슈팅": "troubleshooting",
    "리눅스": "linux",
    "클라우드": "cloud",
    "네트워크": "network",
    "보안": "security",
    "AI/LLM": "ai",
}
PYGMENTS_STYLE = "nord-darker"   # 없으면 monokai 로 폴백
# ────────────────────────────────────────────────────────────────────────────

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
DOCS = os.path.join(ROOT, "docs")

def cat_slug(name):
    return CATEGORIES.get(name, re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "etc")

def read_post(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        raise ValueError(f"front matter 없음: {path}")
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    fname = os.path.basename(path)
    fm = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$", fname)
    date = str(meta.get("date") or (fm.group(1) if fm else ""))
    slug = meta.get("slug") or (fm.group(2) if fm else os.path.splitext(fname)[0])
    text_len = len(re.sub(r"\s+", "", body))
    meta.update({
        "date": date,
        "slug": slug,
        "body_md": body,
        "read_min": max(1, round(text_len / 700)),
        "category": meta.get("category", "트러블슈팅"),
        "tags": meta.get("tags", []) or [],
    })
    return meta

def render_md(text):
    conv = md.Markdown(extensions=[
        "fenced_code", "codehilite", "tables", "toc", "attr_list", "sane_lists",
    ], extension_configs={"codehilite": {"css_class": "highlight", "guess_lang": False}})
    return conv.convert(text)

# ─── 템플릿 ───
BASE = Template("""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$page_title</title>
<meta name="description" content="$desc">
<meta property="og:title" content="$page_title">
<meta property="og:description" content="$desc">
<meta property="og:type" content="$og_type">
<meta property="og:url" content="$canonical">
<meta property="og:site_name" content="$site_title">
<meta property="og:image" content="$og_image">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="$og_image">
<link rel="canonical" href="$canonical">
<link rel="alternate" type="application/rss+xml" title="$site_title" href="${root}feed.xml">
$verification<script>(function(){try{var t=localStorage.getItem('theme');if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',t)}catch(e){}})();</script>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@2.304/css/jetbrains-mono.css">
<link rel="stylesheet" href="${root}assets/style.css">
<link rel="stylesheet" href="${root}assets/highlight.css">
</head>
<body>
<header class="site-head"><div class="wrap">
  <div class="head-row">
    <a class="prompt" href="${root}index.html">~/<span class="dir">$handle</span>&nbsp;$$<span class="cur"></span></a>
    <button id="theme-toggle" class="theme-btn" type="button" aria-label="라이트/다크 전환">☾</button>
  </div>
  <p class="tagline">$tagline</p>
  <nav class="nav">$nav</nav>
</div></header>
<main class="wrap">
$content
</main>
<footer class="site-foot"><div class="wrap"><span>$footer</span><span>$author</span></div></footer>
<script src="${root}assets/app.js" defer></script>
</body>
</html>""")

ENTRY = Template("""<article class="entry" data-search="$search">
  <div class="meta"><span>$date</span><a class="chip" href="${root}c/$cslug.html">--$cslug</a><span>$read min</span></div>
  <h2><a href="${root}p/$slug.html"><span class="g">&#10095;</span>$title</a></h2>
  <p class="sum">$summary</p>
</article>""")

def build_nav(root, active=""):
    home_on = ' class="on"' if active == "home" else ""
    items = [f'<a href="{root}index.html"{home_on}>home</a>']
    for name, slug in CATEGORIES.items():
        on = ' class="on"' if active == slug else ""
        items.append(f'<a href="{root}c/{slug}.html"{on}>--{slug}</a>')
    on = ' class="on"' if active == "archive" else ""
    items.append(f'<a href="{root}archive.html"{on}>--all</a>')
    return "".join(items)


# ─── OG 썸네일 생성 (PIL 없거나 폰트 없으면 조용히 건너뜀) ───
def make_og_images(posts):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL 없음 — OG 이미지 생성 건너뜀"); return
    font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    font_mono = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
    if not os.path.exists(font_path):
        print("한글 폰트 없음 — OG 이미지 생성 건너뜀"); return
    W, H = 1200, 630
    PAPER, INK, GREEN, SOFT, FAINT = "#FAF9F6", "#1C2025", "#1F6B57", "#E7F1ED", "#9AA1A9"
    out_dir = os.path.join(DOCS, "og"); os.makedirs(out_dir, exist_ok=True)
    f_title = ImageFont.truetype(font_path, 62)
    f_small = ImageFont.truetype(font_mono, 30)
    f_chip  = ImageFont.truetype(font_mono, 26)

    def wrap(draw, text, font, max_w):
        lines, cur = [], ""
        for ch in text:
            if draw.textlength(cur + ch, font=font) > max_w and cur:
                lines.append(cur); cur = ch
            else:
                cur += ch
        if cur: lines.append(cur)
        return lines[:4]

    def card(title, chip_text, out_path):
        img = Image.new("RGB", (W, H), PAPER)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 10], fill=GREEN)                       # 상단 그린 바
        d.ellipse([64, 58, 84, 78], fill="#FF5F57")                  # 신호등
        d.ellipse([94, 58, 114, 78], fill="#FEBC2E")
        d.ellipse([124, 58, 144, 78], fill="#28C840")
        d.text((64, 116), f"~/{SITE['handle']} $", font=f_small, fill=GREEN)
        lines = wrap(d, title, f_title, W - 128)
        y = 205
        for ln in lines:
            d.text((64, y), ln, font=f_title, fill=INK); y += 84
        # 하단: 카테고리 칩 + 사이트명
        cw = d.textlength(chip_text, font=f_chip)
        d.rounded_rectangle([64, H-96, 64+cw+36, H-52], radius=22, fill=SOFT)
        d.text((82, H-89), chip_text, font=f_chip, fill=GREEN)
        sw = d.textlength(SITE["title"], font=f_chip)
        d.text((W-64-sw, H-89), SITE["title"], font=f_chip, fill=FAINT)
        img.save(out_path, "PNG")

    card(SITE["tagline"].split("—")[0].strip(), "--home",
         os.path.join(out_dir, "default.png"))
    for p in posts:
        card(p["title"], f'--{cat_slug(p["category"])}',
             os.path.join(out_dir, p["slug"] + ".png"))
    print(f"OG 이미지 {len(posts)+1}개 생성")

def page(path_out, page_title, desc, content, root, og_type="website", nav_active="", og_image=None):
    rel = os.path.relpath(path_out, DOCS).replace(os.sep, "/")
    base = SITE["url"].rstrip("/")
    canonical = base + "/" if rel == "index.html" else f"{base}/{rel}"
    verification = ""
    if SITE.get("google_verification"):
        verification += f'<meta name="google-site-verification" content="{html.escape(SITE["google_verification"])}">\n'
    if SITE.get("naver_verification"):
        verification += f'<meta name="naver-site-verification" content="{html.escape(SITE["naver_verification"])}">\n'
    html_doc = BASE.safe_substitute(
        page_title=page_title, desc=html.escape(desc or SITE["tagline"]),
        og_type=og_type, root=root, handle=SITE["handle"], tagline=html.escape(SITE["tagline"]),
        nav=build_nav(root, nav_active), footer=html.escape(SITE["footer"]),
        author=html.escape(SITE["author"]), content=content,
        canonical=html.escape(canonical), site_title=html.escape(SITE["title"]),
        verification=verification,
        og_image=html.escape(og_image or f'{base}/og/default.png'),
    )
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    open(path_out, "w", encoding="utf-8").write(html_doc)

def main():
    os.makedirs(DOCS, exist_ok=True)
    # pygments css
    try:
        css = HtmlFormatter(style=PYGMENTS_STYLE).get_style_defs(".highlight")
    except Exception:
        css = HtmlFormatter(style="monokai").get_style_defs(".highlight")
    css = ".highlight{background:none!important;}\n.highlight pre{margin:0;}\n" + css
    open(os.path.join(DOCS, "assets", "highlight.css"), "w", encoding="utf-8").write(css)
    open(os.path.join(DOCS, ".nojekyll"), "w").write("")

    posts = [read_post(p) for p in glob.glob(os.path.join(POSTS_DIR, "*.md"))]
    posts.sort(key=lambda x: (x["date"], x["slug"]), reverse=True)

    # 개별 글
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None      # 정렬이 최신순이라 i-1 이 더 최신
        older = posts[i + 1] if i + 1 < len(posts) else None
        body_html = render_md(p["body_md"])
        cslug = cat_slug(p["category"])
        tags = f'<a class="chip" href="../c/{cslug}.html">--{cslug}</a>'
        meta = f'<div class="post-meta"><span>{p["date"]}</span>{tags}<span>{p["read_min"]} min read</span></div>'
        title = f'<h1><span class="g">&#10095;&nbsp;</span>{html.escape(p["title"])}</h1>'
        pn = '<nav class="pn">'
        pn += (f'<a href="../p/{newer["slug"]}.html"><span class="lbl">newer</span>{html.escape(newer["title"])}</a>'
               if newer else '<span></span>')
        pn += (f'<a href="../p/{older["slug"]}.html" style="text-align:right"><span class="lbl">older</span>{html.escape(older["title"])}</a>'
               if older else '<span></span>')
        pn += '</nav>'
        related = [q for q in posts if cat_slug(q["category"]) == cslug and q["slug"] != p["slug"]][:3]
        rel_html = ""
        if related:
            links = "".join(
                f'<a href="../p/{q["slug"]}.html"><span class="g">&#10095;</span>{html.escape(q["title"])}</a>'
                for q in related)
            rel_html = f'<aside class="related"><div class="rel-head">이어서 읽기 · --{cslug}</div>{links}</aside>'
        content = f"<article>{meta}{title}{body_html}{rel_html}{pn}</article>"
        page(os.path.join(DOCS, "p", p["slug"] + ".html"),
             f'{p["title"]} · {SITE["title"]}', p.get("summary", ""),
             content, root="../", og_type="article", nav_active=cslug,
             og_image=f'{SITE["url"].rstrip("/")}/og/{p["slug"]}.png')

    # 홈
    entries = "".join(
        ENTRY.safe_substitute(root="", date=p["date"], cslug=cat_slug(p["category"]),
                              read=p["read_min"], slug=p["slug"],
                              title=html.escape(p["title"]),
                              summary=html.escape(p.get("summary", "")),
                              search=html.escape(" ".join([p["title"], p.get("summary",""),
                                     p["category"], cat_slug(p["category"]),
                                     " ".join(map(str, p["tags"]))]).lower()))
        for p in posts)
    search_box = ('<div class="search"><span class="sig">grep -i</span>'
                  '<input id="q" type="search" placeholder="&quot;검색어&quot; — 제목·요약·태그" '
                  'autocomplete="off" spellcheck="false"></div>')
    home = (f'<section class="list">{search_box}'
            f'<div class="list-head">최근 글 · {len(posts)}개</div>{entries}'
            f'<div class="search-none">일치하는 글이 없어요. 다른 검색어로 시도해보세요.</div></section>')
    page(os.path.join(DOCS, "index.html"), SITE["title"], SITE["tagline"],
         home, root="", nav_active="home")

    # 카테고리별
    for name, slug in CATEGORIES.items():
        sel = [p for p in posts if cat_slug(p["category"]) == slug]
        if not sel:
            body = f'<section class="list"><div class="list-head">--{slug}</div>' \
                   f'<p class="sum" style="padding:20px 0;color:var(--faint)">아직 이 카테고리 글이 없어요.</p></section>'
        else:
            e = "".join(
                ENTRY.safe_substitute(root="../", date=p["date"], cslug=slug, read=p["read_min"],
                                      slug=p["slug"], title=html.escape(p["title"]),
                                      summary=html.escape(p.get("summary", "")),
                                      search="")
                for p in sel)
            body = f'<section class="list"><div class="list-head">--{slug} · {len(sel)}개</div>{e}</section>'
        page(os.path.join(DOCS, "c", slug + ".html"),
             f'--{slug} · {SITE["title"]}', f'{name} 관련 글', body, root="../", nav_active=slug)

    # ─── 아카이브 (월별 전체 글) ───
    months = {}
    for p in posts:
        months.setdefault(p["date"][:7], []).append(p)
    arch = ['<section class="list">']
    for ym in sorted(months, reverse=True):
        y, m = ym.split("-")
        arch.append(f'<div class="list-head">{y}년 {int(m)}월 · {len(months[ym])}개</div>')
        for p in months[ym]:
            arch.append(
                f'<article class="entry"><div class="meta"><span>{p["date"]}</span>'
                f'<a class="chip" href="c/{cat_slug(p["category"])}.html">--{cat_slug(p["category"])}</a></div>'
                f'<h2><a href="p/{p["slug"]}.html"><span class="g">&#10095;</span>{html.escape(p["title"])}</a></h2></article>')
    arch.append("</section>")
    page(os.path.join(DOCS, "archive.html"), f'전체 글 · {SITE["title"]}',
         "월별 전체 글 목록", "".join(arch), root="", nav_active="archive")

    # ─── SEO: sitemap.xml / robots.txt / feed.xml ───
    import email.utils, calendar
    base = SITE["url"].rstrip("/")
    today = datetime.date.today().isoformat()

    make_og_images(posts)

    urls = [(base + "/", today), (base + "/archive.html", today)]
    urls += [(f'{base}/p/{p["slug"]}.html', p["date"]) for p in posts]
    for name, slug in CATEGORIES.items():
        if any(cat_slug(p["category"]) == slug for p in posts):
            urls.append((f"{base}/c/{slug}.html", today))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod in urls:
        sm.append(f"  <url><loc>{html.escape(loc)}</loc><lastmod>{mod}</lastmod></url>")
    sm.append("</urlset>\n")
    open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))

    open(os.path.join(DOCS, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % base)

    items = []
    for p in posts[:20]:
        ts = calendar.timegm(datetime.datetime.strptime(p["date"], "%Y-%m-%d").timetuple())
        items.append(
            "    <item>\n"
            f"      <title>{html.escape(p['title'])}</title>\n"
            f"      <link>{base}/p/{p['slug']}.html</link>\n"
            f"      <guid>{base}/p/{p['slug']}.html</guid>\n"
            f"      <pubDate>{email.utils.formatdate(ts)}</pubDate>\n"
            f"      <description>{html.escape(p.get('summary',''))}</description>\n"
            "    </item>")
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        f"  <title>{html.escape(SITE['title'])}</title>\n"
        f"  <link>{base}/</link>\n"
        f"  <description>{html.escape(SITE['tagline'])}</description>\n"
        "  <language>ko</language>\n"
        + "\n".join(items) + "\n</channel></rss>\n")
    open(os.path.join(DOCS, "feed.xml"), "w", encoding="utf-8").write(feed)

    print(f"built: {len(posts)} posts, {len(CATEGORIES)} categories -> docs/  (+sitemap/robots/feed)")

if __name__ == "__main__":
    main()
