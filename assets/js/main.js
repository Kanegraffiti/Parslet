(function(){
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');

  function setTheme(theme){
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem('theme', theme); } catch(e){}
  }

  const stored = localStorage.getItem('theme');
  if(stored){
    setTheme(stored);
  } else {
    setTheme(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }

  if(toggle){
    toggle.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      setTheme(current);
    });
  }

  // smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if(target){
        e.preventDefault();
        target.scrollIntoView({behavior:'smooth'});
        history.pushState(null,'',link.getAttribute('href'));
      }
    });
  });

  if(location.hash){
    const target = document.querySelector(location.hash);
    if(target) target.scrollIntoView();
  }

  // intersection observer for reveals
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      }
    });
  }, {threshold:0.1});
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  // tabs
  const tabs = document.querySelectorAll('.tabs [role="tab"]');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab));
    tab.addEventListener('keydown', e => {
      let dir = 0;
      if(e.key === 'ArrowRight') dir = 1;
      if(e.key === 'ArrowLeft') dir = -1;
      if(dir !== 0){
        const newTab = tabs[(Array.prototype.indexOf.call(tabs, tab) + dir + tabs.length) % tabs.length];
        newTab.focus();
      }
    });
  });

  function switchTab(newTab){
    tabs.forEach(tab => tab.setAttribute('aria-selected','false'));
    newTab.setAttribute('aria-selected','true');
    document.querySelectorAll('.tab-panel').forEach(p => p.hidden = true);
    const panel = document.getElementById(newTab.getAttribute('aria-controls'));
    if(panel) panel.hidden = false;
  }
})();
