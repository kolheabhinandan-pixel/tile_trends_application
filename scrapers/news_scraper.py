import logging
import feedparser
import time
import re
import hashlib
from datetime import datetime, timedelta
from scrapers.base_scraper import BaseScraper, strip_html_tags
from config import (
    NEWS_QUERIES_INDIA, NEWS_QUERIES_GLOBAL,
    SOCIAL_BRAND_QUERIES, RSS_FEEDS,
    NICHE_TILE_QUERIES,
    NEWS_ENTRIES_PER_QUERY, NEWS_MAX_DAYS,
)

logger = logging.getLogger(__name__)


class NewsScraper(BaseScraper):
    """Enhanced news scraper with 100+ sources and date-based filtering"""

    def __init__(self):
        super().__init__()
        self.seen_titles = set()
        self.today = datetime.now().date()

    def _is_recent(self, timestamp, max_days=None):
        """Check if article was published within max_days"""
        if max_days is None:
            max_days = NEWS_MAX_DAYS
        if not timestamp or timestamp <= 0:
            return True  # Include if no date info
        try:
            article_date = datetime.fromtimestamp(timestamp).date()
            return (self.today - article_date).days <= max_days
        except (ValueError, OSError):
            return True

    def _title_hash(self, title):
        """Create a normalized hash of the title for dedup"""
        normalized = re.sub(r'[^a-z0-9]', '', title.lower())
        return hashlib.md5(normalized.encode()).hexdigest()

    def _is_duplicate(self, title):
        """Check if we already have this article"""
        h = self._title_hash(title)
        if h in self.seen_titles:
            return True
        self.seen_titles.add(h)
        return False

    def scrape_all(self):
        """Scrape ALL news sources — 100+ sources total"""
        all_trends = []

        # 1. India Google News (40 queries)
        logger.info("=" * 50)
        logger.info(f"--- Scraping India News ({len(NEWS_QUERIES_INDIA)} queries) ---")
        for query in NEWS_QUERIES_INDIA:
            trends = self._scrape_google_news(query, region='India')
            all_trends.extend(trends)

        # 2. Global Google News (40 queries)
        logger.info(f"--- Scraping Global News ({len(NEWS_QUERIES_GLOBAL)} queries) ---")
        for query in NEWS_QUERIES_GLOBAL:
            trends = self._scrape_google_news(query, region='Global')
            all_trends.extend(trends)

        # 3. Brand-specific queries (20 queries)
        logger.info(f"--- Scraping Brand News ({len(SOCIAL_BRAND_QUERIES)} queries) ---")
        for query in SOCIAL_BRAND_QUERIES:
            trends = self._scrape_google_news(query, region='India')
            all_trends.extend(trends)

        # 4. Niche tile queries (20 queries)
        logger.info(f"--- Scraping Niche Tile News ({len(NICHE_TILE_QUERIES)} queries) ---")
        for query in NICHE_TILE_QUERIES:
            trends = self._scrape_google_news(query, region='Global')
            all_trends.extend(trends)

        # 5. Direct RSS feeds (15 feeds)
        logger.info(f"--- Scraping Direct RSS Feeds ({len(RSS_FEEDS)} feeds) ---")
        for feed_info in RSS_FEEDS:
            trends = self._scrape_rss_feed(feed_info)
            all_trends.extend(trends)

        total_queries = (
            len(NEWS_QUERIES_INDIA) + len(NEWS_QUERIES_GLOBAL) +
            len(SOCIAL_BRAND_QUERIES) + len(NICHE_TILE_QUERIES) +
            len(RSS_FEEDS)
        )
        logger.info("=" * 50)
        logger.info(f"Total sources queried: {total_queries}")
        logger.info(f"Total news trends collected: {len(all_trends)}")
        return all_trends

    def _scrape_google_news(self, query, region='Global'):
        """Scrape Google News RSS for a query with date filtering"""
        trends = []
        try:
            encoded_query = query.replace(' ', '+')
            gl = 'IN' if region == 'India' else 'US'
            # Use when:7d for 7-day window to get more results
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:{NEWS_MAX_DAYS}d&hl=en-{gl}&gl={gl}&ceid={gl}:en"

            logger.info(f"  Fetching: {query}")
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:NEWS_ENTRIES_PER_QUERY]:
                title = strip_html_tags(entry.title) if hasattr(entry, 'title') else ''
                if not title or len(title) < 15:
                    continue

                if self._is_duplicate(title):
                    continue

                # Parse timestamp
                timestamp = time.time()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        timestamp = time.mktime(entry.published_parsed)
                    except Exception:
                        timestamp = time.time()

                # Only include recent articles
                if not self._is_recent(timestamp):
                    continue

                # Extract source name
                source_name = 'Google News'
                if hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                    source_name = strip_html_tags(entry.source.title)

                # Clean summary
                summary = ''
                if hasattr(entry, 'summary'):
                    summary = strip_html_tags(entry.summary)

                # Extract actual article link
                link = entry.link if hasattr(entry, 'link') else ''

                trend = {
                    'title': title,
                    'source': source_name,
                    'region': region,
                    'link': link,
                    'image_url': '',
                    'trend': self.classify_trend(title, summary),
                    'timestamp': timestamp,
                    'summary': summary[:250] if summary else '',
                    'query': query,
                }
                trends.append(trend)

        except Exception as e:
            logger.error(f"Error scraping news for '{query}': {e}")

        return trends

    def _scrape_rss_feed(self, feed_info):
        """Scrape a direct RSS feed"""
        trends = []
        try:
            logger.info(f"  Fetching RSS: {feed_info['name']}")
            feed = feedparser.parse(feed_info['url'])

            for entry in feed.entries[:12]:
                title = strip_html_tags(entry.title) if hasattr(entry, 'title') else ''
                if not title or len(title) < 15:
                    continue

                if self._is_duplicate(title):
                    continue

                timestamp = time.time()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        timestamp = time.mktime(entry.published_parsed)
                    except Exception:
                        timestamp = time.time()

                if not self._is_recent(timestamp, max_days=14):
                    continue

                # Try to get image from media content
                image_url = ''
                if hasattr(entry, 'media_content') and entry.media_content:
                    image_url = entry.media_content[0].get('url', '')
                elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                    image_url = entry.media_thumbnail[0].get('url', '')

                # Try to get image from content
                if not image_url and hasattr(entry, 'content'):
                    for content in entry.content:
                        if 'value' in content:
                            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content['value'])
                            if img_match:
                                image_url = img_match.group(1)
                                break

                # Try summary for image
                if not image_url and hasattr(entry, 'summary'):
                    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary)
                    if img_match:
                        image_url = img_match.group(1)

                summary = ''
                if hasattr(entry, 'summary'):
                    summary = strip_html_tags(entry.summary)

                link = entry.link if hasattr(entry, 'link') else ''

                trend = {
                    'title': title,
                    'source': feed_info['name'],
                    'region': feed_info.get('region', 'Global'),
                    'link': link,
                    'image_url': image_url,
                    'trend': self.classify_trend(title, summary),
                    'timestamp': timestamp,
                    'summary': summary[:250] if summary else '',
                }
                trends.append(trend)

        except Exception as e:
            logger.error(f"Error scraping RSS feed {feed_info['name']}: {e}")

        return trends


def scrape_news():
    """Main function to scrape all news sources"""
    scraper = NewsScraper()
    return scraper.scrape_all()