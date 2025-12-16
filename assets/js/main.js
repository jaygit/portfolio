// Purpose: Theme toggle and simple pagination for server-rendered lists
// Initialize theme immediately (covers timing where DOMContentLoaded may already have fired)
(function () {
  try {
    var body = document.body || document.getElementsByTagName('body')[0];
    var current = localStorage.getItem('site-theme');
    if (current === 'dark' && body) body.classList.add('dark');
  } catch (e) {
    /* ignore localStorage errors */
  }
})();

document.addEventListener('DOMContentLoaded', function () {
  // Theme buttons (sun/moon)
  var body = document.body;
  var sun = document.getElementById('theme-sun');
  var moon = document.getElementById('theme-moon');

  function setTheme(mode) {
    if (!body) return;
    if (mode === 'dark') {
      body.classList.add('dark');
      try { localStorage.setItem('site-theme', 'dark'); } catch (err) {}
    } else {
      body.classList.remove('dark');
      try { localStorage.setItem('site-theme', 'light'); } catch (err) {}
    }
    // update active states
    if (sun) sun.classList.toggle('active', mode !== 'dark');
    if (moon) moon.classList.toggle('active', mode === 'dark');
  }

  // initialize buttons state
  try {
    var cur = localStorage.getItem('site-theme') || (body.classList.contains('dark') ? 'dark' : 'light');
    setTheme(cur);
  } catch (err) {
    setTheme(body.classList.contains('dark') ? 'dark' : 'light');
  }

  if (sun) sun.addEventListener('click', function () { setTheme('light'); });
  if (moon) moon.addEventListener('click', function () { setTheme('dark'); });


  // Pagination for each project list
  function setupPagination(listEl) {
    var items = Array.from(listEl.querySelectorAll('li'));
    var pageSize = parseInt(listEl.dataset.pageSize || '6', 10);
    var total = items.length;
    var totalPages = Math.max(1, Math.ceil(total / pageSize));
    var className = listEl.dataset.class || '';
    var pager = document.querySelector('.pager[data-class="' + className + '"]');

    function showPage(page) {
      var start = (page - 1) * pageSize;
      var end = start + pageSize;
      items.forEach(function (li, idx) {
        li.style.display = (idx >= start && idx < end) ? '' : 'none';
      });
      if (pager) renderPager(page);
    }

    function renderPager(active) {
      if (!pager) return;
      pager.innerHTML = '';
      if (totalPages <= 1) return;
      var prev = document.createElement('button');
      prev.textContent = '◀';
      prev.disabled = active === 1;
      prev.onclick = function () { showPage(Math.max(1, active - 1)); };
      pager.appendChild(prev);

      for (var p = 1; p <= totalPages; p++) {
        (function (pp) {
          var btn = document.createElement('button');
          btn.textContent = pp;
          if (pp === active) btn.className = 'active';
          btn.onclick = function () { showPage(pp); };
          pager.appendChild(btn);
        })(p);
      }

      var next = document.createElement('button');
      next.textContent = '▶';
      next.disabled = active === totalPages;
      next.onclick = function () { showPage(Math.min(totalPages, active + 1)); };
      pager.appendChild(next);
    }

    // initialize at page 1
    showPage(1);
  }

  document.querySelectorAll('.project-list').forEach(function (ul) {
    setupPagination(ul);
  });

  // Scroll hint: detect scrollable `.proj-meta` areas and update hint state
  function updateMetaState(meta) {
    var isScrollable = meta.scrollHeight > meta.clientHeight + 1;
    meta.classList.toggle('is-scrollable', isScrollable);
    meta.classList.toggle('can-scroll-up', meta.scrollTop > 2);
    meta.classList.toggle('can-scroll-down', meta.scrollTop + meta.clientHeight < meta.scrollHeight - 2);
  }

  function initScrollHints() {
    var metas = Array.from(document.querySelectorAll('.proj-meta'));
    metas.forEach(function (meta) {
      updateMetaState(meta);
      meta.addEventListener('scroll', function () { updateMetaState(meta); });
      // Recompute on resize just in case
      window.addEventListener('resize', function () { updateMetaState(meta); });
    });
  }

  initScrollHints();
});
