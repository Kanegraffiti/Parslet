document.addEventListener('DOMContentLoaded', function () {
  var nav = document.querySelector('.wy-nav-side');
  var toggle = document.querySelector('.wy-nav-top .fa-bars');
  if (nav && toggle) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
    });
  }
});
