#!/usr/bin/env python
"""
Quick start script for Tile Trends Dashboard
"""
import os
import sys
import subprocess
import time

def main():
    print("=" * 60)
    print("🏛️  TILE TRENDS INTELLIGENCE DASHBOARD")
    print("=" * 60)
    print()
    
    # Check if data exists
    data_dir = os.path.join(os.path.dirname(__file__), "data", "processed")
    has_data = os.path.exists(data_dir) and len(os.listdir(data_dir)) > 0
    
    if not has_data:
        print("📊 No data found. Running daily pipeline to collect trends...")
        print()
        
        try:
            subprocess.run([sys.executable, "daily_pipeline.py"], check=True)
            print()
            print("✅ Data collection completed!")
            print()
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running pipeline: {e}")
            print("You can run it manually: python daily_pipeline.py")
            print()
    else:
        print("✅ Data found. Skipping pipeline (run 'python daily_pipeline.py' to update)")
        print()
    
    print("🚀 Starting web dashboard...")
    print("📍 Open your browser to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down dashboard. Goodbye!")

if __name__ == "__main__":
    main()