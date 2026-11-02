/* "Similar homes nearby" on property pages.
   Reads listings-index.json (rebuilt by the pipeline on every run, so it never
   shows a sold or removed listing) and picks the 3 closest matches by
   community, area, property type and price. */
(function () {
  var box = document.getElementById('similar-listings');
  if (!box || !window.fetch) return;
  var grid = box.querySelector('.similar-grid');
  var me = {
    slug: box.dataset.slug,
    city: box.dataset.city,
    sector: box.dataset.sector,
    community: box.dataset.community,
    type: box.dataset.type,
    price: parseFloat(box.dataset.price) || 0
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function score(l) {
    var s = 0;
    if (me.community && l.community === me.community) s += 4;
    if (me.sector && l.sector === me.sector) s += 2;
    if (me.city && l.city === me.city) s += 2;
    if (me.type && l.type === me.type) s += 1;
    if (me.price && l.price) {
      var diff = Math.abs(l.price - me.price) / me.price;
      if (diff <= 0.25) s += 3;
      else if (diff <= 0.5) s += 1.5;
      else if (diff > 1) s -= 2;
      s -= diff; // tie-break toward the closest price
    } else if (me.price && !l.price) {
      s -= 3; // prefer listings that show a price
    }
    return s;
  }

  fetch('../listings-index.json', { cache: 'no-cache' })
    .then(function (r) { return r.ok ? r.json() : []; })
    .then(function (all) {
      var picks = all
        .filter(function (l) { return l.slug !== me.slug && l.image; })
        .map(function (l) { return { l: l, s: score(l) }; })
        .filter(function (x) { return x.s > 1; })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, 3)
        .map(function (x) { return x.l; });
      if (picks.length < 2) return;

      grid.innerHTML = picks.map(function (l) {
        var meta = l.beds ? '<span>' + esc(l.beds) + ' Bed</span><span>' + esc(l.baths) + ' Bath</span>' : '';
        return '<a class="similar-card" href="' + esc(l.slug) + '.html">' +
          '<div class="similar-photo"><img src="' + esc(l.image) + '" alt="' + esc(l.title) + '" loading="lazy"></div>' +
          '<div class="similar-body">' +
            '<div class="similar-title">' + esc(l.title) + '</div>' +
            '<div class="similar-price">' + esc(l.price_label) + '</div>' +
            '<div class="similar-meta"><span>' + esc(l.location) + '</span>' + meta + '</div>' +
          '</div></a>';
      }).join('');
      box.hidden = false;
    })
    .catch(function () {});
})();
