import logging
import re
import hashlib
from scrapers.base_scraper import strip_html_tags
from config import RELEVANCE_KEYWORDS, NEGATIVE_KEYWORDS

logger = logging.getLogger(__name__)


def is_relevant(title, summary=""):
    """
    Check if an article is relevant to tiles & bathware industry.
    Returns True only if the article contains at least one relevance keyword
    AND does not contain negative keywords.
    """
    text = (title + " " + summary).lower()

    # Check for negative keywords first — reject immediately
    for neg_kw in NEGATIVE_KEYWORDS:
        if neg_kw in text:
            return False

    # Check for at least one relevance keyword
    for kw in RELEVANCE_KEYWORDS:
        if kw in text:
            return True

    return False


def clean_trends(trends):
    """Clean, sanitize, deduplicate, and FILTER for relevance"""
    seen_hashes = set()
    cleaned = []
    rejected_count = 0

    for t in trends:
        # Clean title - strip HTML
        title = strip_html_tags(t.get('title', ''))
        if not title or len(title) < 15:
            continue

        # Clean summary - strip ALL HTML tags and links
        summary = strip_html_tags(t.get('summary', ''))

        # Remove Google News redirect artifacts
        summary = re.sub(r'https?://news\.google\.com/[^\s]*', '', summary)

        # ============================================================
        # RELEVANCE FILTER — Only tiles & bathware related content
        # ============================================================
        if not is_relevant(title, summary):
            rejected_count += 1
            logger.debug(f"Rejected (irrelevant): {title[:80]}")
            continue

        # Deduplicate by normalized title
        normalized = re.sub(r'[^a-z0-9]', '', title.lower())
        title_hash = hashlib.md5(normalized.encode()).hexdigest()

        if title_hash in seen_hashes:
            continue
        seen_hashes.add(title_hash)

        # Update the trend with clean data
        t['title'] = title
        t['summary'] = summary.strip()[:250]

        # Ensure link is clean
        link = t.get('link', '')
        if link and not link.startswith('http'):
            t['link'] = ''

        cleaned.append(t)

    logger.info(
        f"Cleaned {len(trends)} trends → {len(cleaned)} relevant unique trends "
        f"(rejected {rejected_count} irrelevant articles)"
    )
    return cleaned