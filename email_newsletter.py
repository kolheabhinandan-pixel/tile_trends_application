"""
Email Newsletter Automation
Sends top 10 tile trends daily to management at 10 AM

Logo Setup:
    Place your company logo PNG file at:
    static/images/logos/logo-johnson.png
"""

import base64
import smtplib
import json
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, date

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logo path - place your PNG logo here
LOGO_PATH = os.path.join(BASE_DIR, "static", "images", "logo-johnson.png")

# ============================================================
# EMAIL CONFIGURATION
# ============================================================
RECIPIENTS = [
    "kolhe.abhinandan@hrjohnsonindia.com",
]

SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "use_tls": True,
    "sender_email": "kolhe.abhinandan@hrjohnsonindia.com",
    "sender_password": "mktu akbl kaxn ilws",
    "sender_name": "Tile Trends Intelligence",
}


def get_logo_cid():
    """Check if logo file exists for CID embedding"""
    if os.path.exists(LOGO_PATH):
        return True
    else:
        logger.warning(f"Logo not found at: {LOGO_PATH}")
        return False


def attach_logo_to_message(msg):
    """Attach the logo as an inline CID image to the email message"""
    try:
        if os.path.exists(LOGO_PATH):
            with open(LOGO_PATH, "rb") as f:
                logo_data = f.read()
            logo_image = MIMEImage(logo_data, _subtype="png")
            logo_image.add_header("Content-ID", "<johnson_logo>")
            logo_image.add_header("Content-Disposition", "inline", filename="logo-johnson.png")
            msg.attach(logo_image)
            logger.info("Logo attached as CID inline image")
            return True
        else:
            logger.warning(f"Logo not found at: {LOGO_PATH}")
            return False
    except Exception as e:
        logger.warning(f"Could not attach logo: {e}")
        return False


def load_todays_data(date_str=None):
    """Load today's processed trends data"""
    if not date_str:
        date_str = date.today().isoformat()

    processed_dir = os.path.join(BASE_DIR, "data", "processed", date_str)

    trends_file = os.path.join(processed_dir, "trends.json")
    kpis_file = os.path.join(processed_dir, "kpis.json")
    newsletter_file = os.path.join(processed_dir, "newsletter.json")

    data = {
        "date": date_str,
        "trends": {},
        "kpis": {},
        "newsletter": {},
    }

    for key, filepath in [("trends", trends_file), ("kpis", kpis_file), ("newsletter", newsletter_file)]:
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data[key] = json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")

    return data


def get_top_trends(data, limit=10):
    """Extract top 10 trends sorted by priority and recency"""
    all_trends = []

    for category, items in data["trends"].items():
        for item in items:
            item["_category"] = category
            all_trends.append(item)

    priority_map = {"high": 3, "medium": 2, "low": 1}
    all_trends.sort(
        key=lambda x: (
            priority_map.get(x.get("priority", "low"), 0),
            x.get("timestamp", 0),
        ),
        reverse=True,
    )

    return all_trends[:limit]


def build_email_html(data, top_trends):
    """Build a beautiful HTML email with top 10 trends using CID logo"""
    date_str = data["date"]
    kpis = data["kpis"]
    total = kpis.get("total_trends", 0)
    sources = kpis.get("total_sources", 0)
    india_count = kpis.get("by_region", {}).get("India", 0)
    global_count = kpis.get("by_region", {}).get("Global", 0)
    categories_count = len(kpis.get("by_category", {}))

    # Use CID reference for logo (works in all email clients)
    has_logo = get_logo_cid()
    logo_html = ""
    if has_logo:
        logo_html = '<img src="cid:johnson_logo" alt="H&amp;R Johnson" style="height:52px;width:auto;margin-bottom:12px;border-radius:6px;" /><br>'

    footer_logo_html = ""
    if has_logo:
        footer_logo_html = '<img src="cid:johnson_logo" alt="H&amp;R Johnson" style="height:32px;width:auto;margin-bottom:10px;opacity:0.85;border-radius:4px;" /><br>'

    # Build trend rows
    trend_rows = ""
    for idx, trend in enumerate(top_trends, 1):
        title = trend.get("title", "Untitled")
        source = trend.get("source", "Unknown")
        region = trend.get("region", "")
        category = trend.get("_category", "General")
        priority = trend.get("priority", "low").upper()
        link = trend.get("link", "#")
        summary = trend.get("summary", "")[:150]

        if priority == "HIGH":
            priority_color = "#ef4444"
            priority_bg = "#fef2f2"
        elif priority == "MEDIUM":
            priority_color = "#f59e0b"
            priority_bg = "#fffbeb"
        else:
            priority_color = "#6b7280"
            priority_bg = "#f3f4f6"

        region_emoji = "🇮🇳" if region == "India" else "🌍"

        trend_rows += f"""
        <tr>
            <td style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="width: 40px; vertical-align: top;">
                            <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; text-align: center; line-height: 36px; color: white; font-weight: 700; font-size: 14px;">
                                {idx}
                            </div>
                        </td>
                        <td style="padding-left: 16px;">
                            <div style="font-size: 16px; font-weight: 600; color: #1f2937; margin-bottom: 6px; line-height: 1.4;">
                                {title}
                            </div>
                            <div style="margin-bottom: 8px;">
                                <span style="display: inline-block; padding: 2px 10px; background: {priority_bg}; color: {priority_color}; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{priority}</span>
                                <span style="display: inline-block; padding: 2px 10px; background: #eff6ff; color: #3b82f6; border-radius: 12px; font-size: 11px; font-weight: 600; margin-left: 4px;">{category}</span>
                                <span style="display: inline-block; padding: 2px 10px; background: #f0fdf4; color: #16a34a; border-radius: 12px; font-size: 11px; font-weight: 600; margin-left: 4px;">{region_emoji} {region}</span>
                            </div>
                            {f'<div style="font-size: 13px; color: #6b7280; margin-bottom: 8px; line-height: 1.5;">{summary}...</div>' if summary else ''}
                            <div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px;">📰 Source: {source}</div>
                            <a href="{link}" target="_blank" style="display: inline-block; padding: 8px 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 20px; font-size: 12px; font-weight: 600;">Read Full Article →</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """

    # Category breakdown
    category_rows = ""
    by_category = kpis.get("by_category", {})
    sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    for cat_name, cat_count in sorted_categories[:8]:
        pct = round((cat_count / total * 100)) if total > 0 else 0
        category_rows += f"""
        <tr>
            <td style="padding: 8px 16px; font-size: 13px; color: #374151; border-bottom: 1px solid #f3f4f6;">{cat_name}</td>
            <td style="padding: 8px 16px; font-size: 13px; color: #6366f1; font-weight: 700; text-align: center; border-bottom: 1px solid #f3f4f6;">{cat_count}</td>
            <td style="padding: 8px 16px; border-bottom: 1px solid #f3f4f6;">
                <div style="background: #e5e7eb; border-radius: 4px; height: 8px; width: 100%;">
                    <div style="background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px; height: 8px; width: {pct}%;"></div>
                </div>
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 32px 16px;">
            <tr>
                <td align="center">
                    <table width="680" cellpadding="0" cellspacing="0" style="max-width: 680px; width: 100%;">

                        <!-- Header with Logo -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 32px; border-radius: 16px 16px 0 0; text-align: center;">
                                {logo_html}
                                <h1 style="color: white; font-size: 28px; font-weight: 800; margin: 0 0 8px 0;">Tile Trends Intelligence</h1>
                                <p style="color: rgba(255,255,255,0.85); font-size: 16px; margin: 0;">Daily Market Report — {date_str}</p>
                                <p style="color: rgba(255,255,255,0.65); font-size: 12px; margin: 6px 0 0 0;">H&amp;R Johnson (India) — A Division of Prism Johnson Ltd.</p>
                            </td>
                        </tr>

                        <!-- KPI Summary -->
                        <tr>
                            <td style="background: white; padding: 32px;">
                                <h2 style="font-size: 20px; color: #1f2937; margin: 0 0 20px 0; font-weight: 700;">📊 Today's Snapshot</h2>
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="25%" style="text-align: center; padding: 16px 8px;">
                                            <div style="font-size: 32px; font-weight: 800; color: #6366f1;">{total}</div>
                                            <div style="font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Trends</div>
                                        </td>
                                        <td width="25%" style="text-align: center; padding: 16px 8px;">
                                            <div style="font-size: 32px; font-weight: 800; color: #ec4899;">{sources}</div>
                                            <div style="font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Sources</div>
                                        </td>
                                        <td width="25%" style="text-align: center; padding: 16px 8px;">
                                            <div style="font-size: 32px; font-weight: 800; color: #f59e0b;">{india_count}</div>
                                            <div style="font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">🇮🇳 India</div>
                                        </td>
                                        <td width="25%" style="text-align: center; padding: 16px 8px;">
                                            <div style="font-size: 32px; font-weight: 800; color: #10b981;">{global_count}</div>
                                            <div style="font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">🌍 Global</div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <tr><td style="background: white; padding: 0 32px;"><hr style="border: none; border-top: 2px solid #e5e7eb; margin: 0;"></td></tr>

                        <!-- Top 10 Trends -->
                        <tr>
                            <td style="background: white; padding: 32px 32px 8px 32px;">
                                <h2 style="font-size: 20px; color: #1f2937; margin: 0 0 4px 0; font-weight: 700;">🔥 Top 10 Trends Today</h2>
                                <p style="font-size: 13px; color: #6b7280; margin: 0 0 16px 0;">Curated from 50+ sources across India & Global markets</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="background: white; padding: 0 12px;">
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    {trend_rows}
                                </table>
                            </td>
                        </tr>

                        <!-- Category Breakdown -->
                        <tr>
                            <td style="background: white; padding: 32px;">
                                <h2 style="font-size: 20px; color: #1f2937; margin: 0 0 16px 0; font-weight: 700;">📈 Category Breakdown</h2>
                                <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                                    <tr style="background: #f9fafb;">
                                        <th style="padding: 10px 16px; font-size: 12px; color: #6b7280; text-align: left; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Category</th>
                                        <th style="padding: 10px 16px; font-size: 12px; color: #6b7280; text-align: center; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Count</th>
                                        <th style="padding: 10px 16px; font-size: 12px; color: #6b7280; text-align: left; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Distribution</th>
                                    </tr>
                                    {category_rows}
                                </table>
                            </td>
                        </tr>

                        <!-- Footer with Logo -->
                        <tr>
                            <td style="background: #1f2937; padding: 32px; border-radius: 0 0 16px 16px; text-align: center;">
                                {footer_logo_html}
                                <p style="color: #9ca3af; font-size: 13px; margin: 0 0 8px 0;">Tile Trends Intelligence — Automated Daily Report</p>
                                <p style="color: #6b7280; font-size: 11px; margin: 0 0 4px 0;">H&amp;R Johnson (India) — A Division of Prism Johnson Ltd.</p>
                                <p style="color: #6b7280; font-size: 11px; margin: 0;">Data scraped from 50+ sources | Generated on {date_str} at {datetime.now().strftime('%H:%M')}</p>
                                <p style="color: #6b7280; font-size: 11px; margin: 8px 0 0 0;">This is an automated email. Please do not reply.</p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return html


def build_plain_text(data, top_trends):
    """Build plain text fallback for email"""
    date_str = data["date"]
    kpis = data["kpis"]

    text = f"""
🏛️ TILE TRENDS INTELLIGENCE — DAILY REPORT
H&R Johnson (India) — A Division of Prism Johnson Ltd.
Date: {date_str}
{'='*60}

📊 TODAY'S SNAPSHOT
• Total Trends: {kpis.get('total_trends', 0)}
• Data Sources: {kpis.get('total_sources', 0)}
• India: {kpis.get('by_region', {}).get('India', 0)} trends
• Global: {kpis.get('by_region', {}).get('Global', 0)} trends

{'='*60}
🔥 TOP 10 TRENDS TODAY
{'='*60}
"""

    for idx, trend in enumerate(top_trends, 1):
        title = trend.get("title", "Untitled")
        source = trend.get("source", "Unknown")
        region = trend.get("region", "")
        category = trend.get("_category", "General")
        priority = trend.get("priority", "low").upper()
        link = trend.get("link", "")
        summary = trend.get("summary", "")[:120]

        text += f"""
{idx}. [{priority}] {title}
   Category: {category} | Region: {region} | Source: {source}
   {f'Summary: {summary}...' if summary else ''}
   🔗 {link}
"""

    text += f"""
{'='*60}
📈 CATEGORY BREAKDOWN
{'='*60}
"""
    by_category = kpis.get("by_category", {})
    for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        text += f"  • {cat}: {count} trends\n"

    text += f"""
{'='*60}
This is an automated report from Tile Trends Intelligence.
H&R Johnson (India) — A Division of Prism Johnson Ltd.
Data scraped from 50+ sources on {date_str}.
"""

    return text


def send_newsletter(date_str=None, recipients=None):
    """Send the daily newsletter email with CID-embedded logo"""
    if not recipients:
        recipients = RECIPIENTS

    if not date_str:
        date_str = date.today().isoformat()

    if not SMTP_CONFIG["sender_email"] or not SMTP_CONFIG["sender_password"]:
        logger.error("❌ SMTP credentials not configured!")
        print("\n" + "="*60)
        print("⚠️  EMAIL SETUP REQUIRED")
        print("="*60)
        print(f"\nTo send emails, update the SMTP_CONFIG in:")
        print(f"  {os.path.join(BASE_DIR, 'email_newsletter.py')}")
        print(f"\nSet these values:")
        print(f'  "sender_email": "your-email@gmail.com"')
        print(f'  "sender_password": "your-app-password"')
        print(f"\nFor Gmail: Enable 2FA → Create App Password at:")
        print(f"  https://myaccount.google.com/apppasswords")
        print("="*60)

        data = load_todays_data(date_str)
        top_trends = get_top_trends(data, 10)
        html = build_email_html(data, top_trends)
        preview_path = os.path.join(BASE_DIR, "data", "processed", date_str, "newsletter_email.html")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n✅ Newsletter HTML saved for preview at:")
        print(f"   {preview_path}")
        return False

    data = load_todays_data(date_str)
    if not data["trends"]:
        logger.error(f"No trends data found for {date_str}")
        return False

    top_trends = get_top_trends(data, 10)
    if not top_trends:
        logger.error("No trends to send")
        return False

    html_body = build_email_html(data, top_trends)
    text_body = build_plain_text(data, top_trends)

    # Use 'related' type to support CID inline images
    msg = MIMEMultipart("related")
    msg["Subject"] = f"🏛️ Tile Trends Daily Report — {date_str} | {data['kpis'].get('total_trends', 0)} Trends from {data['kpis'].get('total_sources', 0)} Sources"
    msg["From"] = f"{SMTP_CONFIG['sender_name']} <{SMTP_CONFIG['sender_email']}>"
    msg["To"] = ", ".join(recipients)

    # Create alternative part for text/html
    msg_alternative = MIMEMultipart("alternative")
    msg_alternative.attach(MIMEText(text_body, "plain", "utf-8"))
    msg_alternative.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(msg_alternative)

    # Attach logo as inline CID image
    logo_attached = attach_logo_to_message(msg)
    if logo_attached:
        print("📎 Logo attached as inline CID image")
    else:
        print("⚠️ Logo not attached (file not found)")

    # Save preview
    preview_path = os.path.join(BASE_DIR, "data", "processed", date_str, "newsletter_email.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_body)

    try:
        if SMTP_CONFIG["use_tls"]:
            server = smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"])
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP_SSL(SMTP_CONFIG["server"], SMTP_CONFIG["port"])

        server.login(SMTP_CONFIG["sender_email"], SMTP_CONFIG["sender_password"])
        server.sendmail(SMTP_CONFIG["sender_email"], recipients, msg.as_string())
        server.quit()

        logger.info(f"✅ Newsletter sent successfully to {', '.join(recipients)}")
        print(f"\n✅ Email sent to: {', '.join(recipients)}")
        print(f"   Subject: Tile Trends Daily Report — {date_str}")
        print(f"   Trends: {len(top_trends)} top trends included")
        print(f"   Logo: {'✅ Embedded via CID' if logo_attached else '⚠️ Not included'}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("❌ SMTP Authentication failed!")
        print("\n❌ Authentication failed. For Gmail:")
        print("   1. Enable 2-Factor Authentication")
        print("   2. Create an App Password at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🏛️ Tile Trends Intelligence — Email Newsletter")
    print("=" * 50)
    send_newsletter()
