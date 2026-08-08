import html
import json
from lib import (
    clean_title, format_price_full, format_area, format_bathrooms,
    gallery_urls, render_amenities, render_agents, whatsapp_link, get_sector,
    meta_description, SITE_URL,
)

PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} &mdash; S &amp; M Realty</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{canonical_url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title} — S & M Realty">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="{hero_image}">
<meta property="og:url" content="{canonical_url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="../favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="../favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="../apple-touch-icon.png">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "RealEstateListing",
  "name": {title_json},
  "description": {meta_desc_json},
  "url": {canonical_url_json},
  "image": {hero_image_json},
  "address": {{
    "@type": "PostalAddress",
    "addressLocality": {city_json},
    "addressRegion": {location_json},
    "addressCountry": "DO"
  }},
  "offers": {{
    "@type": "Offer",
    "price": {price_number},
    "priceCurrency": {currency_json}
  }}
}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,300;0,400;0,500;1,400;1,500&family=Archivo:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/common.css">
<link rel="stylesheet" href="../css/property.css">
</head>
<body>
<header>
  <nav class="wrap">
    <a href="../index.html" class="logo">
      <svg width="42" height="42" viewBox="0 0 42 42" fill="none">
        <circle cx="21" cy="21" r="20" stroke="#9C8158" stroke-width="1"/>
        <text x="21" y="27" text-anchor="middle" font-family="Cormorant, serif" font-style="italic" font-size="17" fill="#1C1A17">S&amp;M</text>
      </svg>
      <span class="logo-word">S &amp; M Realty</span>
    </a>
    <div class="nav-links">
      <a href="../listings.html">All Listings</a>
      <a href="../index.html#process">How We Work</a>
      <a href="../index.html#team">The Team</a>
    </div>
    <button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
  </nav>
</header>

<section class="prop-header">
  <div class="wrap">
    <a href="../listings.html" class="back-link">&larr; All Listings</a>
    <span class="eyebrow">{location}</span>
    <h1>{title}</h1>
    <div class="prop-loc">{location}</div>
    <div class="prop-price">{price}</div>
    <button class="print-listing-btn" onclick="window.print()">Print This Listing</button>
  </div>
</section>

<section class="section tight">
  <div class="wrap">
    <div class="gallery-hero" onclick="openLightbox(0)">
      <img src="{hero_image}" alt="{title}" loading="lazy">
    </div>
    <div class="gallery-grid">
      {thumbnails}
    </div>
  </div>
</section>

<section class="section tight">
  <div class="wrap">
    <div class="prop-specs">
      <div class="prop-spec"><div class="num">{bedrooms}</div><div class="label">Bedrooms</div></div>
<div class="prop-spec"><div class="num">{bathrooms}</div><div class="label">Bathrooms</div></div>
<div class="prop-spec"><div class="num">{area}</div><div class="label">Mt2</div></div>
<div class="prop-spec"><div class="num">{category}</div><div class="label">Property Type</div></div>
    </div>
    <div class="prop-desc">
      {description}
    </div>
    {amenities}
    {agents}
  </div>
</section>

<footer>
  <div class="wrap">
    <p>&copy; 2026 S &amp; M Realty. Licensed Real Estate Brokerage.</p>
  </div>
</footer>

<div class="print-only-footer">
  <p>{canonical_url_plain}</p>
  <p>Sheena Sesook &amp; Michael Galea &mdash; S &amp; M Realty &mdash; +1 809-350-3736</p>
</div>

<div class="lightbox" id="lightbox">
  <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
  <button class="lightbox-nav lightbox-prev" onclick="navLightbox(-1)">&#8249;</button>
  <img id="lightbox-img" src="" alt="">
  <button class="lightbox-nav lightbox-next" onclick="navLightbox(1)">&#8250;</button>
  <div class="lightbox-counter" id="lightbox-counter"></div>
</div>

<a class="whatsapp-float" href="{whatsapp}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">
  <span class="wa-tip">Chat with us</span>
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91C2.13 13.66 2.59 15.36 3.45 16.86L2.05 22L7.31 20.62C8.75 21.41 10.38 21.83 12.04 21.83C17.5 21.83 21.95 17.38 21.95 11.92C21.95 9.27 20.92 6.78 19.05 4.91C17.18 3.03 14.69 2 12.04 2ZM12.04 3.67C14.25 3.67 16.32 4.53 17.88 6.09C19.44 7.65 20.29 9.72 20.29 11.92C20.29 16.46 16.58 20.16 12.03 20.16C10.56 20.16 9.12 19.77 7.85 19.03L7.55 18.86L4.43 19.68L5.27 16.64L5.07 16.33C4.26 15.02 3.83 13.48 3.83 11.91C3.84 7.37 7.5 3.67 12.04 3.67ZM8.53 6.65C8.37 6.65 8.1 6.71 7.87 6.96C7.65 7.21 7 7.81 7 9.02C7 10.24 7.89 11.41 8.01 11.58C8.14 11.74 9.76 14.34 12.32 15.36C14.44 16.21 14.87 16.04 15.34 16C15.8 15.95 16.81 15.39 17.02 14.81C17.24 14.22 17.24 13.72 17.17 13.61C17.11 13.51 16.94 13.45 16.69 13.32C16.44 13.2 15.21 12.59 14.98 12.51C14.75 12.42 14.58 12.38 14.42 12.63C14.25 12.88 13.77 13.45 13.62 13.61C13.48 13.78 13.33 13.8 13.08 13.67C12.83 13.55 12.03 13.28 11.08 12.43C10.34 11.77 9.84 10.96 9.7 10.71C9.55 10.46 9.68 10.32 9.81 10.19C9.92 10.08 10.06 9.9 10.19 9.75C10.31 9.6 10.36 9.5 10.44 9.33C10.53 9.17 10.48 9.02 10.42 8.9C10.36 8.77 9.86 7.54 9.65 7.04C9.44 6.56 9.24 6.62 9.09 6.62C8.94 6.6 8.78 6.65 8.53 6.65Z" fill="#EFEAE1"/>
  </svg>
</a>

<script>
  const photos = {photos_js};
</script>
<script src="../js/lightbox.js"></script>
<script src="../js/nav-toggle.js"></script>
</body>
</html>
'''


def generate_property_page(listing: dict) -> str:
    title = clean_title(listing.get("name", ""))
    location = f'{get_sector(listing)}, {listing.get("city", "")}'.strip(", ")
    images = gallery_urls(listing)
    hero = images[0] if images else ""
    thumb_imgs = images[1:]
    slug = listing.get("slug", "")
    canonical_url = f"{SITE_URL}/properties/{slug}.html"
    meta_desc = meta_description(listing)
    price_number = listing.get("sale_price") or 0
    currency = listing.get("currency_sale") or "USD"

    thumbs = []
    for i, url in enumerate(thumb_imgs, start=1):
        thumbs.append(
            f'<a href="#" class="thumb" onclick="event.preventDefault(); openLightbox({i})">'
            f'<img src="{url}" alt="{html.escape(title)} photo {i + 1}" loading="lazy"></a>'
        )

    category = (listing.get("category") or {}).get("name_en", "") or "—"

    body = PAGE_TEMPLATE.format(
        title=html.escape(title),
        title_json=json.dumps(title),
        location=html.escape(location),
        location_json=json.dumps(location),
        meta_desc=html.escape(meta_desc),
        meta_desc_json=json.dumps(meta_desc),
        canonical_url=canonical_url,
        canonical_url_plain=html.escape(canonical_url),
        canonical_url_json=json.dumps(canonical_url),
        city_json=json.dumps(listing.get("city") or ""),
        hero_image_json=json.dumps(hero),
        price_number=price_number,
        currency_json=json.dumps(currency),
        price=html.escape(format_price_full(listing)),
        hero_image=hero,
        thumbnails="\n".join(thumbs),
        bedrooms=listing.get("room", "—"),
        bathrooms=format_bathrooms(listing),
        area=format_area(listing),
        category=html.escape(category),
        description=listing.get("description") or "",
        amenities=render_amenities(listing),
        agents=render_agents(listing),
        whatsapp=whatsapp_link(listing),
        photos_js=str(images).replace("'", '"'),
    )
    return body
