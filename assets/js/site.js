/* OneVision Lawns & Gardens — shared interactions */
(function () {
  'use strict';

  var header = document.querySelector('.site-header');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- header frost on scroll ---- */
  function onScroll() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 40);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- services mega-dropdown (hover on pointer devices, click everywhere) ---- */
  var dd = document.querySelector('.nav-dropdown');
  if (dd) {
    var trigger = dd.querySelector('.nav-trigger');
    var hoverCapable = window.matchMedia('(hover: hover)').matches;
    var open = function () { dd.classList.add('open'); trigger.setAttribute('aria-expanded', 'true'); };
    var close = function () { dd.classList.remove('open'); trigger.setAttribute('aria-expanded', 'false'); };
    if (hoverCapable) {
      dd.addEventListener('mouseenter', open);
      dd.addEventListener('mouseleave', close);
    }
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      dd.classList.contains('open') ? close() : open();
    });
    document.addEventListener('click', function (e) { if (!dd.contains(e.target)) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  /* ---- mobile nav ---- */
  var burger = document.querySelector('.nav-burger');
  var mobile = document.querySelector('.mobile-nav');
  if (burger && mobile) {
    var setMobile = function (isOpen) {
      mobile.classList.toggle('open', isOpen);
      burger.setAttribute('aria-expanded', String(isOpen));
      burger.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
      document.body.style.overflow = isOpen ? 'hidden' : '';
      if (header) header.classList.toggle('solid', isOpen);
    };
    burger.addEventListener('click', function () { setMobile(!mobile.classList.contains('open')); });
    mobile.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setMobile(false); }); });
    var acc = mobile.querySelector('.m-acc');
    if (acc) {
      acc.addEventListener('click', function () {
        var isOpen = acc.classList.toggle('open');
        acc.setAttribute('aria-expanded', String(isOpen));
      });
    }
    window.addEventListener('resize', function () { if (window.innerWidth > 960) setMobile(false); });
  }

  /* ---- reveal on scroll ---- */
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---- parallax (hero media + macro band), rAF throttled ----
     Heroes: offset grows with scroll from 0, so the photo always starts flush with the top.
     Band:   offset measured from the band's own container, never from the moving element. */
  var px = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  if (px.length && !reduce && window.matchMedia('(hover: hover) and (min-width: 961px)').matches) {
    var ticking = false;
    var update = function () {
      var vh = window.innerHeight, sy = window.scrollY;
      px.forEach(function (el) {
        var speed = parseFloat(el.getAttribute('data-parallax')) || 0.2;
        var host = el.closest('.hero, .page-hero, .band') || el.parentElement;
        var r = host.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var offset = host.classList.contains('band')
          ? (r.top + r.height / 2 - vh / 2) * speed
          : Math.max(0, -r.top) * speed;
        el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)';
      });
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  }

  /* ---- FAQ accordion ---- */
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var btn = item.querySelector('button');
    var panel = item.querySelector('.answer');
    if (!btn || !panel) return;
    btn.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      item.parentElement.querySelectorAll('.faq-item.open').forEach(function (o) {
        o.classList.remove('open');
        o.querySelector('button').setAttribute('aria-expanded', 'false');
        o.querySelector('.answer').style.maxHeight = null;
      });
      if (!isOpen) {
        item.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
        panel.style.maxHeight = panel.scrollHeight + 'px';
      }
    });
  });

  /* ---- quote forms: let the CRM tracking script see the submit, then go to the thank-you page ---- */
  var isFile = window.location.protocol === 'file:';
  function resolveTarget(t) {
    var u = new URL(t || 'thank-you/', window.location.href);
    if (isFile && /\/$/.test(u.pathname)) u = new URL(u.href + 'index.html');
    return u.href;
  }
  document.querySelectorAll('form.quote-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      // Capture phase: runs before any third-party submit listener and cannot be swallowed by one.
      e.preventDefault();
      var hp = form.querySelector('.hp input');
      if (hp && hp.value) return;
      if (!form.checkValidity()) { form.reportValidity(); return; }
      if (form.dataset.sending) return;
      form.dataset.sending = '1';
      form.classList.add('is-sending');
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      try {
        var data = {};
        new FormData(form).forEach(function (v, k) { data[k] = v; });
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({ event: 'quote_form_submit', form_id: form.id || 'quote-form', service_needed: data.service_needed || '' });
        try { sessionStorage.setItem('ov_last_enquiry', JSON.stringify(data)); } catch (err) {}
      } catch (err) {}
      var target = resolveTarget(form.getAttribute('data-redirect'));
      // Give the tracking script's own listener (it fires after this one) a beat to send its beacon.
      window.setTimeout(function () { window.location.assign(target); }, 500);
    }, true);
  });

  /* ---- opened straight from disk: make folder links land on their index.html ---- */
  if (isFile) {
    document.querySelectorAll('a[href]').forEach(function (a) {
      var h = a.getAttribute('href');
      if (!h || /^(https?:|mailto:|tel:|#)/.test(h)) return;
      var u = new URL(h, window.location.href);
      if (/\/$/.test(u.pathname)) a.setAttribute('href', u.pathname + 'index.html' + u.hash);
    });
  }

  /* ---- hero video: only play when it can, fall back to poster ---- */
  var v = document.querySelector('.hero__media video');
  if (v) {
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); }
    else { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  }

  /* ---- current year ---- */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();

/* ---------- Area map: hover sync, tooltip, region focus ---------- */
(function () {
  document.querySelectorAll('.areas-layout').forEach(function (wrap) {
    var map = wrap.querySelector('.area-map');
    if (!map) return;
    var tip = map.querySelector('.am-tip');
    var dots = {};
    map.querySelectorAll('.am-dot').forEach(function (d) { dots[d.getAttribute('data-suburb')] = d; });
    function hot(name, on) {
      var d = dots[name]; if (!d) return;
      d.classList.toggle('is-hot', on);
      if (tip) {
        if (on) {
          var c = d.querySelector('circle:last-of-type');
          var r = map.getBoundingClientRect(), b = c.getBoundingClientRect();
          tip.textContent = name;
          tip.style.left = (b.left - r.left + b.width / 2) + 'px';
          tip.style.top = (b.top - r.top) + 'px';
          tip.classList.add('show');
        } else tip.classList.remove('show');
      }
    }
    Object.keys(dots).forEach(function (name) {
      dots[name].addEventListener('mouseenter', function () { hot(name, true); });
      dots[name].addEventListener('mouseleave', function () { hot(name, false); });
    });
    wrap.querySelectorAll('[data-suburb-ref]').forEach(function (li) {
      li.addEventListener('mouseenter', function () { hot(li.getAttribute('data-suburb-ref'), true); });
      li.addEventListener('mouseleave', function () { hot(li.getAttribute('data-suburb-ref'), false); });
    });
    var cards = wrap.querySelectorAll('.region-card[data-region]');
    var btns = wrap.querySelectorAll('.am-legend button[data-region]');
    function focus(region) {
      map.classList.remove('am-focus-uns', 'am-focus-cc');
      if (region) map.classList.add('am-focus-' + region);
      cards.forEach(function (c) { c.classList.toggle('is-active', c.getAttribute('data-region') === region); });
      btns.forEach(function (b) { b.classList.toggle('is-active', b.getAttribute('data-region') === region); });
    }
    if (window.matchMedia('(hover: hover)').matches) {
      cards.forEach(function (c) {
        c.addEventListener('mouseenter', function () { focus(c.getAttribute('data-region')); });
        c.addEventListener('mouseleave', function () { focus(map.getAttribute('data-default-focus') || null); });
      });
    }
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var r = b.getAttribute('data-region');
        var already = map.classList.contains('am-focus-' + r);
        focus(already ? null : r);
      });
    });
  });
})();
