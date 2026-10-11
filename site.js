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
  var READY = 'braincopia:ready';

  /* ---------------------------------------------------------------- START
     Where a page opens. Two separate things were dragging a refresh back
     down the page: the browser restores the old scroll offset by itself,
     and any click on "The Brain" or "Pick a brain" leaves #services in the
     address bar, so reloading jumped there for ever afterwards.

     A refresh means start again: scroll restoration is turned off and a
     stale hash is dropped from the URL. A hash someone was actually sent
     (a fresh visit to /#services) is still honoured, but re-measured after
     the loader lets go and the fonts land, because the browser's own jump
     is calculated before the hero animates in and lands short. */
  (function start() {
    try { if ('scrollRestoration' in history) history.scrollRestoration = 'manual'; } catch (e) {}

    var nav = (performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null);
    var reloaded = nav ? nav.type === 'reload' : performance.navigation && performance.navigation.type === 1;
    var hash = location.hash;

    if (reloaded || !hash) {
      if (reloaded && hash) {
        try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
      }
      window.scrollTo(0, 0);
      // The browser may still be mid-restore when this runs.
      requestAnimationFrame(function () { window.scrollTo(0, 0); });
      return;
    }

    var target;
    try { target = document.querySelector(hash); } catch (e) { return; }
    if (!target) return;

    function land() {
      target.scrollIntoView({ block: 'start', behavior: 'auto' });
    }
    document.addEventListener(READY, function () { requestAnimationFrame(land); });
    window.addEventListener('load', land);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(land);
  })();

  /* --------------------------------------------------------------- LOADER
     A held breath. The mark arrives, then the page. All this does is decide
     when the overlay leaves and tell the rest of the page it may begin: the
     die must not bounce behind it, and nothing should scroll under it. */
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

    /* Show the control straight away and take it back only if the file
       genuinely fails. Waiting for canplaythrough hides it forever on iOS,
       which does not fetch media at all until the visitor interacts, so the
       event never fires and the button never appears. */
    btn.classList.add('ready');
    audio.addEventListener('error', function () { btn.classList.remove('ready'); });

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

    /* Sound on is the default: a visitor who has never touched the toggle
       gets it. Most browsers refuse to start audio before the page has been
       touched, so the attempt is made again on the first thing the visitor
       does, and again after that if the browser is still not satisfied.
       iOS in particular can refuse the first gesture it is offered, and one
       failed try used to be the end of it: the site stayed silent for the
       whole visit despite the preference saying otherwise. */
    var EVENTS = ['pointerdown', 'keydown', 'touchstart', 'wheel'];
    var tries = 0;

    function armed() {
      function wake() {
        EVENTS.forEach(function (e) { window.removeEventListener(e, wake); });
        start().then(function (playing) {
          if (!playing && ++tries < 4) armed();
        });
      }
      EVENTS.forEach(function (e) { window.addEventListener(e, wake, { passive: true }); });
    }

    start().then(function (playing) { if (!playing) armed(); });
  })();

  /* -------------------------------------------------------- COMPANIONS
     A butterfly and a paper plane, either of which can be flying or not.
     Neither is doing a job: the die says where you are in the page, these
     say nothing at all. That is exactly why these two have switches and
     the die does not.

     The flight is one spring toward a moving target, and the target is
     never the cursor itself but a point circling near it, so each keeps
     overshooting and coming back. A thing that sits exactly under the
     pointer stops reading as alive and starts reading as a cursor. */
  (function companions() {
    var bar = $('#critters');
    var fly = { butterfly: $('#butterfly'), paper: $('#paperPlane') };
    var tap = { butterfly: $('#toggleButterfly'), paper: $('#togglePaper') };
    if (!bar || !fly.butterfly || !fly.paper || reduceMotion) return;

    var PREF = 'braincopia.critters.v1';
    var TRAIT = {
      butterfly: { pull: .055, drag: .80, jitter: 2.6, lead: 90, wander: .9, phase: 0 },
      paper:     { pull: .018, drag: .92, jitter: .35, lead: 150, wander: .35, phase: 2.1 }
    };
    var S = {
      butterfly: { x: window.innerWidth * .5, y: window.innerHeight * .4, vx: 0, vy: 0 },
      paper:     { x: window.innerWidth * .4, y: window.innerHeight * .6, vx: 0, vy: 0 }
    };

    /* No pointer means nothing to follow, so on a phone they fly
       themselves rather than waiting to be led. */
    var hasPointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var px = window.innerWidth * .5, py = window.innerHeight * .4;
    var lastMove = -9999;

    if (hasPointer) {
      window.addEventListener('pointermove', function (e) {
        px = e.clientX; py = e.clientY; lastMove = performance.now();
      }, { passive: true });
    }

    /* Two sines of different periods never line up on a round number, so
       the wandering path does not visibly repeat. The phase offset stops
       the pair flying in formation. */
    function roam(t) {
      return [
        window.innerWidth  * (.5 + .36 * Math.sin(t * .00042) + .1 * Math.sin(t * .0019)),
        window.innerHeight * (.45 + .3 * Math.cos(t * .00058) + .08 * Math.cos(t * .0023))
      ];
    }

    function step(node, kind, now) {
      var s = S[kind], k = TRAIT[kind], tx, ty;
      if (!hasPointer || now - lastMove > 2200) {
        var r = roam(now + k.phase * 4000);
        tx = r[0]; ty = r[1];
      } else {
        tx = px + Math.cos(now * .0013 + k.phase) * k.lead * k.wander;
        ty = py + Math.sin(now * .0017 + k.phase) * k.lead * k.wander - 26;
      }
      s.vx = (s.vx + (tx - s.x) * k.pull) * k.drag;
      s.vy = (s.vy + (ty - s.y) * k.pull) * k.drag;
      s.x += s.vx + (Math.random() - .5) * k.jitter;
      s.y += s.vy + (Math.random() - .5) * k.jitter;

      /* Never off screen: the spring overshoots near an edge, and a
         companion you cannot see is just a running animation. */
      s.x = Math.max(26, Math.min(window.innerWidth - 26, s.x));
      s.y = Math.max(26, Math.min(window.innerHeight - 26, s.y));

      var tilt = kind === 'paper'
        ? Math.atan2(s.vy, s.vx) * 57.3
        : Math.max(-22, Math.min(22, s.vx * 2.2));
      node.style.transform =
        'translate3d(' + (s.x - 19) + 'px,' + (s.y - 17) + 'px,0) rotate(' + tilt + 'deg)';
    }

    (function frame(now) {
      requestAnimationFrame(frame);
      if (!fly.butterfly.hidden) step(fly.butterfly, 'butterfly', now);
      if (!fly.paper.hidden) step(fly.paper, 'paper', now);
    })(0);

    function set(kind, on) {
      fly[kind].hidden = !on;
      tap[kind].setAttribute('aria-pressed', String(on));
    }

    Object.keys(tap).forEach(function (kind) {
      tap[kind].addEventListener('click', function () {
        set(kind, fly[kind].hidden);
        try {
          localStorage.setItem(PREF,
            (fly.butterfly.hidden ? '' : 'b') + (fly.paper.hidden ? '' : 'p'));
        } catch (err) { /* private mode */ }
      });
    });

    /* Someone who switched one off keeps it off. Nobody has chosen on a
       first visit, so the butterfly starts flying and the paper waits. */
    var pref = null;
    try { pref = localStorage.getItem(PREF); } catch (err) {}
    if (pref === null) pref = 'b';
    set('butterfly', pref.indexOf('b') !== -1);
    set('paper', pref.indexOf('p') !== -1);
    bar.classList.add('ready');
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
