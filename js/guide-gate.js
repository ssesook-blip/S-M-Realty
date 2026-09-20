(function(){
  var FORM_ENDPOINT = 'https://formspree.io/f/xdenwkrj';
  var PDF_URL = 'Sosua_Cabarete_DR_Buyers_Guide.pdf';

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

      var data = new FormData();
      data.append('email', email);
      data.append('source', 'Buying Guide PDF Download');
      data.append('_subject', 'New Buying Guide download - ' + email);

      fetch(FORM_ENDPOINT, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: data
      })
        .then(function(){ unlockGuide(); })
        .catch(function(){ unlockGuide(); });

      function unlockGuide(){
        form.innerHTML =
          '<p style="margin:0 0 16px; color: var(--ink);">Thanks — your guide is ready.</p>' +
          '<a href="' + PDF_URL + '" target="_blank" rel="noopener" class="btn fill">Open the Buyer\'s Guide (PDF)</a>';
        window.open(PDF_URL, '_blank');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
