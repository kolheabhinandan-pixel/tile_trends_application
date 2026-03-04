import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bootstrap import cleanup_old_data

if __name__ == "__main__":
    print("Starting cleanup of old data...")
    cleanup_old_data(retention_days=30)
    print("Cleanup completed!")