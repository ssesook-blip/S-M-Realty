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


FIXED_TEAM = [
    {
        "name": "Sheena Sesook",
        "role": "Principal Broker",
        "photo": "../team-sheena.jpg",
        "phone": "+1 809-350-3736",
    },
    {
        "name": "Michael Galea",
        "role": "Principal Broker",
        "photo": "../team-michael.jpg",
        "phone": "+1 829-637-5611",
    },
]


def render_agents(listing: dict) -> str:
    """Always shows the S&M Realty team, regardless of which agent
    AlterEstate's API lists for this specific listing."""
    boxes = []
    for a in FIXED_TEAM:
        boxes.append(f'''<div class="agent-box" style="margin-top:0;">
          <img src="{html.escape(a["photo"])}" alt="{html.escape(a["name"])}">
          <div>
            <div class="agent-name">{html.escape(a["name"])}</div>
            <div class="agent-role">{html.escape(a["role"])}</div>
            <div style="font-size:13px; margin-top:6px;">{html.escape(a["phone"])}</div>
          </div>
        </div>''')
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


SITE_URL = "https://sheenaandmichaelrealtydr.com"


def meta_description(listing: dict) -> str:
    """Short, unique meta description per property for search results."""
    beds = listing.get("room", "")
    baths_raw = format_bathrooms(listing)
    baths = baths_raw[:-2] if baths_raw.endswith(".0") else baths_raw
    location = get_sector(listing)
    city = listing.get("city") or ""
    price = format_price_full(listing)
    loc = f"{location}, {city}".strip(", ")
    parts = []
    if beds:
        parts.append(f"{beds}-bedroom")
    if baths:
        parts.append(f"{baths}-bathroom")
    header = " ".join(parts) + " property" if parts else "Property"
    return f"{header} for sale in {loc} — {price}. Photos, details, and pricing on S & M Realty."


def strip_description(desc: str, max_chars: int = 140) -> str:
    """Turn the API's HTML description into a short plain-text card blurb."""
    if not desc:
        return ""
    text = re.sub(r"<[^>]+>", " ", desc)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


# Bella Vista, Sosúa covers several distinct communities. Split by keyword
# match (checked against title + description) instead of relying on the
# API's single broad "sector" value.
SECTOR_OVERRIDES = [
    ("hispaniola", "Hispaniola"),
    ("panorama village", "Panorama Village"),
    ("panorama", "Panorama Village"),
]


def get_sector(listing: dict) -> str:
    """Sector/neighborhood name, with Bella Vista split into its sub-areas."""
    sector = listing.get("sector") or ""
    if sector.strip().lower() == "bella vista":
        haystack = f'{listing.get("name", "")} {listing.get("description", "")}'.lower()
        for keyword, replacement in SECTOR_OVERRIDES:
            if keyword in haystack:
                return replacement
    return sector


def search_blob(listing: dict) -> str:
    """Matches the data-search format already used in listings.html cards."""
    title = clean_title(listing.get("name", ""))
    price = format_price_card(listing)
    sector = get_sector(listing)
    city = listing.get("city") or ""
    parts = [
        title.lower(),
        f"{price.lower()}, {sector.lower()}, {city.lower()}" if price != "price on request" else f"{sector.lower()}, {city.lower()}",
        f"{sector.lower()}, {city.lower()}",
        city.lower(),
    ]
    return " ".join(p for p in parts if p)
