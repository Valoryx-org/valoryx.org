// Scroll-reveal
(function() {
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.remove('will-reveal');
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

  document.querySelectorAll('.reveal').forEach(function(el) {
    var rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      el.classList.add('visible');
    } else {
      el.classList.add('will-reveal');
    }
    observer.observe(el);
  });
})();

// Mobile navigation
const mobileToggle  = document.getElementById('mobileNavToggle');
const mobileOverlay = document.getElementById('mobileNavOverlay');
const mobilePanel   = document.getElementById('mobileNavPanel');
const mobileClose   = document.getElementById('mobileNavClose');

function openMobileNav()  { mobileOverlay.classList.add('active'); mobilePanel.classList.add('active'); document.body.style.overflow = 'hidden'; }
function closeMobileNav() { mobileOverlay.classList.remove('active'); mobilePanel.classList.remove('active'); document.body.style.overflow = ''; }

if (mobileToggle)  mobileToggle.addEventListener('click', openMobileNav);
if (mobileClose)   mobileClose.addEventListener('click', closeMobileNav);
if (mobileOverlay) mobileOverlay.addEventListener('click', closeMobileNav);
document.querySelectorAll('.mobile-nav-link').forEach(link => link.addEventListener('click', closeMobileNav));
document.addEventListener('keydown', function(e) { if (e.key === 'Escape' && mobilePanel && mobilePanel.classList.contains('active')) closeMobileNav(); });

// Sticky header
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    header.style.borderBottomColor = '#e8ecf0';
    header.style.background = 'rgba(255,255,255,0.95)';
  } else {
    header.style.borderBottomColor = 'transparent';
    header.style.background = 'rgba(255,255,255,0.9)';
  }
});

// Scroll to top
const scrollTopBtn = document.getElementById('scrollTop');
if (scrollTopBtn) {
  window.addEventListener('scroll', () => scrollTopBtn.classList.toggle('active', window.scrollY > 400));
  scrollTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// Active nav link
const sections = document.querySelectorAll('section[id]');
const navLinks  = document.querySelectorAll('nav a[href^="#"]');
function highlightNav() {
  const scrollY = window.scrollY + 100;
  sections.forEach(section => {
    if (scrollY >= section.offsetTop && scrollY < section.offsetTop + section.offsetHeight) {
      const id = section.getAttribute('id');
      navLinks.forEach(link => {
        link.classList.toggle('text-accent',  link.getAttribute('href') === '#' + id);
        link.classList.toggle('text-heading', link.getAttribute('href') !== '#' + id);
      });
    }
  });
}
window.addEventListener('scroll', highlightNav);

// FAQ toggle
function toggleFaq(item) {
  const wasActive = item.classList.contains('active');
  document.querySelectorAll('.faq-item').forEach(el => { el.classList.remove('active'); el.setAttribute('aria-expanded', 'false'); });
  if (!wasActive) { item.classList.add('active'); item.setAttribute('aria-expanded', 'true'); }
}

// Form submit
async function handleSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const btn  = form.querySelector('button');
  const webhook = form.dataset.webhook;
  const orig = btn.textContent;

  // Honeypot check — bots fill the hidden field
  if (form.website && form.website.value) return;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email.value)) {
    form.email.setCustomValidity('Please enter a valid email address');
    form.email.reportValidity();
    return;
  }
  form.email.setCustomValidity('');

  btn.textContent = '…';
  btn.disabled = true;

  try {
    const res = await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.name.value,
        email: form.email.value,
        role: form.role.value,
        message: form.message.value,
        source: 'landing-page'
      })
    });
    if (res.ok) {
      btn.textContent = '✓';
      btn.style.background = '#059652';
      form.reset();
    } else { throw new Error(); }
  } catch {
    btn.textContent = '✕';
    btn.style.background = '#dc2626';
  }
  setTimeout(() => { btn.textContent = orig; btn.style.background = ''; btn.disabled = false; }, 3000);
}

// OS tab switcher
function switchOsTab(os) {
  document.querySelectorAll('.os-tab').forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
  document.querySelectorAll('.os-tab-content').forEach(c => c.classList.remove('active'));
  const tab = document.querySelector(`.os-tab[data-os="${os}"]`);
  if (tab) { tab.classList.add('active'); tab.setAttribute('aria-selected', 'true'); }
  const panel = document.getElementById(`tab-${os}`);
  if (panel) {
    panel.classList.add('active');
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function copyCmd(text, btn) {
  navigator.clipboard.writeText(text).catch(() => {});
  const icon = btn.querySelector('i');
  if (icon) { icon.className = 'bi bi-check2 text-green-400'; setTimeout(() => { icon.className = 'bi bi-clipboard'; }, 1500); }
}

// Auto-detect OS on load
(function() {
  const ua = navigator.userAgent;
  let os = 'docker';
  if (/Win/i.test(ua))   os = 'windows';
  else if (/Mac/i.test(ua))   os = 'macos';
  else if (/Linux/i.test(ua)) os = 'linux';
  switchOsTab(os);
})();

// Language dropdown — click/touch support (hover alone fails on mobile)
(function() {
  const langBtn = document.querySelector('.lang-toggle');
  const langMenu = document.querySelector('.lang-menu');
  if (!langBtn || !langMenu) return;
  langBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    const open = langMenu.classList.toggle('lang-open');
    langBtn.setAttribute('aria-expanded', open);
  });
  document.addEventListener('click', function() { langMenu.classList.remove('lang-open'); langBtn.setAttribute('aria-expanded', 'false'); });
  document.addEventListener('keydown', function(e) { if (e.key === 'Escape') { langMenu.classList.remove('lang-open'); langBtn.setAttribute('aria-expanded', 'false'); } });
})();

// Smooth scroll with header offset
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const targetId = this.getAttribute('href');
    if (targetId === '#') return;
    const target = document.querySelector(targetId);
    if (target) {
      e.preventDefault();
      const headerHeight = document.getElementById('header').offsetHeight;
      window.scrollTo({ top: target.offsetTop - headerHeight - 10, behavior: 'smooth' });
    }
  });
});
