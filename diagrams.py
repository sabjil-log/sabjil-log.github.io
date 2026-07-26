# -*- coding: utf-8 -*-
"""
애니메이션 SVG 다이어그램 모음.
- 글 마크다운에 [[diagram:이름]] 을 쓰면 그 자리에 삽입된다.
- 색은 사이트 CSS 변수(var(--accent) 등)를 그대로 쓰므로 다크모드에 자동 대응.
- 클래스명은 다이어그램별로 접두사(d1-, d2- ...)를 붙여 충돌을 막는다.
"""

_COMMON = """
.dg-box{fill:var(--raise);stroke:var(--line);stroke-width:1.5;}
.dg-t{font-family:var(--sans);font-size:12.5px;fill:var(--ink);}
.dg-ts{font-family:var(--mono);font-size:10.5px;fill:var(--muted);}
.dg-tl{font-family:var(--sans);font-size:13.5px;font-weight:700;fill:var(--ink);}
.dg-ok{fill:var(--accent);}
.dg-no{fill:#E5484D;}
.dg-arrow{stroke:var(--line);stroke-width:1.5;fill:none;}
.dg-wall{stroke:var(--accent);stroke-width:2;stroke-dasharray:5 4;}
@media (prefers-reduced-motion: reduce){
  .dg-anim{animation:none !important;}
}
"""

DIAGRAMS = {}

# ─────────────────────────────────────────────────────────────
DIAGRAMS["stateful-vs-stateless"] = {
    "title": "스테이트풀 vs 스테이트리스 방화벽",
    "caption": "ACG는 나간 요청을 기억해 응답을 자동 통과시키고, NACL은 기억이 없어 응답용 임시 포트를 따로 열어야 합니다.",
    "post": "acg-vs-nacl",
    "svg": """<svg viewBox="0 0 640 320" role="img" aria-label="스테이트풀과 스테이트리스 방화벽 비교">
<style>
""" + _COMMON + """
.d1-pkt{animation:d1-out 3.4s ease-in-out infinite;}
.d1-ret{animation:d1-in 3.4s ease-in-out infinite;}
.d1-ret2{animation:d1-in2 3.4s ease-in-out infinite;}
.d1-x{opacity:0;animation:d1-x 3.4s ease-in-out infinite;}
@keyframes d1-out{0%,8%{transform:translateX(0);opacity:0}
 12%{opacity:1}45%{transform:translateX(190px);opacity:1}52%{opacity:0}100%{opacity:0}}
@keyframes d1-in{0%,50%{transform:translateX(0);opacity:0}
 56%{opacity:1}92%{transform:translateX(-190px);opacity:1}100%{opacity:0}}
@keyframes d1-in2{0%,50%{transform:translateX(0);opacity:0}
 56%{opacity:1}78%{transform:translateX(-105px);opacity:1}86%{transform:translateX(-105px);opacity:0}100%{opacity:0}}
@keyframes d1-x{0%,76%{opacity:0}80%,92%{opacity:1}100%{opacity:0}}
</style>
<text x="16" y="22" class="dg-tl">ACG / 보안그룹 — 스테이트풀</text>
<rect x="16" y="36" width="608" height="106" rx="12" class="dg-box"/>
<rect x="34" y="66" width="74" height="46" rx="8" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
<text x="52" y="94" class="dg-t">서버</text>
<line x1="200" y1="48" x2="200" y2="130" class="dg-wall"/>
<text x="176" y="136" class="dg-ts">ACG</text>
<rect x="532" y="66" width="74" height="46" rx="8" class="dg-box"/>
<text x="556" y="94" class="dg-t">외부</text>
<text x="250" y="66" class="dg-ts">요청 나감</text>
<g class="dg-anim d1-pkt"><circle cx="330" cy="78" r="7" class="dg-ok"/></g>
<text x="250" y="126" class="dg-ts">응답 — 규칙 없이 자동 통과 ✓</text>
<g class="dg-anim d1-ret"><circle cx="520" cy="104" r="7" class="dg-ok"/></g>

<text x="16" y="192" class="dg-tl">NACL — 스테이트리스</text>
<rect x="16" y="206" width="608" height="106" rx="12" class="dg-box"/>
<rect x="34" y="236" width="74" height="46" rx="8" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
<text x="52" y="264" class="dg-t">서버</text>
<line x1="200" y1="218" x2="200" y2="300" class="dg-wall"/>
<text x="170" y="306" class="dg-ts">NACL</text>
<rect x="532" y="236" width="74" height="46" rx="8" class="dg-box"/>
<text x="556" y="264" class="dg-t">외부</text>
<text x="250" y="236" class="dg-ts">인바운드 443 허용 → 요청 OK</text>
<g class="dg-anim d1-pkt"><circle cx="330" cy="248" r="7" class="dg-ok"/></g>
<g class="dg-anim d1-ret2"><circle cx="520" cy="274" r="7" class="dg-no"/></g>
<g class="dg-anim d1-x"><text x="196" y="280" font-size="17" class="dg-no" font-weight="700">✕</text></g>
<text x="250" y="296" class="dg-ts">응답은 임시포트(1024-65535) 미허용 → 차단</text>
</svg>""",
}

# ─────────────────────────────────────────────────────────────
DIAGRAMS["nat-snat"] = {
    "title": "NAT Gateway의 주소 바꿔치기",
    "caption": "발신 주소를 자기 공인 IP로 바꾸고 장부에 적어둡니다. 답장은 장부를 보고 원래 주인에게 배달되죠.",
    "post": "nat-gateway",
    "svg": """<svg viewBox="0 0 640 250" role="img" aria-label="NAT의 SNAT 변환과 장부">
<style>
""" + _COMMON + """
.d2-a{animation:d2-a 4s ease-in-out infinite;}
.d2-b{animation:d2-b 4s ease-in-out infinite;}
.d2-l1{opacity:0;animation:d2-l1 4s ease-in-out infinite;}
.d2-l2{opacity:0;animation:d2-l2 4s ease-in-out infinite;}
.d2-row{opacity:0;animation:d2-row 4s ease-in-out infinite;}
@keyframes d2-a{0%{transform:translateX(0);opacity:0}6%{opacity:1}
 34%{transform:translateX(190px);opacity:1}40%{opacity:0}100%{opacity:0}}
@keyframes d2-b{0%,52%{transform:translateX(0);opacity:0}58%{opacity:1}
 90%{transform:translateX(-190px);opacity:1}100%{opacity:0}}
@keyframes d2-l1{0%,8%{opacity:0}14%,32%{opacity:1}38%{opacity:0}100%{opacity:0}}
@keyframes d2-l2{0%,40%{opacity:0}46%,88%{opacity:1}94%{opacity:0}100%{opacity:0}}
@keyframes d2-row{0%,30%{opacity:0}36%,100%{opacity:1}}
</style>
<rect x="12" y="52" width="96" height="52" rx="8" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
<text x="26" y="74" class="dg-t">private 서버</text>
<text x="26" y="92" class="dg-ts">10.0.3.15</text>
<rect x="256" y="40" width="130" height="76" rx="10" class="dg-box"/>
<text x="278" y="66" class="dg-tl">NAT GW</text>
<text x="278" y="86" class="dg-ts">공인 IP</text>
<text x="278" y="102" class="dg-ts">1.2.3.4</text>
<rect x="536" y="52" width="92" height="52" rx="8" class="dg-box"/>
<text x="556" y="82" class="dg-t">외부 API</text>
<line x1="108" y1="78" x2="256" y2="78" class="dg-arrow"/>
<line x1="386" y1="78" x2="536" y2="78" class="dg-arrow"/>
<g class="dg-anim d2-a"><circle cx="150" cy="78" r="7" class="dg-ok"/></g>
<g class="dg-anim d2-b"><circle cx="480" cy="78" r="7" class="dg-ok"/></g>
<g class="dg-anim d2-l1"><text x="112" y="66" class="dg-ts">from 10.0.3.15:44210</text></g>
<g class="dg-anim d2-l2"><text x="392" y="66" class="dg-ts">from 1.2.3.4:5501 ← 바뀜</text></g>
<rect x="196" y="150" width="250" height="72" rx="10" class="dg-box"/>
<text x="212" y="172" class="dg-tl">장부 (매핑 테이블)</text>
<g class="dg-anim d2-row">
  <text x="212" y="196" class="dg-ts">5501 → 10.0.3.15:44210</text>
  <text x="212" y="212" class="dg-ts">답장은 이 표를 보고 되돌려 배달</text>
</g>
<text x="12" y="238" class="dg-ts">장부는 '나간 통화'에만 생김 → 외부에서 먼저 걸려온 연결은 배달 불가 (단방향)</text>
</svg>""",
}

# ─────────────────────────────────────────────────────────────
DIAGRAMS["rag-pipeline"] = {
    "title": "RAG 2단 검색 파이프라인",
    "caption": "벡터 검색이 넉넉히 후보를 거르고(서류전형), 리랭커가 꼼꼼히 줄 세워(면접) LLM에는 정예만 넘깁니다.",
    "post": "reranker",
    "svg": """<svg viewBox="0 0 640 210" role="img" aria-label="RAG 파이프라인 단계">
<style>
""" + _COMMON + """
.d3-s rect{transition:none;}
.d3-1{animation:d3-h 5s ease-in-out infinite;animation-delay:0s;}
.d3-2{animation:d3-h 5s ease-in-out infinite;animation-delay:1s;}
.d3-3{animation:d3-h 5s ease-in-out infinite;animation-delay:2s;}
.d3-4{animation:d3-h 5s ease-in-out infinite;animation-delay:3s;}
.d3-dot{animation:d3-move 5s ease-in-out infinite;}
@keyframes d3-h{0%,100%{fill:var(--raise);stroke:var(--line)}
 6%,18%{fill:var(--accent-soft);stroke:var(--accent)}}
@keyframes d3-move{0%{transform:translateX(0)}
 18%{transform:translateX(0)}25%{transform:translateX(148px)}
 43%{transform:translateX(148px)}50%{transform:translateX(296px)}
 68%{transform:translateX(296px)}75%{transform:translateX(444px)}
 96%{transform:translateX(444px)}100%{transform:translateX(0);opacity:0}}
</style>
<text x="14" y="24" class="dg-ts">질문</text>
<g class="d3-s">
<rect class="dg-box dg-anim d3-1" x="14" y="34" width="126" height="62" rx="10"/>
<rect class="dg-box dg-anim d3-2" x="162" y="34" width="126" height="62" rx="10"/>
<rect class="dg-box dg-anim d3-3" x="310" y="34" width="126" height="62" rx="10"/>
<rect class="dg-box dg-anim d3-4" x="458" y="34" width="126" height="62" rx="10"/>
</g>
<text x="34" y="60" class="dg-t">임베딩</text>
<text x="34" y="80" class="dg-ts">벡터로 변환</text>
<text x="182" y="60" class="dg-t">벡터 검색</text>
<text x="182" y="80" class="dg-ts">top-50 (빠름·거침)</text>
<text x="330" y="60" class="dg-t">리랭커</text>
<text x="330" y="80" class="dg-ts">top-5 (느림·정확)</text>
<text x="478" y="60" class="dg-t">LLM</text>
<text x="478" y="80" class="dg-ts">근거로만 답변</text>
<line x1="140" y1="65" x2="162" y2="65" class="dg-arrow"/>
<line x1="288" y1="65" x2="310" y2="65" class="dg-arrow"/>
<line x1="436" y1="65" x2="458" y2="65" class="dg-arrow"/>
<g class="dg-anim d3-dot"><circle cx="77" cy="112" r="6" class="dg-ok"/></g>
<text x="14" y="150" class="dg-ts">넉넉히 거르고(k=50) → 야박하게 좁힌다(top-5)</text>
<text x="14" y="172" class="dg-ts">1차에서 정답이 후보에 들어오지 않으면 리랭커도 구제 불가</text>
<text x="14" y="194" class="dg-ts">"근거에 없으면 모른다고 답하라" 지시가 마지막 안전망</text>
</svg>""",
}


def render(name):
    d = DIAGRAMS.get(name)
    if not d:
        return f"<!-- unknown diagram: {name} -->"
    return (f'<figure class="diagram"><div class="dg-cap">{d["title"]}</div>'
            f'{d["svg"]}<figcaption>{d["caption"]}</figcaption></figure>')
