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
    # slug as a tie-breaker keeps the order identical from run to run, so a
    # page only "changes" (and gets a new sitemap date) when listings do.
    return sorted(listings, key=lambda d: (d.get("sale_price") or 10**12, d.get("slug", "")))


# --------------------------------------------------------------------------
# Community spotlight pages (e.g. casa-linda.html)
# --------------------------------------------------------------------------

COMMUNITY_PAGES = {
    # file name       : community name as returned by get_sector()
    "casa-linda.html": "Casa Linda",
}
COMMUNITY_CARD_COUNT = 6


def community_blocks(listings: list, key_prefix: str, card_count: int = COMMUNITY_CARD_COUNT) -> dict:
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

    cards = "\n\n".join(spotlight_card(d) for d in _spread_pick(listings, card_count))
    return {
        f"{key_prefix}-count": f'        <span class="stat-number">{count}</span>',
        f"{key_prefix}-price-range": f'        <span class="stat-number">{price_range}</span>',
        f"{key_prefix}-bedrooms": f'        <span class="stat-number">{bed_range}</span>',
        f"{key_prefix}-cards": cards or '      <p>New listings in this community are coming soon. Contact us for off-market options.</p>',
    }


# --------------------------------------------------------------------------
# Town and community area pages (sosua-real-estate.html etc.)
# --------------------------------------------------------------------------
# file name : (marker key, how to pick listings, number of cards to show)

def _city(name):
    return lambda d: (d.get("city") or "") == name


def _sector(name):
    return lambda d: get_sector(d) == name


AREA_PAGES = {
    "sosua-real-estate.html":         ("sosua", _city("Sosúa"), 12),
    "cabarete-real-estate.html":      ("cabarete", _city("Cabarete"), 12),
    "puerto-plata-real-estate.html":  ("puerto-plata", _city("Puerto Plata"), 9),
    "sosua-ocean-village.html":       ("sosua-ocean-village", _sector("Sosúa Ocean Village"), 9),
    "hispaniola-sosua.html":          ("hispaniola", _sector("Hispaniola"), 9),
    "el-choco-sosua.html":            ("el-choco", _sector("El Choco"), 9),
    "el-batey-sosua.html":            ("el-batey", _sector("El Batey"), 9),
    "kite-beach-cabarete.html":       ("kite-beach", _sector("Kite Beach"), 9),
    "encuentro-beach-cabarete.html":  ("encuentro", _sector("Encuentro Beach"), 9),
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
# Homepage "Explore by Area" section (index.html) and Casa Linda teaser
# --------------------------------------------------------------------------

HOME_TOWNS = [
    ("sosua-real-estate.html", "Sosúa", "Calm swimming beach, the widest choice of homes and everyday convenience."),
    ("cabarete-real-estate.html", "Cabarete", "Beach and watersports town, with strong demand for condos and rentals."),
    ("puerto-plata-real-estate.html", "Puerto Plata", "The region's main city: more space for the money, plus nearby Costambar."),
]
HOME_COMMUNITIES = [
    "sosua-ocean-village.html", "casa-linda.html", "hispaniola-sosua.html", "el-choco-sosua.html",
    "el-batey-sosua.html", "kite-beach-cabarete.html", "encuentro-beach-cabarete.html",
]
COMMUNITY_NAMES = {
    "sosua-ocean-village.html": "Sosúa Ocean Village", "casa-linda.html": "Casa Linda",
    "hispaniola-sosua.html": "Hispaniola", "el-choco-sosua.html": "El Choco",
    "el-batey-sosua.html": "El Batey", "kite-beach-cabarete.html": "Kite Beach",
    "encuentro-beach-cabarete.html": "Encuentro Beach",
}


def _area_listings(filename: str, details: list) -> list:
    if filename == "casa-linda.html":
        return [d for d in details if get_sector(d) == "Casa Linda"]
    _key, pick, _n = AREA_PAGES[filename]
    return [d for d in details if pick(d)]


def _from_price(listings: list) -> str:
    """'· homes from $X', using only listings with bedrooms so a cheap
    land lot doesn't make an area look cheaper than its homes are."""
    prices = [d["sale_price"] for d in listings if d.get("sale_price") and d.get("room")]
    return f"\u00b7 homes from {_short_price(min(prices))}" if prices else ""


def _hero_image(listings: list) -> str:
    """Photo for a town card: the priciest listing with a photo tends to have
    the most striking one."""
    for d in sorted(listings, key=lambda d: (-(d.get("sale_price") or 0), d.get("slug", ""))):
        imgs = gallery_urls(d)
        if imgs:
            return imgs[0]
    return ""


def home_area_blocks(details: list) -> dict:
    towns = []
    for href, name, blurb in HOME_TOWNS:
        ls = _area_listings(href, details)
        img = _hero_image(ls)
        meta = f"{len(ls)} listings {_from_price(ls)}".strip()
        towns.append(f'''      <a href="{href}" class="area-card reveal">
        <div class="area-card-photo photo">{f'<img src="{img}" alt="Property for sale in {html.escape(name)}" loading="lazy">' if img else ''}</div>
        <div class="area-card-body">
          <h3>{html.escape(name)}</h3>
          <p>{html.escape(blurb)}</p>
          <span class="area-card-meta">{html.escape(meta)}</span>
        </div>
      </a>''')
    tiles = []
    for href in HOME_COMMUNITIES:
        ls = _area_listings(href, details)
        meta = f"{len(ls)} listings {_from_price(ls)}".strip()
        tiles.append(f'''      <a href="{href}" class="area-tile reveal">
        <span class="area-tile-name">{html.escape(COMMUNITY_NAMES[href])}</span>
        <span class="area-tile-meta">{html.escape(meta)}</span>
      </a>''')
    return {
        "home-area-towns": "\n".join(towns),
        "home-area-communities": "\n".join(tiles),
    }


def casa_linda_teaser_block(details: list) -> dict:
    ls = _area_listings("casa-linda.html", details)
    prices = [d["sale_price"] for d in ls if d.get("sale_price")]
    if prices:
        text = f"{len(ls)} homes currently listed from {format_price_card({'sale_price': min(prices)})} to {format_price_card({'sale_price': max(prices)})}."
    else:
        text = "Ask us about homes currently available."
    return {"home-casa-linda-summary": text}


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Property page titles: unique, tidy and not too long for Google
# ---------------------------------------------------------------------------
TITLE_BRAND = " \u2014 S & M Realty"
TITLE_MAX = 65


def _cut_words(text: str, limit: int) -> str:
    """Shortens a name to fit, preferring to drop middle sections first
    ('Encuentro Residences \u2014 Choose Your Lot, Choose Your Villa - Villa D6'
    -> 'Encuentro Residences \u2014 Villa D6'), then whole words from the end."""
    if len(text) <= limit:
        return text
    parts = re.split(r"(\s[-\u2013\u2014:|]\s)", text)
    while len(text) > limit and len(parts) >= 5:
        del parts[1:3]
        text = "".join(parts)
    if len(text) <= limit:
        return text
    cut = text[:limit + 1].rsplit(" ", 1)[0]
    words = cut.rstrip(" -\u2013\u2014,:;&/(").split(" ")
    while len(words) > 1 and words[-1].lower() in ("a", "an", "and", "at", "for", "in", "of", "on", "or", "the", "to", "with", "-", "\u2013", "\u2014"):
        words.pop()
    return " ".join(words).rstrip(" -\u2013\u2014,:;&/(")


def _listing_ref(d: dict) -> str:
    m = re.search(r"-(\d+)$", d.get("slug", ""))
    return m.group(1) if m else str(d.get("cid") or d.get("uid") or "")


def _fit(name: str, suffix: str = "") -> str:
    if len(name) + len(suffix) + len(TITLE_BRAND) <= TITLE_MAX:
        return name + suffix + TITLE_BRAND
    short = _cut_words(name, TITLE_MAX - len(suffix)) + suffix
    return short + TITLE_BRAND if len(short) + len(TITLE_BRAND) <= TITLE_MAX else short


def property_page_titles(details: list) -> dict:
    """slug -> the <title> text for that listing page: tidy, at most 65
    characters, and unique. Listings that would otherwise share a title
    (units in the same development) get the price, then the reference
    number, added."""
    names = {d["slug"]: clean_title(d.get("name", "")) for d in details if d.get("slug")}
    groups = {}
    for d in details:
        if d.get("slug") in names:
            groups.setdefault(_fit(names[d["slug"]]).lower(), []).append(d)

    titles = {}
    for group in groups.values():
        if len(group) == 1:
            d = group[0]
            titles[d["slug"]] = _fit(names[d["slug"]])
            continue
        prices = {d["slug"]: (_short_price(d["sale_price"]) if d.get("sale_price") else "") for d in group}
        price_unique = all(prices.values()) and len(set(prices.values())) == len(group)
        for d in group:
            if price_unique:
                suffix = f" \u2013 {prices[d['slug']]}"
            elif prices[d["slug"]]:
                suffix = f" \u2013 {prices[d['slug']]} \u2013 Ref {_listing_ref(d)}"
            else:
                suffix = f" \u2013 Ref {_listing_ref(d)}"
            titles[d["slug"]] = _fit(names[d["slug"]], suffix)
    return titles


def tidy_property_pages(site_dir: str, details: list) -> int:
    """Every run: sets each listing page's <title>/og:title from
    property_page_titles(), and turns any second <h1> (some developers put
    one inside their description) into an <h2>. Only rewrites a file when
    something actually changes."""
    titles = property_page_titles(details)
    changed = 0
    for slug, title in titles.items():
        path = os.path.join(site_dir, "properties", f"{slug}.html")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        original = content
        content = re.sub(r"<title>.*?</title>",
                         lambda m: f"<title>{html.escape(title, quote=False)}</title>",
                         content, count=1, flags=re.S)
        content = re.sub(r'<meta property="og:title" content="[^"]*">',
                         lambda m: f'<meta property="og:title" content="{html.escape(title)}">',
                         content, count=1)
        first = content.find("<h1")
        if first != -1:
            head, rest = content[:first + 3], content[first + 3:]
            end = rest.find("</h1>") + 5
            rest = rest[:end] + re.sub(r"<(/?)h1\b", r"<\1h2", rest[end:])
            content = head + rest
        if content != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            changed += 1
    if changed:
        print(f"  Tidied titles/headings on {changed} listing page(s).")
    return changed


def update_all_auto_sections(site_dir: str, details: list):
    """details: list of full listing detail dicts currently on the site."""
    for filename, community in COMMUNITY_PAGES.items():
        in_community = [d for d in details if get_sector(d) == community]
        prefix = filename.rsplit(".", 1)[0]
        _update_file(os.path.join(site_dir, filename), community_blocks(in_community, prefix))

    _update_file(os.path.join(site_dir, OWNER_FINANCING_PAGE), owner_financing_blocks(details))

    for filename, (key, pick, n_cards) in AREA_PAGES.items():
        _update_file(os.path.join(site_dir, filename),
                     community_blocks([d for d in details if pick(d)], key, n_cards))

    home_blocks = home_area_blocks(details)
    home_blocks.update(casa_linda_teaser_block(details))
    _update_file(os.path.join(site_dir, "index.html"), home_blocks)

    tidy_property_pages(site_dir, details)
