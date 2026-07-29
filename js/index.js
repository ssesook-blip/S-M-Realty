function toggleReview(btn){
  const quote = btn.previousElementSibling;
  const collapsed = quote.classList.toggle('collapsed');
  btn.textContent = collapsed ? 'Read more' : 'Read less';
}
