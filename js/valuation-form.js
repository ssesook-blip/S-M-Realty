/* Seller valuation form (sell-your-property.html) -> Formspree, same endpoint as the
   homepage form. The hidden _subject / lead_source fields mark it as a seller lead. */
(function () {
  var form = document.getElementById('valuation-form');
  if (!form) return;
  var status = form.querySelector('.form-status');
  var button = form.querySelector('button[type="submit"]');

  function say(msg, isError) {
    status.textContent = msg;
    status.classList.toggle('is-error', !!isError);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = form.elements.name.value.trim();
    var email = form.elements.email.value.trim();
    var town = form.elements.town.value;
    if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      say('Please enter your name and a valid email address.', true);
      return;
    }
    if (!town) {
      say('Please choose the town your property is in.', true);
      return;
    }
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
        form.reset();
        button.textContent = 'Sent';
        say('Thank you. We have your request and will be in touch shortly.');
        if (window.fbq) { try { fbq('track', 'Lead', { content_name: 'Seller valuation' }); } catch (err) {} }
      })
      .catch(function () {
        button.disabled = false;
        button.textContent = original;
        say('Something went wrong sending your request. Please try again, or message us on WhatsApp.', true);
      });
  });
})();
