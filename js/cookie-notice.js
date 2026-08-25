document.addEventListener('DOMContentLoaded', function () {
  var STORAGE_KEY = 'sm-cookie-notice-acknowledged';

  var alreadySeen = false;
  try { alreadySeen = localStorage.getItem(STORAGE_KEY) === '1'; } catch (e) {}
  if (alreadySeen) return;

  var banner = document.createElement('div');
  banner.className = 'cookie-notice';
  banner.innerHTML =
    '<p>This site uses your browser\'s local storage to remember a display preference (like Grid vs. List view). No advertising or tracking cookies are used. ' +
    '<a href="' + (window.location.pathname.includes('/properties/') ? '../' : '') + 'privacy-policy.html">Learn more</a></p>' +
    '<button type="button" class="cookie-notice-btn">Got it</button>';

  document.body.appendChild(banner);

  banner.querySelector('.cookie-notice-btn').addEventListener('click', function () {
    banner.classList.add('dismissed');
    try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
    setTimeout(function () { banner.remove(); }, 400);
  });
});
