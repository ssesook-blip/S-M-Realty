import html
from lib import (
    clean_title, format_price_card, price_bucket, format_bathrooms, search_blob,
    strip_description, get_sector,
)


def generate_listing_card(listing: dict) -> str:
    title = clean_title(listing.get("name", ""))
    slug = listing["slug"]
    city = listing.get("city", "")
    sector = get_sector(listing)
    desc = strip_description(listing.get("description", ""))
    price = format_price_card(listing)
    bucket = price_bucket(listing)
    beds = listing.get("room", 0)
    baths = format_bathrooms(listing)
    price_num = listing.get("sale_price") or ""
    image = listing.get("featured_image", "")

    return f'''      <a href="properties/{slug}.html" class="listing reveal" data-city="{html.escape(city)}" data-price="{bucket}" data-beds="{beds}" data-search="{html.escape(search_blob(listing))}" data-price-num="{price_num}">
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
