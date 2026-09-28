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

  /* ---- parallax (hero media + macro band), rAF throttled ---- */
  var px = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  if (px.length && !reduce && window.matchMedia('(hover: hover)').matches) {
    var ticking = false;
    var update = function () {
      var vh = window.innerHeight;
      px.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var speed = parseFloat(el.getAttribute('data-parallax')) || 0.2;
        var offset = (r.top + r.height / 2 - vh / 2) * speed;
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

  /* ---- quote forms: let the CRM tracking script see the submit, then redirect ---- */
  document.querySelectorAll('form.quote-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.querySelector('.hp input') && form.querySelector('.hp input').value) return; // honeypot
      if (!form.checkValidity()) { form.reportValidity(); return; }
      form.classList.add('is-sending');
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.textContent = 'Sending…';
      try {
        var data = {};
        new FormData(form).forEach(function (v, k) { data[k] = v; });
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({ event: 'quote_form_submit', form_id: form.id || 'quote-form', service_needed: data.service_needed || '' });
        try { sessionStorage.setItem('ov_last_enquiry', JSON.stringify(data)); } catch (err) {}
      } catch (err) {}
      var target = form.getAttribute('data-redirect') || '/thank-you/';
      // Give the external tracking script's listener a beat to fire its beacon before we leave.
      window.setTimeout(function () { window.location.assign(target); }, 450);
    });
  });

  /* ---- hero video: only play when it can, fall back to poster ---- */
  var v = document.querySelector('.hero__media video');
  if (v) {
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); }
    else { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  }

  /* ---- current year ---- */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
