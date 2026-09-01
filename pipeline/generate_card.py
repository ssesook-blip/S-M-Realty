import html
from lib import (
    clean_title, format_price_card, price_bucket, format_bathrooms, search_blob,
    strip_description, get_sector, gallery_urls, get_community, amenity_filter_values,
    has_bed_bath_data, is_oceanfront, SITE_URL,
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
    oceanfront = "true" if is_oceanfront(listing) else "false"
    show_bed_bath = has_bed_bath_data(listing)
    listing_url = f"{SITE_URL}/properties/{slug}.html"

    if show_bed_bath:
        meta_html = f'<div class="listing-meta"><span>{beds} Bed</span><span>{baths} Bath</span></div>'
    else:
        meta_html = ''

    share_html = f'''<div class="card-share">
          <button type="button" class="share-btn" data-share="facebook" data-url="{html.escape(listing_url)}" data-title="{html.escape(title)}" aria-label="Share on Facebook" title="Share on Facebook">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M22 12.06C22 6.48 17.52 2 11.94 2S2 6.48 2 12.06c0 5.02 3.66 9.18 8.44 9.94v-7.03H7.9v-2.91h2.54V9.85c0-2.51 1.49-3.89 3.77-3.89 1.09 0 2.23.2 2.23.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.44 2.91h-2.34V22c4.78-.76 8.44-4.92 8.44-9.94z"/></svg>
          </button>
          <button type="button" class="share-btn" data-share="whatsapp" data-url="{html.escape(listing_url)}" data-title="{html.escape(title)}" aria-label="Share on WhatsApp" title="Share on WhatsApp">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.26-1.38a9.9 9.9 0 004.73 1.21c5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2zm5.79 14.09c-.24.68-1.38 1.28-1.9 1.32-.5.05-.87.24-2.95-.61-2.49-1.02-4.09-3.52-4.21-3.68-.12-.16-1.01-1.34-1.01-2.56 0-1.21.64-1.81.86-2.06.22-.24.48-.3.64-.3l.46.01c.15 0 .35-.06.54.41.2.48.68 1.67.74 1.79.06.12.1.27.02.43-.08.16-.12.26-.24.4-.12.14-.25.31-.36.42-.12.12-.24.25-.1.49.14.24.62 1.03 1.34 1.66.92.82 1.7 1.08 1.94 1.2.24.12.38.1.52-.06.14-.16.6-.7.76-.94.16-.24.32-.2.54-.12.22.08 1.4.66 1.64.78.24.12.4.18.46.28.06.1.06.58-.18 1.26z"/></svg>
          </button>
        </div>'''

    return f'''      <a href="properties/{slug}.html" class="listing reveal" data-city="{html.escape(city)}" data-price="{bucket}" data-beds="{beds}" data-baths="{baths_num}" data-type="{html.escape(ptype)}" data-community="{html.escape(community)}" data-oceanfront="{oceanfront}" data-amenities="{html.escape(amenities_attr)}" data-search="{html.escape(search_blob(listing))}" data-price-num="{price_num}">
        <div class="photo" style="position:relative;">
          <img src="{image}" alt="{html.escape(title)}" loading="lazy">
          {share_html}
        </div>
        <div class="listing-body">
          <div class="listing-title">{html.escape(title)}</div>
          <div class="listing-row">
            <div>
              <div class="listing-price">{html.escape(price)}</div>
              <div class="listing-addr">{html.escape(sector)}, {html.escape(city)}</div>
            </div>
            {meta_html}
          </div>
        </div>
        {f'<div class="listing-desc">{html.escape(desc)}</div>' if desc else ''}
      </a>
'''
