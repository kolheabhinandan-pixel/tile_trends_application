from bootstrap import create_daily_folders
from scrapers.india_scraper import scrape_india
from scrapers.global_scraper import scrape_global
from scrapers.news_scraper import scrape_news
from scrapers.image_downloader import download_image, fetch_category_image
from scrapers.base_scraper import BaseScraper
from processors.trend_cleaner import clean_trends
from processors.trend_classifier import classify_trends
from processors.trend_summarizer import summarize_trends
from processors.kpi_generator import generate_kpis
from processors.newsletter_builder import build_newsletter
import json
import os
import logging
from datetime import datetime

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def reclassify_trends(trends):
    """Re-classify all trends using the latest category keywords.
    
    This ensures that even if raw data was scraped with old categories,
    the final output uses the updated Johnson product structure categories.
    """
    scraper = BaseScraper()
    for trend in trends:
        title = trend.get('title', '')
        summary = trend.get('summary', '')
        trend['trend'] = scraper.classify_trend(title, summary)
    return trends


def run_daily_pipeline():
    """Run the complete daily scraping and processing pipeline"""
    logger.info("=" * 60)
    logger.info("Starting daily pipeline")
    logger.info("=" * 60)

    # Create folders for today
    today = create_daily_folders()
    logger.info(f"Processing date: {today}")

    raw_dir = os.path.join(BASE_DIR, "data", "raw", today)
    processed_dir = os.path.join(BASE_DIR, "data", "processed", today)
    images_dir = os.path.join(processed_dir, "images")

    # Step 1: Scrape all sources
    logger.info("Step 1: Scraping data sources...")
    all_trends = []

    try:
        india_trends = scrape_india()
        logger.info(f"✓ Scraped {len(india_trends)} trends from Indian sources")
        all_trends.extend(india_trends)
    except Exception as e:
        logger.error(f"✗ Error scraping Indian sources: {e}")

    try:
        global_trends = scrape_global()
        logger.info(f"✓ Scraped {len(global_trends)} trends from global sources")
        all_trends.extend(global_trends)
    except Exception as e:
        logger.error(f"✗ Error scraping global sources: {e}")

    try:
        news_trends = scrape_news()
        logger.info(f"✓ Scraped {len(news_trends)} trends from news sources (50+ queries)")
        all_trends.extend(news_trends)
    except Exception as e:
        logger.error(f"✗ Error scraping news sources: {e}")

    logger.info(f"Total trends collected: {len(all_trends)}")

    # Save raw data
    with open(os.path.join(raw_dir, "raw_trends.json"), "w", encoding='utf-8') as f:
        json.dump(all_trends, f, indent=2, ensure_ascii=False)

    # Step 2: Clean, deduplicate, and FILTER for relevance
    logger.info("Step 2: Cleaning, deduplicating, and filtering for relevance...")
    cleaned_trends = clean_trends(all_trends)
    logger.info(f"✓ Relevant trends after cleaning: {len(cleaned_trends)}")

    # Step 3: Re-classify trends with latest category keywords
    logger.info("Step 3: Classifying trends into Johnson product categories...")
    cleaned_trends = reclassify_trends(cleaned_trends)
    logger.info(f"✓ Re-classified {len(cleaned_trends)} trends")

    # Step 4: Add sentiment & priority
    logger.info("Step 4: Adding sentiment and priority...")
    classified_trends = classify_trends(cleaned_trends)
    logger.info(f"✓ Classified trends: {len(classified_trends)}")

    # Step 5: Download images from article URLs
    logger.info("Step 5: Downloading article images...")
    image_count = 0
    for trend in classified_trends:
        if trend.get('image_url') and trend['image_url'].startswith('http'):
            try:
                local_path = download_image(trend['image_url'], images_dir)
                if local_path:
                    trend['local_image'] = os.path.relpath(local_path, processed_dir)
                    image_count += 1
            except Exception as e:
                logger.warning(f"Image download error: {e}")
    logger.info(f"✓ Downloaded {image_count} article images")

    # Step 6: Fetch category images for trends without images
    logger.info("Step 6: Fetching category images for trends without images...")
    category_image_cache = {}
    category_counters = {}
    for trend in classified_trends:
        if not trend.get('local_image'):
            category = trend.get('trend', 'General Trend')
            idx = category_counters.get(category, 0)
            cache_key = f"{category}_{idx}"

            if cache_key not in category_image_cache:
                try:
                    local_path = fetch_category_image(category, images_dir, index=idx)
                    if local_path:
                        rel_path = os.path.relpath(local_path, processed_dir)
                        category_image_cache[cache_key] = rel_path
                        image_count += 1
                except Exception as e:
                    logger.warning(f"Category image fetch error: {e}")

            if cache_key in category_image_cache:
                trend['local_image'] = category_image_cache[cache_key]

            category_counters[category] = idx + 1

    logger.info(f"✓ Total images: {image_count}")

    # Step 7: Summarize by category
    logger.info("Step 7: Summarizing trends by category...")
    summarized = summarize_trends(classified_trends)
    logger.info(f"✓ Created summaries for {len(summarized)} categories")

    # Step 8: Generate KPIs
    logger.info("Step 8: Generating KPIs...")
    kpis = generate_kpis(classified_trends)
    logger.info(f"✓ Generated KPIs")

    # Step 9: Build newsletter
    logger.info("Step 9: Building newsletter...")
    newsletter = build_newsletter(classified_trends, kpis, today)
    logger.info(f"✓ Newsletter created")

    # Save processed data
    with open(os.path.join(processed_dir, "trends.json"), "w", encoding='utf-8') as f:
        json.dump(summarized, f, indent=2, ensure_ascii=False)

    with open(os.path.join(processed_dir, "kpis.json"), "w", encoding='utf-8') as f:
        json.dump(kpis, f, indent=2, ensure_ascii=False)

    with open(os.path.join(processed_dir, "newsletter.json"), "w", encoding='utf-8') as f:
        json.dump(newsletter, f, indent=2, ensure_ascii=False)

    logger.info("=" * 60)
    logger.info("✅ Daily pipeline completed successfully!")
    logger.info(f"   Relevant trends: {len(classified_trends)}")
    logger.info(f"   Categories: {len(summarized)}")
    logger.info(f"   Images: {image_count}")
    logger.info("=" * 60)

    return {
        'status': 'success',
        'date': today,
        'total_trends': len(classified_trends),
        'categories': len(summarized),
        'images_downloaded': image_count
    }


if __name__ == "__main__":
    try:
        result = run_daily_pipeline()
        print(json.dumps(result, indent=2))
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(json.dumps({'status': 'error', 'message': str(e)}))