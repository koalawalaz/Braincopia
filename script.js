/* ==========================================================================
   BRAINCOPIA — site behaviour. No dependencies, no build step.
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

  var CATALOGUE = {
    tricks: { name: 'The 29 Tricks',                 price: 0,  note: 'Digital · instant' },
    vol1:   { name: 'Vol. I — The Parallel Universe', price: 12, note: 'PDF · both covers' },
    book:   { name: 'Tripple CH',                     price: 12, note: 'Digital · instant' }
  };

  var COLLECTIONS = [
    'Vol. I — The Parallel Universe', 'Two covers, one price',
    'Tripple CH', 'The 29 Tricks', 'Wear Your Resistance',
    'Printed in Amman'
  ];

  var CHANTS = [
    'AI is not creative. You are.',
    'Nothing is siloed here.',
    'Your voice. Your edition.',
    'Comfort is not our business.',
    'Reality is only the starting point.',
    'We do not gatekeep perspectives.'
  ];

  var ROTATING_WORDS = ['parallel', 'surreal', 'restless', 'wide-awake', 'unfiled'];

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var money = function (n) { return n === 0 ? 'Free' : '$' + n; };

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

  /* ================================================================ CART */
  var STORE_KEY = 'braincopia.cart.v1';
  var cart = load();

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
  function total() {
    return Object.keys(cart).reduce(function (n, id) { return n + CATALOGUE[id].price * cart[id]; }, 0);
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
    if (cartTotal) cartTotal.textContent = money(total());
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
      price.textContent = money(item.price * cart[id]);
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
    if (!CATALOGUE[id]) return;
    cart[id] = (cart[id] || 0) + delta;
    if (cart[id] < 1) delete cart[id];
    if (cart[id] > 99) cart[id] = 99;
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
      right.textContent = money(item.price * cart[id]);
      line.appendChild(left); line.appendChild(right);
      box.appendChild(line);
    });

    var totalLine = document.createElement('div');
    totalLine.className = 'order-line total';
    var tl = document.createElement('span');
    tl.textContent = 'Total';
    var tr = document.createElement('span');
    tr.textContent = money(total());
    totalLine.appendChild(tl); totalLine.appendChild(tr);
    box.appendChild(totalLine);
  }

  /* ------------------------------------------------------------ CHECKOUT */
  function orderText() {
    return Object.keys(cart).map(function (id) {
      return CATALOGUE[id].name + ' x' + cart[id] + ' (' + money(CATALOGUE[id].price * cart[id]) + ')';
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
        errorBox.textContent = 'Please fill in your name, email and address.';
        errorBox.classList.add('show');
        return;
      }
      var data = new FormData(checkoutForm);
      data.append('order', orderText());
      data.append('total', money(total()));
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
