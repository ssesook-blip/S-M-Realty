import html
from lib import (
    clean_title, format_price_card, price_bucket, format_bathrooms, search_blob,
    strip_description, get_sector, gallery_urls, get_community, amenity_filter_values,
)


def generate_listing_card(listing: dict) -> str:
    title = clean_title(listing.get("name", ""))
    slug = listing["slug"]
    city = listing.get("city", "")
    sector = get_sector(listing)
    community = get_community(listing)
    desc = strip_description(listing.get("description", ""))
    price = format_price_card(listing)
    bucket = price_bucket(listing)
    beds = listing.get("room", 0)
    baths_num = int(listing.get("bathroom") or 0)
    baths = format_bathrooms(listing)
    price_num = listing.get("sale_price") or ""
    images = gallery_urls(listing)
    image = images[0] if images else ""
    ptype = (listing.get("category") or {}).get("name_en", "") or ""
    amenities_attr = amenity_filter_values(listing)

    return f'''      <a href="properties/{slug}.html" class="listing reveal" data-city="{html.escape(city)}" data-price="{bucket}" data-beds="{beds}" data-baths="{baths_num}" data-type="{html.escape(ptype)}" data-community="{html.escape(community)}" data-amenities="{html.escape(amenities_attr)}" data-search="{html.escape(search_blob(listing))}" data-price-num="{price_num}">
        <div class="photo" style="position:relative;">
          <img src="{image}" alt="{html.escape(title)}" loading="lazy">
        </div>
        <div class="listing-body">
          <div class="listing-title">{html.escape(title)}</div>
          <div class="listing-row">
            <div>
              <div class="listing-price">{html.escape(price)}</div>
              <div class="listing-addr">{html.escape(sector)}, {html.escape(city)}</div>
            </div>
            <div class="listing-meta"><span>{beds} Bed</span><span>{baths} Bath</span></div>
          </div>
        </div>
        {f'<div class="listing-desc">{html.escape(desc)}</div>' if desc else ''}
      </a>
'''
