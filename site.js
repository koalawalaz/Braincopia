/* ==========================================================================
   BRAINCOPIA. The behaviour every page carries: the loader that hands the
   page over, the die that rolls with the scroll, and the sound toggle.

   Loaded before each page's own script. The handover fires a
   braincopia:ready event on document, and exposes braincopia.ready(fn) for
   anything on a page that must wait for the overlay to leave.
   ========================================================================== */
(function () {
  'use strict';

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --------------------------------------------------------------- LOADER
     A held breath. The mark arrives, then the page. All this does is decide
     when the overlay leaves and tell the rest of the page it may begin: the
     die must not bounce behind it, and nothing should scroll under it. */
  var READY = 'braincopia:ready';
  var handedOver = false;

  function handOver() {
    if (handedOver) return;
    handedOver = true;
    document.documentElement.style.removeProperty('overflow');
    document.dispatchEvent(new CustomEvent(READY));
  }

  (function loader() {
    var el = $('#loader');
    if (!el || reduceMotion) {
      if (el) el.remove();
      handOver();
      return;
    }

    document.documentElement.style.overflow = 'hidden';

    function finish() {
      el.classList.add('done');
      handOver();
      setTimeout(function () { if (el.parentNode) el.remove(); }, 400);
    }

    setTimeout(finish, 480);        // mark in, brief hold, gone
    el.addEventListener('click', finish);
    setTimeout(finish, 4000);       // and never trap the page
  })();

  /* ---------------------------------------------------------------- SOUND
     Browsers refuse to start audio before the visitor has interacted with
     the page, so "plays when you open the site" means: try, and if the
     browser says no, start on the first click, key or touch instead. A
     visitor who turns it off is never asked again, and the toggle is
     always on screen, because a page that makes noise owes you a way to
     stop it. */
  (function sound() {
    var audio = $('#ambience');
    var btn = $('#sound');
    if (!audio || !btn) return;

    var PREF = 'braincopia.sound.v1';
    var VOLUME = 0.34;
    var pref = null;
    try { pref = localStorage.getItem(PREF); } catch (err) { /* private mode */ }

    // No control for audio that will never arrive.
    audio.addEventListener('error', function () { btn.classList.remove('ready'); });
    audio.addEventListener('canplaythrough', function () { btn.classList.add('ready'); });
    if (audio.readyState >= 3) btn.classList.add('ready');

    var fade = 0;
    function ramp(to, done) {
      cancelAnimationFrame(fade);
      var from = audio.volume;
      var t0 = 0;
      (function step(now) {
        if (!t0) t0 = now;
        var k = Math.min(1, (now - t0) / 900);
        audio.volume = from + (to - from) * k;
        if (k < 1) fade = requestAnimationFrame(step);
        else if (done) done();
      })(0);
    }

    function mark(on) {
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.setAttribute('aria-label', on ? 'Turn the sound off' : 'Turn the sound on');
    }

    function start() {
      audio.volume = 0;
      var p = audio.play();
      if (p && p.catch) {
        return p.then(function () { mark(true); ramp(VOLUME); return true; })
                .catch(function () { return false; });
      }
      mark(true); ramp(VOLUME);
      return Promise.resolve(true);
    }

    function stop() {
      ramp(0, function () { audio.pause(); });
      mark(false);
    }

    btn.addEventListener('click', function () {
      var on = btn.getAttribute('aria-pressed') === 'true';
      if (on) {
        stop();
        try { localStorage.setItem(PREF, 'off'); } catch (err) {}
      } else {
        start();
        try { localStorage.setItem(PREF, 'on'); } catch (err) {}
      }
    });

    // Nothing plays into an unwatched tab.
    document.addEventListener('visibilitychange', function () {
      if (btn.getAttribute('aria-pressed') !== 'true') return;
      if (document.hidden) audio.pause();
      else audio.play().catch(function () {});
    });

    if (pref === 'off') { mark(false); return; }

    start().then(function (playing) {
      if (playing) return;
      // Autoplay was refused. Wait for the first thing the visitor does.
      var events = ['pointerdown', 'keydown', 'touchstart', 'wheel'];
      function wake() {
        events.forEach(function (e) { window.removeEventListener(e, wake); });
        start();
      }
      events.forEach(function (e) { window.addEventListener(e, wake, { once: true, passive: true }); });
    });
  })();

  /* ------------------------------------------------------------------ DIE
     A square does not spin as it rolls, it pivots on one corner at a time.
     So the geometry: over a quarter turn the centre swings on an arc of
     radius R (the half-diagonal) about the resting corner, which puts it
     at R*sin(45deg + phi) above the ground and advances the die by exactly
     one side length. Tie the travel to scroll progress and the rotation
     follows from it, never the other way round, or the die skids.

     The face changes mid-tumble, at the point where it is up on a corner
     and the top face is edge-on, so the number is never seen to swap. */
  (function die() {
    var el = $('#die');
    var face = $('#dieFace');
    if (!el || !face || reduceMotion) return;

    var FACES = {
      1: [5], 2: [1, 9], 3: [1, 5, 9],
      4: [1, 3, 7, 9], 5: [1, 3, 5, 7, 9], 6: [1, 3, 4, 6, 7, 9]
    };
    var pips = [];
    for (var i = 1; i <= 9; i++) {
      var pip = document.createElement('span');
      pip.className = 'pip';
      face.appendChild(pip);
      pips.push(pip);
    }
    function show(n) {
      var on = FACES[n];
      pips.forEach(function (pip, idx) {
        pip.classList.toggle('on', on.indexOf(idx + 1) !== -1);
      });
    }

    var shown = 0;
    var queued = false;
    var introing = false;

    function place() {
      queued = false;
      if (introing) return;                    // the intro owns the transform until it lands
      var side = el.offsetWidth;
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      // Up on a corner the square is wider than its side by (sqrt2-1)/2 each
      // way, so inset the track by that much or the corners clip the edges.
      var pad = side * (Math.SQRT2 - 1) / 2;
      var run = window.innerWidth - side - pad * 2;
      if (scrollable <= 0 || run <= 0) return;

      var progress = Math.min(1, Math.max(0, window.scrollY / scrollable));
      var x = pad + progress * run;

      var quarters = (x - pad) / side;         // one quarter turn per side length travelled, measured from rest
      var phi = (quarters - Math.floor(quarters)) * 90;
      var R = side / Math.SQRT2;               // half-diagonal
      var lift = R * Math.sin((45 + phi) * Math.PI / 180) - side / 2;

      el.style.transform = 'translate(' + x + 'px, ' + (-lift) + 'px) rotate(' + (quarters * 90) + 'deg)';

      var n = (Math.round(quarters) % 6 + 6) % 6 + 1;
      if (n !== shown) { shown = n; show(n); }
    }

    function onScroll() {
      if (introing) { introing = false; }       // a scroll during the intro takes over from it
      if (queued) return;
      queued = true;
      requestAnimationFrame(place);
    }

    /* The die drops in on load and bounces itself to rest before the scroll
       takes over. Each impact keeps BOUNCE of the speed it arrived with, so
       the hops shrink the way a real one does; the spin is spent entirely on
       the way down, which lands it flat on a face for the first bounce. */
    var GRAVITY = 3600;      // px/s squared
    var BOUNCE = 0.46;       // share of the speed that survives an impact
    var SPIN = -450;         // degrees turned during the fall

    function heightAt(t, h0) {
      var fall = Math.sqrt(2 * h0 / GRAVITY);
      if (t < fall) return h0 - 0.5 * GRAVITY * t * t;
      t -= fall;
      var v = Math.sqrt(2 * GRAVITY * h0);
      for (var guard = 0; guard < 40; guard++) {
        v *= BOUNCE;
        var dur = 2 * v / GRAVITY;
        if (dur < 0.06) return 0;              // too small to see: it has settled
        if (t < dur) return v * t - 0.5 * GRAVITY * t * t;
        t -= dur;
      }
      return 0;
    }

    function runIntro() {
      var side = el.offsetWidth;
      var pad = side * (Math.SQRT2 - 1) / 2;
      var h0 = Math.max(160, window.innerHeight * 0.62);
      var fall = Math.sqrt(2 * h0 / GRAVITY);
      var start = 0;
      introing = true;
      el.classList.add('ready');

      (function frame(now) {
        if (!introing) { place(); return; }     // handed over to the scroll
        if (!start) start = now;
        var t = (now - start) / 1000;
        var h = heightAt(t, h0);
        var deg = t < fall ? SPIN * (1 - easeOut(t / fall)) : 0;
        el.style.transform = 'translate(' + pad + 'px, ' + (-h) + 'px) rotate(' + deg + 'deg)';
        if (h === 0 && t > fall) { introing = false; place(); return; }
        requestAnimationFrame(frame);
      })(0);
    }

    function easeOut(x) { return 1 - Math.pow(1 - x, 3); }

    show(1);
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);

    // Landing part-way down the page (a reload, a #link) means the die
    // belongs where the scroll says, not falling out of the sky.
    function begin() {
      if (window.scrollY > 4) { el.classList.add('ready'); place(); }
      else { runIntro(); }
    }
    // The die should not be bouncing behind the loader.
    if (handedOver) begin();
    else document.addEventListener(READY, begin, { once: true });
  })();

  /* The sound preference is one key for the whole origin, so turning it off
     on one page keeps it off on the next. */
  window.braincopia = {
    ready: function (fn) {
      if (handedOver) fn();
      else document.addEventListener(READY, fn, { once: true });
    },
    reduceMotion: reduceMotion
  };
})();
