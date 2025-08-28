(function(){
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  const stored = localStorage.getItem('parslet-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  function setTheme(t){
    root.dataset.theme = t;
    localStorage.setItem('parslet-theme', t);
    toggle.textContent = t === 'dark' ? '☀️' : '🌙';
  }
  setTheme(stored ? stored : (prefersDark ? 'dark':'light'));
  toggle.addEventListener('click',()=>{
    setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark');
  });
  
  // sticky header shadow
  const header = document.querySelector('.site-header');
  window.addEventListener('scroll',()=>{
    if(window.scrollY>8) header.classList.add('scrolled');
    else header.classList.remove('scrolled');
  });

  // tabs
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.tab-panel');
  function activate(tab){
    tabs.forEach(t=>t.setAttribute('aria-selected','false'));
    panels.forEach(p=>p.classList.add('hidden'));
    const panel = document.getElementById(tab.id.replace('tab','panel'));
    panel.classList.remove('hidden');
    tab.setAttribute('aria-selected','true');
  }
  tabs.forEach(tab=>{
    tab.addEventListener('click',()=>activate(tab));
  });
  document.querySelector('.tabs').addEventListener('keydown',e=>{
    const idx = Array.prototype.indexOf.call(tabs, document.activeElement);
    if(e.key==='ArrowRight'){ e.preventDefault(); tabs[(idx+1)%tabs.length].focus(); }
    if(e.key==='ArrowLeft'){ e.preventDefault(); tabs[(idx-1+tabs.length)%tabs.length].focus(); }
    if(['ArrowRight','ArrowLeft'].includes(e.key)) activate(document.activeElement);
  });

  // reveal animations
  const observer = new IntersectionObserver(entries =>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  },{threshold:0.1});
  document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
})();
