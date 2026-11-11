(function(){
  // Formspree: emails Sheena and Mike a notification for every download
  var FORM_ENDPOINT = 'https://formspree.io/f/xdenwkrj';
  // MailerLite: adds the lead to "Buyer's Guide Leads" (starts the welcome email series)
  var ML_GUIDE_ENDPOINT = 'https://assets.mailerlite.com/jsonp/2788039/forms/203866275742483518/subscribe';
  // MailerLite: adds opted-in leads to "New Listings Updates" (monthly listings email)
  var ML_LISTINGS_ENDPOINT = 'https://assets.mailerlite.com/jsonp/2788039/forms/203866432118720453/subscribe';
  var PDF_URL = 'Sosua_Cabarete_DR_Buyers_Guide.pdf';

  function mailerliteSubscribe(endpoint, email){
    var d = new FormData();
    d.append('fields[email]', email);
    d.append('ml-submit', '1');
    d.append('anticsrf', 'true');
    return fetch(endpoint, { method: 'POST', body: d }).catch(function(){});
  }

  function trackLead(){
    try { if (typeof fbq === 'function') fbq('track', 'Lead', { content_name: 'Buying Guide PDF' }); } catch (e) {}
    try { if (typeof gtag === 'function') gtag('event', 'generate_lead', { lead_source: 'Buying Guide PDF' }); } catch (e) {}
  }

  function init(){
    var form = document.getElementById('guide-gate-form');
    if (!form) return;
    var emailInput = document.getElementById('guide-gate-email');
    var statusEl = document.getElementById('guide-gate-status');
    var submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', function(e){
      e.preventDefault();
      var email = (emailInput.value || '').trim();
      if (!email || !emailInput.checkValidity()) {
        statusEl.textContent = 'Please enter a valid email address.';
        statusEl.style.color = '#b3261e';
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';
      statusEl.textContent = '';

      var optin = document.getElementById('guide-gate-optin');
      var wantsListings = !!(optin && optin.checked);

      var data = new FormData();
      data.append('email', email);
      data.append('source', 'Buying Guide PDF Download');
      data.append('email_updates', wantsListings ? 'yes' : 'no');
      data.append('_subject', 'New Buying Guide download - ' + email);

      var requests = [
        fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Accept': 'application/json' }, body: data }).catch(function(){}),
        mailerliteSubscribe(ML_GUIDE_ENDPOINT, email)
      ];
      if (wantsListings) requests.push(mailerliteSubscribe(ML_LISTINGS_ENDPOINT, email));

      trackLead();

      // Unlock the guide once the signups are sent (or after 4 seconds at most)
      var done = false;
      function unlockGuide(){
        if (done) return;
        done = true;
        form.innerHTML =
          '<p style="margin:0 0 16px; color: var(--ink);">Thanks — your guide is ready. Check your inbox too: we\'ve sent you a copy.</p>' +
          '<a href="' + PDF_URL + '" target="_blank" rel="noopener" class="btn fill">Open the Buyer\'s Guide (PDF)</a>';
        window.open(PDF_URL, '_blank');
      }
      Promise.all(requests).then(unlockGuide, unlockGuide);
      setTimeout(unlockGuide, 4000);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
