"""Basic ML integration tests for Pulselytics backend.

These tests use synthetic data to validate that training, prediction, and anomaly
endpoints behave without raising exceptions and return expected keys.

They are intentionally lightweight and deterministic.
Run: pytest -q (after installing pytest) or python test_ml_models.py
"""
from __future__ import annotations

import json
from typing import List, Dict
from datetime import datetime, timedelta
import random

import pandas as pd

# Import ML training/prediction functions directly
from ml_models import (
    train_predictor,
    train_detector,
    predict_engagement,
    find_anomalies,
    analyze_trends,
    check_engagement_drop,
)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)


def _synthetic_posts(n: int = 120) -> pd.DataFrame:
    """Generate a synthetic dataframe resembling scraped social media posts."""
    rows: List[Dict] = []
    base_date = datetime.utcnow() - timedelta(days=n)
    platforms = ["instagram", "youtube", "twitter", "facebook"]

    for i in range(n):
        d = base_date + timedelta(days=i)
        platform = random.choice(platforms)
        likes = int(abs(random.gauss(5000 if platform == 'instagram' else 3000, 800)))
        comments = int(abs(random.gauss(150 if platform == 'instagram' else 90, 30)))
        views = int(abs(random.gauss(25000 if platform == 'instagram' else 60000, 5000)))
        caption = f"Post {i} amazing launch #tag{i} @brand{i%5}!" if i % 7 != 0 else f"Low key update {i}"  # vary richness
        rows.append({
            'platform': platform,
            'likes': likes,
            'comments': comments,
            'views': views,
            'caption': caption,
            'upload_date': d.isoformat(),
            'post_url': f"https://example.com/post/{i}",
            'username': 'synthetic_account'
        })
    return pd.DataFrame(rows)


def test_training_predictor():
    df = _synthetic_posts(140)
    result = train_predictor(df)
    assert result.get('status') == 'success', f"Predictor training failed: {result}" 
    # Expect validation metrics presence
    assert 'val_r2_likes' in result and 'val_r2_comments' in result
    assert 'quantiles' in result and isinstance(result['quantiles'], dict)


def test_predict_engagement():
    # Ensure predictor trained first
    df = _synthetic_posts(140)
    train_predictor(df)
    payload = {
        'caption': 'New limited edition sneakers drop! #launch @brand',
        'platform': 'instagram'
    }
    pred = predict_engagement(payload)
    for key in ['predicted_likes','predicted_comments','predicted_views','virality_score','confidence']:
        assert key in pred, f"Missing key in prediction result: {key}" 
    assert pred['predicted_likes'] >= 0 and pred['predicted_comments'] >= 0


def test_anomaly_detector():
    df = _synthetic_posts(120)
    result = train_detector(df)
    assert result.get('status') == 'success', f"Anomaly detector training failed: {result}" 
    anomalies = find_anomalies(df)
    assert isinstance(anomalies, list)
    if anomalies:  # If any anomalies, validate structure of first
        first = anomalies[0]
        for key in ['platform','date','type','severity','metric_values','deviation','alert_message']:
            assert key in first, f"Missing anomaly field: {key}" 


def test_trend_and_drop_analysis():
    df = _synthetic_posts(90)
    # Trend analysis (works regardless of detector training)
    trends = analyze_trends(df)
    for key in ['overall_trend','likes_change_percent','comments_change_percent','alert','recommendation']:
        assert key in trends
    drop_info = check_engagement_drop(df)
    for key in ['drop_detected','change_percent','recent_avg_engagement','previous_avg_engagement','severity','alert_message']:
        assert key in drop_info


if __name__ == '__main__':
    # Simple manual run output
    df = _synthetic_posts(140)
    print('Training predictor...')
    print(train_predictor(df))
    print('Predicting engagement...')
    print(predict_engagement({'caption': 'Sneakers drop!', 'platform': 'instagram'}))
    print('Training anomaly detector...')
    print(train_detector(df))
    print('Finding anomalies...')
    print(find_anomalies(df)[:2])
    print('Trend analysis...')
    print(analyze_trends(df))
    print('Engagement drop check...')
    print(check_engagement_drop(df))
    print('All manual checks completed.')
