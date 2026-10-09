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
// Tawk.to's own bubble, "We Are Here!" sign and greeting popup are hidden.
// Visitors use our own chat button instead (styled like the WhatsApp
// button), which opens the Tawk.to chat window. When the window is closed
// it disappears again, and a badge shows if an agent replies meanwhile.
(function () {
  var TAWK_SRC = 'https://embed.tawk.to/6ac442f3fda00134c81688f5/1k47ab2gt';

  var css = document.createElement('style');
  css.textContent =
    '.chat-float{position:fixed;right:28px;bottom:100px;z-index:200;width:58px;height:58px;border-radius:50%;' +
    'background:#143230;color:#EFEAE1;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;' +
    'box-shadow:0 10px 28px rgba(28,26,23,0.28);transition:transform .3s ease,background .3s ease;}' +
    '.chat-float:hover{background:#1d4744;transform:translateY(-3px);}' +
    '.chat-float svg{width:26px;height:26px;}' +
    '.chat-float .chat-tip{position:absolute;right:calc(100% + 14px);top:50%;transform:translateY(-50%);background:#1C1C1C;' +
    'color:#EFEAE1;font-size:12px;font-weight:600;letter-spacing:.04em;padding:8px 14px;border-radius:6px;white-space:nowrap;' +
    'opacity:0;pointer-events:none;transition:opacity .25s ease;font-family:Archivo,sans-serif;}' +
    '.chat-float:hover .chat-tip{opacity:1;}' +
    '.chat-float .chat-badge{position:absolute;top:-2px;right:-2px;min-width:20px;height:20px;padding:0 5px;border-radius:10px;' +
    'background:#B3261E;color:#fff;font-size:11px;font-weight:700;line-height:20px;text-align:center;display:none;font-family:Archivo,sans-serif;}' +
    '.chat-float.has-unread .chat-badge{display:block;}' +
    '.music-toggle{display:none !important;}' +
    '@media (max-width:640px){.chat-float{right:18px;bottom:82px;width:52px;height:52px;}.chat-float .chat-tip{display:none;}}';
  document.head.appendChild(css);

  window.Tawk_API = window.Tawk_API || {};
  window.Tawk_LoadStart = new Date();
  var api = window.Tawk_API;
  var btn = null;
  var ready = false;
  var wantOpen = false;

  var loaded = false;

  function openChat() {
    if (!ready) { wantOpen = true; loadChat(); return; }
    api.showWidget();
    api.maximize();
    if (btn) btn.classList.remove('has-unread');
  }

  api.onLoad = function () {
    ready = true;
    api.hideWidget();
    if (wantOpen) { wantOpen = false; openChat(); }
  };
  api.onChatMinimized = function () { api.hideWidget(); };
  // Safety net: if the chat window gets closed any other way, hide the
  // Tawk.to bubble again so only our button shows.
  setInterval(function () {
    if (ready && api.isChatMinimized && api.isChatMinimized() && !api.isChatHidden()) api.hideWidget();
  }, 700);
  api.onUnreadCountChanged = function (count) {
    if (!btn) return;
    btn.querySelector('.chat-badge').textContent = count;
    btn.classList.toggle('has-unread', count > 0);
  };

  function addButton() {
    if (document.querySelector('.chat-float')) return;
    btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'chat-float';
    btn.setAttribute('aria-label', 'Live chat with Sheena and Mike');
    btn.innerHTML =
      '<span class="chat-tip">Live chat</span>' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M21 12c0 4.4-4 8-9 8-1.5 0-2.9-.3-4.2-.9L3 20l1.2-3.9C3.4 14.9 3 13.5 3 12c0-4.4 4-8 9-8s9 3.6 9 8z"/>' +
      '<circle cx="8.5" cy="12" r=".6" fill="currentColor"/><circle cx="12" cy="12" r=".6" fill="currentColor"/>' +
      '<circle cx="15.5" cy="12" r=".6" fill="currentColor"/></svg>' +
      '<span class="chat-badge">0</span>';
    btn.addEventListener('click', openChat);
    document.body.appendChild(btn);
  }

  // Cookie consent: Tawk.to only loads on its own once the visitor has
  // accepted cookies (js/consent.js). If they haven't, it loads the moment
  // they click the chat button, since they've asked to chat.
  function loadChat() {
    if (loaded) return;
    loaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = TAWK_SRC;
    s.charset = 'UTF-8';
    s.setAttribute('crossorigin', '*');
    document.body.appendChild(s);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', addButton);
  else addButton();
  function consentOK() { return !window.SMConsent || window.SMConsent.allowed(); }
  function autoLoad() { if (consentOK()) loadChat(); }
  document.addEventListener('sm-consent-change', function (e) {
    if (e.detail && e.detail.value === 'granted') loadChat();
  });
  if (document.readyState === 'complete') autoLoad();
  else window.addEventListener('load', autoLoad);
})();
