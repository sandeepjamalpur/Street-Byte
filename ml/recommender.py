"""
Recommender Engine for StreetByte.
Loads the dataset, computes sentiment scores, and returns ranked recommendations
based on city and budget filters.

Composite Score = 0.40 * rating_norm + 0.40 * sentiment_norm + 0.20 * popularity_norm
"""
import os
import math
import pandas as pd
import numpy as np
from ml.sentiment import analyze_sentiment

# ─── Constants ────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'street_food_data.csv')
RATING_WEIGHT = 0.40
SENTIMENT_WEIGHT = 0.40
POPULARITY_WEIGHT = 0.20

# ─── Singleton dataframe (loaded once at startup) ─────────────────────────────
_df: pd.DataFrame | None = None


def _load_data() -> pd.DataFrame:
    """Load and preprocess the street food dataset."""
    df = pd.read_csv(DATA_PATH)

    # Normalise column names
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    # Clean types
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(3.0)
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(50)
    df['num_reviews'] = pd.to_numeric(df['num_reviews'], errors='coerce').fillna(1)
    df['city'] = df['city'].str.strip().str.title()
    df['food_item'] = df['food_item'].str.strip().str.title()
    df['vendor_name'] = df['vendor_name'].str.strip()
    df['review'] = df['review'].fillna('')

    # ── Sentiment Analysis ────────────────────────────────────────────────────
    sentiments = df['review'].apply(lambda r: analyze_sentiment(r))
    df['sentiment_compound'] = sentiments.apply(lambda s: s['compound'])
    df['sentiment_label'] = sentiments.apply(lambda s: s['label'])
    df['sentiment_css'] = sentiments.apply(lambda s: s['css_class'])

    # ── Normalise Score Components ────────────────────────────────────────────
    # Rating: scale 1–5 → 0–1
    df['rating_norm'] = (df['rating'] - 1) / 4.0

    # Sentiment: scale -1 to +1 → 0–1
    df['sentiment_norm'] = (df['sentiment_compound'] + 1) / 2.0

    # Popularity: log(num_reviews), then min-max normalise
    df['log_reviews'] = df['num_reviews'].apply(lambda x: math.log(x + 1))
    log_min = df['log_reviews'].min()
    log_max = df['log_reviews'].max()
    if log_max > log_min:
        df['popularity_norm'] = (df['log_reviews'] - log_min) / (log_max - log_min)
    else:
        df['popularity_norm'] = 0.5

    # ── Composite Score ───────────────────────────────────────────────────────
    df['score'] = (
        RATING_WEIGHT * df['rating_norm']
        + SENTIMENT_WEIGHT * df['sentiment_norm']
        + POPULARITY_WEIGHT * df['popularity_norm']
    )

    return df


def get_dataframe() -> pd.DataFrame:
    """Return the singleton preprocessed dataframe."""
    global _df
    if _df is None:
        _df = _load_data()
    return _df


def get_cities() -> list[str]:
    """Return sorted list of available cities."""
    df = get_dataframe()
    return sorted(df['city'].unique().tolist())


def recommend(city: str, budget: int, top_n: int = 12) -> list[dict]:
    """
    Return top-N ranked street food entries for a given city and budget.

    Args:
        city: City name (case-insensitive)
        budget: Maximum price in INR
        top_n: Maximum number of results to return

    Returns:
        List of result dicts sorted by composite score (descending)
    """
    df = get_dataframe()

    # Filter by city (case-insensitive) and budget
    city_clean = city.strip().title()
    filtered = df[
        (df['city'] == city_clean) &
        (df['price'] <= budget)
    ].copy()

    if filtered.empty:
        return []

    # Sort by composite score descending
    filtered = filtered.sort_values('score', ascending=False)

    # Remove exact duplicate (same food + same vendor) keeping highest score
    filtered = filtered.drop_duplicates(subset=['food_item', 'vendor_name'])

    # Take top N
    top = filtered.head(top_n)

    results = []
    for _, row in top.iterrows():
        results.append({
            'food_item': row['food_item'],
            'vendor_name': row['vendor_name'],
            'city': row['city'],
            'category': row.get('category', 'snack'),
            'price': int(row['price']),
            'rating': round(float(row['rating']), 1),
            'num_reviews': int(row['num_reviews']),
            'sentiment_label': row['sentiment_label'],
            'sentiment_css': row['sentiment_css'],
            'sentiment_score': round(float(row['sentiment_compound']), 2),
            'composite_score': round(float(row['score']) * 100, 1),
            'review_snippet': _snippet(row['review']),
        })

    return results



def _snippet(review: str, max_len: int = 120) -> str:
    """Return a truncated review snippet."""
    review = str(review).strip()
    if len(review) <= max_len:
        return review
    return review[:max_len].rsplit(' ', 1)[0] + '…'
