document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('toggleSidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  }

  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    if (href === '/' && path === '/') link.classList.add('active');
    else if (href !== '/' && path.startsWith(href)) link.classList.add('active');
  });

  document.querySelectorAll('[data-table-search]').forEach(input => {
    const target = document.querySelector(input.dataset.tableSearch);
    if (!target) return;
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase().trim();
      target.querySelectorAll('tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  });

  const animateCounter = (el, target) => {
    let current = 0;
    const total = Number(target || 0);
    const step = Math.max(1, Math.ceil(total / 24));
    const timer = setInterval(() => {
      current += step;
      if (current >= total) {
        current = total;
        clearInterval(timer);
      }
      el.textContent = current;
    }, 20);
  };

  document.querySelectorAll('[data-counter]').forEach(el => {
    animateCounter(el, el.textContent);
  });

  const liveDashboard = document.querySelector('[data-dashboard-live]');
  if (liveDashboard) {
    fetch('/api/dashboard-stats/')
      .then(r => r.json())
      .then(data => {
        Object.entries(data).forEach(([key, value]) => {
          document.querySelectorAll(`[data-stat="${key}"]`).forEach(el => {
            el.textContent = 0;
            animateCounter(el, value);
          });
        });
      })
      .catch(() => {});
  }
});
