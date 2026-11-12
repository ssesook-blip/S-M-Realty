/* Property-page viewing request form -> Formspree (same endpoint as the homepage valuation form).
   Each submission carries the property name, code, price and page URL as hidden fields.
   If the visitor ticks "send me new listings", they are also added to the
   MailerLite "New Listings Updates" group. */
(function () {
  var ML_LISTINGS_ENDPOINT = 'https://assets.mailerlite.com/jsonp/2788039/forms/203866432118720453/subscribe';

  var form = document.getElementById('property-enquiry');
  if (!form) return;
  var status = form.querySelector('.enquiry-status');
  var button = form.querySelector('button[type="submit"]');

  function say(msg, isError) {
    status.textContent = msg;
    status.classList.toggle('is-error', !!isError);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = form.elements.name.value.trim();
    var email = form.elements.email.value.trim();
    if (!name || !email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      say('Please enter your name and a valid email address.', true);
      return;
    }
    var optin = form.elements.email_updates;
    var wantsListings = !!(optin && optin.checked);
    var original = button.textContent;
    button.disabled = true;
    button.textContent = 'Sending…';
    say('');

    fetch('https://formspree.io/f/xdenwkrj', {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    })
      .then(function (r) {
        if (!r.ok) throw new Error('bad status');
        if (wantsListings) {
          var d = new FormData();
          d.append('fields[email]', email);
          d.append('ml-submit', '1');
          d.append('anticsrf', 'true');
          fetch(ML_LISTINGS_ENDPOINT, { method: 'POST', body: d }).catch(function () {});
        }
        form.reset();
        button.textContent = 'Sent';
        say('Thank you. We have your request and will be in touch shortly.');
        if (window.fbq) { try { fbq('track', 'Lead', { content_name: form.elements.property.value }); } catch (err) {} }
      })
      .catch(function () {
        button.disabled = false;
        button.textContent = original;
        say('Something went wrong sending your request. Please try again, or message us on WhatsApp.', true);
      });
  });
})();

/* Free Buyer's Guide signup box, added to every property page just above
   the viewing request form. Signups go to Formspree (email alert to Sheena
   and Mike) and to the MailerLite "Buyer's Guide Leads" group, which starts
   the 6-email welcome series. */
(function () {
  var FORM_ENDPOINT = 'https://formspree.io/f/xdenwkrj';
  var ML_GUIDE_ENDPOINT = 'https://assets.mailerlite.com/jsonp/2788039/forms/203866275742483518/subscribe';
  var ML_LISTINGS_ENDPOINT = 'https://assets.mailerlite.com/jsonp/2788039/forms/203866432118720453/subscribe';
  var PDF_URL = '../Sosua_Cabarete_DR_Buyers_Guide.pdf';

  var enquire = document.getElementById('enquire');
  if (!enquire || document.getElementById('guide-cta')) return;

  var css =
    '.guide-cta{margin:56px 0 0;padding:32px 24px;background:#143230;color:#EFEAE1;display:grid;grid-template-columns:1fr;gap:22px;align-items:center}' +
    '@media(min-width:820px){.guide-cta{grid-template-columns:1.1fr 1fr;padding:40px 44px;gap:40px}}' +
    '.guide-cta .eyebrow{color:#C9B48F;font-size:12px;letter-spacing:.14em;text-transform:uppercase}' +
    '.guide-cta h2{font-family:Cormorant,serif;font-size:30px;line-height:1.15;margin:8px 0 10px;color:#EFEAE1;font-weight:500}' +
    '.guide-cta p{margin:0;font-size:15px;line-height:1.6;color:rgba(239,234,225,.82)}' +
    '.guide-cta form{display:flex;flex-wrap:wrap;gap:10px}' +
    '.guide-cta input[type=email]{flex:1 1 220px;min-width:0;padding:13px 14px;border:1px solid rgba(239,234,225,.35);background:#EFEAE1;color:#1C1C1C;font:15px Archivo,sans-serif;border-radius:0}' +
    '.guide-cta button{padding:13px 22px;border:1px solid #C9B48F;background:#C9B48F;color:#143230;font:600 12.5px Archivo,sans-serif;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;border-radius:0}' +
    '.guide-cta button:disabled{opacity:.7;cursor:default}' +
    '.guide-cta label.gc-optin{flex-basis:100%;display:flex;gap:9px;align-items:flex-start;font-size:13px;line-height:1.5;color:rgba(239,234,225,.75);cursor:pointer}' +
    '.guide-cta label.gc-optin input{margin:2px 0 0;width:15px;height:15px;flex:none}' +
    '.guide-cta .gc-fine{flex-basis:100%;font-size:12px;color:rgba(239,234,225,.6)}' +
    '.guide-cta .gc-fine a{color:#C9B48F;text-decoration:underline}' +
    '.guide-cta .gc-status{flex-basis:100%;font-size:13px;min-height:18px;color:#F2B8B5}' +
    '.guide-cta a.gc-open{display:inline-block;padding:13px 22px;background:#C9B48F;color:#143230;font:600 12.5px Archivo,sans-serif;letter-spacing:.08em;text-transform:uppercase;text-decoration:none}' +
    '@media print{.guide-cta{display:none!important}}';
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var box = document.createElement('div');
  box.className = 'guide-cta';
  box.id = 'guide-cta';
  box.innerHTML =
    '<div>' +
      '<span class="eyebrow">Free 2026 Buyer\'s Guide</span>' +
      '<h2>Buying on the North Coast? Start here.</h2>' +
      '<p>Closing costs, taxes, owner financing, residency and a full pre-purchase checklist for Sosúa, Cabarete and Puerto Plata, written by a Canadian family who lives here.</p>' +
    '</div>' +
    '<form id="guide-cta-form" novalidate>' +
      '<label for="guide-cta-email" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Email address</label>' +
      '<input type="email" id="guide-cta-email" name="email" placeholder="you@email.com" autocomplete="email" required>' +
      '<button type="submit">Get the Guide</button>' +
      '<label class="gc-optin"><input type="checkbox" id="guide-cta-optin" value="yes"> Also send me new listings and market updates by email. I can unsubscribe at any time.</label>' +
      '<span class="gc-fine">The guide opens right away, and we\'ll send you a few short buying tips over the next month. Unsubscribe any time. See our <a href="../privacy-policy.html">Privacy Policy</a>.</span>' +
      '<span class="gc-status" role="status" aria-live="polite"></span>' +
    '</form>';
  enquire.parentNode.insertBefore(box, enquire);

  var gform = document.getElementById('guide-cta-form');
  var emailInput = document.getElementById('guide-cta-email');
  var statusEl = gform.querySelector('.gc-status');
  var submitBtn = gform.querySelector('button[type="submit"]');
  var propInput = document.querySelector('#property-enquiry input[name="property"]');
  var propName = propInput ? propInput.value : document.title;

  function mlSubscribe(endpoint, email) {
    var d = new FormData();
    d.append('fields[email]', email);
    d.append('ml-submit', '1');
    d.append('anticsrf', 'true');
    return fetch(endpoint, { method: 'POST', body: d }).catch(function () {});
  }

  gform.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = (emailInput.value || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      statusEl.textContent = 'Please enter a valid email address.';
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';
    statusEl.textContent = '';

    var wantsListings = document.getElementById('guide-cta-optin').checked;
    var data = new FormData();
    data.append('email', email);
    data.append('source', 'Buying Guide PDF Download (property page)');
    data.append('property', propName);
    data.append('property_url', location.href);
    data.append('email_updates', wantsListings ? 'yes' : 'no');
    data.append('_subject', 'New Buying Guide download - ' + email);

    var requests = [
      fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Accept': 'application/json' }, body: data }).catch(function () {}),
      mlSubscribe(ML_GUIDE_ENDPOINT, email)
    ];
    if (wantsListings) requests.push(mlSubscribe(ML_LISTINGS_ENDPOINT, email));

    try { if (typeof fbq === 'function') fbq('track', 'Lead', { content_name: 'Buying Guide PDF (property page)' }); } catch (err) {}
    try { if (typeof gtag === 'function') gtag('event', 'generate_lead', { lead_source: 'Buying Guide PDF (property page)' }); } catch (err) {}

    var done = false;
    function unlock() {
      if (done) return;
      done = true;
      gform.innerHTML =
        '<p style="flex-basis:100%;margin:0 0 14px;color:#EFEAE1">Thanks — your guide is ready. We\'ve also sent a copy to your inbox.</p>' +
        '<a class="gc-open" href="' + PDF_URL + '" target="_blank" rel="noopener">Open the Buyer\'s Guide (PDF)</a>';
      window.open(PDF_URL, '_blank');
    }
    Promise.all(requests).then(unlock, unlock);
    setTimeout(unlock, 4000);
  });
})();
