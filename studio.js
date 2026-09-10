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
     Four multi-select dropdowns. Each button carries its own count so a
     closed panel still says what is inside it, and only one opens at a
     time so the row never turns into a stack. Everything chosen still
     travels down to the brief. */
  var picks = $$('.opt input');
  var count = $('#pickCount');
  var serviceField = $('#bService');
  var drops = $$('.drop');
  var presets = $$('.preset');

  function closeDrops(except) {
    drops.forEach(function (d) {
      if (d === except) return;
      $('.drop-btn', d).setAttribute('aria-expanded', 'false');
      $('.drop-panel', d).hidden = true;
    });
  }

  drops.forEach(function (d) {
    var btn = $('.drop-btn', d);
    var panel = $('.drop-panel', d);
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = btn.getAttribute('aria-expanded') === 'true';
      closeDrops(d);
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      panel.hidden = open;
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.drop')) closeDrops(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDrops(null);
  });

  function chosenValues() {
    return picks.filter(function (i) { return i.checked; }).map(function (i) { return i.value; });
  }

  function syncPicks() {
    var chosen = chosenValues();
    var n = chosen.length;

    if (!n) count.textContent = 'Nothing selected yet';
    else if (n >= 4) count.textContent = n + ' selected. That is a package-sized brief.';
    else count.textContent = n + (n === 1 ? ' thing selected' : ' things selected');

    serviceField.value = chosen.join('\n');

    drops.forEach(function (d) {
      var on = $$('input:checked', d).length;
      var tag = $('[data-count]', d);
      tag.textContent = on ? on + ' picked' : 'None';
      if (on) tag.setAttribute('data-on', '');
      else tag.removeAttribute('data-on');
    });

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
        picks.forEach(function (i) { if (wanted.indexOf(i.value) !== -1) i.checked = !on; });
      }
      syncPicks();
    });
  });

  picks.forEach(function (i) { i.addEventListener('change', syncPicks); });
  syncPicks();

  /* Choosing a discipline from the menu opens that dropdown. */
  $$('[data-open]').forEach(function (link) {
    link.addEventListener('click', function () {
      var d = document.getElementById(link.getAttribute('data-open'));
      if (d && d.classList.contains('drop')) {
        closeDrops(d);
        $('.drop-btn', d).setAttribute('aria-expanded', 'true');
        $('.drop-panel', d).hidden = false;
      }
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
