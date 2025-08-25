(function () {
  // Year
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Theme toggle
  const btn = document.getElementById('themeToggle');
  const apply = (m) => {
    if (m === 'light') document.documentElement.dataset.theme = 'light';
    else if (m === 'dark') document.documentElement.dataset.theme = 'dark';
    else document.documentElement.dataset.theme = '';
    localStorage.setItem('parslet-theme', m);
  };
  const current = localStorage.getItem('parslet-theme') || 'system';
  apply(current);
  if (btn) {
    btn.addEventListener('click', () => {
      const v = localStorage.getItem('parslet-theme') || 'system';
      const next = v === 'light' ? 'dark' : v === 'dark' ? 'system' : 'light';
      apply(next);
      btn.textContent = next === 'dark' ? '☀' : '☾';
    });
  }

  // Smooth anchor scroll
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Copy buttons for code blocks
  document.querySelectorAll('pre').forEach((pre) => {
    const btn = document.createElement('button');
    btn.textContent = 'Copy';
    btn.className = 'btn secondary';
    btn.style.position = 'absolute';
    btn.style.top = '6px';
    btn.style.right = '6px';
    btn.addEventListener('click', async () => {
      const code = pre.innerText;
      try { await navigator.clipboard.writeText(code); btn.textContent = 'Copied!'; setTimeout(()=>btn.textContent='Copy',1200); }
      catch { btn.textContent = 'Copy failed'; setTimeout(()=>btn.textContent='Copy',1200); }
    });
    pre.parentNode.insertBefore(btn, pre);
  });
})();
