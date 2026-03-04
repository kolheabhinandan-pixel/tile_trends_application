import logging
from scrapers.base_scraper import BaseScraper, strip_html_tags
from config import GLOBAL_SOURCES

logger = logging.getLogger(__name__)


class GlobalScraper(BaseScraper):
    def scrape_all(self):
        """Scrape all global tile sources"""
        all_trends = []

        for source in GLOBAL_SOURCES:
            logger.info(f"Scraping {source['name']}...")
            trends = self.scrape_source(source)
            all_trends.extend(trends)

        return all_trends

    def scrape_source(self, source):
        """Scrape a single source"""
        trends = []

        try:
            html = self.fetch_page(source['url'])
            soup = self.parse_html(html)

            if not soup:
                return trends

            selectors = [
                'article', '.article', '.post', '.news-item',
                '.content-item', '.story', '.card',
                'div[class*="article"]', 'div[class*="post"]',
            ]

            articles = self.extract_articles(soup, selectors)

            for article in articles:
                trend = {
                    'title': strip_html_tags(article['title']),
                    'source': source['name'],
                    'region': 'Global',
                    'link': article['link'],
                    'image_url': article['image_url'],
                    'summary': strip_html_tags(article.get('summary', '')),
                    'trend': self.classify_trend(article['title']),
                    'timestamp': article['timestamp']
                }
                trends.append(trend)

        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")

        return trends


def scrape_global():
    """Main function to scrape global sources"""
    scraper = GlobalScraper()
    return scraper.scrape_all()