import logging
import time
from scrapers.base_scraper import BaseScraper, strip_html_tags
from config import INDIA_COMPANY_SOURCES

logger = logging.getLogger(__name__)


class IndiaScraper(BaseScraper):
    def scrape_all(self):
        """Scrape all Indian tile company websites"""
        all_trends = []

        for source in INDIA_COMPANY_SOURCES:
            logger.info(f"Scraping {source['name']}...")
            trends = self.scrape_source(source)
            all_trends.extend(trends)

        return all_trends

    def scrape_source(self, source):
        """Scrape a single source - extract meta info and articles"""
        trends = []

        try:
            html = self.fetch_page(source['url'])
            soup = self.parse_html(html)

            if not soup:
                return trends

            # Strategy 1: Try article selectors
            selectors = [
                'article', '.article', '.blog-post', '.post', '.entry',
                '.news-item', '.content-item', '.story', '.card',
                'div[class*="article"]', 'div[class*="post"]',
                'div[class*="news"]', 'div[class*="blog"]',
                'div[class*="product"]', 'div[class*="collection"]',
            ]

            articles = self.extract_articles(soup, selectors)

            # Strategy 2: Extract from meta tags if no articles found
            if not articles:
                articles = self._extract_from_meta(soup, source['url'])

            for article in articles:
                trend = {
                    'title': article['title'],
                    'source': source['name'],
                    'region': 'India',
                    'link': article['link'] if article['link'] else source['url'],
                    'image_url': article['image_url'],
                    'summary': article.get('summary', ''),
                    'trend': self.classify_trend(article['title'], article.get('summary', '')),
                    'timestamp': article['timestamp']
                }
                trends.append(trend)

        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")

        return trends

    def _extract_from_meta(self, soup, url):
        """Extract article info from meta tags and main headings"""
        articles = []

        try:
            title = ""
            title_meta = soup.find('meta', property='og:title')
            if title_meta and title_meta.get('content'):
                title = strip_html_tags(title_meta['content'])
            elif soup.find('h1'):
                title = strip_html_tags(soup.find('h1').get_text(strip=True))

            summary = ""
            desc_meta = soup.find('meta', property='og:description')
            if desc_meta and desc_meta.get('content'):
                summary = strip_html_tags(desc_meta['content'])
            elif soup.find('meta', attrs={'name': 'description'}):
                summary = strip_html_tags(
                    soup.find('meta', attrs={'name': 'description'}).get('content', '')
                )

            image_url = ""
            img_meta = soup.find('meta', property='og:image')
            if img_meta and img_meta.get('content'):
                image_url = img_meta['content']

            if title and len(title) > 10:
                articles.append({
                    'title': title,
                    'link': url,
                    'image_url': image_url,
                    'summary': summary[:200] if summary else '',
                    'timestamp': time.time()
                })
        except Exception as e:
            logger.error(f"Error extracting from meta: {e}")

        return articles


def scrape_india():
    """Main function to scrape Indian sources"""
    scraper = IndiaScraper()
    return scraper.scrape_all()