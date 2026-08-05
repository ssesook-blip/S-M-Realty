const searchFilter = document.getElementById('filter-search');
const cityFilter = document.getElementById('filter-city');
const priceFilter = document.getElementById('filter-price');
const priceMinFilter = document.getElementById('filter-price-min');
const priceMaxFilter = document.getElementById('filter-price-max');
const bedsFilter = document.getElementById('filter-beds');
const cards = document.querySelectorAll('#listings-grid .listing');
const countEl = document.getElementById('result-count');
const noResults = document.getElementById('no-results');

function applyFilters(){
  const query = searchFilter.value.trim().toLowerCase();
  const city = cityFilter.value;
  const price = priceFilter.value;
  const priceMin = parseFloat(priceMinFilter.value);
  const priceMax = parseFloat(priceMaxFilter.value);
  const beds = parseInt(bedsFilter.value) || 0;
  let shown = 0;
  cards.forEach(card => {
    const matchSearch = query === '' || card.dataset.search.includes(query);
    const matchCity = city === 'all' || card.dataset.city === city;
    const matchPrice = price === 'all' || card.dataset.price === price;
    const matchBeds = beds === 0 || parseInt(card.dataset.beds) >= beds;

    const priceNum = card.dataset.priceNum ? parseFloat(card.dataset.priceNum) : null;
    let matchMin = true;
    let matchMax = true;
    if(!isNaN(priceMin)){
      matchMin = priceNum !== null && priceNum >= priceMin;
    }
    if(!isNaN(priceMax)){
      matchMax = priceNum !== null && priceNum <= priceMax;
    }

    const match = matchSearch && matchCity && matchPrice && matchBeds && matchMin && matchMax;
    card.style.display = match ? '' : 'none';
    if(match) shown++;
  });
  countEl.textContent = `Showing ${shown} of 171`;
  noResults.style.display = shown === 0 ? 'block' : 'none';
}

function resetFilters(){
  searchFilter.value = '';
  cityFilter.value = 'all';
  priceFilter.value = 'all';
  priceMinFilter.value = '';
  priceMaxFilter.value = '';
  bedsFilter.value = 'all';
  applyFilters();
}

searchFilter.addEventListener('input', applyFilters);
cityFilter.addEventListener('change', applyFilters);
priceFilter.addEventListener('change', applyFilters);
priceMinFilter.addEventListener('input', applyFilters);
priceMaxFilter.addEventListener('input', applyFilters);
bedsFilter.addEventListener('change', applyFilters);
