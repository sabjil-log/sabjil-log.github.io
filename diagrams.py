# -*- coding: utf-8 -*-
"""
애니메이션 SVG 다이어그램 모음.
- 글 마크다운에 [[diagram:이름]] 을 쓰면 그 자리에 삽입된다.
- 색은 사이트 CSS 변수(var(--accent) 등)를 그대로 쓰므로 다크모드에 자동 대응.
- 클래스명은 다이어그램별로 접두사(d1-, d2- ...)를 붙여 충돌을 막는다.
"""

_COMMON = """
.dg-box{fill:var(--raise);stroke:var(--line);stroke-width:1.5;}
.dg-t{font-family:var(--sans);font-size:12.5px;font-weight:600;fill:var(--dg-blue);}
.dg-ts{font-family:var(--mono);font-size:10.5px;fill:var(--muted);}
.dg-tl{font-family:var(--sans);font-size:13.5px;font-weight:700;fill:var(--dg-red);}
.dg-ok{fill:var(--accent);}
.dg-no{fill:#E5484D;}
.dg-arrow{stroke:var(--line);stroke-width:1.5;fill:none;}
.dg-key{font-family:var(--sans);font-size:13px;font-weight:700;fill:var(--dg-red);}
.dg-lab{font-family:var(--sans);font-size:12.5px;fill:var(--dg-blue);}
.dg-lab2{font-family:var(--mono);font-size:10.5px;fill:var(--dg-blue);}
.dg-warn{font-family:var(--sans);font-size:12.5px;font-weight:700;fill:var(--dg-amber);}
.dg-chk{fill:var(--dg-green);font-weight:700;}
.dg-wall{stroke:var(--accent);stroke-width:2;stroke-dasharray:5 4;}
@media (prefers-reduced-motion: reduce){
  .dg-anim{animation:none !important;}
}
"""

DIAGRAMS = {}

# ══════════════════════════════════════════════════════════════
#  아이콘 라이브러리 — 32×32 기준, (cx, cy) 중심에 배치
# ══════════════════════════════════════════════════════════════
_ICONS = {
 "laptop": """
<rect x="4" y="4" width="24" height="16" rx="2" fill="var(--dg-metal)" stroke="var(--dg-metal-d)" stroke-width="1.7"/>
<rect x="6.5" y="6.5" width="19" height="11" rx="1" fill="var(--dg-screen)"/>
<path d="M1.5 22 h29 l-2.5 3.5 H4 z" fill="var(--dg-metal)" stroke="var(--dg-metal-d)" stroke-width="1.7" stroke-linejoin="round"/>""",
 "server": """
<rect x="6" y="3" width="20" height="26" rx="2.5" fill="var(--dg-metal)" opacity="1" stroke="var(--dg-metal-d)" stroke-width="1.7"/>
<rect x="9" y="6.5" width="14" height="5" rx="1" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.3"/>
<rect x="9" y="13.5" width="14" height="5" rx="1" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.3"/>
<rect x="9" y="20.5" width="14" height="5" rx="1" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.3"/>
<circle cx="20.5" cy="9" r="1.1" fill="var(--dg-green)"/>
<circle cx="20.5" cy="16" r="1.1" fill="var(--dg-green)"/>
<circle cx="20.5" cy="23" r="1.1" fill="var(--dg-amber)"/>""",
 "cloud": """
<path d="M8.5 24 a6 6 0 0 1 0.6 -11.95 a8.2 8.2 0 0 1 15.3 -1 a5.8 5.8 0 0 1 0.6 12.95 z"
      fill="var(--dg-blue-s)" stroke="var(--dg-blue)" stroke-width="1.8" stroke-linejoin="round"/>""",
 "router": """
<rect x="3" y="17" width="26" height="10" rx="3" fill="var(--dg-metal)" stroke="var(--dg-metal-d)" stroke-width="1.7"/>
<path d="M10 17 L 7 6" stroke="var(--dg-metal-d)" stroke-width="2" stroke-linecap="round"/>
<path d="M22 17 L 25 6" stroke="var(--dg-metal-d)" stroke-width="2" stroke-linecap="round"/>
<circle cx="9" cy="22" r="1.2" fill="var(--dg-green)"/>
<circle cx="13.5" cy="22" r="1.2" fill="var(--dg-green)"/>
<circle cx="18" cy="22" r="1.2" fill="var(--dg-amber)"/>""",
 "switch": """
<rect x="2" y="11" width="28" height="11" rx="2" fill="var(--dg-metal)" stroke="var(--dg-metal-d)" stroke-width="1.7"/>
<rect x="5" y="14" width="3.2" height="5" rx="0.6" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.1"/>
<rect x="10" y="14" width="3.2" height="5" rx="0.6" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.1"/>
<rect x="15" y="14" width="3.2" height="5" rx="0.6" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.1"/>
<rect x="20" y="14" width="3.2" height="5" rx="0.6" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.1"/>
<circle cx="26.5" cy="16.5" r="1.2" fill="var(--dg-green)"/>""",
 "firewall": """
<rect x="3" y="6" width="26" height="20" rx="2" fill="var(--dg-red-s)" stroke="var(--dg-red)" stroke-width="1.7"/>
<path d="M3 12.6 h26 M3 19.3 h26" stroke="var(--dg-red)" stroke-width="1.3"/>
<path d="M11 6 v6.6 M20 6 v6.6 M7 12.6 v6.7 M16 12.6 v6.7 M24.5 12.6 v6.7 M11 19.3 v6.7 M20 19.3 v6.7"
      stroke="var(--dg-red)" stroke-width="1.3"/>
<path d="M16 13 c2.6 2.4 3.4 4.2 3.4 6 a3.4 3.4 0 0 1 -6.8 0 c0 -1.8 0.8 -3.6 3.4 -6 z"
      fill="var(--dg-amber)" stroke="var(--dg-red)" stroke-width="1.3"/>""",
 "globe": """
<circle cx="16" cy="16" r="13" fill="var(--dg-blue-s)" stroke="var(--dg-blue)" stroke-width="1.8"/>
<ellipse cx="16" cy="16" rx="5.5" ry="13" fill="none" stroke="var(--dg-blue)" stroke-width="1.4"/>
<path d="M3 16 h26 M5.2 9.5 h21.6 M5.2 22.5 h21.6" stroke="var(--dg-blue)" stroke-width="1.4"/>""",
 "database": """
<path d="M5 8.5 v15 c0 2.4 4.9 4.3 11 4.3 s11 -1.9 11 -4.3 v-15 z"
      fill="var(--dg-violet-s)" stroke="var(--dg-violet)" stroke-width="1.7"/>
<ellipse cx="16" cy="8.5" rx="11" ry="4.3" fill="var(--raise)" stroke="var(--dg-violet)" stroke-width="1.7"/>
<path d="M5 15.5 c0 2.4 4.9 4.3 11 4.3 s11 -1.9 11 -4.3" fill="none" stroke="var(--dg-violet)" stroke-width="1.4"/>""",
 "lock": """
<path d="M10 14 v-3.5 a6 6 0 0 1 12 0 V14" fill="none" stroke="var(--dg-metal-d)" stroke-width="2" stroke-linecap="round"/>
<rect x="6.5" y="14" width="19" height="14" rx="2.5" fill="var(--dg-amber-s)" stroke="var(--dg-amber)" stroke-width="1.8"/>
<circle cx="16" cy="20" r="2" fill="var(--dg-amber)"/>
<path d="M16 21.5 v3" stroke="var(--dg-amber)" stroke-width="2" stroke-linecap="round"/>""",
 "shield": """
<path d="M16 3 L28 7 v9 c0 7.5 -6.4 12.6 -12 14 C10.4 28.6 4 23.5 4 16 V7 z"
      fill="var(--dg-green-s)" stroke="var(--dg-green)" stroke-width="1.8" stroke-linejoin="round"/>
<path d="M10.5 15.5 l4.2 4.2 L22 12" fill="none" stroke="var(--dg-green)" stroke-width="2.6"
      stroke-linecap="round" stroke-linejoin="round"/>""",
 "user": """
<circle cx="16" cy="10" r="6" fill="var(--dg-blue-s)" stroke="var(--dg-blue)" stroke-width="1.8"/>
<path d="M4.5 29 c0 -6.6 5.2 -11 11.5 -11 s11.5 4.4 11.5 11" fill="var(--dg-blue-s)"
      stroke="var(--dg-blue)" stroke-width="1.8" stroke-linecap="round"/>""",
 "gateway": """
<path d="M5 29 V13 a11 11 0 0 1 22 0 v16 z" fill="var(--dg-metal)" stroke="var(--dg-metal-d)" stroke-width="1.8"/>
<path d="M11 29 V15 a5 5 0 0 1 10 0 v14 z" fill="var(--dg-blue-s)" stroke="var(--dg-blue)" stroke-width="1.7"/>
<circle cx="19" cy="22" r="1.2" fill="var(--dg-blue)"/>""",
 "box": """
<path d="M16 3 L28 9 v14 L16 29 L4 23 V9 z" fill="var(--dg-teal)" opacity=".16"/>
<path d="M16 3 L28 9 v14 L16 29 L4 23 V9 z" fill="none" stroke="var(--dg-teal)" stroke-width="1.8" stroke-linejoin="round"/>
<path d="M4 9 L16 15 L28 9 M16 15 v14" fill="none" stroke="var(--dg-teal)" stroke-width="1.5"/>""",
 "doc": """
<path d="M8 3 h11 l6 6 v20 H8 z" fill="var(--raise)" stroke="var(--dg-metal-d)" stroke-width="1.7" stroke-linejoin="round"/>
<path d="M19 3 v6 h6" fill="none" stroke="var(--dg-metal-d)" stroke-width="1.7"/>
<path d="M11.5 15 h10 M11.5 19 h10 M11.5 23 h6" stroke="var(--dg-blue)" stroke-width="1.7" stroke-linecap="round"/>""",
 "brain": """
<path d="M16 5 a6 6 0 0 0 -6 6 a5 5 0 0 0 -2 9 a5.5 5.5 0 0 0 8 6 a5.5 5.5 0 0 0 8 -6 a5 5 0 0 0 -2 -9 a6 6 0 0 0 -6 -6 z"
      fill="var(--dg-violet-s)" stroke="var(--dg-violet)" stroke-width="1.8"/>
<path d="M16 6 v20 M11 12 h4 M17 17 h4 M12 21 h4" fill="none" stroke="var(--dg-violet)" stroke-width="1.4" stroke-linecap="round"/>""",
}


_HALO = {
    "server": "var(--dg-blue-s)", "laptop": "var(--dg-blue-s)", "globe": "var(--dg-blue-s)",
    "cloud": "var(--dg-blue-s)", "user": "var(--dg-blue-s)", "gateway": "var(--dg-blue-s)",
    "doc": "var(--dg-blue-s)", "router": "var(--dg-green-s)", "switch": "var(--dg-green-s)",
    "shield": "var(--dg-green-s)", "box": "var(--dg-green-s)",
    "firewall": "var(--dg-red-s)", "lock": "var(--dg-amber-s)",
    "database": "var(--dg-violet-s)", "brain": "var(--dg-violet-s)",
}

def _icon(name, cx, cy, s=1.0, halo=False):
    """아이콘을 (cx, cy) 중심에 배치. s=1 → 32px. halo=True 면 파스텔 원 배경."""
    body = _ICONS.get(name)
    if not body:
        return ""
    pre = ""
    if halo:
        r = 16 * s + 7
        pre = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
               f'fill="{_HALO.get(name, "var(--dg-blue-s)")}"/>')
    return (pre + f'<g transform="translate({cx - 16 * s:.1f},{cy - 16 * s:.1f}) scale({s:.3f})">'
            f'{body}</g>')


# ─────────────────────────────────────────────────────────────
DIAGRAMS["stateful-vs-stateless"] = {
    "title": "스테이트풀 vs 스테이트리스 방화벽",
    "caption": "ACG는 나간 요청을 기억해 응답을 자동 통과시키고, NACL은 기억이 없어 응답용 임시 포트를 따로 열어야 합니다.",
    "post": "acg-vs-nacl",
    "svg": """<svg viewBox="0 0 640 330" role="img" aria-label="스테이트풀과 스테이트리스 방화벽 비교">
<style>
""" + _COMMON + """
.d1-pkt{animation:d1-out 3.4s ease-in-out infinite;}
.d1-ret{animation:d1-in 3.4s ease-in-out infinite;}
.d1-ret2{animation:d1-in2 3.4s ease-in-out infinite;}
.d1-x{opacity:0;animation:d1-x 3.4s ease-in-out infinite;}
@keyframes d1-out{0%,8%{transform:translateX(0);opacity:0}
 12%{opacity:1}45%{transform:translateX(210px);opacity:1}52%{opacity:0}100%{opacity:0}}
@keyframes d1-in{0%,50%{transform:translateX(0);opacity:0}
 56%{opacity:1}92%{transform:translateX(-210px);opacity:1}100%{opacity:0}}
@keyframes d1-in2{0%,50%{transform:translateX(0);opacity:0}
 56%{opacity:1}78%{transform:translateX(-118px);opacity:1}86%{transform:translateX(-118px);opacity:0}100%{opacity:0}}
@keyframes d1-x{0%,76%{opacity:0}80%,92%{opacity:1}100%{opacity:0}}
</style>
<text x="16" y="24" class="dg-key" font-size="14">ACG / 보안그룹 &#8212; 스테이트풀 (대화를 기억)</text>
<rect x="16" y="34" width="608" height="112" rx="12" class="dg-box"/>
""" + _icon("server", 62, 88, 1.9, halo=True) + """
<text x="44" y="132" class="dg-lab2">서버</text>
""" + _icon("shield", 210, 88, 1.8, halo=True) + """
<text x="188" y="132" class="dg-lab2">ACG</text>
""" + _icon("globe", 566, 88, 1.9, halo=True) + """
<text x="546" y="132" class="dg-lab2">외부</text>
<text x="268" y="66" class="dg-lab">요청 나감</text>
<g class="dg-anim d1-pkt"><circle cx="300" cy="78" r="7" fill="var(--dg-green)"/></g>
<text x="268" y="122" class="dg-lab">응답 &#8212; 규칙 없이 자동 통과 <tspan class="dg-chk">&#10003;</tspan></text>
<g class="dg-anim d1-ret"><circle cx="510" cy="104" r="7" fill="var(--dg-green)"/></g>

<text x="16" y="196" class="dg-key" font-size="14">NACL &#8212; 스테이트리스 (기억 없음)</text>
<rect x="16" y="206" width="608" height="112" rx="12" class="dg-box"/>
""" + _icon("server", 62, 260, 1.9, halo=True) + """
<text x="44" y="304" class="dg-lab2">서버</text>
""" + _icon("firewall", 210, 260, 1.8, halo=True) + """
<text x="186" y="304" class="dg-lab2">NACL</text>
""" + _icon("globe", 566, 260, 1.9, halo=True) + """
<text x="546" y="304" class="dg-lab2">외부</text>
<text x="268" y="238" class="dg-lab">인바운드 443 허용 &#8594; 요청 OK</text>
<g class="dg-anim d1-pkt"><circle cx="300" cy="250" r="7" fill="var(--dg-green)"/></g>
<g class="dg-anim d1-ret2"><circle cx="510" cy="276" r="7" fill="var(--dg-red)"/></g>
<g class="dg-anim d1-x"><text x="238" y="284" font-size="18" fill="var(--dg-red)" font-weight="700">&#10007;</text></g>
<text x="268" y="296" class="dg-warn">응답은 임시포트(1024-65535) 미허용 &#8594; 차단</text>
</svg>""",
}

# ─────────────────────────────────────────────────────────────
DIAGRAMS["nat-snat"] = {
    "title": "NAT Gateway의 주소 바꿔치기",
    "caption": "발신 주소를 자기 공인 IP로 바꾸고 장부에 적어둡니다. 답장은 장부를 보고 원래 주인에게 배달되죠.",
    "post": "nat-gateway",
    "svg": """<svg viewBox="0 0 640 262" role="img" aria-label="NAT의 SNAT 변환과 장부">
<style>
""" + _COMMON + """
.d2-a{animation:d2-a 4s ease-in-out infinite;}
.d2-b{animation:d2-b 4s ease-in-out infinite;}
.d2-l1{opacity:0;animation:d2-l1 4s ease-in-out infinite;}
.d2-l2{opacity:0;animation:d2-l2 4s ease-in-out infinite;}
.d2-row{opacity:0;animation:d2-row 4s ease-in-out infinite;}
@keyframes d2-a{0%{transform:translateX(0);opacity:0}6%{opacity:1}
 34%{transform:translateX(170px);opacity:1}40%{opacity:0}100%{opacity:0}}
@keyframes d2-b{0%,52%{transform:translateX(0);opacity:0}58%{opacity:1}
 90%{transform:translateX(-170px);opacity:1}100%{opacity:0}}
@keyframes d2-l1{0%,8%{opacity:0}14%,32%{opacity:1}38%{opacity:0}100%{opacity:0}}
@keyframes d2-l2{0%,40%{opacity:0}46%,88%{opacity:1}94%{opacity:0}100%{opacity:0}}
@keyframes d2-row{0%,30%{opacity:0}36%,100%{opacity:1}}
</style>
""" + _icon("server", 54, 72, 1.9, halo=True) + """
<text x="14" y="118" class="dg-t">private 서버</text>
<text x="14" y="134" class="dg-ts">10.0.3.15</text>
""" + _icon("gateway", 318, 72, 2.1, halo=True) + """
<text x="286" y="118" class="dg-tl">NAT GW</text>
<text x="286" y="134" class="dg-ts">공인 IP 1.2.3.4</text>
""" + _icon("globe", 584, 72, 1.9, halo=True) + """
<text x="548" y="118" class="dg-t">외부 API</text>
<line x1="92" y1="72" x2="288" y2="72" class="dg-arrow"/>
<line x1="350" y1="72" x2="550" y2="72" class="dg-arrow"/>
<g class="dg-anim d2-a"><circle cx="120" cy="72" r="7" fill="var(--dg-green)"/></g>
<g class="dg-anim d2-b"><circle cx="530" cy="72" r="7" fill="var(--dg-green)"/></g>
<g class="dg-anim d2-l1"><text x="100" y="60" class="dg-lab2">from 10.0.3.15:44210</text></g>
<g class="dg-anim d2-l2"><text x="360" y="60" class="dg-lab2">from 1.2.3.4:5501 &#8592; 바뀜</text></g>
<rect x="196" y="160" width="250" height="72" rx="10" class="dg-box"/>
""" + _icon("doc", 222, 196, 1.3) + """
<text x="250" y="182" class="dg-tl">장부 (매핑 테이블)</text>
<g class="dg-anim d2-row">
  <text x="250" y="204" class="dg-lab2">5501 &#8594; 10.0.3.15:44210</text>
  <text x="250" y="220" class="dg-ts">답장은 이 표를 보고 되돌려 배달</text>
</g>
<text x="14" y="252" class="dg-ts">장부는 '나간 통화'에만 생김 &#8594; 외부에서 먼저 걸려온 연결은 배달 불가 (단방향)</text>
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
""" + _icon("doc", 34, 55, 1.3) + """<text x="60" y="60" class="dg-t">임베딩</text>
<text x="34" y="80" class="dg-ts">벡터로 변환</text>
<text x="182" y="60" class="dg-t">벡터 검색</text>
<text x="182" y="80" class="dg-ts">top-50 (빠름·거침)</text>
<text x="330" y="60" class="dg-t">리랭커</text>
<text x="330" y="80" class="dg-ts">top-5 (느림·정확)</text>
""" + _icon("brain", 478, 55, 1.3) + """<text x="504" y="60" class="dg-t">LLM</text>
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


# ══════════════════════════════════════════════════════════════
#  재사용 생성기 — 흐름도 / 사다리 / 막대 / 2단 비교
# ══════════════════════════════════════════════════════════════
def _add(name, title, caption, post, svg):
    DIAGRAMS[name] = {"title": title, "caption": caption, "post": post, "svg": svg}


def _flow(uid, steps, note=""):
    """가로 흐름도. steps = [(제목, 부제), ...] — 순서대로 하이라이트."""
    n = len(steps); pad = gap = 12; w = 640
    bw = (w - 2 * pad - (n - 1) * gap) / n
    dur = round(n * 1.15, 2); win = round(100.0 / n * 0.6, 1)
    css = [_COMMON]
    for i in range(n):
        css.append(f".{uid}-{i}{{animation:{uid}-h {dur}s ease-in-out infinite;"
                   f"animation-delay:{round(i * dur / n, 2)}s;}}")
    css.append(f"@keyframes {uid}-h{{0%,100%{{fill:var(--raise);stroke:var(--line)}}"
               f"2%,{win}%{{fill:var(--accent-soft);stroke:var(--accent)}}}}")
    h = 116 if note else 96
    o = [f'<svg viewBox="0 0 {w} {h}" role="img"><style>' + "\n".join(css) + "</style>"]
    for i, step in enumerate(steps):
        t, sub = step[0], step[1]
        ic = step[2] if len(step) > 2 else None
        x = pad + i * (bw + gap)
        o.append(f'<rect class="dg-box dg-anim {uid}-{i}" x="{x:.0f}" y="18" '
                 f'width="{bw:.0f}" height="58" rx="10"/>')
        tx = x + 11
        if ic:
            o.append(_icon(ic, x + 32, 47, 1.25, halo=True))
            tx = x + 58
        o.append(f'<text x="{tx:.0f}" y="42" class="dg-key">{t}</text>')
        o.append(f'<text x="{tx:.0f}" y="62" class="dg-lab2">{sub}</text>')
        if i < n - 1:
            o.append(f'<line x1="{x + bw:.0f}" y1="47" x2="{x + bw + gap:.0f}" y2="47" class="dg-arrow"/>')
    if note:
        o.append(f'<text x="{pad}" y="102" class="dg-ts">{note}</text>')
    return "".join(o) + "</svg>"


def _ladder(uid, rows, note=""):
    """세로 사다리. rows = [(층이름, 확인방법, 멈추면 무슨 뜻), ...]"""
    n = len(rows); w = 640; rh = 48
    h = 20 + n * rh + (26 if note else 6)
    dur = round(n * 1.0, 2); win = round(100.0 / n * 0.6, 1)
    css = [_COMMON]
    for i in range(n):
        css.append(f".{uid}-{i}{{animation:{uid}-h {dur}s ease-in-out infinite;"
                   f"animation-delay:{round(i * dur / n, 2)}s;}}")
    css.append(f"@keyframes {uid}-h{{0%,100%{{fill:var(--raise);stroke:var(--line)}}"
               f"2%,{win}%{{fill:var(--accent-soft);stroke:var(--accent)}}}}")
    o = [f'<svg viewBox="0 0 {w} {h}" role="img"><style>' + "\n".join(css) + "</style>"]
    for i, row in enumerate(rows):
        name, how, mean = row[0], row[1], row[2]
        ic = row[3] if len(row) > 3 else None
        y = 12 + i * rh
        o.append(f'<rect class="dg-box dg-anim {uid}-{i}" x="12" y="{y}" width="616" height="38" rx="9"/>')
        if ic:
            o.append(_icon(ic, 36, y + 19, 1.15))
        else:
            o.append(f'<circle cx="34" cy="{y + 19}" r="12" fill="var(--dg-red)" opacity=".12"/>')
            o.append(f'<text x="30" y="{y + 24}" class="dg-ts" fill="var(--dg-red)">{i + 1}</text>')
        o.append(f'<text x="60" y="{y + 24}" class="dg-t">{name}</text>')
        o.append(f'<text x="216" y="{y + 24}" class="dg-lab2">{how}</text>')
        o.append(f'<text x="396" y="{y + 24}" class="dg-ts">{mean}</text>')
    if note:
        o.append(f'<text x="12" y="{h - 8}" class="dg-ts">{note}</text>')
    return "".join(o) + "</svg>"


def _bars(uid, items, maxv, note="", thr=None, thr_label=""):
    """가로 막대. items = [(라벨, 값, 값표기), ...]"""
    n = len(items); w = 640; x0 = 164; bwmax = w - x0 - 128; rh = 44
    h = 16 + n * rh + (28 if note else 8)
    css = [_COMMON, f".{uid}-b{{animation:{uid}-g 2.6s ease-out infinite;transform-origin:left center;}}",
           f"@keyframes {uid}-g{{0%{{transform:scaleX(0)}}45%,100%{{transform:scaleX(1)}}}}"]
    o = [f'<svg viewBox="0 0 {w} {h}" role="img"><style>' + "\n".join(css) + "</style>"]
    if thr is not None:
        tx = x0 + bwmax * thr / maxv
        o.append(f'<line x1="{tx:.0f}" y1="6" x2="{tx:.0f}" y2="{16 + n * rh - 6}" class="dg-wall"/>')
        o.append(f'<text x="{tx + 6:.0f}" y="16" class="dg-ts" fill="var(--dg-red)">{thr_label}</text>')
    for i, item in enumerate(items):
        lab, val, txt = item[0], item[1], item[2]
        ic = item[3] if len(item) > 3 else None
        y = 22 + i * rh
        bw = bwmax * val / maxv
        over = thr is not None and val > thr
        col = "var(--dg-red)" if over else "var(--dg-green)"
        if ic:
            o.append(_icon(ic, 30, y + 13, 0.9, halo=True))
            o.append(f'<text x="52" y="{y + 19}" class="dg-t">{lab}</text>')
        else:
            o.append(f'<text x="12" y="{y + 18}" class="dg-t">{lab}</text>')
        o.append(f'<rect x="{x0}" y="{y + 4}" width="{bwmax}" height="20" rx="5" '
                 f'fill="var(--line-2)"/>')
        o.append(f'<g class="dg-anim {uid}-b" style="animation-delay:{round(i * .18, 2)}s">'
                 f'<rect x="{x0}" y="{y + 4}" width="{bw:.0f}" height="20" rx="5" fill="{col}" opacity=".85"/></g>')
        o.append(f'<text x="{x0 + bw + 8:.0f}" y="{y + 19}" class="dg-ts">{txt}</text>')
    if note:
        o.append(f'<text x="12" y="{h - 8}" class="dg-ts">{note}</text>')
    return "".join(o) + "</svg>"


def _two(uid, lt, ll, rt, rl, note="", licon=None, ricon=None):
    """2단 비교. ll/rl = [(mark, 텍스트)] — mark: ok|no|dot"""
    w = 640; pw = (w - 36) / 2
    rows = max(len(ll), len(rl))
    h = 68 + rows * 24 + (26 if note else 10)
    o = [f'<svg viewBox="0 0 {w} {h}" role="img"><style>' + _COMMON + "</style>"]
    for k, (t, lines, x, ic) in enumerate([(lt, ll, 12, licon), (rt, rl, 24 + pw, ricon)]):
        o.append(f'<rect class="dg-box" x="{x:.0f}" y="10" width="{pw:.0f}" '
                 f'height="{h - (34 if note else 20)}" rx="12"/>')
        tx = x + 16
        if ic:
            o.append(_icon(ic, x + 36, 40, 1.15, halo=True))
            tx = x + 64
        o.append(f'<text x="{tx:.0f}" y="46" class="dg-tl">{t}</text>')
        for i, (mk, txt) in enumerate(lines):
            y = 76 + i * 24
            sym = {"ok": ("✓", "var(--dg-green)"), "no": ("✕", "var(--dg-red)"),
                   "dot": ("·", "var(--muted)")}[mk]
            o.append(f'<text x="{x + 16:.0f}" y="{y}" font-size="13" font-weight="700" '
                     f'fill="{sym[1]}">{sym[0]}</text>')
            o.append(f'<text x="{x + 32:.0f}" y="{y}" class="dg-ts">{txt}</text>')
    if note:
        o.append(f'<text x="12" y="{h - 8}" class="dg-ts">{note}</text>')
    return "".join(o) + "</svg>"


# ── 생성기 기반 다이어그램 등록 ────────────────────────────────
_add("triage-ladder", "접속 실패, 계층별 진단 사다리",
     "아래층부터 한 칸씩 올라가며 확인합니다. 멈춘 층이 곧 범인의 위치예요.",
     "network-triage",
     _ladder("tl", [
         ("DNS 해석", "dig +short 도메인", "실패 → DNS 설정·오타", "globe"),
         ("경로 도달", "traceroute 도메인", "멈춤 → 라우팅 차단", "router"),
         ("포트 응답", "nc -vz 호스트 443", "실패 → 방화벽·앱 부재", "switch"),
         ("리스닝 확인", "ss -tlnp | grep :443", "없음 → 미기동·바인딩", "server"),
         ("방화벽", "ACG / NACL / iptables", "NACL은 응답 포트도", "firewall"),
         ("앱 레벨", "curl -v .../health", "5xx → 앱 내부 오류", "doc"),
     ], "위에서 아래로 내려가는 게 아니라, 아래(네트워크)에서 위(앱)로 올라가며 좁힙니다"))

_add("grep-awk-sed", "grep · awk · sed 역할 분담",
     "줄을 고르고 → 칸을 자르고 → 글자를 다듬는다. 파이프는 접시를 넘기는 컨베이어입니다.",
     "grep-awk-sed",
     _flow("gas", [("grep", "줄 고르기", "doc"),
                   ("awk", "칸 자르기", "switch"),
                   ("sed", "글자 바꾸기", "box")],
           "랭킹 관용구: … | sort | uniq -c | sort -rn | head  ← 세어서 순위 만들기"))

_add("curl-stages", "curl -v가 보여주는 4단계",
     "출력이 어느 단계에서 멈추는지가 곧 진단 결과입니다. refused와 timeout의 구분이 핵심.",
     "curl-verbose",
     _flow("cv", [("DNS", "이름 → IP", "globe"),
                  ("TCP", "Connected", "router"),
                  ("TLS", "인증서 검증", "lock"),
                  ("HTTP", "요청 / 응답", "doc")],
           "refused = 도착했는데 아무도 없음 · timeout = 패킷이 증발 (방화벽 계열)"))

_add("kubectl-five", "kubectl 디버깅 다섯 개의 창",
     "앱의 말 → 쿠버의 말 → 현장 → 설계도 → 직통. 대개 이 순서로 꺼냅니다.",
     "kubectl-five",
     _flow("kf", [("logs", "앱의 말", "doc"),
                  ("describe", "쿠버의 말", "box"),
                  ("exec", "현장 진입", "server"),
                  ("get -o yaml", "설계도", "doc"),
                  ("port-fwd", "직통", "router")],
           "CrashLoop이면 logs --previous 부터 · 연결 문제면 port-forward로 구간 이분탐색"))

_add("healthcheck-gates", "헬스체크가 통과해야 하는 3개의 관문",
     "노크가 닿고(방화벽), 문이 맞고(포트), 대답이 200이어야(경로) 살아있음 도장이 찍힙니다.",
     "lb-healthcheck",
     _flow("hg", [("① 방화벽", "ACG·NACL 통과", "firewall"),
                  ("② 포트", "리스닝 확인", "server"),
                  ("③ 경로+200", "/health 200", "shield")],
           "진단: tcpdump(노크 도착?) → ss(포트 맞나?) → curl 127.0.0.1(200 주나?)"))

_add("static-hosting", "정적 호스팅 3단 구성",
     "버킷은 원본 창고, CDN이 HTTPS·도메인·캐시를 담당합니다. 버킷 단독으로는 HTTPS가 안 돼요.",
     "object-storage-hosting",
     _flow("sh", [("사용자", "브라우저 요청", "user"),
                  ("CDN", "HTTPS·캐시", "cloud"),
                  ("버킷", "정적 파일 원본", "database")],
           "공개 버킷은 사이트 파일만 · SPA는 에러문서를 index.html 로 · 캐시는 해시 파일명으로"))

_add("agent-loop", "에이전트의 실행 루프",
     "모델은 실행 '요청서'를 쓸 뿐이고, 방아쇠는 항상 우리 코드가 당깁니다. 그 사이가 안전장치의 자리죠.",
     "agents-tool-use",
     _flow("al", [("① 도구 명세", "목록 전달", "doc"),
                  ("② 도구 요청", "모델이 지정", "brain"),
                  ("③ 우리가 실행", "승인 게이트", "gateway"),
                  ("④ 결과 회신", "붙여 재질의", "box")],
           "④ 다음 다시 ②로 — 도구 요청이 안 나올 때까지 반복하는 while 루프가 에이전트의 정체"))

_add("mcp-mxn", "M×N 어댑터 지옥 → M+N",
     "도구마다 클라이언트마다 어댑터를 짜던 걸, 표준 콘센트 하나로 수렴시키는 게 MCP의 가치입니다.",
     "what-is-mcp",
     _two("mx", "MCP 없이 — M×N", [
         ("no", "도구 10개 × 클라이언트 4개 = 통합 40번"),
         ("no", "클라이언트마다 연동 방식이 다름"),
         ("no", "도구 하나 고치면 어댑터 전부 손봄"),
         ("dot", "USB 이전의 충전 단자 난립 상태"),
     ], "MCP로 — M+N", [
         ("ok", "도구는 MCP 서버로 1번만 구현"),
         ("ok", "클라이언트는 MCP 지원 1번만"),
         ("ok", "10 + 4 = 14 로 감소"),
         ("dot", "규격 콘센트에 꽂기만"),
     ], "서버가 내놓는 것: Tools(실행) · Resources(읽을 데이터) · Prompts(작업 템플릿)", licon="box", ricon="gateway"))

_add("quantization-size", "양자화별 모델 무게 (14B 기준)",
     "파라미터 개수 × 숫자 하나의 크기. 4bit면 1/4이 되어 16GB 카드에 들어갑니다.",
     "quantization",
     _bars("qz", [("FP16", 28, "28 GB 초과", "box"),
                  ("INT8", 14, "14 GB 아슬", "box"),
                  ("INT4", 7, "7 GB 여유", "box")],
           32, "여기에 KV 캐시·오버헤드가 얹힙니다. 같은 VRAM이면 '큰 모델 4bit'가 대개 이깁니다",
           thr=16, thr_label="16GB 카드 한계"))

_add("finetune-vs-rag", "파인튜닝 vs RAG — 무엇을 넣는가",
     "아는 것(지식)은 RAG, 하는 것(행동)은 파인튜닝. 대부분의 '우리 문서 학습'은 RAG가 답입니다.",
     "finetuning-vs-rag",
     _two("fr", "RAG — 찾아보게 하기", [
         ("ok", "자주 바뀌는 내용 (문서만 교체)"),
         ("ok", "출처·근거 제시 가능"),
         ("ok", "갱신 비용 거의 0"),
         ("no", "말투·형식 일관성은 못 잡음"),
     ], "파인튜닝 — 몸에 배게 하기", [
         ("ok", "말투·페르소나·출력 형식"),
         ("ok", "도메인 방언, 좁은 작업 특화"),
         ("no", "갱신마다 데이터셋+학습 반복"),
         ("no", "지식 주입 수단으로는 신뢰도 낮음"),
     ], "순서 원칙: 프롬프트 엔지니어링 → RAG → 파인튜닝 (싸고 되돌리기 쉬운 것부터)", licon="doc", ricon="brain"))

_add("managed-db-line", "관리형 DB — 책임 경계선",
     "서버 관리는 벤더가, DB 관리는 여전히 우리 몫입니다. 이 선을 모르면 '관리형인데 왜 터지죠'가 됩니다.",
     "managed-db-migration",
     _two("md", "벤더가 해주는 것", [
         ("ok", "설치·패치·하드웨어"),
         ("ok", "자동 백업 실행"),
         ("ok", "장애조치 기능 제공"),
         ("dot", "= 서버 관리"),
     ], "여전히 내 몫", [
         ("no", "파라미터 그룹 (max_connections 등)"),
         ("no", "백업 보존기간 + 복구 리허설"),
         ("no", "다중화 옵션 선택 · 앱의 재연결"),
         ("no", "네트워크 접근 통제 재설계"),
     ], "이관 체크리스트 1번: 기존 SHOW VARIABLES 결과와 새 파라미터 그룹 대조", licon="cloud", ricon="user"))


# ══════════════════════════════════════════════════════════════
#  개별 제작 다이어그램
# ══════════════════════════════════════════════════════════════
_add("unicode-nfc-nfd", "같은 '한', 다른 바이트",
     "화면엔 똑같이 보이지만 저장 방식이 다릅니다. 맥은 자모를 분해(NFD), 윈도우는 합쳐서(NFC) 저장하죠.",
     "onedrive-unicode",
     '<svg viewBox="0 0 640 200" role="img"><style>' + _COMMON + """
.un-p{animation:un-p 3s ease-in-out infinite;}
@keyframes un-p{0%,100%{opacity:.35}50%{opacity:1}}
</style>
""" + _icon("server", 24, 20, 1.05) + """<text x="50" y="24" class="dg-tl">윈도우 · 웹 표준 — NFC (1개)</text>
<rect x="14" y="36" width="290" height="58" rx="10" class="dg-box"/>
<rect x="30" y="48" width="46" height="34" rx="6" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
<text x="42" y="72" class="dg-t">한</text>
<text x="92" y="62" class="dg-ts">코드포인트 1개</text>
<text x="92" y="80" class="dg-ts">len("한") == 1</text>
""" + _icon("laptop", 346, 20, 1.05) + """<text x="372" y="24" class="dg-tl">맥 — NFD (자모 3개)</text>
<rect x="336" y="36" width="290" height="58" rx="10" class="dg-box"/>
<rect x="352" y="48" width="34" height="34" rx="6" fill="none" stroke="var(--muted)" stroke-width="1.3"/>
<text x="362" y="72" class="dg-t">ㅎ</text>
<rect x="392" y="48" width="34" height="34" rx="6" fill="none" stroke="var(--muted)" stroke-width="1.3"/>
<text x="402" y="72" class="dg-t">ㅏ</text>
<rect x="432" y="48" width="34" height="34" rx="6" fill="none" stroke="var(--muted)" stroke-width="1.3"/>
<text x="442" y="72" class="dg-t">ㄴ</text>
<text x="480" y="62" class="dg-ts">코드포인트 3개</text>
<text x="480" y="80" class="dg-ts">len("한") == 3</text>
<rect x="14" y="112" width="612" height="52" rx="10" class="dg-box"/>
<text x="30" y="134" class="dg-t">OneDrive 입장 — 이름이 "다른" 두 파일</text>
<text x="30" y="153" class="dg-ts">제안서.pptx (NFC)  ≠  제안서.pptx (NFD)  → 둘 다 성실하게 보관 → 복제본 발생</text>
<g class="dg-anim un-p"><circle cx="600" cy="138" r="8" class="dg-no"/></g>
<text x="14" y="186" class="dg-ts">해법: 업로드 전 파일명을 NFC로 정규화 (unicodedata.normalize) 또는 영문 파일명 규칙</text>
</svg>""")

_add("cosine-angle", "의미의 닮음은 '각도'로 잰다",
     "벡터의 길이(문장 길이·강도)는 무시하고 방향만 봅니다. 같은 쪽을 가리키면 뜻이 비슷한 거죠.",
     "cosine-similarity",
     '<svg viewBox="0 0 640 240" role="img"><style>' + _COMMON + """
.cs-arc{animation:cs-a 3.2s ease-in-out infinite;}
@keyframes cs-a{0%,100%{opacity:.25}50%{opacity:.9}}
</style>
<line x1="60" y1="200" x2="380" y2="200" class="dg-arrow"/>
<line x1="60" y1="200" x2="60" y2="30" class="dg-arrow"/>
<line x1="60" y1="200" x2="290" y2="70" stroke="var(--accent)" stroke-width="2.4"/>
<circle cx="290" cy="70" r="4" class="dg-ok"/><text x="298" y="66" class="dg-ts">"강아지가 뛴다"</text>
<line x1="60" y1="200" x2="216" y2="76" stroke="var(--accent)" stroke-width="2.4" opacity=".7"/>
<circle cx="216" cy="76" r="4" class="dg-ok"/><text x="150" y="58" class="dg-ts">"반려견이 산책"</text>
<line x1="60" y1="200" x2="330" y2="176" stroke="#E5484D" stroke-width="2.2"/>
<circle cx="330" cy="176" r="4" class="dg-no"/><text x="292" y="196" class="dg-ts">"환율 급등"</text>
<path d="M120 172 A 66 66 0 0 1 128 152" fill="none" stroke="var(--accent)" stroke-width="2" class="dg-anim cs-arc"/>
<text x="132" y="140" class="dg-ts" fill="var(--accent)">작은 각 = 비슷</text>
<path d="M148 196 A 92 92 0 0 0 134 158" fill="none" stroke="#E5484D" stroke-width="2" class="dg-anim cs-arc"/>
<text x="152" y="176" class="dg-ts" fill="#E5484D">큰 각 = 무관</text>
<rect x="410" y="40" width="216" height="150" rx="12" class="dg-box"/>
<text x="428" y="66" class="dg-tl">cos(θ) 값</text>
<text x="428" y="94" class="dg-ts">1 에 가까움 → 같은 방향 (비슷)</text>
<text x="428" y="116" class="dg-ts">0 → 직각 (무관)</text>
<text x="428" y="138" class="dg-ts">-1 → 정반대</text>
<text x="428" y="168" class="dg-ts">길이로 나누는 과정이</text>
<text x="428" y="182" class="dg-ts">곧 '크기 무시'</text>
<text x="14" y="228" class="dg-ts">팁: 정규화된(길이 1) 임베딩이면 내적만 계산해도 코사인과 같아 검색이 더 빠릅니다</text>
</svg>""")

_add("token-split", "토큰은 글자도 단어도 아니다",
     "자주 나오는 덩어리는 큰 블록 하나로, 드문 것은 잘게 쪼개집니다. 한국어가 영어보다 블록을 더 먹는 이유죠.",
     "what-is-token",
     '<svg viewBox="0 0 640 190" role="img"><style>' + _COMMON + """
.tk c{opacity:0;animation:tk-in .5s ease-out forwards;}
@keyframes tk-in{to{opacity:1}}
</style>
<text x="14" y="24" class="dg-tl">영어 — 큰 블록이 풍부</text>
<rect x="14" y="34" width="612" height="46" rx="10" class="dg-box"/>
<text x="28" y="62" class="dg-t">"hello world"</text>
<rect x="180" y="44" width="66" height="26" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.3"/>
<text x="196" y="62" class="dg-ts">hello</text>
<rect x="252" y="44" width="66" height="26" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.3"/>
<text x="266" y="62" class="dg-ts">&#32;world</text>
<text x="340" y="62" class="dg-ts">→ 2 토큰</text>
<text x="14" y="110" class="dg-tl">한국어 — 잘게 쪼개짐</text>
<rect x="14" y="120" width="612" height="46" rx="10" class="dg-box"/>
<text x="28" y="148" class="dg-t">"안녕하세요"</text>
<rect x="180" y="130" width="34" height="26" rx="5" fill="#FCE9EA" stroke="#E5484D" stroke-width="1.2"/><text x="192" y="148" class="dg-ts">안</text>
<rect x="220" y="130" width="34" height="26" rx="5" fill="#FCE9EA" stroke="#E5484D" stroke-width="1.2"/><text x="232" y="148" class="dg-ts">녕</text>
<rect x="260" y="130" width="34" height="26" rx="5" fill="#FCE9EA" stroke="#E5484D" stroke-width="1.2"/><text x="272" y="148" class="dg-ts">하</text>
<rect x="300" y="130" width="34" height="26" rx="5" fill="#FCE9EA" stroke="#E5484D" stroke-width="1.2"/><text x="312" y="148" class="dg-ts">세</text>
<rect x="340" y="130" width="34" height="26" rx="5" fill="#FCE9EA" stroke="#E5484D" stroke-width="1.2"/><text x="352" y="148" class="dg-ts">요</text>
<text x="392" y="148" class="dg-ts">→ 더 많은 토큰 (모델·토크나이저마다 다름)</text>
<text x="14" y="184" class="dg-ts">토큰 개수가 곧 요금 · 컨텍스트 한도 · 생성 속도를 결정합니다</text>
</svg>""")

_add("context-desk", "컨텍스트 윈도우 = 책상 크기",
     "기억력이 아니라 한 번에 펼칠 수 있는 면적입니다. 넘치면 오래된 서류부터 조용히 밀려나고, 가운데는 흐릿해져요.",
     "context-window",
     '<svg viewBox="0 0 640 230" role="img"><style>' + _COMMON + """
.cd-out{animation:cd-out 4s ease-in-out infinite;}
.cd-new{animation:cd-new 4s ease-in-out infinite;}
@keyframes cd-out{0%,40%{transform:translateX(0);opacity:1}75%,100%{transform:translateX(-90px);opacity:0}}
@keyframes cd-new{0%,40%{transform:translateX(90px);opacity:0}75%,100%{transform:translateX(0);opacity:1}}
</style>
<rect x="60" y="40" width="520" height="96" rx="12" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
""" + _icon("doc", 40, 28, 1.3) + """<text x="68" y="32" class="dg-ts" fill="var(--dg-blue)">책상 = 컨텍스트 윈도우 (질문 + 문서 + 대화이력 + 답변 전부 포함)</text>
<g class="dg-anim cd-out"><rect x="76" y="58" width="70" height="60" rx="6" class="dg-box"/>
<text x="86" y="84" class="dg-ts">초반</text><text x="86" y="100" class="dg-ts">대화</text></g>
<rect x="158" y="58" width="70" height="60" rx="6" class="dg-box"/><text x="168" y="92" class="dg-ts">지시문</text>
<rect x="240" y="58" width="70" height="60" rx="6" class="dg-box" opacity=".45"/>
<text x="250" y="84" class="dg-ts" opacity=".7">가운데</text><text x="250" y="100" class="dg-ts" opacity=".7">흐릿</text>
<rect x="322" y="58" width="70" height="60" rx="6" class="dg-box" opacity=".45"/>
<rect x="404" y="58" width="70" height="60" rx="6" class="dg-box"/><text x="414" y="92" class="dg-ts">근거문서</text>
<g class="dg-anim cd-new"><rect x="486" y="58" width="70" height="60" rx="6" fill="var(--raise)" stroke="var(--accent)" stroke-width="1.6"/>
<text x="496" y="84" class="dg-ts">새</text><text x="496" y="100" class="dg-ts">질문</text></g>
<text x="14" y="88" font-size="17" class="dg-no" font-weight="700">✕</text>
<text x="6" y="112" class="dg-ts">밀려남</text>
<text x="14" y="166" class="dg-ts">밀려난 것은 모델에게 '처음부터 없던 것' — 에러 없이 조용히 잘리는 게 진짜 위험</text>
<text x="14" y="188" class="dg-ts">양 끝(맨 앞·맨 뒤)은 잘 쓰고 한가운데는 놓치는 경향 → 중요한 지시는 앞이나 뒤에</text>
<text x="14" y="210" class="dg-ts">대처: 토큰 세기 · 긴 대화는 요약으로 접기 · 문서는 골라서 올리기(RAG)</text>
</svg>""")

_add("temperature-dial", "temperature가 실제로 돌리는 것",
     "확률 분포의 뾰족함을 조절합니다. 낮으면 1등 독식, 높으면 하위 후보도 뽑히죠. top-p는 후보를 잘라냅니다.",
     "temperature-top-p",
     '<svg viewBox="0 0 640 220" role="img"><style>' + _COMMON + """
.tp-b{animation:tp-g 2.8s ease-out infinite;transform-origin:center bottom;}
@keyframes tp-g{0%{transform:scaleY(.2)}40%,100%{transform:scaleY(1)}}
</style>
<text x="14" y="22" class="dg-tl">temperature 낮음 — 뾰족 (1등 독식)</text>
<rect x="14" y="32" width="300" height="130" rx="10" class="dg-box"/>
<g class="dg-anim tp-b">
<rect x="40" y="52" width="42" height="92" rx="4" fill="var(--accent)" opacity=".85"/>
<rect x="98" y="132" width="42" height="12" rx="3" fill="var(--accent)" opacity=".5"/>
<rect x="156" y="137" width="42" height="7" rx="3" fill="var(--accent)" opacity=".4"/>
<rect x="214" y="140" width="42" height="4" rx="2" fill="var(--accent)" opacity=".3"/>
</g>
<line x1="30" y1="144" x2="300" y2="144" class="dg-arrow"/>
<text x="40" y="158" class="dg-ts">서울 92%</text><text x="150" y="158" class="dg-ts">그 외 후보들</text>
<text x="326" y="22" class="dg-tl">temperature 높음 — 평평 (다양성↑)</text>
<rect x="326" y="32" width="300" height="130" rx="10" class="dg-box"/>
<g class="dg-anim tp-b">
<rect x="352" y="84" width="42" height="60" rx="4" fill="var(--accent)" opacity=".85"/>
<rect x="410" y="98" width="42" height="46" rx="4" fill="var(--accent)" opacity=".7"/>
<rect x="468" y="108" width="42" height="36" rx="4" fill="var(--accent)" opacity=".6"/>
<rect x="526" y="116" width="42" height="28" rx="4" fill="var(--accent)" opacity=".5"/>
</g>
<line x1="342" y1="144" x2="612" y2="144" class="dg-arrow"/>
<line x1="462" y1="40" x2="462" y2="152" class="dg-wall"/>
<text x="468" y="52" class="dg-ts" fill="var(--accent)">top-p 컷</text>
<text x="352" y="158" class="dg-ts">누적 확률 p 까지만 뽑기통에</text>
<text x="14" y="186" class="dg-ts">정답이 정해진 일(코드·추출·분류) 낮게 · 발상이 필요한 일 높게 — 다이얼은 한 번에 하나만</text>
<text x="14" y="208" class="dg-ts">상한은 제공자별로 다름 (Anthropic 0~1, OpenAI 0~2) · 높여도 '똑똑해지는' 건 아님</text>
</svg>""")

_add("docker-cache-order", "Dockerfile 순서가 캐시를 살린다",
     "빌드는 바뀐 층부터 위로 다시 만듭니다. 안 바뀌는 의존성을 아래, 자주 바뀌는 코드를 위에 두세요.",
     "docker-layer-cache",
     '<svg viewBox="0 0 640 250" role="img"><style>' + _COMMON + """
.dc-x{animation:dc-p 3s ease-in-out infinite;}
@keyframes dc-p{0%,100%{opacity:.4}50%{opacity:1}}
</style>
""" + _icon("box", 24, 18, 1.05) + """<text x="50" y="22" class="dg-tl">나쁜 순서 — 코드 고치면 전부 재빌드</text>
<rect x="14" y="32" width="300" height="150" rx="10" class="dg-box"/>
<rect x="34" y="130" width="260" height="30" rx="5" fill="var(--line-2)" stroke="var(--line)"/><text x="46" y="150" class="dg-ts">FROM python:3.12  (캐시 유지)</text>
<rect x="34" y="94" width="260" height="30" rx="5" fill="#FCE9EA" stroke="#E5484D"/><text x="46" y="114" class="dg-ts">COPY . .  ← 코드 변경으로 무효화</text>
<rect x="34" y="58" width="260" height="30" rx="5" fill="#FCE9EA" stroke="#E5484D"/><text x="46" y="78" class="dg-ts">RUN pip install  ← 같이 무효화 (느림)</text>
<g class="dg-anim dc-x"><text x="298" y="80" font-size="15" class="dg-no" font-weight="700">✕</text></g>
""" + _icon("box", 336, 18, 1.05) + """<text x="362" y="22" class="dg-tl">좋은 순서 — 의존성 층이 캐시</text>
<rect x="326" y="32" width="300" height="150" rx="10" class="dg-box"/>
<rect x="346" y="148" width="260" height="26" rx="5" fill="var(--line-2)" stroke="var(--line)"/><text x="358" y="165" class="dg-ts">FROM python:3.12</text>
<rect x="346" y="116" width="260" height="26" rx="5" fill="var(--accent-soft)" stroke="var(--accent)"/><text x="358" y="133" class="dg-ts">COPY requirements.txt .   CACHED</text>
<rect x="346" y="84" width="260" height="26" rx="5" fill="var(--accent-soft)" stroke="var(--accent)"/><text x="358" y="101" class="dg-ts">RUN pip install           CACHED ✓</text>
<rect x="346" y="52" width="260" height="26" rx="5" fill="#FFF4E6" stroke="#E8842C"/><text x="358" y="69" class="dg-ts">COPY . .  ← 이 층만 다시</text>
<text x="14" y="206" class="dg-ts">이미지는 겹겹의 투명 필름 — 바뀐 필름과 '그 위의 모든 필름'만 다시 그립니다</text>
<text x="14" y="228" class="dg-ts">확인: 빌드 로그의 CACHED 표시 · docker history 로 층별 크기 점검</text>
</svg>""")

_add("scalein-deadzone", "오토스케일링의 사각지대",
     "확장 70%, 축소 30%로 잡으면 그 사이는 아무 일도 안 일어납니다. 한번 늘어난 서버가 눌러앉는 이유죠.",
     "autoscaling-scalein",
     '<svg viewBox="0 0 640 190" role="img"><style>' + _COMMON + """
.sd-n{animation:sd-n 3.4s ease-in-out infinite;}
@keyframes sd-n{0%,100%{transform:translateX(0)}50%{transform:translateX(120px)}}
</style>
<rect x="60" y="52" width="520" height="34" rx="8" fill="var(--line-2)"/>
<rect x="216" y="52" width="208" height="34" fill="#FFF4E6"/>
<line x1="216" y1="42" x2="216" y2="96" class="dg-wall"/>
<line x1="424" y1="42" x2="424" y2="96" class="dg-wall"/>
""" + _icon("server", 28, 66, 1.05) + """<text x="68" y="42" class="dg-ts">평균 CPU 0%</text>
<text x="540" y="42" class="dg-ts">100%</text>
<text x="180" y="112" class="dg-ts" fill="var(--accent)">축소 30%</text>
<text x="392" y="112" class="dg-ts" fill="var(--accent)">확장 70%</text>
<text x="256" y="74" class="dg-t">사각지대 — 아무 일도 안 일어남</text>
<g class="dg-anim sd-n"><circle cx="250" cy="69" r="7" fill="#E8842C"/></g>
<text x="14" y="146" class="dg-ts">10대로 늘어난 뒤 트래픽이 절반 되어도 대당 CPU 35% → 축소 임계값(30%)에 안 닿음 → 그대로 유지</text>
<text x="14" y="168" class="dg-ts">해법: 사각지대 좁히기 · '평균 50% 유지' 타겟 트래킹으로 전환 · 축소 정책 존재 여부부터 확인</text>
</svg>""")

_add("cutoff-timeline", "지식 컷오프 — 동결된 시점",
     "학습 데이터를 모은 날 이후의 세상은 모델에게 없습니다. 문제는 모른다고 안 하고 아는 척한다는 것.",
     "knowledge-cutoff",
     '<svg viewBox="0 0 640 180" role="img"><style>' + _COMMON + """
.ct-q{animation:ct-q 2.6s ease-in-out infinite;}
@keyframes ct-q{0%,100%{opacity:.4}50%{opacity:1}}
</style>
<line x1="20" y1="76" x2="330" y2="76" stroke="var(--accent)" stroke-width="7" stroke-linecap="round"/>
<line x1="336" y1="76" x2="620" y2="76" stroke="var(--faint)" stroke-width="7" stroke-dasharray="7 7" stroke-linecap="round"/>
<line x1="333" y1="46" x2="333" y2="106" class="dg-wall"/>
<text x="290" y="38" class="dg-ts" fill="var(--accent)">컷오프</text>
""" + _icon("brain", 30, 108, 1.3) + """<text x="58" y="112" class="dg-t">학습된 세상 — 잘 안다</text>
<text x="400" y="112" class="dg-t">모르는 구간</text>
<rect x="216" y="56" width="112" height="40" rx="6" fill="var(--accent-soft)" opacity=".55"/>
<text x="222" y="80" class="dg-ts">직전 몇 달: 어설프게 아는 회색지대</text>
<g class="dg-anim ct-q"><text x="470" y="82" font-size="22" class="dg-no" font-weight="700">?</text></g>
<text x="400" y="132" class="dg-ts">버전 · 가격 · 현직 · 일정</text>
<text x="14" y="162" class="dg-ts">"현재·최신·요즘"이 들어간 질문은 위험군 → 검색·RAG·문서 첨부로 현재를 주입하고 교차 확인</text>
</svg>""")

_add("envelope-keys", "봉투암호화 — DEK와 KEK",
     "데이터는 일회용 열쇠로 잠그고, 그 열쇠를 마스터키로 봉인해 데이터 옆에 붙여둡니다. 마스터키는 금고 밖으로 안 나가죠.",
     "envelope-encryption",
     '<svg viewBox="0 0 640 230" role="img"><style>' + _COMMON + """
.ev-k{animation:ev-k 3.6s ease-in-out infinite;}
@keyframes ev-k{0%,100%{opacity:.35}50%{opacity:1}}
</style>
<rect x="392" y="24" width="234" height="182" rx="12" fill="none" stroke="var(--accent)" stroke-width="1.6" stroke-dasharray="6 4"/>
<text x="404" y="44" class="dg-ts" fill="var(--accent)">KMS — 마스터키는 밖으로 안 나감</text>
<rect x="424" y="60" width="170" height="52" rx="10" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
""" + _icon("shield", 452, 84, 0.95) + """<text x="474" y="88" class="dg-t">마스터키 (KEK)</text>
<text x="442" y="100" class="dg-ts">봉투를 봉인·개봉만</text>
<rect x="14" y="40" width="180" height="70" rx="10" class="dg-box"/>
""" + _icon("doc", 40, 66, 1.3) + """<text x="68" y="70" class="dg-t">데이터 (1GB)</text>
<text x="30" y="86" class="dg-ts">DEK로 로컬에서 암호화</text>
<text x="30" y="102" class="dg-ts">→ 빠름, 네트워크 불필요</text>
<rect x="14" y="126" width="180" height="62" rx="10" fill="var(--raise)" stroke="var(--accent)" stroke-width="1.5"/>
""" + _icon("lock", 40, 150, 1.3) + """<text x="68" y="154" class="dg-t">봉인된 봉투</text>
<text x="30" y="170" class="dg-ts">암호화된 DEK — 데이터와 함께 보관</text>
<path d="M194 158 H 392 V 96" class="dg-arrow"/>
<g class="dg-anim ev-k"><circle cx="300" cy="158" r="7" class="dg-ok"/></g>
<text x="214" y="148" class="dg-ts">봉투만 왕복 (수십 바이트)</text>
<text x="214" y="182" class="dg-ts">평문 DEK는 즉시 파기</text>
<text x="14" y="216" class="dg-ts">이점: 큰 데이터도 빠르게 · 키 회전은 봉투만 재봉인 · 모든 복호화가 KMS를 거쳐 감사 로그 남음</text>
</svg>""")

_add("docker-localhost-3", "컨테이너의 주소 체계 3가지",
     "컨테이너 안의 localhost는 자기 자신입니다. 목적지마다 불러야 하는 주소가 다릅니다.",
     "docker-localhost",
     '<svg viewBox="0 0 640 200" role="img"><style>' + _COMMON + """
.dl-x{animation:dl-p 2.8s ease-in-out infinite;}
@keyframes dl-p{0%,100%{opacity:.45}50%{opacity:1}}
</style>
<rect x="14" y="16" width="612" height="46" rx="10" class="dg-box"/>
""" + _icon("box", 34, 32, 1.05) + """<text x="60" y="38" class="dg-t">① 컨테이너 &#8594; 호스트</text>
<g class="dg-anim dl-x"><text x="300" y="38" class="dg-ts" fill="#E5484D">✕ localhost</text></g>
<text x="404" y="38" class="dg-ts" fill="var(--accent)">✓ host.docker.internal</text>
<text x="28" y="55" class="dg-ts">Linux는 --add-host=host.docker.internal:host-gateway 필요 · 호스트는 0.0.0.0 바인딩</text>
<rect x="14" y="72" width="612" height="46" rx="10" class="dg-box"/>
""" + _icon("box", 34, 88, 1.05) + """<text x="60" y="94" class="dg-t">② 컨테이너 &#8594; 옆 컨테이너</text>
<g class="dg-anim dl-x"><text x="300" y="94" class="dg-ts" fill="#E5484D">✕ localhost</text></g>
<text x="404" y="94" class="dg-ts" fill="var(--accent)">✓ 컨테이너 이름 (예: db)</text>
<text x="28" y="111" class="dg-ts">같은 사용자 정의 네트워크에 있어야 이름 해석됨 (compose는 자동)</text>
<rect x="14" y="128" width="612" height="46" rx="10" class="dg-box"/>
""" + _icon("laptop", 34, 144, 1.05) + """<text x="60" y="150" class="dg-t">③ 호스트 &#8594; 컨테이너</text>
<text x="404" y="150" class="dg-ts" fill="var(--accent)">✓ -p 8080:80 로 포트 공개</text>
<text x="28" y="167" class="dg-ts">-p 없으면 호스트에서 접근 불가가 정상 (담장 안)</text>
<text x="14" y="194" class="dg-ts">예외: --network host 는 컨테이너가 호스트 네트워크를 그대로 사용 (격리 상실, Linux 전용)</text>
</svg>""")

_add("inode-gauge", "용량은 남았는데 'No space left'",
     "디스크에는 용량과 inode(파일 개수 한도), 두 개의 한계가 있습니다. df -h가 아니라 df -i를 봐야 잡히죠.",
     "inode-exhaustion",
     '<svg viewBox="0 0 640 170" role="img"><style>' + _COMMON + """
.ig-b{animation:ig-g 2.6s ease-out infinite;transform-origin:left center;}
@keyframes ig-g{0%{transform:scaleX(0)}45%,100%{transform:scaleX(1)}}
</style>
""" + _icon("database", 26, 22, 1.3) + """<text x="52" y="26" class="dg-t">df -h (용량)</text>
<rect x="160" y="12" width="420" height="22" rx="5" fill="var(--line-2)"/>
<g class="dg-anim ig-b"><rect x="160" y="12" width="126" height="22" rx="5" fill="var(--accent)" opacity=".85"/></g>
<text x="590" y="28" class="dg-ts">30%</text>
""" + _icon("doc", 26, 72, 1.3) + """<text x="52" y="76" class="dg-t">df -i (inode)</text>
<rect x="160" y="62" width="420" height="22" rx="5" fill="var(--line-2)"/>
<g class="dg-anim ig-b" style="animation-delay:.2s"><rect x="160" y="62" width="420" height="22" rx="5" fill="#E5484D" opacity=".85"/></g>
<text x="590" y="78" class="dg-ts" fill="#E5484D">100%</text>
<text x="160" y="106" class="dg-ts">주차장 비유: 바닥 면적(용량)은 남았는데 발급할 주차권(inode)이 동난 상태</text>
<text x="14" y="132" class="dg-ts">파일 1개 = inode 1개 (크기 무관) → 0바이트 파일 수백만 개도 고갈을 일으킵니다</text>
<text x="14" y="154" class="dg-ts">범인 찾기: for d in /var/*; do echo -n "$d: "; find "$d" -xdev -type f | wc -l; done</text>
</svg>""")

_add("ann-search", "전수조사 vs ANN (고속도로망)",
     "모든 문서와 거리를 재는 대신, 미리 깔아둔 링크를 타고 몇 번의 점프로 목적지 근처에 도착합니다.",
     "vector-db-ann",
     '<svg viewBox="0 0 640 210" role="img"><style>' + _COMMON + """
.an-s circle{animation:an-b 2.4s ease-in-out infinite;}
@keyframes an-b{0%,100%{opacity:.25}50%{opacity:.8}}
.an-p{stroke-dasharray:200;animation:an-p 3s ease-in-out infinite;}
@keyframes an-p{0%{stroke-dashoffset:200}55%,100%{stroke-dashoffset:0}}
</style>
<text x="14" y="22" class="dg-tl">전수조사 — 1천만 번 계산</text>
<rect x="14" y="32" width="300" height="130" rx="10" class="dg-box"/>
<g class="an-s">""" + "".join(
    f'<circle cx="{40 + (i % 10) * 27}" cy="{56 + (i // 10) * 24}" r="5" fill="var(--muted)" style="animation-delay:{i * 0.02:.2f}s"/>'
    for i in range(40)) + """</g>
<text x="40" y="152" class="dg-ts">전부 다 재본다 → 정확하지만 실시간 불가</text>
""" + _icon("database", 336, 18, 1.3) + """<text x="362" y="22" class="dg-tl">HNSW — 점프로 몇십 번</text>
<rect x="326" y="32" width="300" height="130" rx="10" class="dg-box"/>
<g opacity=".3">""" + "".join(
    f'<circle cx="{352 + (i % 10) * 27}" cy="{56 + (i // 10) * 24}" r="5" fill="var(--muted)"/>'
    for i in range(40)) + """</g>
<path d="M356 60 L 500 84 L 572 108 L 545 128 L 520 130" fill="none" stroke="var(--accent)"
      stroke-width="2.4" class="dg-anim an-p"/>
<circle cx="356" cy="60" r="6" class="dg-ok"/><circle cx="520" cy="130" r="6" class="dg-ok"/>
<text x="352" y="152" class="dg-ts">위층 장거리 링크 → 아래층 세밀 탐색</text>
<text x="14" y="186" class="dg-ts">정확도 1~2%를 내주고 속도 수백 배를 사는 거래 — 뒤에 리랭커가 있으니 후보군이 살짝 달라도 무해</text>
<text x="14" y="204" class="dg-ts">"분명 있는 문서가 안 나올 때"는 탐색 폭(ef 등) 다이얼부터 올려보세요</text>
</svg>""")

_add("volume-vs-bind", "볼륨 vs 바인드 마운트",
     "컨테이너는 언제든 버려질 수 있는 호텔 방입니다. 살아남을 데이터는 방 밖(볼륨)에 둬야 합니다.",
     "docker-volumes",
     _two("vb", "볼륨 — 운영 데이터", [
         ("ok", "-v pgdata:/var/lib/postgresql/data"),
         ("ok", "도커가 관리, 컨테이너보다 오래 산다"),
         ("ok", "DB·업로드 파일에 사용"),
         ("no", "compose down -v 는 볼륨까지 삭제!"),
     ], "바인드 마운트 — 개발 편의", [
         ("ok", "-v /home/me/src:/app/src (경로로 시작)"),
         ("ok", "에디터 수정이 즉시 반영"),
         ("no", "호스트 경로에 종속 · UID 권한 문제"),
         ("no", "운영 데이터 보관용으로는 부적합"),
     ], "점검: docker inspect 컨테이너 --format '{{json .Mounts}}' — 비어 있으면 데이터가 사라질 위험", licon="database", ricon="doc"))

_add("keyscope", "마스터키 vs 카드키 — 토큰 범위",
     "유출은 언제든 일어납니다. 그때 피해 크기를 정하는 건 토큰에 부여한 범위예요.",
     "least-privilege-tokens",
     _two("ks", "넓은 토큰 (마스터키)", [
         ("no", "계정 전체 저장소 접근"),
         ("no", "읽기+쓰기+삭제+설정 변경"),
         ("no", "만료 없음 / 무기한"),
         ("no", "유출 시 = 계정 전체 사고"),
     ], "fine-grained (카드키)", [
         ("ok", "그 저장소 하나만 선택"),
         ("ok", "Contents: Read and write 만"),
         ("ok", "만료 7일 등 짧게"),
         ("ok", "유출 시 = 그 저장소만, 곧 만료"),
     ], "노출되면 고민 말고 즉시 폐기(revoke) 후 재발급 · CI에서는 값이 아니라 Secret 이름만 참조", licon="lock", ricon="shield"))


# ── 2차 배치 ──────────────────────────────────────────────────
_add("cron-utc-axis", "cron 5칸과 UTC 시차",
     "표현식은 맞는데 시각이 어긋나면, 대개 그 시스템이 UTC로 해석하기 때문입니다.",
     "cron-utc",
     '<svg viewBox="0 0 640 190" role="img"><style>' + _COMMON + """
.cu-m{animation:cu-m 3s ease-in-out infinite;}
@keyframes cu-m{0%,100%{opacity:.4}50%{opacity:1}}
</style>
<rect x="14" y="14" width="612" height="52" rx="10" class="dg-box"/>
<text x="30" y="36" class="dg-t">*  *  *  *  *</text>
<text x="140" y="36" class="dg-ts">분(0-59) · 시(0-23) · 일(1-31) · 월(1-12) · 요일(0-6, 0=일)</text>
<text x="30" y="56" class="dg-ts">0 18 * * *  → 매일 18:00 · */15 * * * * → 15분마다 · 0 9 * * 1 → 월요일 09:00</text>
<line x1="40" y1="112" x2="600" y2="112" class="dg-arrow"/>
<line x1="200" y1="98" x2="200" y2="126" stroke="var(--accent)" stroke-width="2.4"/>
<text x="168" y="92" class="dg-ts" fill="var(--accent)">UTC 18:00</text>
<line x1="440" y1="98" x2="440" y2="126" stroke="#E8842C" stroke-width="2.4"/>
<text x="404" y="92" class="dg-ts" fill="#E8842C">KST 03:00</text>
<path d="M200 132 H 440" stroke="var(--faint)" stroke-width="1.4" stroke-dasharray="4 4" fill="none"/>
<g class="dg-anim cu-m"><text x="286" y="148" class="dg-ts">+9 시간</text></g>
<text x="14" y="172" class="dg-ts">한국 새벽 3시에 돌리려면 3 − 9 = −6 → 전날 18:00 UTC 로 적어야 합니다 (0 18 * * *)</text>
</svg>""")

_add("chunk-overlap", "청크 크기와 오버랩",
     "너무 크면 잡음이 섞이고, 너무 작으면 문맥이 끊깁니다. 겹치는 구간이 경계에 걸린 문장을 구해주죠.",
     "chunking",
     '<svg viewBox="0 0 640 220" role="img"><style>' + _COMMON + """
.co-h{animation:co-h 3s ease-in-out infinite;}
@keyframes co-h{0%,100%{opacity:.35}50%{opacity:.85}}
</style>
<text x="14" y="22" class="dg-t">너무 크게 — 한 조각에 여러 주제(잡음)</text>
<rect x="300" y="8" width="326" height="20" rx="4" fill="var(--line-2)" stroke="var(--line)"/>
<text x="312" y="23" class="dg-ts">환불 + 배송 + 교환 + 회원가입 …</text>
<text x="14" y="60" class="dg-t">너무 작게 — 문맥 끊김</text>
<rect x="300" y="46" width="60" height="20" rx="4" fill="var(--line-2)" stroke="var(--line)"/><text x="308" y="61" class="dg-ts">단, 예외</text>
<rect x="366" y="46" width="60" height="20" rx="4" fill="var(--line-2)" stroke="var(--line)"/>
<rect x="432" y="46" width="60" height="20" rx="4" fill="var(--line-2)" stroke="var(--line)"/>
<text x="500" y="61" class="dg-ts">뭐의 예외인지 모름</text>
""" + _icon("doc", 26, 96, 1.3) + """<text x="54" y="100" class="dg-t">적당히 + 오버랩</text>
<rect x="300" y="86" width="150" height="22" rx="4" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.4"/>
<rect x="410" y="112" width="150" height="22" rx="4" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.4"/>
<rect x="410" y="86" width="40" height="48" rx="3" fill="var(--accent)" opacity=".22" class="dg-anim co-h"/>
<text x="392" y="152" class="dg-ts" fill="var(--accent)">겹침 10~20%</text>
<text x="306" y="101" class="dg-ts">청크 1</text><text x="470" y="127" class="dg-ts">청크 2</text>
<text x="14" y="182" class="dg-ts">기준: "한 조각 = 하나의 완결된 생각" · 300~800토큰에서 시작해 평가로 조정</text>
<text x="14" y="204" class="dg-ts">글자 수로 뚝 자르지 말고 문단 → 문장 경계를 존중 · 청크에 출처 메타데이터를 붙이기</text>
</svg>""")

_add("syn-patterns", "tcpdump로 읽는 SYN 3패턴",
     "서버에서 캡처를 켜고 접속을 시도하면, 세 가지 중 하나가 보입니다. 그게 곧 책임 구간입니다.",
     "tcpdump-basics",
     _ladder("sp", [
         ("① 아무것도 안 보임", "(정적)", "앞단 방화벽·라우팅", "firewall"),
         ("② SYN → RST", "Flags [S] → [R.]", "포트에 앱 없음", "server"),
         ("③ SYN 반복", "재전송 × 3회", "응답 경로 차단", "router"),
     ], "sudo tcpdump -ni any port 8080 -c 30  ← 내가 curl로 재현하며 그 파문만 관찰하는 게 요령"))

_add("load-per-core", "load average는 코어 수로 나눠 읽는다",
     "같은 4.2라도 서버에 따라 의미가 정반대입니다. load ÷ 코어 ≈ 1.0이 만석 기준선이에요.",
     "load-average",
     _bars("lc", [("2코어 load 4.2", 2.1, "2.1배 과부하", "server"),
                  ("4코어 load 4.2", 1.05, "1.05배 만석", "server"),
                  ("16코어 load 4.2", 0.26, "0.26배 한산", "server")],
           2.4, "숫자 3개는 1분/5분/15분 평균 — 1분<15분이면 가라앉는 중, 1분>15분이면 차오르는 중",
           thr=1.0, thr_label="기준선 1.0"))

_add("l7-vs-l4", "ALB(L7) vs NLB(L4)",
     "편지를 뜯어 내용을 읽으면 ALB, 겉면만 보고 던지면 NLB. 여기서 기능·성능·클라이언트IP가 갈립니다.",
     "alb-vs-nlb",
     _two("ln", "ALB — 뜯어 읽는다 (L7)", [
         ("ok", "경로/호스트/헤더 라우팅"),
         ("ok", "TLS 종료 · 리다이렉트 · HTTP 헬스체크"),
         ("no", "HTTP(S)만 · 상대적으로 느림"),
         ("no", "클라이언트 IP가 ALB로 바뀜 → X-Forwarded-For 복원 필요"),
     ], "NLB — 겉면만 본다 (L4)", [
         ("ok", "TCP/UDP 뭐든 (DB·MQTT·게임)"),
         ("ok", "초고성능 저지연 · 고정 IP(EIP) 부착"),
         ("ok", "클라이언트 IP 보존"),
         ("no", "그래서 방화벽을 클라이언트 IP 기준으로 열어야 함"),
     ], "둘 다 필요하면 NLB(고정IP) → ALB(L7 라우팅) → 서버 체인 구성이 흔합니다", licon="doc", ricon="switch"))

_add("route-table-diff", "public / private을 정하는 한 줄",
     "서브넷에 붙은 딱지가 아니라 라우팅 테이블의 기본 경로가 정체를 결정합니다.",
     "public-private-subnet",
     _two("rt", "public 서브넷", [
         ("dot", "10.0.0.0/16 → local"),
         ("ok", "0.0.0.0/0 → igw (인터넷 게이트웨이)"),
         ("dot", "= 양방향 문"),
         ("dot", "LB · 배스천 · NAT GW 가 사는 곳"),
     ], "private 서브넷", [
         ("dot", "10.0.0.0/16 → local"),
         ("no", "0.0.0.0/0 → 없음 (인터넷 직통 불가)"),
         ("ok", "0.0.0.0/0 → nat (나가기 전용 문)"),
         ("dot", "WAS · DB 가 사는 곳"),
     ], "공인 IP를 붙여도 IGW 경로가 없으면 통신 불가 — IP보다 경로가 먼저입니다", licon="globe", ricon="gateway"))

_add("secret-spread", "코드에 박은 비밀은 복제된다",
     "한 번 커밋되면 히스토리·노트북·백업으로 퍼지고 교체가 불가능해집니다. 금고에 두고 실행 시점에 꺼내 쓰세요.",
     "secret-manager",
     _two("ss", "코드에 박기", [
         ("no", "git push → 클론한 모든 노트북에 사본"),
         ("no", "지워도 히스토리에 영원히 남음"),
         ("no", "교체하려면 전 서비스 재배포 → 미룸"),
         ("no", ".env도 결국 평문 파일 (장소만 이동)"),
     ], "Secret Manager", [
         ("ok", "값은 금고에만, 코드엔 '이름'만"),
         ("ok", "누가 언제 꺼냈는지 감사 로그"),
         ("ok", "교체는 금고 값만 갱신 (재배포 불필요)"),
         ("ok", "IAM으로 접근 권한 즉시 회수"),
     ], "이미 커밋했다면 히스토리 청소보다 '즉시 교체'가 1순위 · gitleaks로 재발 차단", licon="doc", ricon="lock"))

_add("backoff-growth", "CrashLoopBackOff의 재시도 간격",
     "죽을 때마다 대기 시간이 늘어납니다. 상태명은 '재시도 중'이라는 뜻일 뿐, 원인은 따로 찾아야 하죠.",
     "crashloopbackoff",
     '<svg viewBox="0 0 640 180" role="img"><style>' + _COMMON + """
.bg-b{animation:bg-g 2.8s ease-out infinite;transform-origin:left center;}
@keyframes bg-g{0%{transform:scaleX(0)}50%,100%{transform:scaleX(1)}}
</style>""" + "".join(
    f'<text x="14" y="{30+i*26}" class="dg-ts">재시도 {i+1}</text>'
    f'<g class="dg-anim bg-b" style="animation-delay:{i*.16:.2f}s">'
    f'<rect x="86" y="{18+i*26}" width="{min(24*2**i,470)}" height="16" rx="4" fill="var(--accent)" opacity=".8"/></g>'
    f'<text x="{min(24*2**i,470)+94}" y="{31+i*26}" class="dg-ts">{10*2**i}s 대기</text>'
    for i in range(5)) + """
<text x="14" y="164" class="dg-ts">순서: logs --previous (유언) → describe (Exit Code·Events) → 톱4 (설정 · OOM 137 · 프로브 · 의존성)</text>
</svg>""")

_add("oom-selection", "OOM Killer의 피해자 선정",
     "메모리가 바닥나면 커널이 oom_score 최고점을 즉살합니다. 로그가 없는 게 오히려 단서예요.",
     "oom-killer",
     _flow("oo", [("메모리 고갈", "지급 불능", "server"),
                  ("oom_score", "많이 쓰면 고점", "box"),
                  ("최고점 즉살", "SIGKILL", "firewall"),
                  ("dmesg 기록", "Killed process", "doc")],
           "확인: dmesg -T | grep -i 'out of memory' · 보호는 OOMScoreAdjust (단, 폭탄 돌리기)"))

_add("cache-bust", "CDN 캐시 — 회수보다 새 이름",
     "무효화는 응급처치고, 근본은 해시 파일명입니다. HTML만 짧게, 해시 붙은 자원은 1년으로.",
     "cdn-cache",
     _two("cb", "무효화 (응급처치)", [
         ("dot", "전 지점에 '그 물건 회수' 공문"),
         ("no", "전파에 시간 · 횟수 제한/비용"),
         ("no", "매 배포마다 /* 는 임시방편"),
     ], "해시 파일명 (근본)", [
         ("ok", "app.3f9c2a.js — 내용 바뀌면 이름도 바뀜"),
         ("ok", "정적 자원 max-age=31536000, immutable"),
         ("ok", "index.html 만 no-cache → 무효화 거의 불필요"),
     ], "안 바뀌는 미스터리는 캐시 키 확인 (쿼리스트링 포함 여부) · 검증은 시크릿 창으로", licon="cloud", ricon="doc"))

_add("cost-leaks", "클라우드 비용이 새는 다섯 군데",
     "범인은 화려한 서비스가 아니라 잊혀진 것들입니다. 월 1회 30분 점검이면 고지서가 달라져요.",
     "cloud-cost-leaks",
     _ladder("cl", [
         ("고아 자원", "미사용 IP · 볼륨", "서버 삭제 시 세트로", "database"),
         ("무한 스냅샷", "백업 개수 세보기", "보존 정책 필수", "doc"),
         ("밤샘 개발서버", "24h 가동 여부", "정지/시작 스케줄", "server"),
         ("안 줄는 스케일링", "스케일링 이력", "축소 정책·사각지대", "box"),
         ("보이지 않는 전송량", "CDN 없는 오리진", "엔드포인트로 우회", "cloud"),
     ], "습관: 태그 규칙(owner/project/expire) · 예산 알람 50·80·100% · 월 1회 정기 점검"))

_add("closed-open-book", "클로즈드북 → 오픈북 (RAG)",
     "모델을 더 똑똑하게 만드는 게 아니라, 답하기 직전에 정답 페이지를 쥐여주는 겁니다.",
     "what-is-rag",
     _two("ob", "그냥 LLM — 클로즈드북", [
         ("no", "학습 때 외운 것만 답한다"),
         ("no", "사내 문서·최신 정보를 모른다"),
         ("no", "모르면 그럴듯하게 지어낸다"),
         ("no", "출처를 댈 수 없다"),
     ], "RAG — 오픈북", [
         ("ok", "질문과 관련된 조각을 찾아 프롬프트에 넣음"),
         ("ok", "문서만 갱신하면 지식도 갱신"),
         ("ok", "'근거에 없으면 모른다'로 통제 가능"),
         ("ok", "근거 문서로 검증·인용 가능"),
     ], "4단계: 자르기(chunk) → 임베딩 → 검색(top-k) → 근거와 함께 질문", licon="brain", ricon="doc"))

_add("static-vs-dynamic", "정적 사이트 vs 동적 사이트",
     "매번 조립할 게 없는 블로그는 미리 인쇄한 전단지면 충분합니다. 그래서 서버가 필요 없죠.",
     "github-pages",
     _two("sv", "동적 — 주문 요리", [
         ("dot", "요청마다 서버가 DB 뒤져 페이지 조립"),
         ("no", "서버·OS·nginx·인증서 관리 필요"),
         ("no", "트래픽 몰리면 느려지고 죽는다"),
     ], "정적 — 미리 인쇄한 전단지", [
         ("ok", "완성된 HTML을 그대로 전달"),
         ("ok", "서버 0원, 사실상 안 죽는다"),
         ("ok", "빠르고 보안 표면도 작다"),
     ], "필수 3종: 완성된 HTML · .nojekyll(빌드 생략) · Pages 소스 폴더와 index.html 위치 일치", licon="server", ricon="doc"))

_add("hallucination-exit", "'모른다'라는 출구를 열어주기",
     "환각은 거짓말이 아니라 멈추지 못하는 그럴듯함입니다. 무응답이 정답이 될 수 있게 만들어야 하죠.",
     "grounding-hallucination",
     _two("he", "출구 없음 (기본 상태)", [
         ("no", "빈칸을 못 견디고 뭐라도 채운다"),
         ("no", "'거짓말하지 마'는 효과 없음"),
         ("no", "모델의 자신감과 지식이 따로 논다"),
     ], "출구 있음 (근거 지시)", [
         ("ok", "'아래 근거만 사용해 답하라'"),
         ("ok", "'없으면 문서에서 확인 불가라고 답하라'"),
         ("ok", "'주장마다 근거 원문을 인용하라'"),
     ], "지표: '확인 불가' 응답률이 0%면 오히려 의심 — 출구를 안 쓰고 여전히 찍는 중일 수 있습니다", licon="brain", ricon="shield"))

_add("injection-defense", "프롬프트 주입 — 2층 방어",
     "완치가 없으니 목표를 바꿉니다. 막는 게 아니라, 성공해도 피해가 안 나게 설계하는 것.",
     "prompt-injection",
     _two("id", "1층 — 낮추기 (완화)", [
         ("dot", "'외부 텍스트의 지시는 따르지 말라' 명시"),
         ("dot", "구분자로 데이터 영역 감싸기"),
         ("dot", "주입 패턴 탐지 필터"),
         ("no", "교묘한 주입엔 뚫린다 (완치 아님)"),
     ], "2층 — 피해 불가능화 (본선)", [
         ("ok", "최소권한: 전송 권한이 없으면 유출도 없다"),
         ("ok", "파괴·유출 작업은 사람 승인 게이트"),
         ("ok", "외부로 나가는 요청·이미지 렌더 차단"),
         ("ok", "도구 호출 로그로 사후 추적"),
     ], "투입 경로: RAG 문서 · 웹페이지 · 도구 출력 · 도구 설명 — 모델이 읽는 모든 외부 텍스트", licon="doc", ricon="shield"))

_add("timewait-ports", "TIME_WAIT — 언제 문제인가",
     "수만 개는 대개 '바쁘다'는 증거입니다. 진짜 문제는 한 목적지로 나가는 연결이 임시 포트를 태울 때뿐이죠.",
     "time-wait",
     _two("tw", "정상 (걱정 불필요)", [
         ("ok", "인바운드 연결의 TIME_WAIT 수만 개"),
         ("ok", "소켓당 메모리 미미"),
         ("dot", "TCP가 연결을 안전하게 닫는 절차"),
     ], "위험 (포트 고갈)", [
         ("no", "같은 목적지로 초당 수백 개 신규 아웃바운드"),
         ("no", "임시 포트(약 2.8만) 소진"),
         ("no", "cannot assign requested address"),
     ], "판별: ss -tan state time-wait 로 목적지 집계 · 해법은 커널 튜닝이 아니라 keep-alive/커넥션 풀", licon="switch", ricon="firewall"))

_add("empty-kitchen", "크론은 '빈 주방'에서 실행된다",
     "터미널에서 되는 스크립트가 크론에서만 죽는 건, 코드가 아니라 실행 환경이 다르기 때문입니다.",
     "cron-env",
     _two("ek", "내 터미널 (내 주방)", [
         ("ok", "PATH에 /usr/local/bin 등 다 있음"),
         ("ok", ".bashrc의 환경변수 로드됨"),
         ("ok", "작업 디렉토리 = 내가 있던 곳"),
         ("ok", "셸 = bash"),
     ], "크론 (빈 주방)", [
         ("no", "PATH는 /usr/bin:/bin 정도"),
         ("no", ".bashrc를 읽지 않음 → 변수 없음"),
         ("no", "작업 디렉토리 = 홈"),
         ("no", "셸 = sh (dash일 수도)"),
     ], "재현: env -i /bin/sh -c 스크립트 · 처방: PATH 명시 · env 로드 · cd 스크립트위치 · 로그 리다이렉트", licon="laptop", ricon="server"))


_add("journal-order", "죽는 서비스, 보는 순서",
     "status는 요약본, journalctl이 전문입니다. 원인은 대개 넷 중 하나예요.",
     "journalctl-debug",
     _flow("jo", [("status", "종료코드", "server"),
                  ("journalctl -u", "유언 전문", "doc"),
                  ("원인 톱4", "앱·OOM·의존성", "box"),
                  ("-f 재현", "죽는 순간", "brain")],
           "종료코드가 힌트: 203/EXEC 경로·권한 · 217/USER 계정 없음 · signal=KILL 이면 dmesg로 OOM 확인"))

_add("iam-routine", "최소권한, 네 가지 습관",
     "완벽한 설계가 아니라 루틴입니다. 읽기전용에서 시작해 그룹으로 주고, 앱엔 역할을, 분기마다 회수.",
     "iam-least-privilege",
     _ladder("ir", [
         ("① 읽기전용 시작", "ReadOnly 부여", "막히는 것만 추가", "doc"),
         ("② 그룹·역할에만", "사람 → 그룹 → 정책", "입퇴사 = 멤버십", "user"),
         ("③ 앱엔 역할", "인스턴스 역할", "영구 키 제거", "lock"),
         ("④ 분기마다 회수", "admin·미사용 키", "90일 미사용 비활성", "shield"),
     ], "비상구를 설계에 포함: 봉인된 break-glass admin (MFA+알림) — 새벽 장애가 원칙을 무너뜨리지 않게"))


# ── 3차 배치 ──────────────────────────────────────────────────
_add("mtu-fragmentation", "MTU 초과 — 쪼개지거나 버려진다",
     "터널이 헤더를 덧붙여 봉투가 작아지면, 큰 패킷은 조각화되거나 DF 플래그 때문에 통째로 폐기됩니다.",
     "mtu-fragmentation",
     '<svg viewBox="0 0 640 290" role="img"><style>' + _COMMON + """
.mf-a{animation:mf-a 4.2s ease-in-out infinite;}
.mf-f1{opacity:0;animation:mf-f1 4.2s ease-in-out infinite;}
.mf-f2{opacity:0;animation:mf-f2 4.2s ease-in-out infinite;}
.mf-b{animation:mf-b 4.2s ease-in-out infinite;}
.mf-x{opacity:0;animation:mf-x 4.2s ease-in-out infinite;}
@keyframes mf-a{0%{transform:translateX(0);opacity:1}32%{transform:translateX(190px);opacity:1}
 38%{opacity:0}100%{opacity:0}}
@keyframes mf-f1{0%,36%{opacity:0;transform:translateX(0)}42%{opacity:1}
 82%{opacity:1;transform:translateX(200px)}100%{opacity:0}}
@keyframes mf-f2{0%,42%{opacity:0;transform:translateX(0)}48%{opacity:1}
 88%{opacity:1;transform:translateX(200px)}100%{opacity:0}}
@keyframes mf-b{0%{transform:translateX(0);opacity:1}36%{transform:translateX(190px);opacity:1}
 44%{transform:translateX(190px);opacity:.3}100%{opacity:.3}}
@keyframes mf-x{0%,42%{opacity:0}48%,92%{opacity:1}100%{opacity:0}}
</style>
<text x="14" y="22" class="dg-tl">조각화 허용 — 쪼개서 통과 (느려짐)</text>
<rect x="14" y="32" width="612" height="104" rx="12" class="dg-box"/>
<rect x="300" y="40" width="30" height="88" rx="6" fill="none" stroke="var(--accent)" stroke-width="2"/>
<rect x="304" y="66" width="22" height="36" rx="4" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.4"/>
""" + _icon("router", 244, 148, 1.05) + """<text x="274" y="152" class="dg-ts">터널 입구 — 실효 MTU 1400</text>
<g class="dg-anim mf-a"><rect x="40" y="66" width="120" height="36" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>
<text x="56" y="89" class="dg-ts">패킷 1500</text></g>
<g class="dg-anim mf-f1"><rect x="352" y="52" width="56" height="26" rx="4" fill="var(--accent)" opacity=".8"/></g>
<g class="dg-anim mf-f2"><rect x="352" y="90" width="56" height="26" rx="4" fill="var(--accent)" opacity=".8"/></g>
<text x="474" y="70" class="dg-ts">조각 1</text>
<text x="474" y="108" class="dg-ts">조각 2</text>
<text x="14" y="182" class="dg-tl">DF 플래그 있음 — 폐기 + ICMP 회신</text>
<rect x="14" y="192" width="612" height="88" rx="12" class="dg-box"/>
<rect x="300" y="200" width="30" height="72" rx="6" fill="none" stroke="var(--accent)" stroke-width="2"/>
<rect x="304" y="222" width="22" height="30" rx="4" fill="var(--paper)" stroke="var(--accent)" stroke-width="1.4"/>
<g class="dg-anim mf-b"><rect x="40" y="220" width="120" height="34" rx="5" fill="#FCE9EA" stroke="#E5484D" stroke-width="1.5"/>
<text x="52" y="242" class="dg-ts">1500 + DF</text></g>
<g class="dg-anim mf-x"><text x="296" y="248" font-size="19" class="dg-no" font-weight="700">✕</text>
<text x="352" y="228" class="dg-ts">ICMP "조각화 필요, 1400으로" 회신</text>
<text x="352" y="250" class="dg-ts">방화벽이 그 ICMP를 막으면 → 무한 재전송</text></g>
</svg>""")

_add("blast-radius", "장애 반경 — 어디까지 죽으면 우리도 죽나",
     "리전은 도시, AZ는 그 도시의 다른 건물. 서버만 흩뿌리고 NAT·DB가 한쪽에 있으면 이름만 멀티 AZ입니다.",
     "region-az",
     '<svg viewBox="0 0 640 270" role="img"><style>' + _COMMON + """
.br-die{animation:br-die 5s ease-in-out infinite;}
.br-x{opacity:0;animation:br-x 5s ease-in-out infinite;}
.br-warn{opacity:0;animation:br-w 5s ease-in-out infinite;}
.br-shift{animation:br-s 5s ease-in-out infinite;}
@keyframes br-die{0%,34%{opacity:1}46%,88%{opacity:.22}100%{opacity:1}}
@keyframes br-x{0%,40%{opacity:0}50%,88%{opacity:1}100%{opacity:0}}
@keyframes br-w{0%,54%{opacity:0}64%,88%{opacity:1}100%{opacity:0}}
@keyframes br-s{0%,40%{opacity:.25}54%,90%{opacity:1}100%{opacity:.25}}
</style>
<rect x="14" y="26" width="612" height="164" rx="14" fill="none" stroke="var(--faint)"
      stroke-dasharray="6 4" stroke-width="1.3"/>
<text x="26" y="44" class="dg-ts">리전 (서울) — 도시</text>
<g class="dg-anim br-die">
<rect x="34" y="56" width="270" height="118" rx="10" class="dg-box"/>
<text x="48" y="78" class="dg-t">가용영역 A — 건물 1</text>
""" + _icon("server", 76, 106, 1.15) + _icon("server", 148, 106, 1.15) + """
""" + _icon("gateway", 66, 148, 1.0) + """<text x="88" y="153" class="dg-warn" font-size="11">NAT GW (한쪽에만!)</text>
</g>
<g class="dg-anim br-x"><text x="200" y="122" font-size="26" class="dg-no" font-weight="700">✕</text>
<text x="196" y="146" class="dg-ts" fill="#E5484D">정전</text></g>
<rect x="332" y="56" width="270" height="118" rx="10" class="dg-box"/>
<text x="346" y="78" class="dg-t">가용영역 B — 건물 2</text>
<g class="dg-anim br-shift">
""" + _icon("server", 374, 106, 1.15) + _icon("server", 446, 106, 1.15) + """
</g>
<g class="dg-anim br-warn"><text x="346" y="152" class="dg-ts" fill="#E8842C">살아있지만 외부 통신 불가</text>
<text x="346" y="166" class="dg-ts" fill="#E8842C">→ NAT이 죽은 AZ에 있었다</text></g>
<text x="14" y="214" class="dg-ts">서버 1대 죽음 → LB+2대 / AZ 죽음 → 존 분산 / 리전 죽음 → 타 리전 (비용·복잡도 급증)</text>
<text x="14" y="236" class="dg-ts">멀티 AZ가 못 막는 것: 한쪽에만 있는 NAT · 단일 DB · failover를 못 견디는 앱 · 로컬 디스크에 둔 상태</text>
<text x="14" y="258" class="dg-ts">AZ 간은 1~2ms(동기 복제 가능), 리전 간은 수십~수백ms(비동기가 현실) — 이 물리가 설계를 정합니다</text>
</svg>""")

_add("eval-loop", "LLM 앱 평가 루프",
     "골든셋으로 돌리고, 채점하고, 이전 버전과 비교하고, 고쳐서 다시. 같은 저울로 매번 재는 게 핵심입니다.",
     "llm-eval",
     '<svg viewBox="0 0 640 250" role="img"><style>' + _COMMON + """
.el-1{animation:el-h 5.6s ease-in-out infinite;animation-delay:0s;}
.el-2{animation:el-h 5.6s ease-in-out infinite;animation-delay:1.4s;}
.el-3{animation:el-h 5.6s ease-in-out infinite;animation-delay:2.8s;}
.el-4{animation:el-h 5.6s ease-in-out infinite;animation-delay:4.2s;}
@keyframes el-h{0%,100%{fill:var(--raise);stroke:var(--line)}
 4%,22%{fill:var(--accent-soft);stroke:var(--accent)}}
</style>
<rect class="dg-box dg-anim el-1" x="18" y="30" width="140" height="60" rx="10"/>
""" + _icon("doc", 42, 50, 1.3) + """<text x="70" y="54" class="dg-t">① 골든셋</text>
<text x="36" y="74" class="dg-ts">실제 질문 50~200개</text>
<rect class="dg-box dg-anim el-2" x="250" y="30" width="140" height="60" rx="10"/>
<text x="268" y="54" class="dg-t">② 일괄 실행</text>
<text x="268" y="74" class="dg-ts">현재 버전으로</text>
<rect class="dg-box dg-anim el-3" x="482" y="30" width="140" height="60" rx="10"/>
""" + _icon("brain", 506, 50, 1.3) + """<text x="534" y="54" class="dg-t">③ 채점</text>
<text x="500" y="74" class="dg-ts">규칙 · LLM · 사람</text>
<rect class="dg-box dg-anim el-4" x="250" y="158" width="140" height="60" rx="10"/>
<text x="268" y="182" class="dg-t">④ 유형별 비교</text>
<text x="268" y="202" class="dg-ts">이전 버전 대비</text>
<line x1="158" y1="60" x2="250" y2="60" class="dg-arrow"/>
<line x1="390" y1="60" x2="482" y2="60" class="dg-arrow"/>
<path d="M552 90 v50 h-162" class="dg-arrow"/>
<path d="M250 188 h-162 v-98" class="dg-arrow"/>
<text x="400" y="132" class="dg-ts">결과 수집</text>
<text x="34" y="132" class="dg-ts">고쳐서 다시</text>
<text x="18" y="238" class="dg-ts">지표: 정답률 · 검색 재현율(RAG) · 근거 충실도 · '모른다' 응답률 — 0%면 오히려 의심</text>
</svg>""")




# ── 4차 배치 ──────────────────────────────────────────────────
_add("chmod-bits", "권한 숫자 = 4 + 2 + 1의 덧셈",
     "r(4) w(2) x(1) 스위치의 합이 한 자리, 그게 소유자·그룹·그외로 세 번 반복됩니다.",
     "chmod-755",
     '<svg viewBox="0 0 640 230" role="img"><style>' + _COMMON + """
.cb-on{animation:cb-p 3s ease-in-out infinite;}
@keyframes cb-p{0%,100%{opacity:.75}50%{opacity:1}}
</style>
<text x="14" y="26" class="dg-tl">chmod 755 를 분해하면</text>
<text x="70" y="66" font-size="30" font-weight="800" fill="var(--dg-red)" font-family="var(--mono)">7</text>
<text x="300" y="66" font-size="30" font-weight="800" fill="var(--dg-blue)" font-family="var(--mono)">5</text>
<text x="510" y="66" font-size="30" font-weight="800" fill="var(--dg-green)" font-family="var(--mono)">5</text>
<text x="40" y="88" class="dg-ts">소유자 (user)</text>
<text x="272" y="88" class="dg-ts">그룹 (group)</text>
<text x="478" y="88" class="dg-ts">그외 (others)</text>
<g class="dg-anim cb-on">
<rect x="20" y="100" width="46" height="30" rx="6" fill="var(--dg-red-s)" stroke="var(--dg-red)" stroke-width="1.5"/>
<text x="32" y="120" class="dg-t" fill="var(--dg-red)">r 4</text>
<rect x="72" y="100" width="46" height="30" rx="6" fill="var(--dg-red-s)" stroke="var(--dg-red)" stroke-width="1.5"/>
<text x="82" y="120" class="dg-t" fill="var(--dg-red)">w 2</text>
<rect x="124" y="100" width="46" height="30" rx="6" fill="var(--dg-red-s)" stroke="var(--dg-red)" stroke-width="1.5"/>
<text x="136" y="120" class="dg-t" fill="var(--dg-red)">x 1</text>
</g>
<text x="60" y="152" class="dg-ts">4+2+1 = 7 (전부)</text>
<rect x="250" y="100" width="46" height="30" rx="6" fill="var(--dg-blue-s)" stroke="var(--dg-blue)" stroke-width="1.5"/>
<text x="262" y="120" class="dg-t">r 4</text>
<rect x="302" y="100" width="46" height="30" rx="6" fill="none" stroke="var(--line)" stroke-width="1.3" stroke-dasharray="4 3"/>
<text x="311" y="120" class="dg-ts">w —</text>
<rect x="354" y="100" width="46" height="30" rx="6" fill="var(--dg-blue-s)" stroke="var(--dg-blue)" stroke-width="1.5"/>
<text x="366" y="120" class="dg-t">x 1</text>
<text x="288" y="152" class="dg-ts">4+1 = 5 (읽기+실행)</text>
<rect x="460" y="100" width="46" height="30" rx="6" fill="var(--dg-green-s)" stroke="var(--dg-green)" stroke-width="1.5"/>
<text x="472" y="120" class="dg-t" fill="var(--dg-green)">r 4</text>
<rect x="512" y="100" width="46" height="30" rx="6" fill="none" stroke="var(--line)" stroke-width="1.3" stroke-dasharray="4 3"/>
<text x="521" y="120" class="dg-ts">w —</text>
<rect x="564" y="100" width="46" height="30" rx="6" fill="var(--dg-green-s)" stroke="var(--dg-green)" stroke-width="1.5"/>
<text x="576" y="120" class="dg-t" fill="var(--dg-green)">x 1</text>
<text x="498" y="152" class="dg-ts">4+1 = 5</text>
<text x="14" y="186" class="dg-ts">표준 조합: 실행물·디렉토리 755 · 일반 파일 644 · 비밀(키·.env) 600</text>
<text x="14" y="208" class="dg-ts">디렉토리의 x 는 '통과' — 경로 중간에 x 빠지면 안이 안 열립니다 (namei -l 로 색출)</text>
</svg>""")

_add("dns-records", "도메인에 붙는 안내판 4종",
     "A는 주소, CNAME은 별명, MX는 우편함, TXT는 소유확인·메일인증 메모. 반영 지연의 범인은 TTL 캐시입니다.",
     "dns-records",
     _ladder("dr", [
         ("A", "example.com → 1.2.3.4", "이름을 IP에 직결", "globe"),
         ("CNAME", "www → example.com", "별명 (루트엔 불가)", "doc"),
         ("MX", "메일 → mx.google.com", "우편함 위치 (숫자=우선순위)", "gateway"),
         ("TXT", "소유확인 · SPF/DKIM", "메모 — 메일 스팸행 방지의 핵심", "shield"),
     ], "확인: dig +short 도메인 [A|CNAME|MX|TXT] · 변경 계획은 TTL을 먼저 300으로 낮추고"))

_add("multi-agent", "에이전트 하나 vs 멀티에이전트",
     "쪼개면 분업·병렬을 얻고 전달 손실·비용을 잃습니다. 기준: 사람 팀이라도 쪼갤 일인가.",
     "multi-agent",
     _two("ma", "에이전트 하나 + 좋은 도구", [
         ("ok", "추적·디버깅 쉬움, 비용 예측 가능"),
         ("ok", "맥락이 한 곳에 — 전달 손실 없음"),
         ("ok", "대부분의 작업은 이걸로 충분"),
         ("no", "긴 작업에서 책상(컨텍스트)이 붐빔"),
     ], "오케스트레이터 + 작업자", [
         ("ok", "컨텍스트 격리 — 각자 깨끗한 책상"),
         ("ok", "권한 분리 (조회/실행) · 병렬 실행"),
         ("no", "전달마다 정보 손실, 호출 수 곱증가"),
         ("no", "3~4단 넘으면 잃는 게 커지기 시작"),
     ], "순서: 프롬프트 → 도구 → 에이전트 하나 → 그래도 안 되면 분할 · 평가는 단계별로",
        licon="brain", ricon="user"))
