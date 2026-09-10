(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  $('#year').textContent = new Date().getFullYear();

  /* -------------------------------------------------------------- STAND
     One scale with three stops instead of a list. The slider is the whole
     control: every stop is a diagnosis, and whichever one is left showing
     travels down to the brief so nobody retypes what they already chose.
     Nothing reaches the brief until the visitor actually moves it, so a
     default position never puts words in their mouth. */
  var range = $('#standRange');
  var items = $$('.stand-item');
  var stops = $$('.stand-stop');
  var track = $('.stand-track');
  var panel = $('#standPanel');
  var count = $('#pickCount');
  var serviceField = $('#bService');
  var presets = $$('.preset');
  var detail = $('#presetDetail');
  var detailHead = $('#presetDetailHead');
  var detailList = $('#presetList');
  var presetPick = null;
  var presetBtn = null;
  var moved = false;

  /* A count of pieces is a price tag. The pieces themselves are the answer to
     what am I actually getting, so the chosen package opens and says. Built
     node by node rather than as markup, out of habit. */
  function showPieces() {
    detailList.textContent = '';
    if (!presetBtn) { detail.hidden = true; return; }

    var pieces = (presetBtn.getAttribute('data-pieces') || '').split('|');
    detail.hidden = false;
    detail.style.setProperty('--accent', presetBtn.style.getPropertyValue('--accent'));
    detailHead.textContent = presetPick + ' is ' + pieces.length + ' pieces';
    pieces.forEach(function (name) {
      var li = document.createElement('li');
      var span = document.createElement('span');
      span.textContent = name;
      li.appendChild(span);
      detailList.appendChild(li);
    });
  }

  function showStand() {
    var i = Math.min(items.length - 1, Math.max(0, parseInt(range.value, 10) || 0));
    var accent = items[i].style.getPropertyValue('--accent');

    items.forEach(function (el, n) {
      el.classList.toggle('on', n === i);
      el.setAttribute('aria-hidden', n === i ? 'false' : 'true');
    });
    stops.forEach(function (b, n) { b.setAttribute('aria-current', n === i ? 'true' : 'false'); });

    track.style.setProperty('--p', i / (items.length - 1));
    track.style.setProperty('--accent', accent);
    panel.style.setProperty('--accent', accent);
    stops[i].style.setProperty('--accent', accent);
    range.setAttribute('aria-valuetext', items[i].getAttribute('data-problem'));
  }

  function syncPicks() {
    var lines = [];
    if (moved) lines.push('Problem: ' + $('.stand-item.on').getAttribute('data-problem'));
    if (presetBtn) {
      lines.push('Package: ' + presetPick);
      (presetBtn.getAttribute('data-pieces') || '').split('|').forEach(function (name) {
        lines.push('  \u2022 ' + name);
      });
    }

    count.textContent = !lines.length ? 'Drag the slider to where you stand'
      : moved ? 'We think we know what that is. Tell us if we are wrong.'
      : 'Package chosen.';

    serviceField.value = lines.join('\n');
    serviceField.rows = Math.min(9, Math.max(2, lines.length));
    presets.forEach(function (btn) {
      var name = btn.getAttribute('data-name');
      btn.setAttribute('aria-pressed', name && name === presetPick ? 'true' : 'false');
    });
  }

  range.addEventListener('input', function () {
    moved = true;
    showStand();
    syncPicks();
  });

  stops.forEach(function (btn) {
    btn.addEventListener('click', function () {
      range.value = btn.getAttribute('data-i');
      moved = true;
      showStand();
      syncPicks();
    });
  });

  presets.forEach(function (btn) {
    btn.setAttribute('aria-pressed', 'false');
    btn.addEventListener('click', function () {
      var name = btn.getAttribute('data-name');
      if (!name) {                               // Clear
        presetPick = null; presetBtn = null;
        moved = false;
      } else if (presetPick === name) {           // Pressing it again closes it
        presetPick = null; presetBtn = null;
      } else {
        presetPick = name; presetBtn = btn;
      }
      showPieces();
      syncPicks();
    });
  });

  showStand();
  showPieces();
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
