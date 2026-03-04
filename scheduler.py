"""
Daily Scheduler for Tile Trends Intelligence
Runs the pipeline and sends email newsletter at 10 AM daily

Usage:
    python scheduler.py              # Run scheduler (waits until 10 AM)
    python scheduler.py --now        # Run immediately (pipeline + email)
    python scheduler.py --email-only # Send email only (no scraping)
"""

import schedule
import time
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def daily_job():
    """Run the full daily pipeline + send email"""
    logger.info("=" * 60)
    logger.info(f"🕐 Starting scheduled job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Step 1: Run the scraping pipeline
    try:
        from daily_pipeline import run_daily_pipeline
        result = run_daily_pipeline()
        logger.info(f"Pipeline result: {result}")

        if result.get("status") != "success":
            logger.error("Pipeline failed, skipping email")
            return
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return

    # Step 2: Send email newsletter
    try:
        from email_newsletter import send_newsletter
        today = result.get("date")
        success = send_newsletter(date_str=today)
        if success:
            logger.info("✅ Email newsletter sent successfully!")
        else:
            logger.warning("⚠️ Email not sent (check SMTP config)")
    except Exception as e:
        logger.error(f"Email error: {e}", exc_info=True)

    logger.info("=" * 60)
    logger.info("✅ Daily job completed!")
    logger.info("=" * 60)


def send_email_only():
    """Send email for today's existing data without re-scraping"""
    from datetime import date
    from email_newsletter import send_newsletter
    today = date.today().isoformat()
    print(f"\n📧 Sending email for {today}...")
    send_newsletter(date_str=today)


def run_scheduler():
    """Run the scheduler - waits and executes at 10:00 AM daily"""
    logger.info("🕐 Tile Trends Scheduler Started")
    logger.info(f"   Scheduled time: 10:00 AM daily")
    logger.info(f"   Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"   Recipients: kolhe.abhinandan@hrjohnsonindia.com")
    logger.info("   Press Ctrl+C to stop")
    logger.info("")

    # Schedule the job at 10:00 AM every day
    schedule.every().day.at("10:00").do(daily_job)

    # Keep running
    while True:
        schedule.run_pending()
        next_run = schedule.next_run()
        if next_run:
            time_left = next_run - datetime.now()
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            sys.stdout.write(f"\r⏳ Next run in: {hours:02d}h {minutes:02d}m {seconds:02d}s   ")
            sys.stdout.flush()
        time.sleep(30)


if __name__ == "__main__":
    import os
    os.makedirs("logs", exist_ok=True)

    if "--now" in sys.argv:
        print("🚀 Running immediately (pipeline + email)...")
        daily_job()
    elif "--email-only" in sys.argv:
        print("📧 Sending email only (no scraping)...")
        send_email_only()
    else:
        run_scheduler()