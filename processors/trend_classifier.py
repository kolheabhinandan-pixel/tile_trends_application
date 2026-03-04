import logging

logger = logging.getLogger(__name__)


def classify_trends(trends):
    """Additional classification and enrichment of trends with tile-specific context"""
    classified = []

    for trend in trends:
        title_lower = trend['title'].lower()
        summary_lower = trend.get('summary', '').lower()
        combined = title_lower + ' ' + summary_lower

        # Sentiment analysis — tile industry specific
        positive_words = [
            'innovative', 'new', 'latest', 'trending', 'popular', 'growth',
            'launch', 'expand', 'award', 'breakthrough', 'leading', 'best',
            'premium', 'luxury', 'success', 'record', 'boost', 'demand',
            'collection', 'design', 'modern', 'sustainable', 'eco-friendly',
            'showroom', 'unveiled', 'introduced', 'showcase',
        ]
        negative_words = [
            'challenge', 'issue', 'problem', 'decline', 'loss', 'fail',
            'drop', 'slow', 'concern', 'risk', 'crisis', 'shortage',
            'dumping', 'anti-dumping', 'closure', 'shutdown',
        ]

        if any(word in combined for word in positive_words):
            trend['sentiment'] = 'positive'
        elif any(word in combined for word in negative_words):
            trend['sentiment'] = 'negative'
        else:
            trend['sentiment'] = 'neutral'

        # Priority based on tile-industry keywords
        high_priority = [
            'breakthrough', 'revolutionary', 'game-changing', 'record',
            'billion', 'crore', 'major', 'first', 'exclusive',
            'johnson', 'h&r johnson', 'porselano', 'marbonite', 'endura',
            'prism johnson', 'large format', 'mega slab',
            'cersaie', 'coverings', 'exhibition',
        ]
        medium_priority = [
            'innovative', 'new', 'latest', 'launch', 'expand',
            'growth', 'trend', 'collection', 'design', 'market',
            'kajaria', 'somany', 'orient bell', 'nitco', 'agl',
            'ceramic', 'vitrified', 'porcelain', 'sanitaryware',
            'bath fitting', 'marble', 'quartz',
        ]

        if any(word in combined for word in high_priority):
            trend['priority'] = 'high'
        elif any(word in combined for word in medium_priority):
            trend['priority'] = 'medium'
        else:
            trend['priority'] = 'low'

        classified.append(trend)

    return classified