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
  // ===============================
  // SIKARIS searchable dropdown
  // Berlaku untuk semua elemen <select> pada form/list tanpa CDN/library eksternal.
  // Select asli tetap dipakai Django untuk submit value, UI ini hanya layer pencarian.
  // ===============================
  const closeAllSearchableSelects = (except = null) => {
    document.querySelectorAll('.sikaris-searchable-select.open').forEach(wrapper => {
      if (except && wrapper === except) return;
      wrapper.classList.remove('open');
      const button = wrapper.querySelector('.sikaris-select-display');
      if (button) button.setAttribute('aria-expanded', 'false');
    });
  };

  const normalizeText = (text) => (text || '')
    .toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();

  const initSearchableSelect = (select) => {
    if (!select || select.dataset.searchableInitialized === '1') return;
    if (select.multiple || Number(select.getAttribute('size') || 0) > 1) return;
    if (select.dataset.noSearch === 'true' || select.classList.contains('no-searchable')) return;

    select.dataset.searchableInitialized = '1';
    select.classList.add('sikaris-native-select');

    const wrapper = document.createElement('div');
    wrapper.className = 'sikaris-searchable-select';
    if (select.disabled) wrapper.classList.add('disabled');

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'sikaris-select-display';
    button.setAttribute('aria-haspopup', 'listbox');
    button.setAttribute('aria-expanded', 'false');

    const labelSpan = document.createElement('span');
    labelSpan.className = 'sikaris-select-current';
    const arrowSpan = document.createElement('span');
    arrowSpan.className = 'sikaris-select-arrow';
    arrowSpan.textContent = '⌄';
    button.appendChild(labelSpan);
    button.appendChild(arrowSpan);

    const panel = document.createElement('div');
    panel.className = 'sikaris-select-panel';

    const search = document.createElement('input');
    search.type = 'text';
    search.className = 'sikaris-select-search';
    search.placeholder = select.dataset.placeholder || 'Ketik untuk mencari...';
    search.autocomplete = 'off';

    const list = document.createElement('div');
    list.className = 'sikaris-select-options';
    list.setAttribute('role', 'listbox');

    const empty = document.createElement('div');
    empty.className = 'sikaris-select-empty';
    empty.textContent = 'Data tidak ditemukan';
    empty.style.display = 'none';

    panel.appendChild(search);
    panel.appendChild(list);
    panel.appendChild(empty);
    wrapper.appendChild(button);
    wrapper.appendChild(panel);

    select.insertAdjacentElement('afterend', wrapper);

    const getSelectedText = () => {
      const opt = select.options[select.selectedIndex];
      return opt ? opt.textContent.trim() : '---------';
    };

    const updateButton = () => {
      labelSpan.textContent = getSelectedText() || '---------';
      wrapper.classList.toggle('has-value', !!select.value);
      wrapper.classList.toggle('disabled', !!select.disabled);
    };

    const renderOptions = () => {
      list.innerHTML = '';
      Array.from(select.options).forEach((opt, index) => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'sikaris-select-option';
        item.setAttribute('role', 'option');
        item.dataset.value = opt.value;
        item.dataset.index = String(index);
        item.dataset.searchText = normalizeText(opt.textContent);
        item.textContent = opt.textContent.trim() || '---------';
        if (opt.disabled) item.disabled = true;
        if (opt.selected) item.classList.add('selected');
        item.addEventListener('click', () => {
          if (opt.disabled) return;
          select.selectedIndex = index;
          select.value = opt.value;
          select.dispatchEvent(new Event('change', { bubbles: true }));
          updateButton();
          closeAllSearchableSelects();
        });
        list.appendChild(item);
      });
    };

    const filterOptions = () => {
      const q = normalizeText(search.value);
      let visible = 0;
      list.querySelectorAll('.sikaris-select-option').forEach(item => {
        const show = !q || item.dataset.searchText.includes(q);
        item.style.display = show ? '' : 'none';
        if (show) visible += 1;
      });
      empty.style.display = visible ? 'none' : '';
    };

    const markSelected = () => {
      list.querySelectorAll('.sikaris-select-option').forEach(item => {
        item.classList.toggle('selected', item.dataset.value === select.value);
      });
    };

    button.addEventListener('click', (event) => {
      event.preventDefault();
      if (select.disabled) return;
      const willOpen = !wrapper.classList.contains('open');
      closeAllSearchableSelects(wrapper);
      wrapper.classList.toggle('open', willOpen);
      button.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      if (willOpen) {
        renderOptions();
        markSelected();
        search.value = '';
        filterOptions();
        setTimeout(() => search.focus(), 20);
      }
    });

    search.addEventListener('input', filterOptions);
    search.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeAllSearchableSelects();
        button.focus();
      }
      if (event.key === 'Enter') {
        event.preventDefault();
        const first = Array.from(list.querySelectorAll('.sikaris-select-option'))
          .find(item => item.style.display !== 'none' && !item.disabled);
        if (first) first.click();
      }
    });

    select.addEventListener('change', () => {
      updateButton();
      markSelected();
    });

    updateButton();
  };

  document.querySelectorAll('select').forEach(initSearchableSelect);

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.sikaris-searchable-select')) {
      closeAllSearchableSelects();
    }
  });

  // Jika ada form/field yang ditambahkan dinamis, tetap otomatis dijadikan searchable.
  const observer = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (!(node instanceof HTMLElement)) return;
        if (node.matches && node.matches('select')) initSearchableSelect(node);
        node.querySelectorAll && node.querySelectorAll('select').forEach(initSearchableSelect);
      });
    });
  });
  observer.observe(document.body, { childList: true, subtree: true });

});
