from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


def normalize_timestamp(timestamp):
    """Normalize timestamp to float for consistent handling"""
    if timestamp is None:
        return 0.0
    if isinstance(timestamp, (float, int)):
        return float(timestamp)
    if isinstance(timestamp, time.struct_time):
        return time.mktime(timestamp)
    return 0.0


def build_newsletter(trends, kpis, date_str):
    """Build a newsletter-style summary"""
    newsletter = {
        'date': date_str,
        'title': f'Tile Trends Newsletter - {date_str}',
        'summary': generate_executive_summary(trends, kpis, date_str),
        'top_trends': get_top_trends(trends, 5),
        'regional_insights': get_regional_insights(trends),
        'kpis': kpis
    }
    return newsletter


def generate_executive_summary(trends, kpis, date_str):
    """Generate executive summary"""
    total_trends = len(trends)
    top_category = max(kpis['by_category'].items(), key=lambda x: x[1])[0] if kpis['by_category'] else 'N/A'
    india_count = kpis['by_region'].get('India', 0)
    global_count = kpis['by_region'].get('Global', 0)
    sources_count = kpis['total_sources']

    summary = f"""📊 Daily Tile Intelligence Report — {date_str}

Today we tracked {total_trends} tile trends from {sources_count} sources across India and global markets.

🇮🇳 India: {india_count} trends | 🌍 Global: {global_count} trends

🔥 Top Category: {top_category} ({kpis['by_category'].get(top_category, 0)} mentions)

📈 Key Highlights:
• {sources_count} unique data sources monitored
• {len(kpis.get('trending_up', []))} categories trending up
• {kpis['by_priority'].get('high', 0)} high-priority trends detected

This report covers the latest developments in tile design, manufacturing, market growth, and innovation from 50+ sources including Google News, industry RSS feeds, and company websites."""

    return summary.strip()


def get_top_trends(trends, limit=5):
    """Get top trends by priority"""
    sorted_trends = sorted(trends, key=lambda x: (
        {'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'low'), 1),
        normalize_timestamp(x.get('timestamp', 0))
    ), reverse=True)
    return sorted_trends[:limit]


def get_regional_insights(trends):
    """Get insights by region"""
    insights = {}

    for trend in trends:
        region = trend.get('region', 'Unknown')
        if region not in insights:
            insights[region] = {
                'count': 0,
                'top_category': {},
                'sources': set()
            }

        insights[region]['count'] += 1
        insights[region]['sources'].add(trend.get('source', 'Unknown'))

        category = trend.get('trend', 'General')
        insights[region]['top_category'][category] = insights[region]['top_category'].get(category, 0) + 1

    for region in insights:
        insights[region]['sources'] = list(insights[region]['sources'])
        if insights[region]['top_category']:
            insights[region]['top_category'] = max(
                insights[region]['top_category'].items(), key=lambda x: x[1]
            )[0]
        else:
            insights[region]['top_category'] = 'N/A'

    return insights