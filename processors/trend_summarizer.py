import logging
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


def normalize_timestamp(timestamp):
    """Normalize timestamp to float for consistent sorting"""
    if timestamp is None:
        return 0.0
    if isinstance(timestamp, (float, int)):
        return float(timestamp)
    if isinstance(timestamp, time.struct_time):
        return time.mktime(timestamp)
    return 0.0


def summarize_trends(trends):
    """Group trends by category and create summaries"""
    summary = defaultdict(list)

    for trend in trends:
        category = trend.get('trend', 'General Trend')
        summary[category].append(trend)

    # Sort each category by priority and timestamp
    for category in summary:
        summary[category] = sorted(
            summary[category],
            key=lambda x: (
                {'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'low'), 1),
                normalize_timestamp(x.get('timestamp', 0))
            ),
            reverse=True
        )

    return dict(summary)