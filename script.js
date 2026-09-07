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

  /* period marks a recurring line, and max caps it: nobody holds two of the
     same monthly subscription, so the cart must not let them try. */
  var CATALOGUE = {
    vol1: { name: 'Vol. I: The Parallel Universe', price: 7, period: 'month', max: 1,
            note: 'Subscription · both covers' },
    book: { name: 'Tripple CH',                    price: 12,
            note: 'Digital · instant' }
  };

  var COLLECTIONS = [
    'Vol. I: The Parallel Universe', 'Two covers, one price',
    'Tripple CH', 'Wear Your'
  ];

  var CHANTS = [
    'AI is not creative. You are.',
    'For outsiders and beautiful misfits.',
    'Your voice. Your edition.',
    'Unapologetic. Visually obsessive.',
    'Comfort is not our business.',
    'Reality is only the starting point.'
  ];

  var ROTATING_WORDS = ['parallel', 'surreal', 'restless', 'wide-awake', 'unfiled'];

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var money = function (n) { return '$' + n; };   // nothing is free any more, and an empty cart reads $0
  var priced = function (item, qty) {
    var amount = money(item.price * (qty || 1));
    return item.period ? amount + ' / ' + item.period : amount;
  };

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
    var rotator = $('#rotator');
    var i = 0;

    function setChant() {
      if (!chant) return;
      chant.textContent = '';
      var span = document.createElement('span');
      span.textContent = CHANTS[i % CHANTS.length];
      chant.appendChild(span);
    }
    function setWord() {
      if (rotator) rotator.textContent = ROTATING_WORDS[i % ROTATING_WORDS.length];
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
    if (window.scrollY > 4) {
      el.classList.add('ready');
      place();
    } else {
      runIntro();
    }
  })();

  /* ================================================================ CART */
  var STORE_KEY = 'braincopia.cart.v1';
  var cart = load();
  save();   // a catalogue change leaves dead ids in storage; load() drops them, this writes the cleaned cart back

  function load() {
    try {
      var raw = JSON.parse(localStorage.getItem(STORE_KEY) || '{}');
      var clean = {};
      Object.keys(raw).forEach(function (id) {
        var qty = parseInt(raw[id], 10);
        if (CATALOGUE[id] && qty > 0) clean[id] = Math.min(qty, 99);
      });
      return clean;
    } catch (err) { return {}; }
  }
  function save() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(cart)); } catch (err) { /* private mode */ }
  }
  function count() {
    return Object.keys(cart).reduce(function (n, id) { return n + cart[id]; }, 0);
  }
  /* A basket can hold a one-off and a subscription at once, and they are not
     the same number. Adding them would tell someone they are paying $19 when
     they are paying $12 now and $7 every month after. */
  function totals() {
    var once = 0, monthly = 0;
    Object.keys(cart).forEach(function (id) {
      var item = CATALOGUE[id];
      var sum = item.price * cart[id];
      if (item.period) monthly += sum; else once += sum;
    });
    return { once: once, monthly: monthly };
  }
  function totalLabel() {
    var t = totals();
    if (t.once && t.monthly) return money(t.once) + ' + ' + money(t.monthly) + ' / month';
    if (t.monthly) return money(t.monthly) + ' / month';
    return money(t.once);
  }

  var cartCount = $('#cartCount');
  var cartLines = $('#cartLines');
  var cartEmpty = $('#cartEmpty');
  var cartTotal = $('#cartTotal');
  var goCheckout = $('#goCheckout');

  function render() {
    var ids = Object.keys(cart);

    if (cartCount) {
      cartCount.textContent = String(count());
      cartCount.hidden = count() === 0;
    }
    if (cartTotal) cartTotal.textContent = totalLabel();
    if (goCheckout) goCheckout.disabled = ids.length === 0;
    if (cartEmpty) cartEmpty.style.display = ids.length ? 'none' : 'block';
    if (!cartLines) return;

    cartLines.textContent = '';
    ids.forEach(function (id) {
      var item = CATALOGUE[id];

      var row = document.createElement('div');
      row.className = 'line-item';

      var left = document.createElement('div');
      var h = document.createElement('h4');
      h.textContent = item.name;
      var meta = document.createElement('p');
      meta.className = 'meta';
      meta.textContent = item.note;
      left.appendChild(h);
      left.appendChild(meta);

      var right = document.createElement('div');
      var price = document.createElement('p');
      price.className = 'price';
      price.textContent = priced(item, cart[id]);
      right.appendChild(price);

      var qty = document.createElement('div');
      qty.className = 'qty';
      var minus = document.createElement('button');
      minus.type = 'button';
      minus.textContent = '−';
      minus.setAttribute('aria-label', 'Remove one ' + item.name);
      var num = document.createElement('span');
      num.textContent = String(cart[id]);
      var plus = document.createElement('button');
      plus.type = 'button';
      plus.textContent = '+';
      plus.disabled = cart[id] >= (item.max || 99);
      plus.setAttribute('aria-label', 'Add one ' + item.name);
      minus.addEventListener('click', function () { change(id, -1); });
      plus.addEventListener('click', function () { change(id, 1); });
      qty.appendChild(minus); qty.appendChild(num); qty.appendChild(plus);
      right.appendChild(qty);

      row.appendChild(left);
      row.appendChild(right);
      cartLines.appendChild(row);
    });
  }

  function change(id, delta) {
    var item = CATALOGUE[id];
    if (!item) return;
    var cap = item.max || 99;
    cart[id] = (cart[id] || 0) + delta;
    if (cart[id] < 1) delete cart[id];
    else if (cart[id] > cap) cart[id] = cap;
    save(); render();
  }

  $$('[data-add]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      change(btn.getAttribute('data-add'), 1);
      openDrawer();
    });
  });

  /* -------------------------------------------------------- CART DRAWER */
  var drawer = $('#drawer');
  var backdrop = $('#drawerBackdrop');
  var cartView = $('#cartView');
  var checkoutForm = $('#checkoutForm');
  var confirmView = $('#confirmView');
  var drawerFoot = $('#drawerFoot');
  var lastFocus = null;

  function openDrawer() {
    if (!drawer) return;
    lastFocus = document.activeElement;
    drawer.classList.add('open');
    backdrop.classList.add('open');
    drawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    var close = $('#drawerClose');
    if (close) close.focus();
  }
  function closeDrawer() {
    if (!drawer) return;
    drawer.classList.remove('open');
    backdrop.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function showCart() {
    cartView.style.display = '';
    checkoutForm.style.display = 'none';
    confirmView.style.display = 'none';
    drawerFoot.style.display = '';
  }
  function showCheckout() {
    buildSummary();
    cartView.style.display = 'none';
    checkoutForm.style.display = '';
    confirmView.style.display = 'none';
    drawerFoot.style.display = 'none';
  }
  function showConfirm() {
    cartView.style.display = 'none';
    checkoutForm.style.display = 'none';
    confirmView.style.display = '';
    drawerFoot.style.display = 'none';
  }

  var cartOpen = $('#cartOpen');
  if (cartOpen) cartOpen.addEventListener('click', function () { showCart(); openDrawer(); });
  var drawerClose = $('#drawerClose');
  if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
  if (backdrop) backdrop.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer && drawer.classList.contains('open')) closeDrawer();
  });
  if (goCheckout) goCheckout.addEventListener('click', showCheckout);
  var backToCart = $('#backToCart');
  if (backToCart) backToCart.addEventListener('click', showCart);
  var confirmClose = $('#confirmClose');
  if (confirmClose) confirmClose.addEventListener('click', function () { showCart(); closeDrawer(); });

  /* ------------------------------------------------------ ORDER SUMMARY
     Built node by node with textContent. The summary echoes back what the
     customer typed, so nothing here is ever assembled as an HTML string. */
  function buildSummary() {
    var box = $('#orderSummary');
    if (!box) return;
    box.textContent = '';

    Object.keys(cart).forEach(function (id) {
      var item = CATALOGUE[id];
      var line = document.createElement('div');
      line.className = 'order-line';
      var left = document.createElement('span');
      left.textContent = item.name + ' × ' + cart[id];
      var right = document.createElement('span');
      right.textContent = priced(item, cart[id]);
      line.appendChild(left); line.appendChild(right);
      box.appendChild(line);
    });

    var totalLine = document.createElement('div');
    totalLine.className = 'order-line total';
    var tl = document.createElement('span');
    tl.textContent = 'Total';
    var tr = document.createElement('span');
    tr.textContent = totalLabel();
    totalLine.appendChild(tl); totalLine.appendChild(tr);
    box.appendChild(totalLine);
  }

  /* ------------------------------------------------------------ CHECKOUT */
  function orderText() {
    return Object.keys(cart).map(function (id) {
      return CATALOGUE[id].name + ' x' + cart[id] + ' (' + priced(CATALOGUE[id], cart[id]) + ')';
    }).join('\n');
  }

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

  if (checkoutForm) {
    checkoutForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      var errorBox = $('#checkoutError');
      var button = $('#placeOrder');
      if (!checkoutForm.checkValidity()) {
        errorBox.textContent = 'Please fill in your name and email.';
        errorBox.classList.add('show');
        return;
      }
      var data = new FormData(checkoutForm);
      data.append('order', orderText());
      data.append('total', totalLabel());
      data.append('_subject', 'Braincopia order');

      var ok = await post(FORMSPREE_ENDPOINT, data, errorBox, button, 'Sending…');
      if (!ok) return;                       // stay put and show the error
      cart = {}; save(); render();
      checkoutForm.reset();
      showConfirm();
    });
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

  render();
})();
