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
  var presetPick = null;
  var moved = false;

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
    if (presetPick) lines.push('Package: ' + presetPick);

    count.textContent = !lines.length ? 'Drag the slider to where you stand'
      : moved ? 'We think we know what that is. Tell us if we are wrong.'
      : 'Package chosen.';

    serviceField.value = lines.join('\n');
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
        presetPick = null;
        moved = false;
      } else {
        presetPick = (presetPick === name) ? null : name;
      }
      syncPicks();
    });
  });

  showStand();
  syncPicks();

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
