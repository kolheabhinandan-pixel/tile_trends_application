import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data retention (30 days)
DATA_RETENTION_DAYS = 30

# Scraping configuration
REQUEST_TIMEOUT = 20
MAX_RETRIES = 2
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# How many entries to fetch per Google News query (higher = more trends)
NEWS_ENTRIES_PER_QUERY = 8

# How many days back to look for articles
NEWS_MAX_DAYS = 7

# ============================================================
# RELEVANCE FILTER — ONLY tiles & bathware related content
# ============================================================
RELEVANCE_KEYWORDS = [
    # Core product terms
    "tile", "tiles", "tiling", "tiled",
    "ceramic", "ceramics", "porcelain",
    "vitrified", "glazed", "gvt", "pgvt", "dgvt",
    "bathware", "bath fitting", "bath fittings",
    "sanitaryware", "sanitary ware",
    "marble", "quartz", "countertop", "countertops",
    "faucet", "faucets", "shower", "showers",
    "wash basin", "basin", "toilet", "urinal",
    "bidet", "commode", "cistern",

    # Application types
    "wall tile", "floor tile", "wall tiles", "floor tiles",
    "elevation tile", "parking tile", "exterior tile",
    "kitchen tile", "bathroom tile", "terrace tile",
    "mosaic", "mosaic tile",
    "backsplash", "splashback",
    "flooring trend", "flooring design",

    # Special tiles
    "anti static tile", "anti-static", "cool roof", "sri tile",
    "germ free", "germ-free", "swimming pool tile",
    "staircase tile", "landscaping tile", "radiation shielding",
    "tac tile", "tac tiles", "industrial tile",

    # Tile types & finishes
    "large format", "slab tile", "mega slab", "large-sized",
    "sintered stone", "porcelain slab",
    "terrazzo", "marble look", "wood look", "wood-look",
    "stone look", "natural stone", "travertine", "slate",
    "3d tile", "textured tile", "embossed tile",
    "metallic tile", "metallic finish",
    "digital print", "inkjet tile",
    "polished tile", "matt tile", "matte tile", "glossy tile",
    "rustic tile", "carving tile", "sugar finish",
    "nano polished", "double charge",
    "azulejo", "azulejos",

    # Industry-specific terms
    "tile industry", "tile market", "tile manufacturing",
    "tile export", "tile import", "tile production",
    "tile design", "tile trend", "tile collection",
    "tile showroom", "tile exhibition", "tile expo",
    "tile pairing", "tile pairings",
    "tile realism", "tile valuation",
    "cersaie", "coverings", "cevisama", "ceramitec",
    "surfaces '26", "surfaces '25", "surfaces 26",
    "morbi", "morbi tiles", "gujarat tiles",
    "floor covering", "floor coverings",

    # Brands (Johnson ecosystem)
    "johnson tiles", "h&r johnson", "hr johnson", "hrjohnson",
    "porselano", "marbonite", "endura tiles",
    "prism johnson",

    # Competitor brands (India)
    "kajaria", "somany", "orient bell", "orientbell",
    "nitco", "asian granito", "agl tiles",
    "cera sanitaryware", "cera india",
    "rak ceramics", "simpolo", "varmora",
    "lavish ceramics", "qutone", "nexion",
    "exxaro tiles", "regalia ceramics",
    "sunheart tiles", "lioli ceramics",
    "iconic ceramics", "lycos ceramic",
    "winasia ceramic", "steuler tiles",

    # Global brands
    "marazzi", "porcelanosa", "daltile", "mohawk tile",
    "florim", "iris ceramica", "laminam",
    "crossville", "emser tile", "interface tile",
    "villeroy", "boch", "roca", "laufen",
    "duravit", "grohe", "hansgrohe", "kohler",
    "american standard", "toto sanitaryware",
    "geberit", "ideal standard",
    "casalgrande padana", "refin ceramiche",
    "lea ceramiche", "panaria ceramica",
    "atlas concorde", "fap ceramiche",
    "mutina", "41zero42",

    # Spaces & applications
    "bathroom design", "kitchen backsplash",
    "wall cladding", "facade tile",
    "residential flooring", "commercial flooring",
    "industrial flooring", "outdoor flooring",
    "pool tile", "pool design",
    "spa tile", "hotel bathroom",
]

# ============================================================
# NEGATIVE KEYWORDS — Reject articles containing these
# ============================================================
NEGATIVE_KEYWORDS = [
    "stock price", "share price", "nse", "bse",
    "quarterly results", "profit loss", "balance sheet",
    "cricket", "football", "soccer", "tennis",
    "election", "political", "politics", "vote",
    "movie", "film", "bollywood", "hollywood", "entertainment",
    "recipe", "cooking", "food",
    "weather forecast",
    "cryptocurrency", "bitcoin", "forex",
    "murder", "crime", "accident",
    "ipl", "world cup",
]

# ============================================================
# 100+ DIVERSE SOURCES FOR DYNAMIC DAILY SCRAPING
# ============================================================

# -------------------------------------------------------
# GOOGLE NEWS RSS QUERIES — INDIA (40 queries)
# -------------------------------------------------------
NEWS_QUERIES_INDIA = [
    # Johnson & Prism Johnson
    "H&R Johnson tiles India news",
    "Johnson tiles India latest",
    "Prism Johnson tiles news",
    "Porselano tiles India",
    "Marbonite tiles India",
    "Endura tiles India",

    # Major Indian brands
    "Kajaria tiles latest news",
    "Kajaria ceramics new collection",
    "Somany ceramics tiles news",
    "Somany tiles new launch",
    "Asian Granito India tiles",
    "AGL tiles India news",
    "NITCO tiles India news",
    "NITCO tiles new collection",
    "Orient Bell tiles news",
    "Orient Bell tiles design",
    "Cera Sanitaryware India news",
    "Cera India tiles bathroom",
    "RAK Ceramics India tiles",
    "Exxaro tiles India news",
    "Simpolo tiles India",
    "Varmora tiles India",
    "Qutone tiles India",
    "Nexion tiles India",

    # Industry & market
    "ceramic tiles India industry news",
    "vitrified tiles India market",
    "tile manufacturing India news",
    "India tiles export news",
    "India tiles import news",
    "morbi tiles Gujarat news",
    "morbi ceramic cluster news",
    "India construction tiles demand",
    "India tile industry growth",
    "Indian ceramic industry news",

    # Product categories
    "bathroom tiles India trends",
    "floor tiles India design",
    "wall tiles India trends",
    "large format tiles India",
    "porcelain slab tiles India",
    "sanitaryware India market news",
    "bath fittings India trends",
    "kitchen tiles India design",
    "elevation tiles India exterior",
    "vitrified tiles India latest",
]

# -------------------------------------------------------
# GOOGLE NEWS RSS QUERIES — GLOBAL (40 queries)
# -------------------------------------------------------
NEWS_QUERIES_GLOBAL = [
    # Industry news
    "tile industry news today",
    "ceramic tiles global market news",
    "porcelain tiles innovation news",
    "tile market growth forecast",
    "global ceramic tile industry",
    "tile manufacturing technology news",
    "ceramic tile production news",
    "tile industry trends 2026",

    # Design & trends
    "tile design trends latest",
    "large format tiles design trend",
    "terrazzo tiles trend interior",
    "marble look tiles design",
    "wood look tiles flooring trend",
    "3D tiles wall design trend",
    "textured tiles interior design",
    "mosaic tiles art design",
    "outdoor tiles patio design",
    "luxury tiles interior design",
    "bathroom tile design trends",
    "kitchen backsplash tile trends",
    "sustainable tiles eco-friendly",
    "digital printing tiles technology",

    # Exhibitions & events
    "Cersaie tiles exhibition news",
    "Coverings tile expo news",
    "Cevisama tiles fair news",
    "tile exhibition 2026 news",

    # Global brands
    "Marazzi tiles new collection",
    "Porcelanosa tiles news",
    "Daltile new products tiles",
    "Mohawk tile flooring news",
    "Villeroy Boch tiles news",
    "Roca tiles sanitaryware news",
    "Laminam porcelain slab news",
    "Atlas Concorde tiles news",
    "Florim ceramics tiles news",
    "Iris Ceramica tiles news",

    # Sanitaryware & bath global
    "sanitaryware global market news",
    "bath fittings design trends global",
    "countertop marble quartz trends",
    "Kohler bathroom products news",
    "Grohe bath fittings news",
    "Duravit sanitaryware news",
]

# -------------------------------------------------------
# BRAND-SPECIFIC QUERIES (20 queries)
# -------------------------------------------------------
SOCIAL_BRAND_QUERIES = [
    # Indian brands - launches & collections
    "Kajaria ceramics tiles new launch 2026",
    "Somany tiles new collection launch",
    "Orient Bell tiles design collection",
    "AGL tiles new range launch",
    "NITCO tiles collection launch",
    "Cera India sanitaryware new product",
    "Johnson tiles India collection launch",
    "RAK Ceramics tiles new design",
    "Simpolo tiles launch collection",
    "Prism Johnson tiles news update",
    "Varmora tiles new collection",
    "Qutone tiles launch India",
    "Exxaro tiles new range",
    "Nexion tiles India launch",

    # Global brands - launches
    "Marazzi new tile collection launch",
    "Porcelanosa new product launch",
    "Daltile new collection 2026",
    "Atlas Concorde new tiles",
    "Laminam new slab collection",
    "Roca new sanitaryware launch",
]

# -------------------------------------------------------
# INDIAN TILE COMPANY WEBSITES (15 sources)
# -------------------------------------------------------
INDIA_COMPANY_SOURCES = [
    {"name": "Kajaria Ceramics", "url": "https://www.kajariaceramics.com/", "type": "company"},
    {"name": "Somany Ceramics", "url": "https://www.somanytiles.com/", "type": "company"},
    {"name": "Asian Granito (AGL)", "url": "https://www.aglasiangranito.com/", "type": "company"},
    {"name": "NITCO Tiles", "url": "https://www.nitco.in/", "type": "company"},
    {"name": "Orient Bell", "url": "https://www.orientbell.com/", "type": "company"},
    {"name": "Cera Sanitaryware", "url": "https://www.cera-india.com/", "type": "company"},
    {"name": "H&R Johnson", "url": "https://www.hrjohnsonindia.com/", "type": "company"},
    {"name": "RAK Ceramics India", "url": "https://www.rakceramics.com/in/", "type": "company"},
    {"name": "Simpolo Tiles", "url": "https://www.simpolo.net/", "type": "company"},
    {"name": "Varmora Tiles", "url": "https://www.varmora.com/", "type": "company"},
    {"name": "Qutone Tiles", "url": "https://www.qutonetiles.com/", "type": "company"},
    {"name": "Nexion Tiles", "url": "https://www.nexiontiles.com/", "type": "company"},
    {"name": "Exxaro Tiles", "url": "https://www.exxarotiles.com/", "type": "company"},
    {"name": "Lioli Ceramics", "url": "https://www.lioli.in/", "type": "company"},
    {"name": "Regalia Ceramics", "url": "https://www.regaliaceramics.com/", "type": "company"},
]

# -------------------------------------------------------
# GLOBAL TILE & DESIGN WEBSITES (15 sources)
# -------------------------------------------------------
GLOBAL_SOURCES = [
    # Design & architecture publications
    {"name": "Dezeen Tiles", "url": "https://www.dezeen.com/tag/tiles/", "type": "design"},
    {"name": "ArchDaily Tiles", "url": "https://www.archdaily.com/tag/tiles", "type": "architecture"},
    {"name": "Tile Magazine", "url": "https://www.tilemagazine.com/", "type": "magazine"},
    {"name": "Tile Letter", "url": "https://www.tileletter.com/", "type": "magazine"},

    # Global tile brands
    {"name": "Marazzi", "url": "https://www.marazzi.it/en/", "type": "brand"},
    {"name": "Porcelanosa", "url": "https://www.porcelanosa.com/", "type": "brand"},
    {"name": "Daltile", "url": "https://www.daltile.com/", "type": "brand"},
    {"name": "Atlas Concorde", "url": "https://www.atlasconcorde.com/en/", "type": "brand"},
    {"name": "Florim Ceramics", "url": "https://www.florim.com/en/", "type": "brand"},
    {"name": "Laminam", "url": "https://www.laminam.com/en/", "type": "brand"},
    {"name": "Casalgrande Padana", "url": "https://www.casalgrandepadana.com/en/", "type": "brand"},

    # Sanitaryware & bath brands
    {"name": "Villeroy & Boch", "url": "https://www.villeroy-boch.com/", "type": "brand"},
    {"name": "Roca", "url": "https://www.roca.com/", "type": "brand"},
    {"name": "Duravit", "url": "https://www.duravit.com/", "type": "brand"},
    {"name": "Kohler", "url": "https://www.kohler.com/", "type": "brand"},
]

# -------------------------------------------------------
# RSS FEEDS (15 feeds)
# -------------------------------------------------------
RSS_FEEDS = [
    # Design publications
    {"name": "Dezeen Tiles RSS", "url": "https://www.dezeen.com/tag/tiles/feed/", "region": "Global"},
    {"name": "Dezeen Bathrooms RSS", "url": "https://www.dezeen.com/tag/bathrooms/feed/", "region": "Global"},
    {"name": "ArchDaily Tiles RSS", "url": "https://www.archdaily.com/tag/tiles/feed", "region": "Global"},
    {"name": "ArchDaily Ceramics RSS", "url": "https://www.archdaily.com/tag/ceramics/feed", "region": "Global"},

    # Industry publications
    {"name": "Construction World India", "url": "https://www.constructionworld.in/rss-feed", "region": "India"},
    {"name": "Tile Magazine RSS", "url": "https://www.tilemagazine.com/feed/", "region": "Global"},

    # Google News RSS — persistent topic feeds
    {"name": "GNews Ceramic Tiles", "url": "https://news.google.com/rss/search?q=ceramic+tiles+industry&hl=en&gl=US&ceid=US:en", "region": "Global"},
    {"name": "GNews Tile Design", "url": "https://news.google.com/rss/search?q=tile+design+trends&hl=en&gl=US&ceid=US:en", "region": "Global"},
    {"name": "GNews Sanitaryware", "url": "https://news.google.com/rss/search?q=sanitaryware+bathroom+market&hl=en&gl=US&ceid=US:en", "region": "Global"},
    {"name": "GNews India Tiles", "url": "https://news.google.com/rss/search?q=tiles+India+ceramic&hl=en-IN&gl=IN&ceid=IN:en", "region": "India"},
    {"name": "GNews Morbi Tiles", "url": "https://news.google.com/rss/search?q=morbi+tiles+ceramic&hl=en-IN&gl=IN&ceid=IN:en", "region": "India"},
    {"name": "GNews Large Format", "url": "https://news.google.com/rss/search?q=large+format+porcelain+tiles&hl=en&gl=US&ceid=US:en", "region": "Global"},
    {"name": "GNews Bath Fittings", "url": "https://news.google.com/rss/search?q=bath+fittings+bathroom+design&hl=en&gl=US&ceid=US:en", "region": "Global"},
    {"name": "GNews Tile Exhibition", "url": "https://news.google.com/rss/search?q=tile+exhibition+cersaie+coverings&hl=en&gl=US&ceid=US:en", "region": "Global"},
    {"name": "GNews Flooring Trends", "url": "https://news.google.com/rss/search?q=flooring+tiles+trends&hl=en&gl=US&ceid=US:en", "region": "Global"},
]

# -------------------------------------------------------
# NICHE TILE QUERIES — for deeper coverage (20 queries)
# -------------------------------------------------------
NICHE_TILE_QUERIES = [
    # Specific product types
    "porcelain slab countertop news",
    "sintered stone surface news",
    "terrazzo flooring design news",
    "mosaic tile art design news",
    "subway tile design trends",
    "hexagonal tile design trends",
    "penny tile bathroom design",
    "encaustic cement tile design",
    "zellige tile moroccan design",
    "handmade ceramic tile artisan",

    # Specific applications
    "swimming pool tile design",
    "outdoor patio tile trends",
    "fireplace tile surround design",
    "shower tile waterproofing",
    "commercial kitchen tile",
    "hospital tile flooring",
    "hotel lobby tile design",
    "retail store tile flooring",
    "restaurant tile design",
    "spa bathroom tile luxury",
]

# ============================================================
# TOTAL SOURCE COUNT:
# Google News India: 40 queries
# Google News Global: 40 queries
# Brand queries: 20 queries
# Niche queries: 20 queries
# India company websites: 15 sources
# Global websites: 15 sources
# RSS feeds: 15 feeds
# TOTAL: 165 sources
# ============================================================

# ============================================================
# TREND CATEGORIES — Based on Johnson's product structure
# ============================================================
TREND_CATEGORIES = [
    "Wall Tiles",
    "Floor Tiles",
    "Floor & Wall Tiles",
    "Large Format Tiles",
    "Medium Format Tiles",
    "Small Format Tiles",
    "Ceramic Tiles",
    "Glazed Vitrified Tiles",
    "Vitrified Tiles",
    "Industrial Tiles",
    "Kitchen Tiles",
    "Bathroom Tiles",
    "Terrace & Outdoor Tiles",
    "Elevation Tiles",
    "Residential Flooring",
    "Commercial Flooring",
    "Parking & Exterior Tiles",
    "Special Tiles",
    "Bath Fittings",
    "Sanitaryware",
    "Marble & Quartz",
    "Terrazzo",
    "Marble Look",
    "Wood Look",
    "Natural Stone Look",
    "3D & Textured Tiles",
    "Metallic Finish",
    "Digital Printing",
    "Market & Industry News",
    "New Collection Launch",
    "Exhibition & Events",
    "Technology & Innovation",
    "Eco-Friendly & Sustainability",
    "Tile Design & Trends",
]

# Image search keywords per category
CATEGORY_IMAGE_KEYWORDS = {
    "Wall Tiles": "wall tile design modern interior",
    "Floor Tiles": "floor tile design porcelain",
    "Floor & Wall Tiles": "floor wall tile ceramic design",
    "Large Format Tiles": "large format porcelain tile slab interior",
    "Medium Format Tiles": "medium format ceramic tile bathroom",
    "Small Format Tiles": "small mosaic tile design pattern",
    "Ceramic Tiles": "ceramic tile modern design",
    "Glazed Vitrified Tiles": "glazed vitrified tile polished floor",
    "Vitrified Tiles": "vitrified polished tile floor",
    "Industrial Tiles": "industrial tile heavy duty floor",
    "Kitchen Tiles": "kitchen tile backsplash design",
    "Bathroom Tiles": "bathroom tile design modern",
    "Terrace & Outdoor Tiles": "outdoor terrace tile patio design",
    "Elevation Tiles": "elevation tile exterior facade",
    "Residential Flooring": "residential floor tile living room",
    "Commercial Flooring": "commercial floor tile office",
    "Parking & Exterior Tiles": "parking tile exterior heavy duty",
    "Special Tiles": "special tile anti static germ free",
    "Bath Fittings": "bath fittings modern bathroom",
    "Sanitaryware": "sanitaryware modern bathroom design",
    "Marble & Quartz": "marble quartz countertop luxury",
    "Terrazzo": "terrazzo tile floor modern design",
    "Marble Look": "marble look porcelain tile luxury",
    "Wood Look": "wood look ceramic tile flooring",
    "Natural Stone Look": "natural stone look tile travertine",
    "3D & Textured Tiles": "3d textured wall tile modern interior",
    "Metallic Finish": "metallic finish tile gold copper",
    "Digital Printing": "digital printed ceramic tile design",
    "Market & Industry News": "tile industry market growth",
    "New Collection Launch": "new tile collection showroom display",
    "Exhibition & Events": "tile exhibition cersaie booth",
    "Technology & Innovation": "tile manufacturing technology innovation",
    "Eco-Friendly & Sustainability": "sustainable green ceramic tile eco",
    "Tile Design & Trends": "modern tile design interior trends",
    "General Trend": "modern tile design interior",
}

# Paths
def get_raw_path(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(BASE_DIR, "data", "raw", date_str)

def get_processed_path(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(BASE_DIR, "data", "processed", date_str)

def get_images_path(date_str=None):
    return os.path.join(get_processed_path(date_str), "images")