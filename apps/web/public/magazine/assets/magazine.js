(function() {
  const years = [];
  for (let y = 1958; y <= 2024; y++) years.push(y);
  const base = window.location.pathname.replace(/\/?index\.html$/, '').replace(/\/$/, '') || '.';
  const grid = document.getElementById('year-grid');
  years.forEach(function(year) {
    const a = document.createElement('a');
    a.className = 'year-card';
    a.href = base + '/' + year + '.html';
    a.textContent = year;
    grid.appendChild(a);
  });
})();
