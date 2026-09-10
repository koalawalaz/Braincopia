(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  $('#year').textContent = new Date().getFullYear();

  /* ------------------------------------------------------ SERVICES MENU */
  var trigger = $('#svcTrigger');
  var menu = $('#svcMenu');

  function closeMenu() {
    menu.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
  }
  trigger.addEventListener('click', function (e) {
    e.stopPropagation();
    var open = trigger.getAttribute('aria-expanded') === 'true';
    menu.hidden = open;
    trigger.setAttribute('aria-expanded', open ? 'false' : 'true');
  });
  document.addEventListener('click', function (e) {
    if (!menu.hidden && !menu.contains(e.target) && e.target !== trigger) closeMenu();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !menu.hidden) { closeMenu(); trigger.focus(); }
  });

  /* ------------------------------------------------------------- PICKER
     Every choice made up here is carried down to the brief, so nobody has
     to type out what they already clicked. */
  var picks = $$('.pick input');
  var count = $('#pickCount');
  var serviceField = $('#bService');

  var presets = $$('.preset');

  function chosenValues() {
    return picks.filter(function (i) { return i.checked; }).map(function (i) { return i.value; });
  }

  function syncPicks() {
    var chosen = chosenValues();
    var n = chosen.length;

    /* The bar says what the selection has become, not just how many boxes are
       ticked. Four or more is a package-sized brief and worth saying so. */
    if (!n) count.textContent = 'Nothing selected yet';
    else if (n >= 4) count.textContent = n + ' selected. That is a package-sized brief.';
    else count.textContent = n + (n === 1 ? ' thing selected' : ' things selected');

    serviceField.value = chosen.join('\n');

    /* A preset reads as on only while everything in it is still ticked. */
    presets.forEach(function (btn) {
      var want = btn.getAttribute('data-preset');
      if (!want) return;
      var all = want.split('|').every(function (v) { return chosen.indexOf(v) !== -1; });
      btn.setAttribute('aria-pressed', all ? 'true' : 'false');
    });
  }

  presets.forEach(function (btn) {
    btn.setAttribute('aria-pressed', 'false');
    btn.addEventListener('click', function () {
      var want = btn.getAttribute('data-preset');
      if (!want) {
        picks.forEach(function (i) { i.checked = false; });
      } else {
        var wanted = want.split('|');
        var on = btn.getAttribute('aria-pressed') === 'true';
        picks.forEach(function (i) {
          if (wanted.indexOf(i.value) !== -1) i.checked = !on;
        });
      }
      syncPicks();
    });
  });

  picks.forEach(function (i) { i.addEventListener('change', syncPicks); });
  syncPicks();

  /* Choosing a discipline from the menu should land you on that group. */
  $$('[data-open]').forEach(function (link) {
    link.addEventListener('click', function () {
      closeMenu();
      $('#mobileNav').classList.remove('open');
      $('#menuToggle').setAttribute('aria-expanded', 'false');
    });
  });

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
