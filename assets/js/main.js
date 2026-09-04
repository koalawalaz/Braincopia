/* Braincopia — site behaviour. No dependencies, no build step. */
(function () {
  'use strict';

  /* ---- mobile navigation ------------------------------------------------ */
  var toggle = document.querySelector('.nav-toggle');
  var drawer = document.querySelector('.nav-drawer');
  if (toggle && drawer) {
    toggle.addEventListener('click', function () {
      var open = drawer.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---- mark the current page in the nav --------------------------------- */
  var here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .nav-drawer a').forEach(function (a) {
    if (a.getAttribute('href') === here) a.classList.add('is-current');
  });

  /* ---- archive filtering ------------------------------------------------ */
  var filters = document.querySelectorAll('[data-filter]');
  if (filters.length) {
    var items = document.querySelectorAll('[data-tags]');
    var empty = document.querySelector('.empty-state');
    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var key = btn.getAttribute('data-filter');
        filters.forEach(function (b) { b.classList.toggle('is-active', b === btn); });
        var shown = 0;
        items.forEach(function (item) {
          var match = key === 'all' || item.getAttribute('data-tags').split(' ').indexOf(key) > -1;
          item.classList.toggle('is-hidden', !match);
          if (match) shown++;
        });
        if (empty) empty.classList.toggle('is-hidden', shown > 0);
      });
    });
  }

  /* ---- reading progress ------------------------------------------------- */
  var bar = document.querySelector('.readbar i');
  if (bar) {
    var paint = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var pct = h > 0 ? (window.scrollY / h) * 100 : 0;
      bar.style.width = Math.min(100, Math.max(0, pct)) + '%';
    };
    window.addEventListener('scroll', paint, { passive: true });
    window.addEventListener('resize', paint);
    paint();
  }

  /* ---- newsletter forms -------------------------------------------------
     Front end only. Point ACTION at your provider (ConvertKit, Buttondown,
     Mailchimp) or post to your own endpoint inside the fetch below.        */
  document.querySelectorAll('[data-signup]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = form.parentNode.querySelector('.form-status');
      var email = form.querySelector('input[type="email"]');
      if (!email || !email.value) return;
      if (status) {
        status.textContent = 'You are on the list. The next dispatch lands in your inbox first.';
        status.style.color = '#14724A';
      }
      form.reset();
    });
  });

  /* ---- share buttons ---------------------------------------------------- */
  document.querySelectorAll('[data-copy-link]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var label = btn.textContent;
      var done = function () {
        btn.textContent = 'Link copied';
        setTimeout(function () { btn.textContent = label; }, 1800);
      };
      if (navigator.clipboard) {
        navigator.clipboard.writeText(location.href).then(done, done);
      } else {
        done();
      }
    });
  });

  /* ---- footer year ------------------------------------------------------ */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
