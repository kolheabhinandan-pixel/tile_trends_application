#!/usr/bin/env python
"""
Test script to verify the setup is correct
"""
import os
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import flask
        import requests
        import bs4
        import lxml
        import feedparser
        print("✅ All required packages installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_folders():
    """Test if folder structure is correct"""
    print("\nTesting folder structure...")
    required_folders = [
        "scrapers",
        "processors",
        "templates",
        "static",
        "static/css",
        "static/js",
        "logs",
        "scripts"
    ]
    
    all_exist = True
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"✅ {folder}")
        else:
            print(f"❌ {folder} - missing")
            all_exist = False
    
    return all_exist

def test_files():
    """Test if required files exist"""
    print("\nTesting required files...")
    required_files = [
        "app.py",
        "bootstrap.py",
        "daily_pipeline.py",
        "config.py",
        "requirements.txt",
        "scrapers/base_scraper.py",
        "scrapers/india_scraper.py",
        "scrapers/global_scraper.py",
        "scrapers/news_scraper.py",
        "processors/trend_cleaner.py",
        "processors/kpi_generator.py",
        "templates/base.html",
        "templates/index.html",
        "static/css/dashboard.css"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - missing")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("🏛️  TILE TRENDS DASHBOARD - SETUP TEST")
    print("=" * 60)
    print()
    
    test1 = test_imports()
    test2 = test_folders()
    test3 = test_files()
    
    print("\n" + "=" * 60)
    if test1 and test2 and test3:
        print("✅ ALL TESTS PASSED!")
        print("\nYou're ready to go! Next steps:")
        print("1. Run: python bootstrap.py")
        print("2. Run: python daily_pipeline.py")
        print("3. Run: python app.py")
        print("4. Open: http://localhost:5000")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before proceeding.")
    print("=" * 60)

if __name__ == "__main__":
    main()