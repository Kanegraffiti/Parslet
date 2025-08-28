(function () {
  const root = document.documentElement;
  const stored = localStorage.getItem("parslet-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  if (stored) {
    root.dataset.theme = stored;
  } else if (prefersDark) {
    root.dataset.theme = "dark";
  }

  const toggle = document.getElementById("theme-toggle");
  toggle.addEventListener("click", () => {
    const current = root.dataset.theme === "dark" ? "light" : "dark";
    root.dataset.theme = current;
    localStorage.setItem("parslet-theme", current);
  });

  const header = document.querySelector("header");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 8) header.classList.add("scrolled");
    else header.classList.remove("scrolled");
  });

  document.querySelectorAll(".tabs").forEach((tabs) => {
    const tabButtons = tabs.querySelectorAll('[role="tab"]');
    const tabPanels = tabs.querySelectorAll('[role="tabpanel"]');
    tabButtons.forEach((btn, i) => {
      btn.addEventListener("click", () => activate(i));
      btn.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight") activate((i + 1) % tabButtons.length);
        if (e.key === "ArrowLeft")
          activate((i - 1 + tabButtons.length) % tabButtons.length);
      });
    });
    function activate(index) {
      tabButtons.forEach((b, i) => {
        const selected = i === index;
        b.setAttribute("aria-selected", selected);
        b.tabIndex = selected ? 0 : -1;
        tabPanels[i].hidden = !selected;
      });
      tabButtons[index].focus();
    }
    activate(0);
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 },
  );

  document
    .querySelectorAll("[data-animate]")
    .forEach((el) => observer.observe(el));
})();
