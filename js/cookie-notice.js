document.addEventListener('DOMContentLoaded', function () {
  var STORAGE_KEY = 'sm-cookie-notice-v2';

  var alreadySeen = false;
  try { alreadySeen = localStorage.getItem(STORAGE_KEY) === '1'; } catch (e) {}
  if (alreadySeen) return;

  var banner = document.createElement('div');
  banner.className = 'cookie-notice';
  banner.innerHTML =
    '<p>This site uses cookies for Google Analytics, the Meta Pixel and our live chat (Tawk.to), to understand how visitors use the site, measure our ads and let you chat with us. ' +
    '<a href="' + (window.location.pathname.includes('/properties/') ? '../' : '') + 'privacy-policy.html">Learn more</a></p>' +
    '<button type="button" class="cookie-notice-btn">Got it</button>';

  document.body.appendChild(banner);

  banner.querySelector('.cookie-notice-btn').addEventListener('click', function () {
    banner.classList.add('dismissed');
    try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
    setTimeout(function () { banner.remove(); }, 400);
  });
});
