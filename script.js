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

  /* The ticker says what we sell: the umbrella, then its three parts. It
     used to carry "No meetings required", from a stamp the site no longer
     has, and a bare "Wear Your", which reads as an unfinished sentence
     among service names. Wear Your is still linked in the footer, where a
     brand name has context. */
  var COLLECTIONS = [
    'The Brain', 'The Concept', 'The Voice', 'The Decision'
  ];

  var ROTATING_WORDS = ['parallel', 'surreal'];

  var CHANTS = [
    'AI is not creative. You are.',
    'Your voice. Your rules.',
    'Unapologetic. Visually obsessive.',
    'Comfort is not our business.',
    'Reality is only the starting point.'
  ];


  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ------------------------------------------------------------ ENTRANCE
     The hero arrives after the loader lets go, rather than being there all
     along. The class is added here and not in the markup, so a page whose
     script never runs is a page with a hero on it. */
  (function entrance() {
    var hero = document.querySelector('[data-enter]');
    if (!hero) return;
    var go = function () { hero.classList.add('in'); };
    if (window.braincopia && window.braincopia.ready) window.braincopia.ready(go);
    else go();
  })();

  /* ------------------------------------------------------------ MARQUEE */
  (function marquee() {
    var track = $('#marqueeTrack');
    if (!track) return;

    function add(name) {
      var span = document.createElement('span');
      span.textContent = name;
      track.appendChild(span);
    }

    /* The keyframe slides the track by -50%, so one run has to be at least
       as wide as the window or the loop shows the gap behind it. Four short
       words are not, on a wide screen, so the run repeats until it is and
       only then is doubled. */
    var width = track.parentNode.offsetWidth || 1280;
    var guard = 0;
    do {
      COLLECTIONS.forEach(add);
      guard += 1;
    } while (track.scrollWidth < width && guard < 12);

    var run = track.innerHTML;
    track.insertAdjacentHTML('beforeend', run);
  })();

  /* -------------------------------------------------- HERO CHANT + WORD */
  (function hero() {
    var chant = $('#chant');
    var rotator = $('#rotator');
    var article = $('#article');
    var i = 0;

    function setChant() {
      if (!chant) return;
      chant.textContent = '';
      var span = document.createElement('span');
      span.textContent = CHANTS[i % CHANTS.length];
      chant.appendChild(span);
    }
    function setWord() {
      if (!rotator) return;
      var word = ROTATING_WORDS[i % ROTATING_WORDS.length];
      rotator.textContent = word;
      /* unfiled is the only one that takes an, and a headline that reads
         "a unfiled universe" undoes the sentence it is selling. */
      if (article) article.textContent = /^[aeiou]/i.test(word) ? 'An' : 'A';
    }

    setChant(); setWord();
    if (reduceMotion) return;             // one line, held still
    setInterval(function () { i++; setChant(); setWord(); }, 2600);
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

  /* ------------------------------------------------------------ THE RAIL
     A row of quotes you swipe. The scrolling is the browser's, with snap
     points doing the work, so a phone behaves the way a phone should with
     no JavaScript involved at all. This only adds what a pointer needs:
     arrows, dots, and the arithmetic to know when neither is wanted.

     Everything is measured rather than configured, so adding a card to the
     markup is the whole job of adding a card. */
  (function rail() {
    var track = $('#saidTrack');
    var nav = $('#saidNav');
    if (!track || !nav) return;

    var prev = $('#saidPrev');
    var next = $('#saidNext');
    var dotWrap = $('#saidDots');
    var dots = [];

    function pageWidth() { return track.clientWidth; }
    /* Count pages from how far the track can travel, not from how wide it
       is. Its width includes the padding that holds the card shadows, and
       dividing that by the viewport invented a page the arrows could never
       reach: four cards, two screens, three dots. The slack absorbs that
       padding and any sub-pixel rounding. */
    function pageCount() {
      var far = track.scrollWidth - track.clientWidth;
      return 1 + Math.ceil(Math.max(0, far - 24) / pageWidth());
    }
    function pageNow() {
      return Math.min(pageCount() - 1, Math.round(track.scrollLeft / pageWidth()));
    }
    function overflows() { return track.scrollWidth - track.clientWidth > 2; }

    function goTo(i) {
      track.scrollTo({
        left: i * pageWidth(),
        behavior: reduceMotion ? 'auto' : 'smooth'
      });
    }

    function buildDots() {
      var want = pageCount();
      if (dots.length === want) return;
      dotWrap.textContent = '';
      dots = [];
      for (var i = 0; i < want; i++) {
        (function (n) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'rail-dot';
          b.setAttribute('aria-label', 'Testimonials ' + (n + 1) + ' of ' + want);
          b.addEventListener('click', function () { goTo(n); });
          dotWrap.appendChild(b);
          dots.push(b);
        })(i);
      }
    }

    function sync() {
      /* Two cards on a laptop need no controls: there is nowhere to go. */
      nav.hidden = !overflows();
      if (nav.hidden) return;
      buildDots();
      var at = pageNow();
      dots.forEach(function (d, i) {
        d.setAttribute('aria-current', i === at ? 'true' : 'false');
      });
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 2;
    }

    prev.addEventListener('click', function () { goTo(Math.max(0, pageNow() - 1)); });
    next.addEventListener('click', function () { goTo(Math.min(pageCount() - 1, pageNow() + 1)); });

    /* Scroll fires far more often than anything here needs to run. */
    var queued = false;
    track.addEventListener('scroll', function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; sync(); });
    }, { passive: true });

    window.addEventListener('resize', function () { dots = []; sync(); });
    sync();
  })();

  /* ----------------------------------------------------------- THE STEPS
     Four fields at once reads as paperwork. One question at a time reads as
     a conversation, and the only cost is two clicks.

     Every field stays in the form the whole way through, hidden rather than
     built on demand, so FormData still collects all of it on submit and a
     visitor who goes back does not lose what they typed. */
  (function steps() {
    var form = $('#contactForm');
    if (!form) return;
    var panes = $$('.step', form);
    if (panes.length < 2) return;

    var count = $('#stepCount');
    var back = $('#stepBack');
    var next = $('#stepNext');
    var send = $('#contactSubmit');
    var err = $('#contactError');
    var at = 0;

    function show(i, focus) {
      at = i;
      panes.forEach(function (p, n) { p.hidden = n !== i; });
      count.textContent = 'Step ' + (i + 1) + ' of ' + panes.length;
      back.hidden = i === 0;
      next.hidden = i === panes.length - 1;
      send.hidden = i !== panes.length - 1;
      err.classList.remove('show');
      err.textContent = '';   /* role=alert: stale text must not be re-announced */
      if (focus) {
        var first = panes[i].querySelector('input, textarea');
        if (first) first.focus();
      }
    }

    /* The browser cannot focus an invalid field it is not showing, so each
       step is checked on its own rather than leaning on the form's. */
    function valid() {
      var fields = $$('input, textarea', panes[at]);
      for (var i = 0; i < fields.length; i++) {
        if (!fields[i].checkValidity()) {
          err.textContent = fields[i].validity.valueMissing
            ? 'This one we need.'
            : 'That does not look right yet.';
          err.classList.add('show');
          fields[i].focus();
          return false;
        }
      }
      return true;
    }

    next.addEventListener('click', function () { if (valid()) show(at + 1, true); });
    back.addEventListener('click', function () { show(at - 1, true); });

    /* Enter means next until the last step, where the submit button is the
       one in the form and Enter can have it. */
    form.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' || e.target.tagName === 'TEXTAREA') return;
      if (at < panes.length - 1) { e.preventDefault(); next.click(); }
    });

    show(0, false);
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
