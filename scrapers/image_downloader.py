import os
import logging
import requests
import hashlib
import time
from urllib.parse import urlparse, quote

logger = logging.getLogger(__name__)

# Reliable free image API
UNSPLASH_SEARCH_URL = "https://source.unsplash.com/800x600/?{query}"
PICSUM_URL = "https://picsum.photos/seed/{seed}/800/600"


def download_image(image_url, save_dir, filename=None):
    """Download an image from URL and save it locally"""
    if not image_url or not image_url.startswith('http'):
        return None

    try:
        os.makedirs(save_dir, exist_ok=True)

        if not filename:
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
            ext = _get_extension(image_url)
            filename = f"img_{url_hash}{ext}"

        filepath = os.path.join(save_dir, filename)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            return filepath

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/*,*/*;q=0.8',
            'Referer': 'https://www.google.com/',
        }

        response = requests.get(image_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type and 'octet-stream' not in content_type:
            logger.warning(f"Not an image: {content_type} for {image_url}")
            return None

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        if os.path.getsize(filepath) < 500:
            os.remove(filepath)
            return None

        logger.info(f"✓ Downloaded image: {filename}")
        return filepath

    except Exception as e:
        logger.warning(f"Failed to download {image_url}: {e}")
        return None


# After this many timeouts/errors, a source is skipped for the rest of the run
MAX_SOURCE_FAILURES = 2
CATEGORY_IMAGE_TIMEOUT = 5
_source_failures = {}


def _source_available(name):
    return _source_failures.get(name, 0) < MAX_SOURCE_FAILURES


def _record_failure(name, category, error):
    _source_failures[name] = _source_failures.get(name, 0) + 1
    logger.warning(f"{name} failed for {category}: {error}")
    if not _source_available(name):
        logger.warning(f"{name} is not responding - skipping it for the rest of this run")


def _reuse_previous_image(filename, save_dir, filepath):
    """Copy the same category image from the most recent earlier day, if any"""
    import shutil
    processed_root = os.path.dirname(os.path.dirname(os.path.abspath(save_dir)))
    today = os.path.basename(os.path.dirname(os.path.abspath(save_dir)))
    try:
        days = sorted((d for d in os.listdir(processed_root) if d < today), reverse=True)
    except OSError:
        return None
    for day in days[:30]:
        candidate = os.path.join(processed_root, day, "images", filename)
        if os.path.exists(candidate) and os.path.getsize(candidate) > 1000:
            shutil.copyfile(candidate, filepath)
            logger.info(f"✓ Reused {filename} from {day}")
            return filepath
    return None


def fetch_category_image(category, save_dir, index=0):
    """Fetch a relevant image for a trend category using free image sources"""
    from config import CATEGORY_IMAGE_KEYWORDS

    os.makedirs(save_dir, exist_ok=True)

    keywords = CATEGORY_IMAGE_KEYWORDS.get(category, "modern tile design")
    safe_category = category.lower().replace(' ', '_').replace('&', 'and')
    filename = f"{safe_category}_{index}.jpg"
    filepath = os.path.join(save_dir, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        return filepath

    # Strategy 1: Try Unsplash source (redirects to random matching image)
    if _source_available("Unsplash"):
        try:
            search_query = quote(keywords)
            url = f"https://source.unsplash.com/800x600/?{search_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
            response = requests.get(url, headers=headers, timeout=CATEGORY_IMAGE_TIMEOUT, allow_redirects=True)
            if response.status_code == 200 and len(response.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✓ Fetched Unsplash image for {category}")
                return filepath
            _record_failure("Unsplash", category, f"HTTP {response.status_code}")
        except Exception as e:
            _record_failure("Unsplash", category, e)

    # Strategy 2: Try Picsum (random but consistent per seed)
    if _source_available("Picsum"):
        try:
            seed = hashlib.md5(f"{category}_{index}".encode()).hexdigest()[:8]
            url = f"https://picsum.photos/seed/{seed}/800/600"
            response = requests.get(url, timeout=CATEGORY_IMAGE_TIMEOUT, allow_redirects=True)
            if response.status_code == 200 and len(response.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✓ Fetched Picsum image for {category}")
                return filepath
            _record_failure("Picsum", category, f"HTTP {response.status_code}")
        except Exception as e:
            _record_failure("Picsum", category, e)

    # Strategy 3: Reuse the same category image from an earlier day
    return _reuse_previous_image(filename, save_dir, filepath)


def _get_extension(url):
    """Get file extension from URL"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
        if path.endswith(ext):
            return ext
    return '.jpg'
