from flask import Flask, render_template, jsonify, send_from_directory, abort, Response
import os
import json
from datetime import datetime, timedelta, date
import logging

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_available_dates():
    """Get list of available data dates"""
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    if not os.path.exists(processed_dir):
        return []

    dates = []
    for item in os.listdir(processed_dir):
        date_path = os.path.join(processed_dir, item)
        if os.path.isdir(date_path):
            dates.append(item)

    return sorted(dates, reverse=True)


def load_json_file(filepath, default=None):
    """Safely load JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")

    return default if default is not None else {}


@app.route("/")
def index():
    """Homepage with date selector"""
    dates = get_available_dates()
    return render_template("index.html", dates=dates)


@app.route("/date/<date_str>")
def date_view(date_str):
    """View trends for a specific date"""
    base_path = os.path.join(BASE_DIR, "data", "processed", date_str)

    if not os.path.exists(base_path):
        abort(404)

    kpis = load_json_file(os.path.join(base_path, "kpis.json"))
    trends = load_json_file(os.path.join(base_path, "trends.json"))
    newsletter = load_json_file(os.path.join(base_path, "newsletter.json"))

    return render_template("date_view.html",
                           date=date_str,
                           kpis=kpis,
                           trends=trends,
                           newsletter=newsletter)


@app.route("/date/<date_str>/trend/<trend_category>")
def trend_detail(date_str, trend_category):
    """View details for a specific trend category"""
    base_path = os.path.join(BASE_DIR, "data", "processed", date_str)
    trends = load_json_file(os.path.join(base_path, "trends.json"))

    category_trends = trends.get(trend_category, [])

    return render_template("trend_detail.html",
                           date=date_str,
                           trend_category=trend_category,
                           items=category_trends)


@app.route("/images/<date_str>/<path:filename>")
def serve_image(date_str, filename):
    """Serve images from the processed data directory"""
    images_dir = os.path.join(BASE_DIR, "data", "processed", date_str)
    try:
        return send_from_directory(images_dir, filename)
    except Exception:
        abort(404)


@app.route("/email/<date_str>")
def email_template(date_str):
    """View the email newsletter template for a specific date - ready to copy-paste into Gmail"""
    from generate_email import load_data, get_top_trends, generate_gmail_template

    processed_dir = os.path.join(BASE_DIR, "data", "processed", date_str)
    if not os.path.exists(os.path.join(processed_dir, "trends.json")):
        abort(404)

    data = load_data(date_str)
    top_trends = get_top_trends(data, 10)
    html = generate_gmail_template(data, top_trends)

    return Response(html, mimetype='text/html')


@app.route("/email/")
@app.route("/email")
def email_latest():
    """Redirect to latest date's email template"""
    dates = get_available_dates()
    if dates:
        from generate_email import load_data, get_top_trends, generate_gmail_template
        date_str = dates[0]
        data = load_data(date_str)
        top_trends = get_top_trends(data, 10)
        html = generate_gmail_template(data, top_trends)
        return Response(html, mimetype='text/html')
    else:
        return "No data available. Run: python daily_pipeline.py", 404


@app.route("/api/dates")
def api_dates():
    """API endpoint for available dates"""
    dates = get_available_dates()
    return jsonify(dates)


@app.route("/api/date/<date_str>/kpis")
def api_kpis(date_str):
    """API endpoint for KPIs"""
    base_path = os.path.join(BASE_DIR, "data", "processed", date_str)
    kpis = load_json_file(os.path.join(base_path, "kpis.json"))
    return jsonify(kpis)


@app.route("/api/date/<date_str>/trends")
def api_trends(date_str):
    """API endpoint for trends"""
    base_path = os.path.join(BASE_DIR, "data", "processed", date_str)
    trends = load_json_file(os.path.join(base_path, "trends.json"))
    return jsonify(trends)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
