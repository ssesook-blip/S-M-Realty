"""
Auto-updating listing sections on hand-written pages.

Some pages (community spotlights like casa-linda.html, and buyer guides like
owner-financing-dominican-republic.html) are written by hand, but include a
block of listing cards that should always match what's actually for sale.

Those blocks are wrapped in marker comments:

    <!-- AUTO:some-key:start -->
    ...generated HTML...
    <!-- AUTO:some-key:end -->

Everything between a start/end pair is regenerated from
property_details_cache.json on every pipeline run. Everything outside the
markers (your written content, photos, layout) is never touched.

To add another auto-updating page later, add markers to the page and a small
entry in update_all_auto_sections() below.
"""
import html
import os
import re

from lib import clean_title, format_price_card, gallery_urls, get_sector


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _replace_block(content: str, key: str, new_html: str) -> tuple:
    pattern = re.compile(
        r"(<!-- AUTO:" + re.escape(key) + r":start -->)(.*?)(<!-- AUTO:" + re.escape(key) + r":end -->)",
        re.DOTALL,
    )
    new_content, n = pattern.subn(lambda m: m.group(1) + "\n" + new_html + "\n" + m.group(3), content, count=1)
    return new_content, n


def _update_file(path: str, blocks: dict) -> bool:
    if not os.path.exists(path):
        print(f"  (auto sections: {os.path.basename(path)} not found, skipped)")
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    for key, new_html in blocks.items():
        content, n = _replace_block(content, key, new_html)
        if n == 0:
            print(f"  (auto sections: marker '{key}' not found in {os.path.basename(path)})")
    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Updated auto sections in {os.path.basename(path)}")
        return True
    return False


def _short_price(value) -> str:
    """$230,900 -> $230.9K ; $1,350,000 -> $1.35M"""
    if value >= 1_000_000:
        s = f"{value / 1_000_000:.2f}".rstrip("0").rstrip(".")
        return f"${s}M"
    s = f"{value / 1_000:.1f}".rstrip("0").rstrip(".")
    return f"${s}K"


def _spread_pick(items: list, n: int) -> list:
    """Pick n items spread evenly across an already-sorted list, so a
    spotlight shows the full range (entry-level to top end) rather than
    just the cheapest few."""
    if len(items) <= n:
        return items
    step = (len(items) - 1) / (n - 1)
    return [items[round(i * step)] for i in range(n)]


def spotlight_card(d: dict, tag: str = "") -> str:
    slug = d["slug"]
    title = clean_title(d.get("name", ""))
    images = gallery_urls(d)
    image = images[0] if images else ""
    price = format_price_card(d)
    sector = get_sector(d)
    city = d.get("city", "")
    addr = ", ".join(x for x in (sector, city) if x)
    if d.get("room") is not None:
        baths = d.get("bathroom") or 0
        baths = int(baths) if float(baths).is_integer() else baths
        meta = f'<div class="listing-meta"><span>{d.get("room")} Bed</span><span>{baths} Bath</span></div>'
    else:
        meta = ""
    tag_html = f'\n          <div class="listing-terms">{html.escape(tag)}</div>' if tag else ""
    return f'''      <a href="properties/{slug}.html" class="listing reveal">
        <div class="photo">
          <img src="{image}" alt="{html.escape(title)}" loading="lazy">
        </div>
        <div class="listing-body">
          <div class="listing-title">{html.escape(title)}</div>
          <div class="listing-row">
            <div>
              <div class="listing-price">{html.escape(price)}</div>
              <div class="listing-addr">{html.escape(addr)}</div>
            </div>
            {meta}
          </div>{tag_html}
        </div>
      </a>'''


def _by_price(listings: list) -> list:
    return sorted(listings, key=lambda d: (d.get("sale_price") or 10**12))


# --------------------------------------------------------------------------
# Community spotlight pages (e.g. casa-linda.html)
# --------------------------------------------------------------------------

COMMUNITY_PAGES = {
    # file name       : community name as returned by get_sector()
    "casa-linda.html": "Casa Linda",
}
COMMUNITY_CARD_COUNT = 6


def community_blocks(listings: list, key_prefix: str) -> dict:
    listings = _by_price(listings)
    prices = [d["sale_price"] for d in listings if d.get("sale_price")]
    beds = [int(d["room"]) for d in listings if d.get("room")]

    count = str(len(listings))
    if prices:
        lo, hi = min(prices), max(prices)
        price_range = _short_price(lo) if lo == hi else f"{_short_price(lo)}&ndash;{_short_price(hi)}"
    else:
        price_range = "&mdash;"
    if beds:
        bed_range = str(min(beds)) if min(beds) == max(beds) else f"{min(beds)}&ndash;{max(beds)}"
    else:
        bed_range = "&mdash;"

    cards = "\n\n".join(spotlight_card(d) for d in _spread_pick(listings, COMMUNITY_CARD_COUNT))
    return {
        f"{key_prefix}-count": f'        <span class="stat-number">{count}</span>',
        f"{key_prefix}-price-range": f'        <span class="stat-number">{price_range}</span>',
        f"{key_prefix}-bedrooms": f'        <span class="stat-number">{bed_range}</span>',
        f"{key_prefix}-cards": cards or '      <p>New listings in this community are coming soon. Contact us for off-market options.</p>',
    }


# --------------------------------------------------------------------------
# Owner-financing guide
# --------------------------------------------------------------------------

OWNER_FINANCING_PAGE = "owner-financing-dominican-republic.html"
FINANCING_PATTERN = re.compile(
    r"(owner|seller|vendor|developer)[\s-]*financ"
    r"|financing\s+(is\s+)?available"
    r"|financiamiento\s+(directo|del\s+(propietario|due))",
    re.IGNORECASE,
)


def offers_financing(d: dict) -> bool:
    text = f"{d.get('name', '')} {d.get('description') or ''}"
    return bool(FINANCING_PATTERN.search(text))


def owner_financing_blocks(listings: list) -> dict:
    matches = _by_price([d for d in listings if offers_financing(d)])
    n = len(matches)
    count_html = (
        f'    <p class="auto-count reveal">{n} owner-financed {"property" if n == 1 else "properties"} available right now</p>'
        if n else
        '    <p class="auto-count reveal">No owner-financed listings right now. Message us; new ones come up regularly.</p>'
    )
    cards = "\n\n".join(spotlight_card(d, tag="Financing available") for d in matches)
    return {
        "owner-financing-count": count_html,
        "owner-financing-cards": cards,
    }


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def update_all_auto_sections(site_dir: str, details: list):
    """details: list of full listing detail dicts currently on the site."""
    for filename, community in COMMUNITY_PAGES.items():
        in_community = [d for d in details if get_sector(d) == community]
        prefix = filename.rsplit(".", 1)[0]
        _update_file(os.path.join(site_dir, filename), community_blocks(in_community, prefix))

    _update_file(os.path.join(site_dir, OWNER_FINANCING_PAGE), owner_financing_blocks(details))
