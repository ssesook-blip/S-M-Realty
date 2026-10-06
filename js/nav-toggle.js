document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    var isOpen = links.classList.toggle('open');
    toggle.classList.toggle('open', isOpen);
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Close the menu after tapping a link, so navigating (or jumping to an
  // in-page anchor) doesn't leave the dropdown open underneath.
  links.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      links.classList.remove('open');
      toggle.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
});

// ---------- LIVE CHAT (Tawk.to) ----------
// Loaded after the page finishes so it never slows the site down.
// Bubble sits on the right, stacked above the music and WhatsApp buttons.
(function () {
  var TAWK_SRC = 'https://embed.tawk.to/6ac442f3fda00134c81688f5/1k47ab2gt';

  window.Tawk_API = window.Tawk_API || {};
  window.Tawk_LoadStart = new Date();
  window.Tawk_API.customStyle = {
    visibility: {
      desktop: { position: 'br', xOffset: 22, yOffset: 160 },
      mobile:  { position: 'br', xOffset: 12, yOffset: 136 }
    }
  };

  function loadChat() {
    var s = document.createElement('script');
    s.async = true;
    s.src = TAWK_SRC;
    s.charset = 'UTF-8';
    s.setAttribute('crossorigin', '*');
    document.body.appendChild(s);
  }
  if (document.readyState === 'complete') loadChat();
  else window.addEventListener('load', loadChat);
})();
