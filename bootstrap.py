import os
from datetime import date, datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_daily_folders():
    """Create folder structure for today's data"""
    today = date.today().isoformat()
    
    # Create raw data folders
    raw_path = os.path.join(BASE_DIR, "data", "raw", today)
    raw_html_cache = os.path.join(raw_path, "html_cache")
    
    # Create processed data folders
    processed_path = os.path.join(BASE_DIR, "data", "processed", today)
    images_path = os.path.join(processed_path, "images")
    
    # Create all subdirectories for images
    image_subdirs = [
        "large_format",
        "terrazzo",
        "marble_look",
        "eco_tiles",
        "textured",
        "wood_look",
        "general"
    ]
    
    # Create directories
    os.makedirs(raw_path, exist_ok=True)
    os.makedirs(raw_html_cache, exist_ok=True)
    os.makedirs(processed_path, exist_ok=True)
    os.makedirs(images_path, exist_ok=True)
    
    for subdir in image_subdirs:
        os.makedirs(os.path.join(images_path, subdir), exist_ok=True)
    
    # Create logs directory
    logs_path = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_path, exist_ok=True)
    
    # Create archive directory
    archive_path = os.path.join(BASE_DIR, "data", "archive")
    os.makedirs(archive_path, exist_ok=True)
    
    logger.info(f"✓ Created folder structure for {today}")
    
    return today

def cleanup_old_data(retention_days=30):
    """Archive data older than retention period"""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    raw_base = os.path.join(BASE_DIR, "data", "raw")
    processed_base = os.path.join(BASE_DIR, "data", "processed")
    archive_base = os.path.join(BASE_DIR, "data", "archive")
    
    for base_path in [raw_base, processed_base]:
        if not os.path.exists(base_path):
            continue
        
        for date_folder in os.listdir(base_path):
            try:
                folder_date = datetime.strptime(date_folder, "%Y-%m-%d")
                if folder_date < cutoff_date:
                    # Move to archive
                    src = os.path.join(base_path, date_folder)
                    dst = os.path.join(archive_base, date_folder)
                    
                    if not os.path.exists(dst):
                        import shutil
                        shutil.move(src, dst)
                        logger.info(f"✓ Archived {date_folder}")
            except ValueError:
                continue

if __name__ == "__main__":
    create_daily_folders()
    cleanup_old_data()