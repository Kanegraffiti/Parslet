(function () {
  // Year
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // THEME TOGGLE (light/dark/system)
  const root = document.documentElement;
  const btn = document.getElementById('themeToggle');

  function applyTheme(mode) {
    // mode: 'light' | 'dark' | 'system'
    root.dataset.theme = (mode === 'system') ? '' : mode;
    localStorage.setItem('parslet-theme', mode);
    if (btn) {
      btn.setAttribute('aria-pressed', mode !== 'system');
      btn.title = `Theme: ${mode}`;
      btn.textContent = mode === 'light' ? '☀' : mode === 'dark' ? '☾' : 'A';
    }
  }
  const saved = localStorage.getItem('parslet-theme') || 'system';
  applyTheme(saved);

  if (btn) {
    btn.addEventListener('click', () => {
      const current = localStorage.getItem('parslet-theme') || 'system';
      const next = current === 'light' ? 'dark' : current === 'dark' ? 'system' : 'light';
      applyTheme(next);
    });
  }

  // Smooth in-page anchor scroll
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

  // Copy buttons for code blocks
  document.querySelectorAll('pre').forEach((pre) => {
    if (pre.parentNode.querySelector('.copy-btn')) return;
    const b = document.createElement('button');
    b.textContent = 'Copy';
    b.className = 'btn secondary copy-btn';
    b.style.position = 'absolute'; b.style.top = '6px'; b.style.right = '6px';
    b.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(pre.innerText); b.textContent = 'Copied!'; setTimeout(()=>b.textContent='Copy',1200); }
      catch { b.textContent = 'Copy failed'; setTimeout(()=>b.textContent='Copy',1200); }
    });
    pre.parentNode.style.position = 'relative';
    pre.parentNode.insertBefore(b, pre);
  });

  // Collapsible use-case flows
  function toggleFlow(btn) {
    const id = btn.getAttribute('data-target');
    const panel = document.getElementById(id);
    if (!panel) return;
    const isHidden = panel.hasAttribute('hidden');
    if (isHidden) {
      panel.removeAttribute('hidden');
      btn.textContent = 'Hide flow';
      // retrigger SVG draw animation
      panel.querySelectorAll('.flow-svg .b').forEach(p => {
        p.style.animation = 'none'; void p.offsetWidth; p.style.animation = null;
      });
    } else {
      panel.setAttribute('hidden', '');
      btn.textContent = 'View flow';
    }
  }
  document.querySelectorAll('.flow-toggle').forEach(b => {
    b.addEventListener('click', () => toggleFlow(b));
    b.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleFlow(b); } });
  });
})();
