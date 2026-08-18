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


# AlterEstate's amenity data comes back in Spanish (it's a Dominican Republic
# platform). This maps the common terms to English for display on the site.
# Unmatched terms fall back to a cleaned-up (title-cased) version of the
# original rather than disappearing, so nothing silently vanishes if a new
# amenity term shows up that isn't in this list yet.
AMENITY_TRANSLATIONS = {
    "AMUEBLADO": "Furnished",
    "SEMI AMUEBLADO": "Semi-Furnished",
    "SIN AMUEBLAR": "Unfurnished",
    "AREA DE JUEGOS INFANTILES": "Children's Play Area",
    "AREA INFANTIL": "Children's Play Area",
    "BALCÓN": "Balcony",
    "BALCON": "Balcony",
    "BALCÓN TIPO TERRAZA": "Terrace Balcony",
    "BALCON TIPO TERRAZA": "Terrace Balcony",
    "TERRAZA": "Terrace",
    "CANCHA DE BASKET BALL": "Basketball Court",
    "CANCHA DE BALONCESTO": "Basketball Court",
    "CANCHA DE TENIS": "Tennis Court",
    "CANCHA DE PADEL": "Padel Court",
    "CANCHA DE PÁDEL": "Padel Court",
    "CANCHA MULTIUSO": "Multi-Purpose Court",
    "CENTROS COMERCIALES CERCANOS": "Nearby Shopping Centers",
    "SUPERMERCADO CERCANO": "Nearby Supermarket",
    "GAS COMÚN": "Gas Utility Included",
    "GAS COMUN": "Gas Utility Included",
    "LOBBY": "Lobby",
    "PARQUEOS": "Parking",
    "PARQUEO": "Parking",
    "PARQUEO TECHADO": "Covered Parking",
    "PARQUEO VISITANTE": "Visitor Parking",
    "PLANTA ELÉCTRICA": "Backup Generator",
    "PLANTA ELECTRICA": "Backup Generator",
    "INVERSOR": "Power Inverter",
    "RESIDENCIAL CERRADO": "Gated Community",
    "URBANIZACIÓN CERRADA": "Gated Community",
    "URBANIZACION CERRADA": "Gated Community",
    "VIGILANCIA 24 HORAS": "24-Hour Security",
    "SEGURIDAD 24 HORAS": "24-Hour Security",
    "SEGURIDAD": "Security",
    "PISCINA": "Pool",
    "PISCINA COMÚN": "Shared Pool",
    "PISCINA COMUN": "Shared Pool",
    "PISCINA PRIVADA": "Private Pool",
    "JACUZZI": "Jacuzzi",
    "GIMNASIO": "Gym",
    "AREA SOCIAL": "Social Area",
    "ÁREA SOCIAL": "Social Area",
    "SALON DE FIESTAS": "Event Room",
    "SALÓN DE FIESTAS": "Event Room",
    "SALA DE JUEGOS": "Game Room",
    "ÁREA BBQ": "BBQ Area",
    "AREA BBQ": "BBQ Area",
    "ASCENSOR": "Elevator",
    "ELEVADOR": "Elevator",
    "LAVANDERÍA": "Laundry Room",
    "LAVANDERIA": "Laundry Room",
    "AREA DE LAVADO": "Laundry Area",
    "ÁREA DE LAVADO": "Laundry Area",
    "AIRE ACONDICIONADO": "Air Conditioning",
    "CALENTADOR": "Water Heater",
    "CISTERNA": "Water Cistern",
    "TANQUE DE AGUA": "Water Tank",
    "BOMBA DE AGUA": "Water Pump",
    "WALK IN CLOSET": "Walk-In Closet",
    "CLOSET": "Closets",
    "COCINA EQUIPADA": "Equipped Kitchen",
    "LINEA BLANCA": "Appliances Included",
    "LÍNEA BLANCA": "Appliances Included",
    "AMOBLADO": "Furnished",
    "VISTA AL MAR": "Ocean View",
    "VISTA PANORAMICA": "Panoramic View",
    "VISTA PANORÁMICA": "Panoramic View",
    "ACCESO A LA PLAYA": "Beach Access",
    "FRENTE A LA PLAYA": "Beachfront",
    "JARDIN": "Garden",
    "JARDÍN": "Garden",
    "ÁREA VERDE": "Green Area",
    "AREA VERDE": "Green Area",
    "PET FRIENDLY": "Pet Friendly",
    "SE ACEPTAN MASCOTAS": "Pets Allowed",
    "AMENIDADES DE LUJO": "Luxury Amenities",
    "MUELLE": "Dock",
    "CANCHA DE VOLEIBOL": "Volleyball Court",
    "AREA COMERCIAL": "Commercial Area",
    "ÁREA COMERCIAL": "Commercial Area",
}


def translate_amenity(term: str) -> str:
    key = term.strip().upper()
    if key in AMENITY_TRANSLATIONS:
        return AMENITY_TRANSLATIONS[key]
    return _word_level_translate(term)


# Fallback for any amenity phrase not covered by the exact-match dictionary
# above. Translates word-by-word using common Spanish real-estate vocabulary,
# so a brand-new term the site has never seen still comes out in English
# instead of silently staying in Spanish. Not as polished as a proper phrase
# match, but it means nothing slips through untranslated going forward.
WORD_TRANSLATIONS = {
    "de": "", "del": "", "con": "with", "y": "and", "en": "in", "a": "to",
    "la": "", "el": "", "los": "", "las": "", "un": "", "una": "",
    "area": "Area", "área": "Area", "cancha": "Court", "campo": "Field",
    "piscina": "Pool", "alberca": "Pool", "jardin": "Garden", "jardín": "Garden",
    "terraza": "Terrace", "balcon": "Balcony", "balcón": "Balcony",
    "parqueo": "Parking", "parqueos": "Parking", "estacionamiento": "Parking",
    "garaje": "Garage", "seguridad": "Security", "vigilancia": "Security",
    "residencial": "Residential", "cerrado": "Gated", "cerrada": "Gated",
    "amueblado": "Furnished", "amoblado": "Furnished", "sin": "Without",
    "gimnasio": "Gym", "elevador": "Elevator", "ascensor": "Elevator",
    "lavanderia": "Laundry", "lavandería": "Laundry", "lavado": "Laundry",
    "planta": "Generator", "electrica": "Electric", "eléctrica": "Electric",
    "inversor": "Inverter", "generador": "Generator", "gas": "Gas",
    "comun": "Shared", "común": "Shared", "privada": "Private", "privado": "Private",
    "vista": "View", "mar": "Ocean", "playa": "Beach", "frente": "Front",
    "panoramica": "Panoramic", "panorámica": "Panoramic",
    "infantil": "Children's", "infantiles": "Children's", "juegos": "Play",
    "ninos": "Kids", "niños": "Kids", "tenis": "Tennis", "basket": "Basketball",
    "baloncesto": "Basketball", "voleibol": "Volleyball", "padel": "Padel",
    "multiuso": "Multi-Purpose", "salon": "Room", "salón": "Room",
    "fiestas": "Event", "social": "Social", "comercial": "Commercial",
    "comerciales": "Commercial", "centros": "Centers", "cercanos": "Nearby",
    "cercano": "Nearby", "supermercado": "Supermarket", "closet": "Closet",
    "cocina": "Kitchen", "equipada": "Equipped", "equipado": "Equipped",
    "calentador": "Water Heater", "cisterna": "Water Cistern",
    "tanque": "Tank", "agua": "Water", "bomba": "Pump", "aire": "Air",
    "acondicionado": "Conditioning", "mascotas": "Pets", "aceptan": "Allowed",
    "muelle": "Dock", "lujo": "Luxury", "amenidades": "Amenities",
    "urbanizacion": "Community", "urbanización": "Community",
    "24": "24-Hour", "horas": "Hour", "techado": "Covered", "visitante": "Visitor",
    "visitantes": "Visitors", "para": "for", "montana": "Mountain", "montaña": "Mountain",
    "sala": "Room", "cine": "Cinema", "zona": "Zone", "barbacoa": "BBQ", "asador": "Grill",
    "techo": "Roof", "patio": "Patio", "huerto": "Garden", "solar": "Lot",
    "deposito": "Storage", "depósito": "Storage", "trastero": "Storage Room",
    "oficina": "Office", "recepcion": "Reception", "recepción": "Reception",
    "portero": "Doorman", "conserje": "Concierge", "camara": "Camera", "cámara": "Camera",
    "camaras": "Cameras", "cámaras": "Cameras", "vigilante": "Guard", "alarma": "Alarm",
    "cerca": "Fence", "cable": "Cable", "internet": "Internet", "wifi": "WiFi",
    "fibra": "Fiber", "optica": "Optic", "óptica": "Optic", "walk": "Walk-In",
    "in": "In", "spa": "Spa", "sauna": "Sauna", "bar": "Bar", "grill": "Grill",
    "coworking": "Coworking", "yoga": "Yoga", "pilates": "Pilates", "estudio": "Studio",
    "biblioteca": "Library", "juegos": "Play Area", "recreativa": "Recreational",
    "recreativo": "Recreational", "deportiva": "Sports", "deportivo": "Sports",
    "nivel": "Level", "niveles": "Levels", "1er": "1st", "1ro": "1st", "1ra": "1st",
    "2do": "2nd", "2da": "2nd", "3er": "3rd", "3ro": "3rd", "3ra": "3rd",
    "4to": "4th", "4ta": "4th", "primer": "First", "segundo": "Second",
    "tercer": "Third", "cuarto": "Fourth", "piso": "Floor",
}


def _word_level_translate(term: str) -> str:
    words = term.strip().split()
    out = []
    for w in words:
        bare = w.strip(".,()").lower()
        translated = WORD_TRANSLATIONS.get(bare)
        if translated is None:
            out.append(w.capitalize())
        elif translated:
            out.append(translated)
        # empty string (articles/prepositions we drop) contributes nothing
    result = " ".join(out).strip()
    return result if result else term.strip().title()


def render_amenities(listing: dict) -> str:
    amenities = listing.get("amenities") or []
    if not amenities:
        return ""
    translated = [translate_amenity(a) for a in amenities]
    tags = "\n".join(f'<span class="amenity-tag">{html.escape(a)}</span>' for a in translated)
    return f'<h2 style="margin-top:50px; font-size:24px;">Amenities</h2><div class="amenities">{tags}</div>'


def amenity_filter_values(listing: dict) -> str:
    """Pipe-separated list of this listing's translated amenity names, for
    the data-amenities attribute the listings-page filter reads from.
    Kept separate from render_amenities() since that one produces HTML."""
    amenities = listing.get("amenities") or []
    translated = [translate_amenity(a) for a in amenities]
    return "|".join(translated)


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


# Named gated communities / developments that AlterEstate doesn't reliably
# assign as their own "sector" — sometimes a listing inside one of these
# gets tagged with a broad raw sector instead (e.g. "Sosúa Abajo" or
# "Bella Vista"). Rather than only checking when the raw sector happens to
# be one specific value, every listing's title + description gets checked
# against this list, so a community gets recognized no matter what raw
# sector AlterEstate put it under. More specific phrases are listed first
# so they win over shorter, looser matches (e.g. "panorama village" before
# the bare "panorama").
SECTOR_OVERRIDES = [
    ("sosua ocean village", "Sosúa Ocean Village"),
    ("sosúa ocean village", "Sosúa Ocean Village"),
    ("panorama village", "Panorama Village"),
    ("hispaniola", "Hispaniola"),
    ("panorama", "Panorama Village"),
    ("casa linda", "Casa Linda"),
    ("agua dulce", "Agua Dulce"),
    ("el choco", "El Choco"),
]


def _match_community(listing: dict) -> str:
    """Returns the matched named community from SECTOR_OVERRIDES, or ''
    if none of the listing's title/description mentions one."""
    haystack = f'{listing.get("name", "")} {listing.get("description", "")}'.lower()
    for keyword, replacement in SECTOR_OVERRIDES:
        if keyword in haystack:
            return replacement
    return ""


def get_sector(listing: dict) -> str:
    """Sector/neighborhood name. Checks the listing's own title and
    description for known named communities first (see SECTOR_OVERRIDES
    above) and uses that if found, regardless of what raw sector value
    AlterEstate assigned; otherwise falls back to that raw sector."""
    community = _match_community(listing)
    if community:
        return community
    return listing.get("sector") or ""


# Ordered list of known communities shown in the "Communities" filter
# dropdown on listings.html — kept separate from SECTOR_OVERRIDES' keyword
# list since a couple of those have duplicate accented/unaccented entries
# pointing at the same display name.
KNOWN_COMMUNITIES = [
    "Sosúa Ocean Village",
    "Hispaniola",
    "Panorama Village",
    "Casa Linda",
    "Agua Dulce",
]


def get_community(listing: dict) -> str:
    """Like get_sector(), but returns '' instead of falling back to the raw
    AlterEstate sector — used for the site's community filter dropdown,
    which should only match listings that genuinely mention one of the
    named communities, not just whatever broad sector AlterEstate assigned."""
    return _match_community(listing)


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
