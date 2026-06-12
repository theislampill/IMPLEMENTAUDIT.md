(() => {
  document.documentElement.classList.add('js');
  const sideNav = document.querySelector('.side-nav');
  if (sideNav) {
    if (!sideNav.id) sideNav.id = 'docs-menu';
    let toggle = document.querySelector('.docs-menu-toggle');
    if (!toggle) {
      toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'docs-menu-toggle';
      toggle.textContent = 'Docs menu';
      sideNav.before(toggle);
    }
    toggle.setAttribute('aria-controls', sideNav.id);
    toggle.setAttribute('aria-expanded', sideNav.classList.contains('is-open') ? 'true' : 'false');
    toggle.addEventListener('click', () => {
      const open = !sideNav.classList.contains('is-open');
      sideNav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    const activeNavLink = sideNav.querySelector('a.active');
    if (activeNavLink && sideNav.scrollHeight > sideNav.clientHeight) {
      requestAnimationFrame(() => {
        const centered =
          activeNavLink.offsetTop -
          (sideNav.clientHeight / 2) +
          (activeNavLink.offsetHeight / 2);
        sideNav.scrollTop = Math.max(0, centered);
      });
    }
  }

  const spotlightCards = Array.from(document.querySelectorAll('.card-spotlight'));
  for (const card of spotlightCards) {
    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      card.classList.add('is-spotlight-active');
      card.style.setProperty('--mouse-x', `${x.toFixed(2)}%`);
      card.style.setProperty('--mouse-y', `${y.toFixed(2)}%`);
    });
    card.addEventListener('pointerleave', () => {
      card.classList.remove('is-spotlight-active');
      card.style.removeProperty('--mouse-x');
      card.style.removeProperty('--mouse-y');
    });
  }

  const magnetLinks = Array.from(document.querySelectorAll('.magnet-link'));
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const coarsePointer = window.matchMedia('(pointer: coarse)');
  if (magnetLinks.length && !reducedMotion.matches && !coarsePointer.matches) {
    const resetMagnet = (link) => {
      link.classList.remove('is-magnet-active');
      link.style.removeProperty('--magnet-x');
      link.style.removeProperty('--magnet-y');
    };
    const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
    const padding = 24;
    const strength = 36;
    window.addEventListener('pointermove', (event) => {
      for (const link of magnetLinks) {
        const rect = link.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const distX = Math.abs(centerX - event.clientX);
        const distY = Math.abs(centerY - event.clientY);
        if (distX < rect.width / 2 + padding && distY < rect.height / 2 + padding) {
          const x = clamp((event.clientX - centerX) / strength, -4, 4);
          const y = clamp((event.clientY - centerY) / strength, -4, 4);
          link.classList.add('is-magnet-active');
          link.style.setProperty('--magnet-x', `${x.toFixed(2)}px`);
          link.style.setProperty('--magnet-y', `${y.toFixed(2)}px`);
        } else {
          resetMagnet(link);
        }
      }
    }, { passive: true });
    window.addEventListener('pointerleave', () => {
      for (const link of magnetLinks) resetMagnet(link);
    });
    for (const link of magnetLinks) {
      link.addEventListener('blur', () => resetMagnet(link));
    }
  }

  const tocLinks = Array.from(document.querySelectorAll('.toc a[href^="#"], .mobile-toc a[href^="#"]'));
  if (!tocLinks.length) return;

  const entries = tocLinks
    .map((link) => {
      const id = decodeURIComponent(link.getAttribute('href').slice(1));
      return { link, target: document.getElementById(id) };
    })
    .filter((entry) => entry.target);

  if (!entries.length) return;

  const isVisible = (link) => !!(link.offsetWidth || link.offsetHeight || link.getClientRects().length);

  const setActiveEntry = (current) => {
    for (const entry of entries) {
      const active = entry.target === current.target && isVisible(entry.link);
      entry.link.classList.toggle('is-active', active);
      if (active) entry.link.setAttribute('aria-current', 'true');
      else entry.link.removeAttribute('aria-current');
    }
  };

  const setActive = () => {
    const anchor = Math.min(220, window.innerHeight * 0.32);
    let current = entries[0];

    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 8) {
      current = entries[entries.length - 1];
    } else {
      let closest = entries[0];
      let closestDistance = Number.POSITIVE_INFINITY;
      for (const entry of entries) {
        const distance = Math.abs(entry.target.getBoundingClientRect().top - anchor);
        if (distance < closestDistance) {
          closest = entry;
          closestDistance = distance;
        }
        if (entry.target.getBoundingClientRect().top <= anchor) current = entry;
      }
      if (current === entries[0] && entries[0].target.getBoundingClientRect().top > anchor) current = closest;
    }

    setActiveEntry(current);
  };

  for (const entry of entries) {
    entry.link.addEventListener('click', () => setActiveEntry(entry));
  }
  setActive();
  window.addEventListener('scroll', setActive, { passive: true });
  window.addEventListener('resize', setActive);
})();
