/* ═══════════════════════════════════════════════════════
   AI Travel Planner – Main JavaScript
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Navbar Scroll Effect ────────────────────────────
  const navbar = document.getElementById('mainNavbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
  }

  // ── Back to Top ─────────────────────────────────────
  const backToTopBtn = document.getElementById('backToTop');
  if (backToTopBtn) {
    window.addEventListener('scroll', () => {
      backToTopBtn.style.display = window.scrollY > 300 ? 'flex' : 'none';
    });
    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── Auto-dismiss Alerts ─────────────────────────────
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Counter Animation ───────────────────────────────
  const counters = document.querySelectorAll('[data-counter]');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => observer.observe(c));

  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-counter'));
    let current = 0;
    const increment = Math.ceil(target / 60);
    const timer = setInterval(() => {
      current = Math.min(current + increment, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 30);
  }

  // ── Favorite Toggle (AJAX) ──────────────────────────
  document.querySelectorAll('.btn-favorite').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.getAttribute('data-url');
      const icon = this.querySelector('i');
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');

      fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(r => r.json())
      .then(data => {
        if (data.is_favorited) {
          icon.classList.replace('far', 'fas');
          this.classList.add('text-danger');
        } else {
          icon.classList.replace('fas', 'far');
          this.classList.remove('text-danger');
        }
        showToast(data.message, data.is_favorited ? 'success' : 'info');
      })
      .catch(() => showToast('Error updating favorites', 'danger'));
    });
  });

  // ── Toast Notification ──────────────────────────────
  window.showToast = function (message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    const id = 'toast-' + Date.now();
    const icons = { success: 'check-circle', danger: 'exclamation-triangle', warning: 'exclamation-circle', info: 'info-circle' };
    const html = `
      <div id="${id}" class="toast align-items-center text-bg-${type} border-0 mb-2" role="alert">
        <div class="d-flex">
          <div class="toast-body">
            <i class="fas fa-${icons[type] || 'info-circle'} me-2"></i>${message}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    toastContainer.insertAdjacentHTML('beforeend', html);
    const toast = new bootstrap.Toast(document.getElementById(id), { delay: 4000 });
    toast.show();
    document.getElementById(id).addEventListener('hidden.bs.toast', () => {
      document.getElementById(id)?.remove();
    });
  };

  function createToastContainer() {
    const div = document.createElement('div');
    div.id = 'toastContainer';
    div.style.cssText = 'position:fixed;top:80px;right:20px;z-index:1100;min-width:280px';
    document.body.appendChild(div);
    return div;
  }

  // ── Image Preview on Upload ─────────────────────────
  document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {
    input.addEventListener('change', function () {
      const preview = document.getElementById(this.id + '-preview') ||
                      this.parentElement.querySelector('.img-preview');
      if (!preview || !this.files[0]) return;
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
      };
      reader.readAsDataURL(this.files[0]);
    });
  });

  // ── Form Validation Highlight ───────────────────────
  document.querySelectorAll('form.needs-validation').forEach(form => {
    form.addEventListener('submit', e => {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });

  // ── Confirm Delete Dialogs ──────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      const msg = this.getAttribute('data-confirm') || 'Are you sure you want to delete this?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ── Search Live Filter (Tables) ─────────────────────
  const searchInput = document.getElementById('tableSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('[data-searchable] tr:not(.header-row)').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── Tooltip Init ────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // ── Popover Init ────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
    new bootstrap.Popover(el);
  });

  // ── Mobile Touch Swipe for Cards ────────────────────
  let startX = 0;
  document.addEventListener('touchstart', e => startX = e.touches[0].clientX, { passive: true });

});

// ── AI Chat Widget ───────────────────────────────────
function initAiChat() {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('chatInput');
  const container = document.getElementById('chatContainer');
  const sessionId = document.getElementById('sessionId')?.value;

  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, 'user');
    input.value = '';
    input.disabled = true;

    const typingEl = appendTyping();

    try {
      const res = await fetch('/ai/chat/message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf(),
        },
        body: JSON.stringify({ message, session_id: sessionId }),
      });
      const data = await res.json();
      typingEl.remove();
      appendMessage(data.response || data.error || 'Something went wrong.', 'ai');
    } catch {
      typingEl.remove();
      appendMessage('Network error. Please try again.', 'ai');
    } finally {
      input.disabled = false;
      input.focus();
    }
  });

  function appendMessage(text, role) {
    const div = document.createElement('div');
    div.className = 'd-flex mb-3 ' + (role === 'user' ? 'justify-content-end' : 'justify-content-start');
    const bubble = document.createElement('div');
    bubble.className = role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai';
    bubble.innerHTML = text.replace(/\n/g, '<br>');
    div.appendChild(bubble);
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
  }

  function appendTyping() {
    const div = document.createElement('div');
    div.className = 'd-flex mb-3 justify-content-start';
    div.innerHTML = '<div class="chat-bubble-ai"><span class="typing-dots">●●●</span></div>';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
  }
}

function getCsrf() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

document.addEventListener('DOMContentLoaded', initAiChat);
