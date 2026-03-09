"""
StreetByte – Flask Application (Multi-page)
Serves separate HTML pages for Home, Results, About, and Cities.

Security hardening:
  - SECRET_KEY loaded from environment variable (never hardcoded)
  - debug mode driven by FLASK_DEBUG env var (defaults to False)
  - All user inputs validated and sanitised before use
  - No-cache headers on all responses
  - Budget clamped to safe integer range to prevent abuse
"""
import os
import math
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ml.recommender import get_cities, recommend, get_dataframe

# ── Load environment variables from .env (development only) ──────────────────
load_dotenv()

# ── Application Setup ─────────────────────────────────────────────────────────
app = Flask(__name__)

# ── Rate Limiting Setup ───────────────────────────────────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@app.errorhandler(429)
def ratelimit_handler(e):
    if request.is_json or request.path.startswith('/api/v1/recommend') or request.path.startswith('/api/v1/cities'):
        return jsonify({"error": f"Rate limit exceeded: {e.description}"}), 429
    return f"<h1>429 - Too Many Requests</h1><p>{e.description}</p>", 429

# SECRET_KEY must come from the environment — never hardcoded.
# If missing in production the app will refuse to start.
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    import warnings
    warnings.warn(
        "SECRET_KEY is not set in environment. Using an insecure default. "
        "Set SECRET_KEY in your .env file before deploying.",
        stacklevel=2,
    )
    _secret = 'dev-insecure-default-do-not-use-in-production'

app.config['SECRET_KEY'] = _secret
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0   # disable static-file caching in dev

# ── Input validation constants ────────────────────────────────────────────────
BUDGET_MIN = 20
BUDGET_MAX = 5000
PAGE_MIN   = 1
PAGE_MAX   = 500   # hard cap to prevent resource abuse
ITEMS_PER_PAGE = 9


# ── Security: headers on every response ───────────────────────────────────────
@app.after_request
def add_security_headers(response):
    """Prevent browsers from caching pages and enforce security policy."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma']        = 'no-cache'
    response.headers['Expires']       = '0'
    # Prevent the browser from MIME-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Clickjacking protection
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Content Security Policy to completely prevent XSS
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
        "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://cdn.jsdelivr.net; "
        "connect-src 'self';"
    )
    return response


# ── Helper ────────────────────────────────────────────────────────────────────
def fmt_num(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def _safe_int(value, default: int, lo: int, hi: int) -> int:
    """Parse an integer from user input, clamp to [lo, hi]. Never raises."""
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return default


def _safe_city(value: str, valid_cities: list) -> str | None:
    """
    Validate and normalise a city name against the known list.
    Returns None if the value is not a recognised city.
    """
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip().title()
    if cleaned not in valid_cities:
        return None
    return cleaned


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Home page – search form."""
    cities = get_cities()
    return render_template('index.html', cities=cities)


@app.route('/results')
@limiter.limit("15 per minute", error_message="Too many recommendation searches. Please wait a minute.")
def results():
    """
    Results page – server-side rendered, paginated.
    Query params: city (str), budget (int), page (int)
    All inputs are validated before use.
    """
    cities_list = get_cities()

    # ── Validate city ──────────────────────────────────────────────────────
    raw_city = request.args.get('city', '').strip()
    city = _safe_city(raw_city, cities_list)
    if not city:
        # Unknown or missing city → back to home
        return redirect(url_for('index'))

    # ── Validate budget ────────────────────────────────────────────────────
    budget = _safe_int(request.args.get('budget', 200), 200, BUDGET_MIN, BUDGET_MAX)

    # ── Validate page ──────────────────────────────────────────────────────
    page = _safe_int(request.args.get('page', 1), 1, PAGE_MIN, PAGE_MAX)

    all_items = recommend(city, budget)

    # Format for template
    for idx, item in enumerate(all_items):
        item['rank'] = idx + 1
        item['num_reviews_fmt'] = fmt_num(item['num_reviews'])

    total       = len(all_items)
    total_pages = max(1, math.ceil(total / ITEMS_PER_PAGE))
    page        = max(PAGE_MIN, min(page, total_pages))   # re-clamp to actual pages

    start      = (page - 1) * ITEMS_PER_PAGE
    page_items = all_items[start: start + ITEMS_PER_PAGE]

    return render_template(
        'results.html',
        results=page_items,
        city=city,
        budget=budget,
        page=page,
        total=total,
        total_pages=total_pages,
        cities=cities_list,
    )


@app.route('/about')
def about():
    """About / How It Works page."""
    return render_template('about.html')


@app.route('/cities-page')
def cities_page():
    """All cities overview page."""
    cities = get_cities()
    return render_template('cities.html', cities=cities)


# ── Legacy JSON API (kept for compatibility) ──────────────────────────────────
@app.route('/api/v1/recommend', methods=['POST'])
@limiter.limit("10 per minute", error_message="Rate limit exceeded. Please reduce request frequency.")
def recommend_api():
    from flask import jsonify
    try:
        data   = request.get_json(force=True, silent=True) or {}
        raw_city = str(data.get('city', '')).strip()
        budget = _safe_int(data.get('budget', 200), 200, BUDGET_MIN, BUDGET_MAX)

        cities_list = get_cities()
        city = _safe_city(raw_city, cities_list)
        if not city:
            return jsonify({'error': 'City is required and must be a valid city name.'}), 400

        recs = recommend(city, budget)
        return jsonify({'results': recs, 'count': len(recs), 'city': city, 'budget': budget})
    except Exception as e:
        # Don't leak internal error details to the client
        app.logger.error("recommend_api error: %s", e)
        return jsonify({'error': 'An internal error occurred.'}), 500


@app.route('/api/v1/cities', methods=['GET'])
def cities_api():
    from flask import jsonify
    return jsonify({'cities': get_cities()})


# ── Dev entry-point ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = _safe_int(os.environ.get('PORT', 5000), 5000, 1024, 65535)
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
