"""
Generate Email Newsletter Template
===================================
Run this script daily after the pipeline to generate a copy-paste email template.

Usage:
    python generate_email.py              # Generate for today
    python generate_email.py 2026-02-16   # Generate for specific date

Output:
    - Opens the email in your default browser
    - Saves HTML file you can copy-paste into Gmail
"""

import base64
import json
import os
import sys
import webbrowser
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_logo_base64():
    """Get the Johnson logo as base64 data URI for email embedding"""
    logo_path = os.path.join(BASE_DIR, "static", "images", "logo-johnson.png")
    try:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{data}"
    except Exception as e:
        print(f"Warning: Could not load logo: {e}")
    return None


def load_data(date_str):
    """Load processed data for a date"""
    processed_dir = os.path.join(BASE_DIR, "data", "processed", date_str)
    data = {"date": date_str, "trends": {}, "kpis": {}}

    for key, filename in [("trends", "trends.json"), ("kpis", "kpis.json")]:
        filepath = os.path.join(processed_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data[key] = json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")

    return data


def get_top_trends(data, limit=10):
    """Get top 10 trends by priority"""
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


def generate_gmail_template(data, top_trends):
    """Generate a Gmail-friendly HTML email template"""
    date_str = data["date"]
    kpis = data["kpis"]
    total = kpis.get("total_trends", 0)
    sources = kpis.get("total_sources", 0)
    india_count = kpis.get("by_region", {}).get("India", 0)
    global_count = kpis.get("by_region", {}).get("Global", 0)

    # Get logo
    logo_data_uri = get_logo_base64()
    logo_html = ""
    if logo_data_uri:
        logo_html = f'<img src="{logo_data_uri}" alt="H&amp;R Johnson" style="height:52px;width:auto;margin-bottom:12px;border-radius:6px;" /><br>'

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
            priority_color = "#dc2626"
            priority_bg = "#fef2f2"
            priority_emoji = "🔴"
        elif priority == "MEDIUM":
            priority_color = "#d97706"
            priority_bg = "#fffbeb"
            priority_emoji = "🟡"
        else:
            priority_color = "#6b7280"
            priority_bg = "#f3f4f6"
            priority_emoji = "⚪"

        region_emoji = "🇮🇳" if region == "India" else "🌍"

        trend_rows += f"""
        <tr>
            <td style="padding:16px 20px;border-bottom:1px solid #e5e7eb;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td width="44" valign="top">
                            <div style="width:36px;height:36px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%;text-align:center;line-height:36px;color:#fff;font-weight:700;font-size:14px;">{idx}</div>
                        </td>
                        <td style="padding-left:14px;">
                            <div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:6px;line-height:1.4;">{title}</div>
                            <div style="margin-bottom:8px;">
                                <span style="display:inline-block;padding:2px 10px;background:{priority_bg};color:{priority_color};border-radius:12px;font-size:11px;font-weight:700;letter-spacing:0.3px;">{priority_emoji} {priority}</span>
                                <span style="display:inline-block;padding:2px 10px;background:#eff6ff;color:#2563eb;border-radius:12px;font-size:11px;font-weight:600;margin-left:4px;">{category}</span>
                                <span style="display:inline-block;padding:2px 10px;background:#f0fdf4;color:#16a34a;border-radius:12px;font-size:11px;font-weight:600;margin-left:4px;">{region_emoji} {region}</span>
                            </div>
                            {f'<div style="font-size:13px;color:#6b7280;margin-bottom:8px;line-height:1.5;">{summary}</div>' if summary else ''}
                            <div style="font-size:12px;color:#9ca3af;margin-bottom:10px;">📰 {source}</div>
                            <a href="{link}" target="_blank" style="display:inline-block;padding:8px 20px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;text-decoration:none;border-radius:20px;font-size:12px;font-weight:600;">Read Article →</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>"""

    # Category breakdown
    category_rows = ""
    by_category = kpis.get("by_category", {})
    sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    for cat_name, cat_count in sorted_cats[:8]:
        pct = round((cat_count / total * 100)) if total > 0 else 0
        category_rows += f"""
                                    <tr>
                                        <td style="padding:6px 12px;font-size:13px;color:#374151;border-bottom:1px solid #f3f4f6;">{cat_name}</td>
                                        <td style="padding:6px 12px;font-size:13px;color:#6366f1;font-weight:700;text-align:center;border-bottom:1px solid #f3f4f6;">{cat_count}</td>
                                        <td style="padding:6px 12px;border-bottom:1px solid #f3f4f6;">
                                            <div style="background:#e5e7eb;border-radius:4px;height:8px;width:100%;"><div style="background:linear-gradient(90deg,#667eea,#764ba2);border-radius:4px;height:8px;width:{pct}%;"></div></div>
                                        </td>
                                    </tr>"""

    # Footer logo
    footer_logo_html = ""
    if logo_data_uri:
        footer_logo_html = f'<img src="{logo_data_uri}" alt="H&amp;R Johnson" style="height:32px;width:auto;margin-bottom:10px;opacity:0.85;border-radius:4px;" /><br>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>Tile Trends Daily Report — {date_str}</title>
    <style>
        /* Copy button styles - only visible in browser preview */
        .copy-bar {{
            position:fixed;top:0;left:0;right:0;background:#1f2937;padding:12px 24px;
            display:flex;align-items:center;justify-content:space-between;z-index:9999;
            box-shadow:0 4px 6px rgba(0,0,0,0.3);
        }}
        .copy-bar p {{ color:#e5e7eb;margin:0;font-family:sans-serif;font-size:14px; }}
        .copy-bar button {{
            background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;
            padding:10px 24px;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;
            transition:all 0.2s;
        }}
        .copy-bar button:hover {{ transform:translateY(-1px);box-shadow:0 4px 12px rgba(102,126,234,0.4); }}
        .copy-bar .subject-text {{
            background:#374151;color:#a5b4fc;padding:6px 14px;border-radius:6px;
            font-family:monospace;font-size:13px;margin:0 12px;user-select:all;
        }}
        #email-content {{ margin-top:60px; }}
        .copied-msg {{ color:#34d399;font-weight:600;display:none;margin-left:12px;font-family:sans-serif;font-size:13px; }}

        @media print {{ .copy-bar {{ display:none; }} #email-content {{ margin-top:0; }} }}
    </style>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;">

    <!-- BROWSER TOOLBAR - Won't appear in email -->
    <div class="copy-bar">
        <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;">
            <p>📧 <strong>Subject:</strong></p>
            <span class="subject-text">🏛️ Tile Trends Daily Report — {date_str} | {total} Trends from {sources} Sources</span>
            <p>→ <strong>To:</strong> kolhe.abhinandan@hrjohnsonindia.com</p>
        </div>
        <div style="display:flex;align-items:center;">
            <button onclick="copyEmail()">📋 Copy Email Content</button>
            <span class="copied-msg" id="copiedMsg">✅ Copied!</span>
        </div>
    </div>

    <!-- EMAIL CONTENT - Copy everything below this line -->
    <div id="email-content">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f3f4f6;padding:24px 8px;">
        <tr>
            <td align="center">
                <table width="660" cellpadding="0" cellspacing="0" border="0" style="max-width:660px;width:100%;">

                    <!-- HEADER WITH LOGO -->
                    <tr>
                        <td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:36px 28px;border-radius:16px 16px 0 0;text-align:center;">
                            {logo_html}
                            <h1 style="color:#fff;font-size:26px;font-weight:800;margin:0 0 6px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">Tile Trends Intelligence</h1>
                            <p style="color:rgba(255,255,255,0.85);font-size:15px;margin:0;font-family:sans-serif;">Daily Market Report — {date_str}</p>
                            <p style="color:rgba(255,255,255,0.65);font-size:12px;margin:6px 0 0 0;font-family:sans-serif;">H&amp;R Johnson (India) — A Division of Prism Johnson Ltd.</p>
                        </td>
                    </tr>

                    <!-- KPI SNAPSHOT -->
                    <tr>
                        <td style="background:#fff;padding:28px 24px;">
                            <h2 style="font-size:18px;color:#111827;margin:0 0 16px 0;font-weight:700;font-family:sans-serif;">📊 Today's Snapshot</h2>
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td width="25%" style="text-align:center;padding:12px 4px;">
                                        <div style="font-size:30px;font-weight:800;color:#6366f1;font-family:sans-serif;">{total}</div>
                                        <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:1px;font-weight:600;font-family:sans-serif;">Trends</div>
                                    </td>
                                    <td width="25%" style="text-align:center;padding:12px 4px;">
                                        <div style="font-size:30px;font-weight:800;color:#ec4899;font-family:sans-serif;">{sources}</div>
                                        <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:1px;font-weight:600;font-family:sans-serif;">Sources</div>
                                    </td>
                                    <td width="25%" style="text-align:center;padding:12px 4px;">
                                        <div style="font-size:30px;font-weight:800;color:#f59e0b;font-family:sans-serif;">{india_count}</div>
                                        <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:1px;font-weight:600;font-family:sans-serif;">🇮🇳 India</div>
                                    </td>
                                    <td width="25%" style="text-align:center;padding:12px 4px;">
                                        <div style="font-size:30px;font-weight:800;color:#10b981;font-family:sans-serif;">{global_count}</div>
                                        <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:1px;font-weight:600;font-family:sans-serif;">🌍 Global</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- DIVIDER -->
                    <tr><td style="background:#fff;padding:0 24px;"><hr style="border:none;border-top:2px solid #e5e7eb;margin:0;"></td></tr>

                    <!-- TOP 10 TRENDS -->
                    <tr>
                        <td style="background:#fff;padding:24px 24px 8px 24px;">
                            <h2 style="font-size:18px;color:#111827;margin:0 0 4px 0;font-weight:700;font-family:sans-serif;">🔥 Top 10 Trends Today</h2>
                            <p style="font-size:12px;color:#6b7280;margin:0 0 12px 0;font-family:sans-serif;">Curated from 50+ sources across India &amp; Global markets</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background:#fff;padding:0 4px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">{trend_rows}
                            </table>
                        </td>
                    </tr>

                    <!-- CATEGORY BREAKDOWN -->
                    <tr>
                        <td style="background:#fff;padding:28px 24px;">
                            <h2 style="font-size:18px;color:#111827;margin:0 0 14px 0;font-weight:700;font-family:sans-serif;">📈 Category Breakdown</h2>
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
                                <tr style="background:#f9fafb;">
                                    <th style="padding:8px 12px;font-size:11px;color:#6b7280;text-align:left;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;font-family:sans-serif;">Category</th>
                                    <th style="padding:8px 12px;font-size:11px;color:#6b7280;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;font-family:sans-serif;">Count</th>
                                    <th style="padding:8px 12px;font-size:11px;color:#6b7280;text-align:left;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;font-family:sans-serif;">Distribution</th>
                                </tr>{category_rows}
                            </table>
                        </td>
                    </tr>

                    <!-- FOOTER WITH LOGO -->
                    <tr>
                        <td style="background:#1f2937;padding:28px;border-radius:0 0 16px 16px;text-align:center;">
                            {footer_logo_html}
                            <p style="color:#9ca3af;font-size:12px;margin:0 0 6px 0;font-family:sans-serif;">Tile Trends Intelligence — Daily Report</p>
                            <p style="color:#6b7280;font-size:11px;margin:0 0 4px 0;font-family:sans-serif;">H&amp;R Johnson (India) — A Division of Prism Johnson Ltd.</p>
                            <p style="color:#6b7280;font-size:11px;margin:0;font-family:sans-serif;">Data from 50+ sources | {date_str} | {datetime.now().strftime('%I:%M %p')}</p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
    </div>

    <script>
    function copyEmail() {{
        const content = document.getElementById('email-content');
        const range = document.createRange();
        range.selectNodeContents(content);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        document.execCommand('copy');
        selection.removeAllRanges();
        const msg = document.getElementById('copiedMsg');
        msg.style.display = 'inline';
        setTimeout(() => {{ msg.style.display = 'none'; }}, 3000);
    }}
    </script>
</body>
</html>"""

    return html


def main():
    # Get date
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = date.today().isoformat()

    print(f"\n🏛️ Tile Trends Intelligence — Email Template Generator")
    print(f"{'='*55}")
    print(f"📅 Date: {date_str}")

    # Check data exists
    processed_dir = os.path.join(BASE_DIR, "data", "processed", date_str)
    if not os.path.exists(os.path.join(processed_dir, "trends.json")):
        print(f"\n❌ No data found for {date_str}")
        print(f"   Run the pipeline first: python daily_pipeline.py")
        return

    # Load data
    data = load_data(date_str)
    top_trends = get_top_trends(data, 10)
    kpis = data["kpis"]

    print(f"📊 Trends: {kpis.get('total_trends', 0)} | Sources: {kpis.get('total_sources', 0)}")
    print(f"🇮🇳 India: {kpis.get('by_region', {}).get('India', 0)} | 🌍 Global: {kpis.get('by_region', {}).get('Global', 0)}")
    print(f"🔥 Top 10 trends selected")

    # Generate HTML
    html = generate_gmail_template(data, top_trends)

    # Save file
    output_path = os.path.join(processed_dir, "email_template.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Email template saved: {output_path}")
    print(f"   File size: {os.path.getsize(output_path):,} bytes")

    # Open in browser
    print(f"\n🌐 Opening in browser...")
    try:
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
    except Exception:
        pass

    print(f"\n{'='*55}")
    print(f"📧 HOW TO SEND:")
    print(f"{'='*55}")
    print(f"1. Open the HTML file in your browser (should open automatically)")
    print(f"2. Click the '📋 Copy Email Content' button at the top")
    print(f"3. Open Gmail → Compose New Email")
    print(f"4. To: kolhe.abhinandan@hrjohnsonindia.com")
    print(f"5. Subject: 🏛️ Tile Trends Daily Report — {date_str} | {kpis.get('total_trends', 0)} Trends")
    print(f"6. Paste (Ctrl+V) in the email body")
    print(f"7. Send! ✉️")
    print(f"{'='*55}")
    print()

    # Also accessible via Flask
    print(f"💡 TIP: You can also view this at:")
    print(f"   http://127.0.0.1:5000/email/{date_str}")
    print()


if __name__ == "__main__":
    main()