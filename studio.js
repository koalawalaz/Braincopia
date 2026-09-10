(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  $('#year').textContent = new Date().getFullYear();

  /* ----------------------------------------------------------- PROBLEMS
     One statement at a time, because this is a diagnosis rather than a
     shopping list. Whatever is chosen travels down to the brief along with
     any package, so nobody types out what they already clicked. */
  var probs = $$('.prob input');
  var presetInputs = [];
  var count = $('#pickCount');
  var serviceField = $('#bService');
  var presets = $$('.preset');
  var presetPick = null;

  function syncPicks() {
    var chosen = probs.filter(function (i) { return i.checked; }).map(function (i) { return i.value; });
    var lines = [];
    if (chosen.length) lines.push('Problem: ' + chosen[0]);
    if (presetPick) lines.push('Package: ' + presetPick);

    count.textContent = lines.length
      ? (chosen.length ? 'We think we know what that is. Tell us if we are wrong.' : 'Package chosen.')
      : 'Nothing chosen yet';

    serviceField.value = lines.join('\n');

    presets.forEach(function (btn) {
      var name = btn.getAttribute('data-name');
      btn.setAttribute('aria-pressed', name && name === presetPick ? 'true' : 'false');
    });
  }

  probs.forEach(function (i) { i.addEventListener('change', syncPicks); });

  presets.forEach(function (btn) {
    btn.setAttribute('aria-pressed', 'false');
    btn.addEventListener('click', function () {
      var name = btn.getAttribute('data-name');
      if (!name) {                               // Clear
        probs.forEach(function (i) { i.checked = false; });
        presetPick = null;
      } else {
        presetPick = (presetPick === name) ? null : name;
      }
      syncPicks();
    });
  });

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
