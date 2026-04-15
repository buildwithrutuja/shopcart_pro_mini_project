// ShopCart Pro — main.js v3.0

document.addEventListener('DOMContentLoaded', function () {

  // ── THEME (Dark / Light) ──────────────────────────────
  var html    = document.documentElement;
  var toggle  = document.getElementById('themeToggle');
  var label   = document.getElementById('theme-label');
  var saved   = localStorage.getItem('scp-theme') || 'light';
  applyTheme(saved);

  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('scp-theme', next);
    });
  }

  function applyTheme(t) {
    html.setAttribute('data-theme', t);
    if (label) label.textContent = t === 'dark' ? '🌙 Dark' : '☀️ Light';
    // Fix Bootstrap components for dark mode
    if (t === 'dark') {
      document.querySelectorAll('.form-control,.form-select,.coupon-input').forEach(function(el){
        el.style.colorScheme = 'dark';
      });
    }
  }

  // ── AUTO-DISMISS ALERTS ───────────────────────────────
  setTimeout(function () {
    document.querySelectorAll('.alert-dismissible').forEach(function (a) {
      try { bootstrap.Alert.getOrCreateInstance(a).close(); } catch(e) {}
    });
  }, 5000);

  // ── NAVBAR SCROLL SHADOW ──────────────────────────────
  var nav = document.querySelector('.navbar');
  window.addEventListener('scroll', function () {
    if (nav) {
      nav.style.boxShadow = window.scrollY > 20
        ? '0 4px 28px rgba(0,0,0,0.35)' : 'none';
    }
  });

  // ── SCROLL REVEAL ─────────────────────────────────────
  var io = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.product-card, .stat-card, .feature-badge, .cart-item-card').forEach(function(el) {
    el.style.opacity    = '0';
    el.style.transform  = 'translateY(18px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    io.observe(el);
  });

  // ── ADD-TO-CART BUTTON ANIMATION ──────────────────────
  document.querySelectorAll('.add-cart-btn').forEach(function(btn) {
    btn.addEventListener('click', function () {
      btn.style.transform = 'scale(0.82) rotate(-8deg)';
      setTimeout(function() { btn.style.transform = ''; }, 280);
    });
  });

  // ── COUPON CODE COPY (data-copy attr) ─────────────────
  document.querySelectorAll('[data-copy]').forEach(function(el) {
    el.addEventListener('click', function () {
      var code = el.getAttribute('data-copy');
      if (navigator.clipboard) navigator.clipboard.writeText(code);
      showToast('Copied: ' + code);
    });
  });

  // ── TOOLTIPS ──────────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
    new bootstrap.Tooltip(el);
  });

  // ── IMG ERROR FALLBACK ────────────────────────────────
  document.querySelectorAll('img').forEach(function(img) {
    img.addEventListener('error', function () {
      if (!img.dataset.errored) {
        img.dataset.errored = '1';
        img.style.display = 'none';
      }
    });
  });

  // ── GLOBAL TOAST ──────────────────────────────────────
  window.showToast = function (msg) {
    var t = document.getElementById('siteToast') || document.getElementById('globalToast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'siteToast';
      t.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:#0f2027;color:white;padding:11px 22px;border-radius:12px;font-size:0.86rem;font-weight:500;z-index:9999;opacity:0;transition:all 0.38s;box-shadow:0 20px 60px rgba(0,0,0,0.4);border:1px solid rgba(16,185,129,0.3);white-space:nowrap;';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    t.style.transform = 'translateX(-50%) translateY(0)';
    clearTimeout(t._t);
    t._t = setTimeout(function () {
      t.style.opacity = '0';
      t.style.transform = 'translateX(-50%) translateY(80px)';
    }, 2800);
  };

});
