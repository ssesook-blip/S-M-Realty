"""
Shared formatting helpers used by both the property-page generator
and the listings.html card generator.
"""
import html
import re

MAIN_WHATSAPP_NUMBER = "18093503736"  # shared company line used on all pages


def clean_title(name: str) -> str:
    """Some listing names have marketing suffixes like ' | US$198,000 | Income-Producing...'
    Strip anything after the first pipe, matching the clean style of existing pages."""
    return name.split("|")[0].strip()


def format_price_full(listing: dict) -> str:
    """Property-page style price, e.g. 'USD 209,000' or 'Price on request'."""
    price = listing.get("sale_price")
    currency = listing.get("currency_sale") or "USD"
    if price:
        return f"{currency} {int(round(price)):,}"
    return "Price on request"


def format_price_card(listing: dict) -> str:
    """Listing-card style price, e.g. '$265,000' or 'Price on request'."""
    price = listing.get("sale_price")
    if price:
        return f"${int(round(price)):,}"
    return "Price on request"


def price_bucket(listing: dict) -> str:
    """Matches the data-price buckets already used by listings-filter.js."""
    price = listing.get("sale_price")
    if not price:
        return ""
    if price < 250_000:
        return "under250"
    if price < 500_000:
        return "250-500"
    if price < 750_000:
        return "500-750"
    return "750plus"


def format_area(listing: dict) -> str:
    area = listing.get("property_area")
    measurer = listing.get("property_area_measurer") or "Mt2"
    if area is None:
        return "—"
    if float(area).is_integer():
        return f"{int(area)} {measurer}"
    return f"{area:g} {measurer}"


def format_bathrooms(listing: dict) -> str:
    baths = listing.get("bathroom") or 0
    return f"{float(baths):.1f}"


def gallery_urls(listing: dict) -> list:
    gallery = listing.get("gallery_image") or []
    urls = [g.get("image") for g in gallery if g.get("image")]
    if not urls and listing.get("featured_image"):
        urls = [listing["featured_image"]]
    return urls


def render_amenities(listing: dict) -> str:
    amenities = listing.get("amenities") or []
    if not amenities:
        return ""
    tags = "\n".join(f'<span class="amenity-tag">{html.escape(a)}</span>' for a in amenities)
    return f'<h2 style="margin-top:50px; font-size:24px;">Amenities</h2><div class="amenities">{tags}</div>'


def render_agents(listing: dict) -> str:
    agents = listing.get("agents") or []
    boxes = []
    for a in agents:
        name = f'{a.get("first_name", "")} {a.get("last_name", "")}'.strip()
        role = a.get("position") or ""
        phone = a.get("phone") or ""
        avatar = a.get("avatar") or ""
        boxes.append(f'''<div class="agent-box" style="margin-top:0;">
          <img src="{html.escape(avatar)}" alt="{html.escape(name)}">
          <div>
            <div class="agent-name">{html.escape(name)}</div>
            <div class="agent-role">{html.escape(role)}</div>
            <div style="font-size:13px; margin-top:6px;">{html.escape(phone)}</div>
          </div>
        </div>''')
    if not boxes:
        return ""
    return f'<div style="display:flex; gap:20px; flex-wrap:wrap; margin-top:40px;">\n        {"".join(boxes)}</div>'


def whatsapp_link(listing: dict) -> str:
    name = clean_title(listing.get("name", ""))
    cid = listing.get("cid", "")
    text = (
        f"Hi! I'm interested in real estate on the North Coast of the Dominican Republic. "
        f"I'm looking for more information about this property (Property code: {cid})."
        f" Please get in touch when you have a moment."
    )
    from urllib.parse import quote
    return f"https://wa.me/{MAIN_WHATSAPP_NUMBER}?text={quote(text)}"


def search_blob(listing: dict) -> str:
    """Matches the data-search format already used in listings.html cards."""
    title = clean_title(listing.get("name", ""))
    price = format_price_card(listing)
    sector = listing.get("sector") or ""
    city = listing.get("city") or ""
    parts = [
        title.lower(),
        f"{price.lower()}, {sector.lower()}, {city.lower()}" if price != "price on request" else f"{sector.lower()}, {city.lower()}",
        f"{sector.lower()}, {city.lower()}",
        city.lower(),
    ]
    return " ".join(p for p in parts if p)
