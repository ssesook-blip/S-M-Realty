function toggleReview(btn){
  const quote = btn.previousElementSibling;
  const collapsed = quote.classList.toggle('collapsed');
  btn.textContent = collapsed ? 'Read more' : 'Read less';
}
  function submitValuationForm(event, form) {
  event.preventDefault();
  const button = form.querySelector('button');
  const originalText = button.textContent;
  button.textContent = 'Sending…';
  const data = new FormData(form);
  fetch('https://formspree.io/f/xdenwkrj', {
    method: 'POST',
    body: data,
    headers: { 'Accept': 'application/json' }
  })
    .then(response => {
      if (response.ok) {
        button.textContent = 'Sent';
        form.reset();
      } else {
        button.textContent = 'Error — try again';
        setTimeout(() => { button.textContent = originalText; }, 3000);
      }
    })
    .catch(() => {
      button.textContent = 'Error — try again';
      setTimeout(() => { button.textContent = originalText; }, 3000);
    });
}
(function(){
  const btn = document.getElementById('music-toggle');
  const audio = document.getElementById('bg-music');
  if (!btn || !audio) return;
  let playing = false;
  btn.addEventListener('click', function(){
    if (playing) {
      audio.pause();
      btn.classList.remove('playing');
    } else {
      audio.play().catch(() => {});
      btn.classList.add('playing');
    }
    playing = !playing;
    btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
  });
})();
