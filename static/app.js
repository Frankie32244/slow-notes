(() => {
  let saved;
  try { saved = new Set(JSON.parse(localStorage.getItem('slow-notes-saved') || '[]')); }
  catch { saved = new Set(); }
  let timer;
  document.querySelectorAll('.bookmark').forEach(button => {
    const update = () => {
      const active = saved.has(button.dataset.slug);
      button.setAttribute('aria-pressed', String(active));
      button.textContent = active ? '♥' : '♡';
      button.title = active ? '取消收藏' : '收藏文章';
    };
    update();
    button.addEventListener('click', () => {
      const slug = button.dataset.slug;
      saved.has(slug) ? saved.delete(slug) : saved.add(slug);
      update();
      let message = saved.has(slug) ? '已收藏，留给下次慢慢读。' : '已取消收藏';
      try { localStorage.setItem('slow-notes-saved', JSON.stringify([...saved])); }
      catch { message = '浏览器未允许存储，本次收藏仅在当前页面保留。'; }
      const toast = document.getElementById('toast');
      toast.textContent = message;
      toast.classList.add('show');
      clearTimeout(timer);
      timer = setTimeout(() => toast.classList.remove('show'), 2500);
    });
  });
})();
