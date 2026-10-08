(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  $('#year').textContent = new Date().getFullYear();

  /* --------------------------------------------------------------- OFFERS
     Three products, one at a time. Whichever is chosen travels down to the
     brief so nobody retypes what they already clicked, and nothing reaches
     the brief until somebody actually chooses. */
  var offers = $$('.offer input');
  var count = $('#pickCount');
  var serviceField = $('#bService');

  function syncPicks() {
    var chosen = offers.filter(function (i) { return i.checked; });

    count.textContent = chosen.length
      ? 'Tell us what it is for and we will say if it is the right one.'
      : 'Pick one, or just tell us what is going on';

    serviceField.value = chosen.length ? chosen[0].value : '';
  }

  offers.forEach(function (i) { i.addEventListener('change', syncPicks); });
  syncPicks();

  /* ------------------------------------------------------------- THE STAMP
     The joke is well down the page, so it comes down when the band arrives
     rather than on load, which is the only moment anybody is there to see
     it. Arming in here means a page whose script never ran shows the stamp
     plainly instead of hiding it forever. */
  (function stamp() {
    var mark = $('.stamp');
    if (!mark) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches
        || !('IntersectionObserver' in window)) return;

    mark.classList.add('armed');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        mark.classList.add('struck');
        io.unobserve(e.target);
      });
    }, { threshold: 0.9 });
    io.observe(mark);
  })();

  /* -------------------------------------------------------- MOBILE MENU */
  var toggle = $('#menuToggle');
  var mobile = $('#mobileNav');
  toggle.addEventListener('click', function () {
    var open = mobile.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  $$('a', mobile).forEach(function (a) {
    a.addEventListener('click', function () {
      mobile.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });

  /* --------------------------------------------------------------- BRIEF
     Posts to the same Formspree form as the magazine, so no real address
     ever appears in the page source. */
  var ENDPOINT = 'https://formspree.io/f/mvkowogd';
  var form = $('#briefForm');
  var err = $('#formError');
  var done = $('#formDone');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    err.classList.remove('show');
    if (!form.checkValidity()) {
      err.textContent = 'Please fill in your name, email and the brief.';
      err.classList.add('show');
      return;
    }
    var button = $('#briefSubmit');
    var label = button.textContent;
    button.disabled = true;
    button.textContent = 'Sending...';

    var data = new FormData(form);
    data.append('_subject', 'Braincopia Studio brief');

    fetch(ENDPOINT, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
      .then(function (res) {
        if (!res.ok) throw new Error('rejected');
        form.reset();
        done.textContent = 'Brief received. We answer within two weeks, either way.';
        done.classList.add('show');
      })
      .catch(function () {
        err.textContent = 'That did not send. Check your connection and try again.';
        err.classList.add('show');
      })
      .then(function () {
        button.disabled = false;
        button.textContent = label;
      });
  });
})();
