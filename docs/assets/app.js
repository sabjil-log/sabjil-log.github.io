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
