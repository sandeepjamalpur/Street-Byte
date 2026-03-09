"""
Sentiment Analysis module using VADER (Valence Aware Dictionary and sEntiment Reasoner).
Returns compound sentiment scores and categorical labels for customer reviews.
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a given review text.

    Returns:
        dict with keys:
            - compound: float in [-1, 1]
            - label: 'Positive' | 'Neutral' | 'Negative'
            - css_class: CSS class string for badge coloring
    """
    if not text or not isinstance(text, str):
        return {"compound": 0.0, "label": "Neutral", "css_class": "badge-neutral"}

    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "Positive"
        css_class = "badge-positive"
    elif compound <= -0.05:
        label = "Negative"
        css_class = "badge-negative"
    else:
        label = "Neutral"
        css_class = "badge-neutral"

    return {"compound": round(compound, 4), "label": label, "css_class": css_class}


def batch_analyze(reviews: list) -> list:
    """Analyze a list of review strings and return list of sentiment dicts."""
    return [analyze_sentiment(r) for r in reviews]
