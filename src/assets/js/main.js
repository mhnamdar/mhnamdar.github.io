import { CosmicWeb } from './cosmic-web.js';

const ready = (fn) => document.readyState === 'loading'
  ? document.addEventListener('DOMContentLoaded', fn, { once: true })
  : fn();

ready(() => {
  const canvas = document.querySelector('#cosmic-web');
  if (canvas) new CosmicWeb(canvas);

  setupMobileMenu();
  setupTheme();
  setupReveal();
  setupTilt();
  setupParallax();
  setupBlogFilters();
  setupPrint();
  setupPageTransitions();
});

function setupMobileMenu() {
  const button = document.querySelector('.mobile-menu-button');
  const menu = document.querySelector('.mobile-menu');
  if (!button || !menu) return;
  button.addEventListener('click', () => {
    const open = menu.classList.toggle('is-open');
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  menu.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      menu.classList.remove('is-open');
      button.setAttribute('aria-expanded', 'false');
    }
  });
}

function setupTheme() {
  let saved = null;
  try { saved = localStorage.getItem('mhn-theme'); } catch (_) { /* opaque file origin */ }
  if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'theme-toggle';
  button.setAttribute('aria-label', 'Toggle light and dark theme');
  button.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  button.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('mhn-theme', next); } catch (_) { /* preview without storage */ }
  });
  document.body.append(button);
}

function setupReveal() {
  const items = [...document.querySelectorAll('.reveal')];
  if (!items.length) return;
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    items.forEach((el) => el.classList.add('is-visible'));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .08, rootMargin: '0px 0px -35px' });
  items.forEach((item, index) => {
    item.style.transitionDelay = `${Math.min(index % 4, 3) * 55}ms`;
    observer.observe(item);
  });
}

function setupTilt() {
  if (matchMedia('(pointer: coarse)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.tilt-card').forEach((card) => {
    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - .5;
      const y = (event.clientY - rect.top) / rect.height - .5;
      card.style.transform = `perspective(850px) rotateX(${-y * 3.5}deg) rotateY(${x * 4.5}deg) translateY(-2px)`;
    });
    card.addEventListener('pointerleave', () => { card.style.transform = ''; });
  });
}

function setupParallax() {
  const element = document.querySelector('[data-parallax]');
  if (!element || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const host = element.closest('.home-hero');
  host?.addEventListener('pointermove', (event) => {
    const rect = host.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - .5;
    const y = (event.clientY - rect.top) / rect.height - .5;
    element.style.translate = `${x * 7}px ${y * 5}px`;
  }, { passive: true });
  host?.addEventListener('pointerleave', () => { element.style.translate = ''; }, { passive: true });
}

function setupBlogFilters() {
  const buttons = [...document.querySelectorAll('[data-blog-filter]')];
  const cards = [...document.querySelectorAll('.blog-index-grid .blog-card')];
  if (!buttons.length || !cards.length) return;
  buttons.forEach((button) => button.addEventListener('click', () => {
    const category = button.dataset.blogFilter;
    buttons.forEach((item) => item.classList.toggle('is-active', item === button));
    cards.forEach((card) => {
      const visible = category === 'all' || card.dataset.category === category;
      card.classList.toggle('is-hidden', !visible);
    });
  }));
}

function setupPrint() {
  document.querySelector('[data-print-cv]')?.addEventListener('click', () => window.print());
}

function setupPageTransitions() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (!link || link.target === '_blank' || link.hasAttribute('download') || link.href.startsWith('mailto:')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || url.pathname === location.pathname && url.hash) return;
    event.preventDefault();
    document.body.animate([{ opacity: 1 }, { opacity: .22 }], { duration: 150, fill: 'forwards', easing: 'ease-out' });
    setTimeout(() => { location.href = link.href; }, 135);
  });
}
