// --- Shuffle listing order on every page load, so repeat visitors don't
// keep seeing the same properties sitting first every time. This runs
// before the filter logic below grabs its reference to the cards, so
// everything downstream (filtering, view toggle, counts) works on
// whatever order comes out of the shuffle. ---
(function shuffleListings(){
  const grid = document.getElementById('listings-grid');
  if (!grid) return;
  const items = Array.from(grid.children);
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  items.forEach(item => grid.appendChild(item));
})();

const searchFilter = document.getElementById('filter-search');
const cityFilter = document.getElementById('filter-city');
const priceFilter = document.getElementById('filter-price');
const communityFilter = document.getElementById('filter-community');
const typeFilter = document.getElementById('filter-type');
const bathsFilter = document.getElementById('filter-baths');
const oceanfrontFilter = document.getElementById('filter-oceanfront');
const priceMinFilter = document.getElementById('filter-price-min');
const priceMaxFilter = document.getElementById('filter-price-max');
const bedsFilter = document.getElementById('filter-beds');
const cards = document.querySelectorAll('#listings-grid .listing');
const countEl = document.getElementById('result-count');
const noResults = document.getElementById('no-results');
const amenitiesPanel = document.getElementById('amenities-panel');
const amenitiesToggle = document.getElementById('amenities-toggle');
const TOTAL_LISTINGS = cards.length;

// --- Populate Property Type dropdown from whatever's actually in the cards ---
if (typeFilter) {
  const types = new Set();
  cards.forEach(card => {
    const t = card.dataset.type;
    if (t) types.add(t);
  });
  Array.from(types).sort().forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    typeFilter.appendChild(opt);
  });
}

// --- Populate the Amenities panel from whatever's actually in the cards, with live counts ---
if (amenitiesPanel) {
  const counts = {};
  cards.forEach(card => {
    const list = (card.dataset.amenities || '').split('|').filter(Boolean);
    list.forEach(a => { counts[a] = (counts[a] || 0) + 1; });
  });
  Object.keys(counts).sort().forEach(name => {
    const label = document.createElement('label');
    label.className = 'amenity-check';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.value = name;
    input.className = 'amenity-checkbox';
    label.appendChild(input);
    label.appendChild(document.createTextNode(` ${name} (${counts[name]})`));
    amenitiesPanel.appendChild(label);
  });
}

function selectedAmenities() {
  if (!amenitiesPanel) return [];
  return Array.from(amenitiesPanel.querySelectorAll('.amenity-checkbox:checked')).map(cb => cb.value);
}

function applyFilters(){
  const query = searchFilter.value.trim().toLowerCase();
  const city = cityFilter.value;
  const price = priceFilter.value;
  const community = communityFilter.value;
  const type = typeFilter ? typeFilter.value : 'all';
  const minBaths = bathsFilter ? (parseInt(bathsFilter.value) || 0) : 0;
  const oceanfrontOnly = oceanfrontFilter ? oceanfrontFilter.checked : false;
  const priceMin = parseFloat(priceMinFilter.value);
  const priceMax = parseFloat(priceMaxFilter.value);
  const beds = parseInt(bedsFilter.value) || 0;
  const wantedAmenities = selectedAmenities();
  let shown = 0;
  cards.forEach(card => {
    const matchSearch = query === '' || card.dataset.search.includes(query);
    const matchCity = city === 'all' || card.dataset.city === city;
    const matchPrice = price === 'all' || card.dataset.price === price;
    const matchCommunity = community === 'all' || card.dataset.community === community;
    const matchType = type === 'all' || card.dataset.type === type;
    const matchBaths = minBaths === 0 || parseInt(card.dataset.baths) >= minBaths;
    const matchBeds = beds === 0 || parseInt(card.dataset.beds) >= beds;
    const matchOceanfront = !oceanfrontOnly || card.dataset.oceanfront === 'true';

    const cardAmenities = (card.dataset.amenities || '').split('|');
    const matchAmenities = wantedAmenities.every(a => cardAmenities.includes(a));

    const priceNum = card.dataset.priceNum ? parseFloat(card.dataset.priceNum) : null;
    let matchMin = true;
    let matchMax = true;
    if(!isNaN(priceMin)){
      matchMin = priceNum !== null && priceNum >= priceMin;
    }
    if(!isNaN(priceMax)){
      matchMax = priceNum !== null && priceNum <= priceMax;
    }

    const match = matchSearch && matchCity && matchPrice && matchCommunity && matchType &&
                  matchBaths && matchBeds && matchOceanfront && matchMin && matchMax && matchAmenities;
    card.style.display = match ? '' : 'none';
    if(match) shown++;
  });
  countEl.textContent = `Showing ${shown} of ${TOTAL_LISTINGS}`;
  noResults.style.display = shown === 0 ? 'block' : 'none';
}

function resetFilters(){
  searchFilter.value = '';
  cityFilter.value = 'all';
  priceFilter.value = 'all';
  communityFilter.value = 'all';
  if (typeFilter) typeFilter.value = 'all';
  if (bathsFilter) bathsFilter.value = 'all';
  if (oceanfrontFilter) oceanfrontFilter.checked = false;
  priceMinFilter.value = '';
  priceMaxFilter.value = '';
  bedsFilter.value = 'all';
  if (amenitiesPanel) {
    amenitiesPanel.querySelectorAll('.amenity-checkbox:checked').forEach(cb => cb.checked = false);
  }
  applyFilters();
}

searchFilter.addEventListener('input', applyFilters);
cityFilter.addEventListener('change', applyFilters);
priceFilter.addEventListener('change', applyFilters);
communityFilter.addEventListener('change', applyFilters);
if (typeFilter) typeFilter.addEventListener('change', applyFilters);
if (bathsFilter) bathsFilter.addEventListener('change', applyFilters);
if (oceanfrontFilter) oceanfrontFilter.addEventListener('change', applyFilters);
priceMinFilter.addEventListener('input', applyFilters);
priceMaxFilter.addEventListener('input', applyFilters);
bedsFilter.addEventListener('change', applyFilters);
if (amenitiesPanel) {
  amenitiesPanel.addEventListener('change', applyFilters);
}
if (amenitiesToggle && amenitiesPanel) {
  amenitiesToggle.addEventListener('click', function(){
    const isOpen = amenitiesPanel.classList.toggle('open');
    amenitiesToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    amenitiesToggle.classList.toggle('open', isOpen);
  });
}

// --- Grid / List view toggle ---
(function(){
  const grid = document.getElementById('listings-grid');
  const gridBtn = document.getElementById('view-grid-btn');
  const listBtn = document.getElementById('view-list-btn');
  if (!grid || !gridBtn || !listBtn) return;

  function setView(view){
    if (view === 'list') {
      grid.classList.add('list-view');
      listBtn.classList.add('active');
      gridBtn.classList.remove('active');
    } else {
      grid.classList.remove('list-view');
      gridBtn.classList.add('active');
      listBtn.classList.remove('active');
    }
    try { localStorage.setItem('sm-listings-view', view); } catch(e) {}
  }

  gridBtn.addEventListener('click', () => setView('grid'));
  listBtn.addEventListener('click', () => setView('list'));

  let saved = 'grid';
  try { saved = localStorage.getItem('sm-listings-view') || 'grid'; } catch(e) {}
  setView(saved);
})();

// --- Per-card social share buttons ---
document.querySelectorAll('.share-btn').forEach(function(btn){
  btn.addEventListener('click', function(e){
    e.preventDefault();
    e.stopPropagation();
    const platform = btn.dataset.share;
    const url = encodeURIComponent(btn.dataset.url);
    const title = encodeURIComponent(btn.dataset.title);
    let shareUrl = '';
    if (platform === 'facebook') {
      shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    } else if (platform === 'whatsapp') {
      shareUrl = `https://wa.me/?text=${title}%20${url}`;
    }
    if (shareUrl) {
      window.open(shareUrl, '_blank', 'noopener,width=600,height=500');
    }
  });
});
