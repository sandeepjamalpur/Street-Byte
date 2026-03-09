/* StreetByte – main.js v2.0  */
'use strict';

/* ═══════════════════════════════════════
   PAGE LOADER
═══════════════════════════════════════ */
(function initLoader() {
  const loader = document.getElementById('page-loader');
  if (!loader) return;
  window.addEventListener('load', () => {
    setTimeout(() => loader.classList.add('done'), 300);
    setTimeout(() => loader.remove(), 900);
  });
})();

/* ═══════════════════════════════════════
   CURSOR GLOW TRAIL
═══════════════════════════════════════ */
(function initCursorGlow() {
  const glow = document.querySelector('.cursor-glow');
  if (!glow) return;
  let rx = 0, ry = 0;
  document.addEventListener('mousemove', e => {
    rx = e.clientX; ry = e.clientY;
  });
  function tick() {
    glow.style.left = rx + 'px';
    glow.style.top  = ry + 'px';
    requestAnimationFrame(tick);
  }
  tick();
})();

/* ═══════════════════════════════════════
   SCROLL REVEAL (IntersectionObserver)
═══════════════════════════════════════ */
(function initScrollReveal() {
  const targets = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
  if (!targets.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  targets.forEach(t => io.observe(t));
})();

/* ═══════════════════════════════════════
   COUNT-UP ANIMATION
═══════════════════════════════════════ */
function animateCountUp(el, target, duration = 1400, suffix = '') {
  let start = null;
  const startVal = 0;
  function step(ts) {
    if (!start) start = ts;
    const progress = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(startVal + (target - startVal) * ease) + suffix;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

(function initCountUp() {
  const els = document.querySelectorAll('[data-count]');
  if (!els.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = +el.dataset.count;
        const suffix = el.dataset.suffix || '';
        animateCountUp(el, target, 1400, suffix);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.5 });
  els.forEach(e => io.observe(e));
})();

/* ═══════════════════════════════════════
   NAVBAR SCROLL
═══════════════════════════════════════ */
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });
}

/* ═══════════════════════════════════════
   MOBILE NAV TOGGLE
═══════════════════════════════════════ */
(function initMobileNav() {
  const toggle = document.querySelector('.nav-toggle');
  const links  = document.querySelector('.nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', () => {
    links.classList.toggle('mobile-open');
    toggle.classList.toggle('active');
  });
  // Close on link click
  links.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => links.classList.remove('mobile-open'));
  });
})();

/* ═══════════════════════════════════════
   RIPPLE EFFECT ON BUTTONS
═══════════════════════════════════════ */
(function initRipple() {
  document.querySelectorAll('.btn-search, .btn-search-sm, .hero-cta, .page-btn, .page-num').forEach(btn => {
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.addEventListener('click', function(e) {
      const r = document.createElement('span');
      r.className = 'ripple-effect';
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height) * 2;
      r.style.width = r.style.height = size + 'px';
      r.style.left = (e.clientX - rect.left - size / 2) + 'px';
      r.style.top  = (e.clientY - rect.top  - size / 2) + 'px';
      this.appendChild(r);
      setTimeout(() => r.remove(), 600);
    });
  });
})();

/* ═══════════════════════════════════════
   SCORE BAR ANIMATION (Results Page)
═══════════════════════════════════════ */
function revealScoreBars() {
  const bars = document.querySelectorAll('.score-bar-fill[data-width]');
  if (!bars.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        bar.style.width = bar.dataset.width + '%';
        io.unobserve(bar);
      }
    });
  }, { threshold: 0.3 });
  bars.forEach(b => io.observe(b));
}

/* ═══════════════════════════════════════
   TOAST NOTIFICATION
═══════════════════════════════════════ */
function showToast(msg, type = 'info', duration = 3200) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add('show'));
  });
  setTimeout(() => toast.classList.remove('show'), duration);
}

/* ═══════════════════════════════════════
   TYPEWRITER EFFECT
═══════════════════════════════════════ */
function typewriter(el, words, speed = 90, pause = 1800) {
  if (!el) return;
  let wi = 0, ci = 0, deleting = false;
  function type() {
    const word = words[wi];
    if (!deleting) {
      el.textContent = word.slice(0, ci + 1);
      ci++;
      if (ci === word.length) {
        deleting = true;
        setTimeout(type, pause);
        return;
      }
    } else {
      el.textContent = word.slice(0, ci - 1);
      ci--;
      if (ci === 0) {
        deleting = false;
        wi = (wi + 1) % words.length;
      }
    }
    setTimeout(type, deleting ? speed / 2 : speed);
  }
  type();
}

/* ═══════════════════════════════════════
   BUDGET SLIDER (Home Page)
═══════════════════════════════════════ */
const budgetSlider  = document.getElementById('budget-slider');
const budgetDisplay = document.getElementById('budget-display');
if (budgetSlider && budgetDisplay) {
  function syncSlider() {
    const min = +budgetSlider.min, max = +budgetSlider.max, val = +budgetSlider.value;
    budgetDisplay.textContent = 'Rs ' + val;
    budgetSlider.style.setProperty('--val', ((val - min) / (max - min) * 100) + '%');
  }
  budgetSlider.addEventListener('input', syncSlider);
  syncSlider();
}

/* ═══════════════════════════════════════
   BUDGET SLIDER (Results Page)
═══════════════════════════════════════ */
const sliderR  = document.getElementById('budget-slider-r');
const displayR = document.getElementById('budget-display-r');
if (sliderR && displayR) {
  function syncSliderR() {
    const min = +sliderR.min, max = +sliderR.max, val = +sliderR.value;
    displayR.textContent = 'Rs ' + val;
    sliderR.style.setProperty('--val', ((val - min) / (max - min) * 100) + '%');
  }
  sliderR.addEventListener('input', syncSliderR);
  syncSliderR();
}

/* ═══════════════════════════════════════
   STAGGER CARDS ON LOAD
═══════════════════════════════════════ */
(function staggerCards() {
  document.querySelectorAll('.food-card, .city-card, .step-card, .tech-card, .preview-step').forEach((card, i) => {
    card.classList.add('reveal');
    card.style.transitionDelay = (i * 0.08) + 's';
  });
})();

/* ═══════════════════════════════════════
   SCORE BAR SHIMMER on hover
═══════════════════════════════════════ */
document.querySelectorAll('.food-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    const bar = card.querySelector('.score-bar-fill');
    if (bar && bar.dataset.width) bar.style.width = bar.dataset.width + '%';
  });
});

/* ═══════════════════════════════════════
   INIT TYPEWRITER (if element exists)
═══════════════════════════════════════ */
const twEl = document.getElementById('typewriter-word');
if (twEl) {
  typewriter(twEl, ['Street Food', 'Hidden Gems', 'Top Vendors', 'Local Flavours']);
}

/* ═══════════════════════════════════════
   INIT SCORE BARS
═══════════════════════════════════════ */
revealScoreBars();

/* ═══════════════════════════════════════
   SMOOTH ANCHOR SCROLL
═══════════════════════════════════════ */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});
