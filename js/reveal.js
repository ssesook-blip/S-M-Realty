const revealEls = document.querySelectorAll('.reveal');
const revealThreshold = window.REVEAL_THRESHOLD || 0.15;
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
  });
}, { threshold: revealThreshold });
revealEls.forEach(el => io.observe(el));
