import logging
from collections import Counter

logger = logging.getLogger(__name__)

def generate_kpis(trends):
    """Generate Key Performance Indicators from trends data"""
    
    kpis = {
        'total_trends': len(trends),
        'total_sources': len(set(t.get('source', 'Unknown') for t in trends)),
        'by_category': {},
        'by_region': {},
        'by_source': {},
        'by_priority': {},
        'by_sentiment': {}
    }
    
    # Count by category
    categories = [t.get('trend', 'General') for t in trends]
    kpis['by_category'] = dict(Counter(categories))
    
    # Count by region
    regions = [t.get('region', 'Unknown') for t in trends]
    kpis['by_region'] = dict(Counter(regions))
    
    # Count by source
    sources = [t.get('source', 'Unknown') for t in trends]
    kpis['by_source'] = dict(Counter(sources))
    
    # Count by priority
    priorities = [t.get('priority', 'low') for t in trends]
    kpis['by_priority'] = dict(Counter(priorities))
    
    # Count by sentiment
    sentiments = [t.get('sentiment', 'neutral') for t in trends]
    kpis['by_sentiment'] = dict(Counter(sentiments))
    
    # Calculate growth metrics (if historical data available)
    kpis['trending_up'] = [
        cat for cat, count in kpis['by_category'].items() 
        if count >= 3
    ]
    
    return kpis