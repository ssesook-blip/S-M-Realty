"""
Incremental site updater for S&M Realty.

Workflow:
  1. Fetch current listings (summary) for the configured search terms.
  2. Compare slugs against known_listings.json (the set already on the site).
  3. For genuinely new slugs, fetch full detail records.
  4. Generate a properties/<slug>.html page for each.
  5. Insert a card for each into listings.html.
  6. Update the running totals shown on the page (header count, filter count, JS).
  7. Update known_listings.json so the next run only picks up newer listings.

This script is written to run standalone (e.g. from GitHub Actions) given:
  - AETOKEN env var (AlterEstate API token)
  - repo checked out with site/ (index.html, listings.html, properties/, css/, js/)
    and known_listings.json at the repo root
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from generate_page import generate_property_page
from generate_card import generate_listing_card

import requests

TOKEN = os.environ.get("AETOKEN", "")
FILTER_URL = "https://secure.alterestate.com/api/v1/properties/filter/"
DETAIL_URL = "https://secure.alterestate.com/api/v1/properties/view/{slug}/"
SEARCH_TERMS = ["Costambar", "Sosua", "Cabarete", "Puerto Plata"]

SITE_DIR = os.environ.get("SITE_DIR", ".")
PROPERTIES_DIR = os.path.join(SITE_DIR, "properties")
LISTINGS_HTML = os.path.join(SITE_DIR, "listings.html")
INDEX_HTML = os.path.join(SITE_DIR, "index.html")
KNOWN_LISTINGS_FILE = os.path.join(SITE_DIR, "known_listings.json")
DETAILS_CACHE_FILE = os.path.join(SITE_DIR, "property_details_cache.json")


def load_details_cache() -> dict:
    if os.path.exists(DETAILS_CACHE_FILE):
        with open(DETAILS_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_details_cache(cache: dict):
    with open(DETAILS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
SITEMAP_FILE = os.path.join(SITE_DIR, "sitemap.xml")

STATIC_PAGES = ["", "listings.html", "buying-guide.html"]


def generate_sitemap(slugs: set):
    from lib import SITE_URL
    import datetime

    today = datetime.date.today().isoformat()
    urls = []
    for page in STATIC_PAGES:
        loc = f"{SITE_URL}/{page}" if page else f"{SITE_URL}/"
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n  </url>")
    for slug in sorted(slugs):
        loc = f"{SITE_URL}/properties/{slug}.html"
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n  </url>")

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) +
        "\n</urlset>\n"
    )
    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"  sitemap.xml written with {len(urls)} URLs.")


FEED_FILE = os.path.join(SITE_DIR, "properties-feed.xml")


def generate_properties_feed(details: list):
    """Standalone real estate listing feed built directly from this website's
    own data (only the properties actually shown on sheenaandmichaelrealtydr.com),
    independent of AlterEstate's own account-level portal syndication.
    Uses common, widely-recognized real estate feed fields so most portal
    intake systems (Properstar/ListGlobally included) can read or adapt to it."""
    from lib import clean_title, get_sector, gallery_urls, SITE_URL, strip_description
    import datetime
    import xml.sax.saxutils as sx

    def esc(s):
        return sx.escape(str(s or ""))

    today = datetime.date.today().isoformat()
    items = []
    for d in details:
        slug = d.get("slug", "")
        title = clean_title(d.get("name", ""))
        price = d.get("sale_price") or 0
        currency = d.get("currency_sale") or "USD"
        city = d.get("city") or ""
        sector = get_sector(d)
        beds = d.get("room", 0)
        baths = d.get("bathroom", 0)
        area = d.get("property_area", 0)
        area_unit = d.get("property_area_measurer") or "m2"
        category = (d.get("category") or {}).get("name_en", "") or ""
        description = strip_description(d.get("description") or "", max_chars=2000)
        images = gallery_urls(d)
        photos_xml = "\n    ".join(f"<Photo><URL>{esc(u)}</URL></Photo>" for u in images)
        listing_url = f"{SITE_URL}/properties/{slug}.html"

        items.append(f'''  <Listing>
    <ListingID>{esc(slug)}</ListingID>
    <ListingURL>{esc(listing_url)}</ListingURL>
    <Title>{esc(title)}</Title>
    <Description>{esc(description)}</Description>
    <PropertyType>{esc(category)}</PropertyType>
    <ListingStatus>Active</ListingStatus>
    <Price currency="{esc(currency)}">{price}</Price>
    <Bedrooms>{beds}</Bedrooms>
    <Bathrooms>{baths}</Bathrooms>
    <LivingArea unit="{esc(area_unit)}">{area}</LivingArea>
    <Address>
      <City>{esc(city)}</City>
      <Neighborhood>{esc(sector)}</Neighborhood>
      <Country>Dominican Republic</Country>
    </Address>
    <Photos>
    {photos_xml}
    </Photos>
    <ProviderName>S &amp; M Realty</ProviderName>
    <ProviderURL>{esc(SITE_URL)}</ProviderURL>
    <LeadRoutingEmail>info@sheenaandmichaelrealtydr.com</LeadRoutingEmail>
  </Listing>''')

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<PropertyFeed generated="{today}" provider="S &amp; M Realty" source="{SITE_URL}">\n'
        + "\n".join(items) +
        "\n</PropertyFeed>\n"
    )
    with open(FEED_FILE, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"  properties-feed.xml written with {len(items)} listings.")


def fetch_all_listings():
    headers = {"aetoken": TOKEN}
    all_results = []
    url = FILTER_URL
    for term in SEARCH_TERMS:
        params = {"search": term}
        page_url = url
        while page_url:
            resp = requests.get(page_url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            all_results.extend(data.get("results", []))
            page_url = data.get("next")
            params = None
    dedup = {p["cid"]: p for p in all_results}
    return list(dedup.values())


def fetch_detail(slug):
    headers = {"aetoken": TOKEN}
    resp = requests.get(DETAIL_URL.format(slug=slug), headers=headers)
    resp.raise_for_status()
    return resp.json()


def load_known_slugs():
    if os.path.exists(KNOWN_LISTINGS_FILE):
        with open(KNOWN_LISTINGS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    # First run: seed from whatever's already in properties/
    if os.path.isdir(PROPERTIES_DIR):
        return {fn[:-5] for fn in os.listdir(PROPERTIES_DIR) if fn.endswith(".html")}
    return set()


def save_known_slugs(slugs):
    with open(KNOWN_LISTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(slugs), f, indent=2, ensure_ascii=False)


def remove_cards_from_listings_html(removed_slugs: set):
    if not removed_slugs:
        return
    with open(LISTINGS_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    for slug in removed_slugs:
        # Match from this card's opening <a> up to its closing </a>.
        # Cards don't nest anchor tags, so a non-greedy match to the next
        # </a> always lands on this card's own closing tag.
        pattern = re.compile(
            r'\s*<a href="properties/' + re.escape(slug) + r'\.html".*?</a>\s*\n?',
            re.DOTALL,
        )
        content, n = pattern.subn("", content, count=1)
        if n == 0:
            print(f"    (card for {slug} not found in listings.html — already removed?)")

    with open(LISTINGS_HTML, "w", encoding="utf-8") as f:
        f.write(content)


def insert_cards_into_listings_html(new_cards_html: str):
    if not new_cards_html:
        return
    with open(LISTINGS_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    marker = '<p class="no-results" id="no-results">'
    idx = content.index(marker)
    content = content[:idx] + new_cards_html + content[idx:]

    with open(LISTINGS_HTML, "w", encoding="utf-8") as f:
        f.write(content)


def update_listing_counts(new_total: int):
    with open(LISTINGS_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Update "All N active listings" copy in the page header
    content = re.sub(
        r"All \d+ active listings", f"All {new_total} active listings", content
    )

    # Update "Showing N of N" in the filter-count span
    content = re.sub(
        r'(id="result-count">Showing )\d+( of )\d+',
        rf"\g<1>{new_total}\g<2>{new_total}",
        content,
    )

    with open(LISTINGS_HTML, "w", encoding="utf-8") as f:
        f.write(content)

    # Update the hardcoded total in listings-filter.js
    js_path = os.path.join(SITE_DIR, "js", "listings-filter.js")
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()
        js = re.sub(r"of \d+`", f"of {new_total}`", js)
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(js)


def update_index_html(new_total: int):
    if not os.path.exists(INDEX_HTML):
        return
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r"View All \d+ Listings", f"View All {new_total} Listings", content
    )
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(content)


def count_existing_cards() -> int:
    with open(LISTINGS_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'class="listing reveal"', content))


def delete_property_files(removed_slugs: set):
    for slug in removed_slugs:
        path = os.path.join(PROPERTIES_DIR, f"{slug}.html")
        if os.path.exists(path):
            os.remove(path)


def replace_all_cards_in_listings_html(all_cards_html: str):
    """Used only in --full mode: swaps the entire card grid at once instead
    of inserting/removing individual cards."""
    with open(LISTINGS_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    grid_marker = 'id="listings-grid">'
    end_marker = '<p class="no-results" id="no-results">'
    start = content.index(grid_marker) + len(grid_marker)
    end = content.index(end_marker)
    content = content[:start] + all_cards_html + content[end:]

    with open(LISTINGS_HTML, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if not TOKEN:
        print("ERROR: AETOKEN environment variable not set.")
        sys.exit(1)

    full_rebuild = os.environ.get("FULL_REBUILD", "").lower() in ("1", "true", "yes")

    print("Fetching current listing summaries...")
    summaries = fetch_all_listings()
    current_slugs = {s["slug"]: s for s in summaries}
    print(f"  {len(current_slugs)} listings currently match the search terms.")

    if full_rebuild:
        print("FULL REBUILD requested: regenerating every listing page and card...")
        os.makedirs(PROPERTIES_DIR, exist_ok=True)
        all_cards = []
        all_details = []
        ok_slugs = []
        for slug in sorted(current_slugs):
            print(f"  Refreshing {slug} ...")
            try:
                detail = fetch_detail(slug)
            except requests.exceptions.HTTPError as e:
                print(f"    FAILED: {e}")
                continue
            page_html = generate_property_page(detail)
            with open(os.path.join(PROPERTIES_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
                f.write(page_html)
            all_cards.append(generate_listing_card(detail))
            all_details.append(detail)
            ok_slugs.append(slug)

        replace_all_cards_in_listings_html("".join(all_cards))
        new_total = len(ok_slugs)
        update_listing_counts(new_total)
        update_index_html(new_total)
        save_known_slugs(set(ok_slugs))
        generate_sitemap(set(ok_slugs))
        save_details_cache({slug: d for slug, d in zip(ok_slugs, all_details)})
        generate_properties_feed(all_details)
        print(f"Full rebuild complete. Site now shows {new_total} listings.")
        return

    known = load_known_slugs()
    new_slugs = set(current_slugs) - known
    removed_slugs = known - set(current_slugs)
    print(f"  {len(new_slugs)} new listing(s) to add.")
    print(f"  {len(removed_slugs)} listing(s) no longer returned by the API (will be removed).")

    if not new_slugs and not removed_slugs:
        print("Nothing changed. Site is up to date.")
        return

    os.makedirs(PROPERTIES_DIR, exist_ok=True)
    new_cards = []
    added_slugs = []
    added_details = {}

    for slug in sorted(new_slugs):
        print(f"  Fetching detail for {slug} ...")
        try:
            detail = fetch_detail(slug)
        except requests.exceptions.HTTPError as e:
            print(f"    FAILED: {e}")
            continue

        page_html = generate_property_page(detail)
        page_path = os.path.join(PROPERTIES_DIR, f"{slug}.html")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_html)

        new_cards.append(generate_listing_card(detail))
        added_slugs.append(slug)
        added_details[slug] = detail

    if removed_slugs:
        print(f"  Removing {len(removed_slugs)} delisted page(s) and card(s)...")
        remove_cards_from_listings_html(removed_slugs)
        delete_property_files(removed_slugs)

    if new_cards:
        insert_cards_into_listings_html("".join(new_cards))

    new_total = count_existing_cards()
    update_listing_counts(new_total)
    update_index_html(new_total)

    updated_known = (known | set(added_slugs)) - removed_slugs
    save_known_slugs(updated_known)
    generate_sitemap(updated_known)

    cache = load_details_cache()
    cache.update(added_details)
    for slug in removed_slugs:
        cache.pop(slug, None)
    save_details_cache(cache)
    generate_properties_feed([cache[s] for s in updated_known if s in cache])

    print(
        f"Added {len(added_slugs)} listing(s), removed {len(removed_slugs)} listing(s). "
        f"Site now shows {new_total} listings."
    )


if __name__ == "__main__":
    main()
