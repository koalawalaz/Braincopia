/* ==========================================================================
   BRAINCOPIA. Site behaviour, No dependencies, no build step.
   ========================================================================== */
(function () {
  'use strict';

  /* ---------------------------------------------------------------------
     CONFIGURATION

     The real inbox lives in the Formspree dashboard, never in this file and
     never in the page. Replace the id below with your own form id; nothing
     else needs changing. No mailto: or wa.me link appears anywhere in the
     source, which is the point.
     --------------------------------------------------------------------- */
  var FORMSPREE_ENDPOINT = 'https://formspree.io/f/mvkowogd';

  var COLLECTIONS = [
    'The Spark', 'The Voice', 'The Second Opinion',
    'No meetings required', 'Wear Your'
  ];

  var CHANTS = [
    'AI is not creative. You are.',
    'For outsiders and beautiful misfits.',
    'Your voice. Your edition.',
    'Unapologetic. Visually obsessive.',
    'Comfort is not our business.',
    'Reality is only the starting point.'
  ];


  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ------------------------------------------------------------ MARQUEE */
  (function marquee() {
    var track = $('#marqueeTrack');
    if (!track) return;
    // Two identical runs so the -50% keyframe loops seamlessly.
    var run = COLLECTIONS.concat(COLLECTIONS);
    run.forEach(function (name) {
      var span = document.createElement('span');
      span.textContent = name;
      track.appendChild(span);
    });
  })();

  /* -------------------------------------------------- HERO CHANT + WORD */
  (function hero() {
    var chant = $('#chant');
    var i = 0;

    function setChant() {
      if (!chant) return;
      chant.textContent = '';
      var span = document.createElement('span');
      span.textContent = CHANTS[i % CHANTS.length];
      chant.appendChild(span);
    }
    setChant();
    if (reduceMotion) return;             // one line, held still
    setInterval(function () { i++; setChant(); }, 2600);
  })();

  /* -------------------------------------------------------- MOBILE MENU */
  (function menu() {
    var toggle = $('#menuToggle');
    var nav = $('#mobileNav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    $$('a', nav).forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  })();

  /* ------------------------------------------------------ SCROLL REVEAL */
  (function reveal() {
    var items = $$('.reveal');
    if (!items.length) return;
    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('visible'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
  })();

  /* --------------------------------------------------------------- OFFERS
     Three products, one at a time. Whichever is chosen travels down to the
     brief so nobody retypes what they already clicked, and nothing reaches
     the brief until somebody actually chooses. */
  (function offers() {
    var picks = $$('.offer input');
    var count = $('#pickCount');
    var field = $('#bService');
    if (!picks.length || !field) return;

    function sync() {
      var chosen = picks.filter(function (i) { return i.checked; });
      count.textContent = chosen.length
        ? 'Tell us what it is for and we will say if it is the right one.'
        : 'Pick one, or just tell us what is going on';
      field.value = chosen.length ? chosen[0].value : '';
    }
    picks.forEach(function (i) { i.addEventListener('change', sync); });
    sync();
  })();

  /* ---------------------------------------------------------------- STAMP
     It comes down when the section arrives, which is the only moment anybody
     is there to see it. Armed in here, so a page whose script never ran
     shows the stamp plainly instead of hiding it forever. */
  (function stamp() {
    var mark = $('.stamp');
    if (!mark || reduceMotion || !('IntersectionObserver' in window)) return;
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

  async function post(endpoint, data, errorBox, button, busyLabel) {
    errorBox.classList.remove('show');
    var original = button.textContent;
    button.disabled = true;
    button.textContent = busyLabel;
    try {
      var res = await fetch(endpoint, {
        method: 'POST',
        body: data,
        headers: { Accept: 'application/json' }
      });
      if (!res.ok) throw new Error('rejected');
      return true;
    } catch (err) {
      errorBox.textContent = 'That did not send. Check your connection and try again.';
      errorBox.classList.add('show');
      return false;
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  }

  var contactForm = $('#contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      var errorBox = $('#contactError');
      var button = $('#contactSubmit');
      var done = $('#contactDone');
      if (!contactForm.checkValidity()) {
        errorBox.textContent = 'Please fill in your name, email and message.';
        errorBox.classList.add('show');
        return;
      }
      var data = new FormData(contactForm);
      data.append('_subject', 'Braincopia enquiry');
      var ok = await post(FORMSPREE_ENDPOINT, data, errorBox, button, 'Sending…');
      if (!ok) return;
      contactForm.reset();
      done.style.display = 'block';
    });
  }

  /* --------------------------------------------------------------- MISC */
  var year = $('#year');
  if (year) year.textContent = String(new Date().getFullYear());

})();
