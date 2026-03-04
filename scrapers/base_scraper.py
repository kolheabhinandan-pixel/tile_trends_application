import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from config import REQUEST_TIMEOUT, MAX_RETRIES, USER_AGENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def strip_html_tags(text):
    """Remove all HTML tags and return clean text"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def fetch_page(self, url, retries=MAX_RETRIES):
        """Fetch a webpage with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT, verify=True)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None

    def parse_html(self, html):
        """Parse HTML content"""
        if not html:
            return None
        return BeautifulSoup(html, 'html.parser')

    def extract_articles(self, soup, selectors):
        """Extract articles from parsed HTML using CSS selectors"""
        articles = []
        if not soup:
            return articles

        try:
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements[:10]:
                        article = self.extract_article_data(elem)
                        if article:
                            articles.append(article)
                    break
        except Exception as e:
            logger.error(f"Error extracting articles: {e}")

        return articles

    def extract_article_data(self, element):
        """Extract title, link, image from article element"""
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            if not title or len(title) < 10:
                return None

            link_elem = element.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = ""

            img_elem = element.find('img', src=True)
            image_url = ""
            if img_elem:
                image_url = img_elem.get('src', '') or img_elem.get('data-src', '') or img_elem.get('data-lazy-src', '')
            if image_url and not image_url.startswith('http'):
                image_url = ""

            summary = ""
            summary_elem = element.find(['p', 'div'], class_=lambda x: x and any(
                kw in x.lower() for kw in ['summary', 'description', 'excerpt', 'teaser', 'intro']
            ))
            if summary_elem:
                summary = strip_html_tags(summary_elem.get_text(strip=True)[:300])

            return {
                'title': strip_html_tags(title),
                'link': link,
                'image_url': image_url,
                'summary': summary,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error extracting article data: {e}")
            return None

    def classify_trend(self, title, content=""):
        """Classify article into trend category based on Johnson's product structure.
        
        Categories are checked in order from most specific to most general.
        The last category 'Tile Design & Trends' acts as a catch-all for
        tile-related content that doesn't fit a specific category.
        """
        text = (title + " " + content).lower()

        # Ordered keyword map — more specific categories first, general last
        keywords_map = {
            # Other Product Categories
            'Bath Fittings': [
                'bath fitting', 'bath fittings', 'faucet', 'faucets',
                'shower head', 'rain shower', 'hand shower',
                'tap', 'mixer tap', 'bath accessories', 'towel rail',
                'showerhead', 'bath hardware',
                'shower upgrade', 'shower ideas', 'walk-in shower',
                'shower enclosure', 'shower room', 'shower panel',
                'shower curtain', 'shower design', 'shower fitting',
                'shower remodel', 'shower reuses',
            ],
            'Sanitaryware': [
                'sanitaryware', 'sanitary ware', 'toilet', 'wash basin',
                'water closet', 'urinal', 'bidet', 'commode', 'pedestal',
                'cistern', 'seat cover', 'wc',
            ],
            'Marble & Quartz': [
                'marble slab', 'quartz slab', 'quartz countertop',
                'marble countertop', 'engineered stone', 'quartzite slab',
                'countertop', 'kitchen top', 'vanity top',
                'marble & quartz', 'marble and quartz',
            ],

            # Special Tiles
            'Special Tiles': [
                'anti static', 'anti-static', 'cool roof', 'sri tile',
                'germ free', 'germ-free', 'swimming pool tile',
                'pool tile', 'pool design',
                'staircase tile', 'staircase solution', 'landscaping tile',
                'radiation shielding', 'tac tile', 'tac tiles',
                'anti slip', 'anti-slip',
            ],

            # Application-specific spaces
            'Elevation Tiles': [
                'elevation', 'facade', 'exterior wall', 'cladding',
                'exterior cladding', 'building facade', 'wall cladding',
            ],
            'Kitchen Tiles': [
                'kitchen tile', 'kitchen tiles', 'backsplash', 'splashback',
                'kitchen wall', 'kitchen floor', 'kitchen design tile',
                'kitchen backsplash',
            ],
            'Bathroom Tiles': [
                'bathroom tile', 'bathroom tiles', 'bathroom wall',
                'bathroom floor', 'bathroom design', 'wet area',
                'all-marble bathroom', 'marble bathroom',
                'bathroom remodel', 'bathroom renovation',
                'bathroom feel', 'bathroom spa',
                'spa bathroom', 'spa tile',
            ],
            'Terrace & Outdoor Tiles': [
                'terrace', 'outdoor tile', 'patio tile', 'balcony tile',
                'garden tile', 'deck tile', 'outdoor flooring',
                'outdoor patio',
            ],
            'Parking & Exterior Tiles': [
                'parking tile', 'parking floor', 'exterior floor',
                'driveway tile', 'heavy duty tile', 'heavy traffic',
            ],

            # Size
            'Large Format Tiles': [
                'large format', 'large-format', 'large-sized',
                'big tile', 'slab', 'mega slab',
                '1200x2400', '800x1600', '1200x1800',
                'porcelain slab', 'sintered stone',
            ],

            # Design Trends
            'Terrazzo': ['terrazzo', 'venetian'],
            'Marble Look': [
                'marble look', 'marble effect', 'carrara', 'calacatta',
                'onyx look', 'statuario', 'marble finish',
            ],
            'Wood Look': [
                'wood look', 'wood-look', 'wood effect', 'timber look',
                'plank tile', 'wooden tile', 'wood finish tile',
            ],
            'Natural Stone Look': [
                'stone look', 'natural stone', 'travertine', 'slate look',
                'quartzite look', 'limestone look', 'sandstone look',
            ],
            '3D & Textured Tiles': [
                '3d tile', '3d tiles', 'three-dimensional', 'textured tile',
                'relief tile', 'tactile', 'embossed tile', 'carved tile',
                'textured surface',
            ],
            'Metallic Finish': [
                'metallic tile', 'metallic finish', 'gold tile',
                'copper tile', 'bronze tile', 'metal look',
            ],
            'Digital Printing': [
                'digital print', 'inkjet', 'digital tile', 'hd print',
                'digital printing', 'digitally printed',
            ],
            'Eco-Friendly & Sustainability': [
                'eco-friendly', 'sustainable tile', 'green tile',
                'recycled tile', 'carbon neutral', 'eco tile',
                'sustainability', 'green building', 'biomaterial',
                'regenerative', 'recycled material',
                'reuses water', 'water saving', 'water-saving',
            ],

            # Tile Types
            'Glazed Vitrified Tiles': [
                'glazed vitrified', 'gvt', 'pgvt', 'dgvt',
                'polished glazed', 'nano polished',
            ],
            'Vitrified Tiles': [
                'vitrified', 'double charge', 'soluble salt',
                'full body vitrified',
            ],
            'Industrial Tiles': [
                'industrial tile', 'industrial tiles', 'industrial floor',
                'acid resistant', 'chemical resistant', 'factory floor',
            ],
            'Ceramic Tiles': [
                'ceramic tile', 'ceramic tiles', 'wall ceramic',
                'floor ceramic', 'ceramic design',
                'ceramic unit', 'ceramic units', 'ceramic cluster',
                'ceramic sector', 'ceramic industry',
                'ceramic manufacturing',
            ],

            # Flooring by space
            'Commercial Flooring': [
                'commercial floor', 'commercial tile', 'office floor',
                'retail floor', 'hotel floor', 'hospitality tile',
                'hotel lobby', 'retail store', 'restaurant tile',
                'hospital tile', 'commercial kitchen',
            ],
            'Residential Flooring': [
                'residential floor', 'home floor', 'living room tile',
                'bedroom tile', 'residential tile', 'bedroom flooring',
            ],

            # Application (broad)
            'Wall Tiles': [
                'wall tile', 'wall tiles', 'wall only', 'accent wall',
                'feature wall', 'wall decor tile',
            ],
            'Floor Tiles': [
                'floor tile', 'floor tiles', 'floor only', 'flooring tile',
                'floor covering', 'floor coverings',
                'flooring trend', 'flooring design',
            ],
            'Floor & Wall Tiles': [
                'floor and wall', 'floor & wall', 'multi-purpose tile',
            ],

            # Industry
            'Exhibition & Events': [
                'exhibition', 'expo', 'cersaie', 'coverings', 'cevisama',
                'ceramitec', 'tile show', 'tile fair', 'trade show',
                'surfaces \'26', 'surfaces \'25', 'surfaces 26',
            ],
            'New Collection Launch': [
                'launch', 'collection', 'new range', 'introduce', 'unveil',
                'showcase', 'new series', 'new design', 'new product',
                'expands range', 'expand range',
            ],
            'Technology & Innovation': [
                'technology', 'innovation', 'smart tile', 'automation',
                'robotic', 'ai tile', 'manufacturing tech',
                'gypsum plaster', 'plaster',
            ],
            'Market & Industry News': [
                'market', 'growth', 'revenue', 'expansion', 'industry',
                'forecast', 'billion', 'crore', 'export', 'import',
                'production', 'capacity', 'demand', 'supply',
                'financial result', 'quarterly', 'q3', 'q4', 'q1', 'q2',
                'chro', 'ceo', 'managing director',
                'valuation', 'earnings',
                'honoured', 'honored', 'award', 'best brand',
                'ngt', 'edc case', 'regulation',
                'preferred by', 'leading brand',
                'integrated home', 'surface solutions',
                'participation', 'corporate', 'conference', 'investor',
                'mid-cap', 'mid cap', 'small-cap', 'large-cap',
            ],

            # Catch-all for tile-related content that doesn't fit above
            'Tile Design & Trends': [
                'tile', 'tiles', 'tiling', 'tiled',
                'porcelain', 'flooring trend', 'flooring design',
                'interior tile', 'tile pairing', 'tile pairings',
                'tile design', 'tile trend', 'tile style',
                'timeless tile', 'tile realism',
                'azulejo', 'azulejos',
                'choose tile', 'choosing tile', 'right tile',
                'subway tile', 'hexagonal tile', 'penny tile',
                'encaustic', 'zellige', 'cement tile',
                'handmade tile', 'artisan tile',
                'fireplace tile', 'surround tile',
            ],
        }

        for category, keywords in keywords_map.items():
            if any(word in text for word in keywords):
                return category

        return 'General Trend'