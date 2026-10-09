/* S & M Realty - cookie consent (GDPR / UK GDPR / CCPA / PIPEDA)
 *
 * Loaded at the very top of <head> on every page, BEFORE Google Analytics
 * and the Meta Pixel, so their default consent state is set first.
 *
 * - Visitors in Europe (EU/EEA/UK/Switzerland, by device time zone):
 *   analytics, ad and chat cookies stay OFF until they click "Accept".
 * - Everyone else: on by default, with a "Decline" option (opt-out).
 *   A browser Global Privacy Control signal is treated as "Decline".
 * - The choice is remembered for 12 months; "Cookie settings" in the
 *   footer reopens the banner so it can be changed at any time.
 *
 * Other scripts can check window.SMConsent.allowed() and listen for the
 * 'sm-consent-change' event (used by the live chat, and later by maps).
 */
(function () {
  var KEY = 'sm-consent-v1';
  var MAX_AGE = 365 * 24 * 60 * 60 * 1000;

  var EU_EXTRA = ['Atlantic/Canary', 'Atlantic/Madeira', 'Atlantic/Azores', 'Atlantic/Reykjavik',
    'Atlantic/Faroe', 'Africa/Ceuta', 'Asia/Nicosia', 'Asia/Famagusta', 'America/Guadeloupe',
    'America/Martinique', 'America/Cayenne', 'America/St_Barthelemy', 'America/Marigot',
    'Indian/Reunion', 'Indian/Mayotte', 'Arctic/Longyearbyen'];

  function inEurope() {
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
      if (!tz) return true;
      return tz.indexOf('Europe/') === 0 || EU_EXTRA.indexOf(tz) !== -1;
    } catch (e) { return true; } // unknown -> be strict
  }

  function readStored() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return null;
      var o = JSON.parse(raw);
      if (!o || (o.v !== 'granted' && o.v !== 'denied')) return null;
      if (Date.now() - (o.t || 0) > MAX_AGE) return null;
      return o.v;
    } catch (e) { return null; }
  }

  var europe = inEurope();
  var gpc = !!(navigator.globalPrivacyControl);
  var stored = readStored();
  var state = stored || ((europe || gpc) ? 'denied' : 'granted');

  // ---- Google consent mode (must run before gtag('config')) ----
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  function gConsent(mode, v) {
    var s = v === 'granted' ? 'granted' : 'denied';
    window.gtag('consent', mode, {
      ad_storage: s, analytics_storage: s, ad_user_data: s, ad_personalization: s,
      functionality_storage: 'granted', security_storage: 'granted'
    });
  }
  gConsent('default', state);
  window.gtag('set', 'ads_data_redaction', state !== 'granted');

  function apply(v) {
    gConsent('update', v);
    window.gtag('set', 'ads_data_redaction', v !== 'granted');
    if (window.fbq) window.fbq('consent', v === 'granted' ? 'grant' : 'revoke');
  }

  function save(v) {
    state = v;
    try { localStorage.setItem(KEY, JSON.stringify({ v: v, t: Date.now() })); } catch (e) {}
    apply(v);
    try { document.dispatchEvent(new CustomEvent('sm-consent-change', { detail: { value: v } })); } catch (e) {}
  }

  window.SMConsent = {
    allowed: function () { return state === 'granted'; },
    europe: europe,
    open: function () { showBanner(true); }
  };

  // ---- Banner UI ----
  function base() {
    var s = document.querySelector('script[src*="consent.js"]');
    var src = s ? s.getAttribute('src') : 'js/consent.js';
    return src.replace(/js\/consent\.js.*$/, '');
  }

  function addStyles() {
    if (document.getElementById('sm-consent-css')) return;
    var css = document.createElement('style');
    css.id = 'sm-consent-css';
    css.textContent =
      '.sm-consent{position:fixed;left:20px;bottom:20px;z-index:400;max-width:400px;background:#143230;color:rgba(239,234,225,.88);' +
      'padding:20px 22px;font-family:Archivo,sans-serif;font-size:13px;line-height:1.55;box-shadow:0 10px 30px rgba(0,0,0,.3);' +
      'transition:opacity .35s ease,transform .35s ease;}' +
      '.sm-consent.out{opacity:0;transform:translateY(10px);}' +
      '.sm-consent h2{font-family:Cormorant,serif;font-weight:500;font-size:20px;color:#EFEAE1;margin:0 0 8px;}' +
      '.sm-consent p{margin:0 0 14px;}' +
      '.sm-consent a{color:#C9A979;text-decoration:underline;}' +
      '.sm-consent-btns{display:flex;gap:10px;flex-wrap:wrap;}' +
      '.sm-consent-btns button{flex:1;min-width:120px;font-family:Archivo,sans-serif;font-size:11px;font-weight:600;letter-spacing:.08em;' +
      'text-transform:uppercase;padding:11px 16px;cursor:pointer;border:1px solid rgba(239,234,225,.55);background:transparent;color:#EFEAE1;' +
      'transition:background .2s ease,color .2s ease,border-color .2s ease;}' +
      '.sm-consent-btns button:hover,.sm-consent-btns button:focus-visible{background:#9C8158;border-color:#9C8158;color:#1C1C1C;outline:none;}' +
      '.sm-consent-link{background:none;border:none;padding:0;font:inherit;color:inherit;cursor:pointer;text-decoration:underline;}' +
      '.sm-consent-link:hover{color:#C9A979;}' +
      '.cookie-notice{display:none !important;}' +
      '@media (max-width:640px){.sm-consent{left:12px;right:12px;bottom:12px;max-width:none;padding:18px;}}';
    document.head.appendChild(css);
  }

  var banner = null;
  function showBanner(force) {
    if (banner) return;
    addStyles();
    banner = document.createElement('div');
    banner.className = 'sm-consent';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Cookie preferences');
    banner.innerHTML =
      '<h2>Your privacy</h2>' +
      '<p>We use cookies for Google Analytics, the Meta Pixel (to measure our ads) and our live chat. ' +
      'You can accept or decline them. The site works either way. ' +
      '<a href="' + base() + 'privacy-policy.html#cookies">Privacy &amp; cookie policy</a></p>' +
      '<div class="sm-consent-btns">' +
      '<button type="button" data-v="denied">Decline</button>' +
      '<button type="button" data-v="granted">Accept</button>' +
      '</div>';
    document.body.appendChild(banner);
    banner.addEventListener('click', function (e) {
      var v = e.target && e.target.getAttribute && e.target.getAttribute('data-v');
      if (!v) return;
      save(v);
      var b = banner; banner = null;
      b.classList.add('out');
      setTimeout(function () { if (b.parentNode) b.parentNode.removeChild(b); }, 400);
    });
  }

  function addFooterLink() {
    var host = document.querySelector('.footer-bottom') || document.querySelector('footer .wrap');
    if (!host || host.querySelector('.sm-consent-link')) return;
    var span = document.createElement('span');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'sm-consent-link';
    btn.textContent = 'Cookie settings';
    btn.addEventListener('click', function () { showBanner(true); });
    if (host.classList.contains('footer-bottom')) { span.appendChild(btn); host.appendChild(span); }
    else { var p = document.createElement('p'); p.style.marginTop = '10px'; p.style.fontSize = '12px'; p.appendChild(btn); host.appendChild(p); }
  }

  function onReady() {
    addStyles();
    addFooterLink();
    if (!stored) showBanner(false);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', onReady);
  else onReady();
})();
