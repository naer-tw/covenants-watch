// AABE 自家人軟閘門 (pre-launch noindex 期間)
// 注意:純前端 gate,非真正驗證 — 僅阻擋偶遇訪客,API 不擋
(function () {
  var path = location.pathname;
  // 例外:登入頁本身 / API JSON / sitemap / robots / CNAME
  if (
    path.endsWith('/login.html') ||
    path.startsWith('/api/') ||
    /\/(sitemap\.xml|robots\.txt|llms\.txt|CNAME)$/.test(path)
  ) return;
  if (localStorage.getItem('aabe_insider_v1') === 'ok') return;
  // 未登入 → 轉登入頁,保留目標
  var rel = path.replace(/^\//, '') || 'index.html';
  var target = encodeURIComponent(rel + location.search + location.hash);
  // 計算 base 路徑(支援子目錄部署)
  var base = '';
  var depth = (path.match(/\//g) || []).length - 1;
  if (depth > 0) base = '../'.repeat(depth);
  location.replace(base + 'login.html?next=' + target);
})();
