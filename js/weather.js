/* Live North Coast weather for the homepage - data from Open-Meteo (free, no API key) */
(function(){
  var root = document.getElementById('weather');
  if (!root) return;

  var TOWNS = [
    { name: 'Sosúa',        lat: 19.7550, lon: -70.5175 },
    { name: 'Puerto Plata', lat: 19.7934, lon: -70.6884 },
    { name: 'Cabarete',     lat: 19.7500, lon: -70.4100 }
  ];
  var ICONS = {
    sun:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg>',
    moon:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z"/></svg>',
    partly:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8.5" r="3.2"/><path d="M9 2.5v1.3M3 8.5h1.3M4.8 4.3l.9.9M13.2 4.3l-.9.9"/><path d="M8 19.5h9.5a3.5 3.5 0 0 0 0-7 5 5 0 0 0-9.4 1.3A2.9 2.9 0 0 0 8 19.5z"/></svg>',
    cloud: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 18.5h10.5a4 4 0 0 0 0-8 5.8 5.8 0 0 0-11 1.6A3.3 3.3 0 0 0 7 18.5z"/></svg>',
    fog:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M4 9h16M3 13h18M5 17h14"/></svg>',
    rain:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 14.5h10.5a4 4 0 0 0 0-8 5.8 5.8 0 0 0-11 1.6A3.3 3.3 0 0 0 7 14.5z"/><path d="M8.5 17.5l-1 2.5M12.5 17.5l-1 2.5M16.5 17.5l-1 2.5"/></svg>',
    storm: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 14.5h10.5a4 4 0 0 0 0-8 5.8 5.8 0 0 0-11 1.6A3.3 3.3 0 0 0 7 14.5z"/><path d="M12.5 15.5l-2 3.5h3l-2 3.5"/></svg>'
  };
  function describe(code, isDay){
    var r;
    if (code === 0) r = ['Clear', 'sun'];
    else if (code === 1) r = ['Mostly sunny', 'sun'];
    else if (code === 2) r = ['Partly cloudy', 'partly'];
    else if (code === 3) r = ['Overcast', 'cloud'];
    else if (code === 45 || code === 48) r = ['Fog', 'fog'];
    else if (code >= 51 && code <= 57) r = ['Drizzle', 'rain'];
    else if (code >= 61 && code <= 67) r = ['Rain', 'rain'];
    else if (code >= 80 && code <= 82) r = ['Showers', 'rain'];
    else if (code >= 95) r = ['Thunderstorms', 'storm'];
    else r = ['Cloudy', 'cloud'];
    if (isDay === 0 && r[1] === 'sun') r = ['Clear night', 'moon'];
    return r;
  }

  var unit = 'F', data = null;
  try { unit = localStorage.getItem('wx-unit') || 'F'; } catch(e){}

  function t(c){ return Math.round(unit === 'F' ? c * 9/5 + 32 : c) + '°'; }
  function w(k){ return unit === 'F' ? Math.round(k * 0.621) + ' mph' : Math.round(k) + ' km/h'; }
  function dayName(iso, i){
    return i === 0 ? 'Today' : new Date(iso + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short' });
  }

  function render(){
    root.querySelector('.wx-grid').innerHTML = data.map(function(d, i){
      var c = d.current, now = describe(c.weather_code, c.is_day);
      var days = d.daily.time.map(function(iso, j){
        var dd = describe(d.daily.weather_code[j]);
        var p = d.daily.precipitation_probability_max[j];
        return '<li><span class="d">' + dayName(iso, j) + '</span>' + ICONS[dd[1]] +
          '<span class="rain">' + (p >= 20 ? p + '% rain' : '') + '</span>' +
          '<span class="hl">' + t(d.daily.temperature_2m_max[j]) + '<span>' + t(d.daily.temperature_2m_min[j]) + '</span></span></li>';
      }).join('');
      return '<article class="wx-card">' +
        '<h3 class="wx-town">' + TOWNS[i].name + '</h3>' +
        '<div class="wx-now">' + ICONS[now[1]] + '<span class="wx-temp">' + t(c.temperature_2m) + '</span>' +
        '<span class="wx-cond">' + now[0] + '</span></div>' +
        '<p class="wx-meta">Feels like ' + t(c.apparent_temperature) + ' &middot; Wind ' + w(c.wind_speed_10m) + '</p>' +
        '<ul class="wx-days">' + days + '</ul></article>';
    }).join('');
    root.querySelectorAll('.wx-units button').forEach(function(b){
      b.setAttribute('aria-pressed', b.dataset.unit === unit ? 'true' : 'false');
    });
  }

  root.querySelectorAll('.wx-units button').forEach(function(b){
    b.addEventListener('click', function(){
      unit = b.dataset.unit;
      try { localStorage.setItem('wx-unit', unit); } catch(e){}
      if (data) render();
    });
  });

  var url = 'https://api.open-meteo.com/v1/forecast' +
    '?latitude=' + TOWNS.map(function(x){ return x.lat; }).join(',') +
    '&longitude=' + TOWNS.map(function(x){ return x.lon; }).join(',') +
    '&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,is_day' +
    '&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max' +
    '&timezone=America%2FSanto_Domingo&forecast_days=5';

  fetch(url)
    .then(function(r){ if (!r.ok) throw 0; return r.json(); })
    .then(function(json){ data = Array.isArray(json) ? json : [json]; render(); })
    .catch(function(){ root.style.display = 'none'; }); // hide quietly if the service is ever down
})();
