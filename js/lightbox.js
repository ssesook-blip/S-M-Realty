let currentIndex = 0;
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');
const lightboxCounter = document.getElementById('lightbox-counter');
function openLightbox(i){ currentIndex = i; updateLightbox(); lightbox.classList.add('open'); }
function closeLightbox(){ lightbox.classList.remove('open'); }
function navLightbox(dir){ currentIndex = (currentIndex + dir + photos.length) % photos.length; updateLightbox(); }
function updateLightbox(){ lightboxImg.src = photos[currentIndex]; lightboxCounter.textContent = (currentIndex+1) + ' / ' + photos.length; }
document.addEventListener('keydown', (e) => {
  if(!lightbox.classList.contains('open')) return;
  if(e.key === 'Escape') closeLightbox();
  if(e.key === 'ArrowLeft') navLightbox(-1);
  if(e.key === 'ArrowRight') navLightbox(1);
});
lightbox.addEventListener('click', (e) => { if(e.target === lightbox) closeLightbox(); });
