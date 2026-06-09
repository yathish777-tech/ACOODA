// ─── ACOODA Main JS ────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar Toggle (mobile) ──────────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    // Close sidebar on outside click
    document.addEventListener('click', function (e) {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Landing Nav: scroll effect ────────────────────────
  const landingNav = document.getElementById('landingNav');
  if (landingNav) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 60) {
        landingNav.classList.add('scrolled');
      } else {
        landingNav.classList.remove('scrolled');
      }
    });
  }

  // ── Landing Nav: mobile toggle ────────────────────────
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });
    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  // ── Smooth Scroll for anchor links ───────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Auto-dismiss alerts ───────────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    if (!alert.querySelector('.alert-close')) {
      setTimeout(() => {
        alert.style.transition = 'opacity .4s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 400);
      }, 5000);
    }
  });

  // ── Drag & Drop for file upload ───────────────────────
  const fileUploadArea = document.getElementById('fileUploadArea');
  if (fileUploadArea) {
    ['dragover', 'dragenter'].forEach(evt => {
      fileUploadArea.addEventListener(evt, function (e) {
        e.preventDefault();
        fileUploadArea.style.borderColor = 'var(--primary)';
        fileUploadArea.style.background = 'rgba(30,58,95,.04)';
      });
    });
    ['dragleave', 'drop'].forEach(evt => {
      fileUploadArea.addEventListener(evt, function (e) {
        fileUploadArea.style.borderColor = '';
        fileUploadArea.style.background = '';
      });
    });
    fileUploadArea.addEventListener('drop', function (e) {
      e.preventDefault();
      const files = e.dataTransfer.files;
      const fileInput = document.getElementById('documentFile');
      if (fileInput && files.length) {
        fileInput.files = files;
        fileInput.dispatchEvent(new Event('change'));
      }
    });
  }

  // ── Active nav item highlight ─────────────────────────
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href && path.startsWith(href) && href !== '/') {
      item.classList.add('active');
    }
  });

  // ── Role-option radio visual ──────────────────────────
  document.querySelectorAll('.role-option input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function () {
      document.querySelectorAll('.role-option').forEach(opt => {
        opt.style.borderColor = '';
        opt.style.background = '';
        opt.style.color = '';
      });
      if (this.checked) {
        const label = this.closest('.role-option');
        label.style.borderColor = 'var(--primary)';
        label.style.background = 'rgba(30,58,95,.06)';
        label.style.color = 'var(--primary)';
      }
    });
  });

  // ── Confirm forms ─────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  console.log('✅ ACOODA JS loaded');
});
