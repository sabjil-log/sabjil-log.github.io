/* ---- 다크모드 토글 (초기 적용은 head 인라인 스크립트가 담당) ---- */
(function () {
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;
  function icon() {
    btn.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀' : '☾';
  }
  btn.addEventListener('click', function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    icon();
  });
  icon();
})();

/* ---- 코드블록 복사 버튼 ---- */
document.querySelectorAll('article pre').forEach(function (pre) {
  var btn = document.createElement('button');
  btn.className = 'copy';
  btn.type = 'button';
  btn.textContent = 'copy';
  btn.addEventListener('click', function () {
    var code = pre.querySelector('code');
    var text = code ? code.innerText : pre.innerText;
    navigator.clipboard.writeText(text).then(function () {
      btn.textContent = 'copied';
      btn.classList.add('done');
      setTimeout(function () { btn.textContent = 'copy'; btn.classList.remove('done'); }, 1400);
    });
  });
  pre.appendChild(btn);
});

/* ---- 홈 검색: 제목/요약/카테고리 실시간 필터 ---- */
(function () {
  var input = document.getElementById('q');
  if (!input) return;
  var entries = Array.prototype.slice.call(document.querySelectorAll('.entry'));
  var none = document.querySelector('.search-none');
  var head = document.querySelector('.list-head');
  var total = entries.length;
  input.addEventListener('input', function () {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    entries.forEach(function (el) {
      var hit = !q || (el.getAttribute('data-search') || '').indexOf(q) !== -1;
      el.style.display = hit ? '' : 'none';
      if (hit) shown++;
    });
    if (none) none.style.display = shown ? 'none' : 'block';
    if (head) head.textContent = q ? ('검색 결과 · ' + shown + '개') : ('최근 글 · ' + total + '개');
  });
})();

/* ---- giscus 테마 동기화 ---- */
(function () {
  function giscusTheme() {
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    var frame = document.querySelector('iframe.giscus-frame');
    if (frame) frame.contentWindow.postMessage(
      { giscus: { setConfig: { theme: dark ? 'dark' : 'light' } } }, 'https://giscus.app');
  }
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.addEventListener('click', function(){ setTimeout(giscusTheme, 60); });
  window.addEventListener('message', function (e) {   // giscus 로드 완료 시 1회 맞춤
    if (e.origin === 'https://giscus.app') giscusTheme();
  });
})();
