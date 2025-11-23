"""
Feature engineering utilities for ML models.

Separation from predictor logic allows independent testing and reuse.
"""
from __future__ import annotations

from typing import List
import pandas as pd

BASE_FEATURES: List[str] = [
    # Time-derived
    'hour_of_day', 'day_of_week', 'is_weekend', 'month',
    # Caption meta
    'caption_length', 'word_count', 'hashtag_count', 'mention_count',
    'emoji_count', 'has_question', 'has_exclamation', 'has_url',
    # Placeholder baseline feature
    'avg_engagement_rate'
]

PLATFORM_PREFIX = 'platform_'


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create feature dataframe from raw posts dataframe.

    The function is defensive: missing columns are handled gracefully.
    """
    out = pd.DataFrame()
    if df.empty:
        return out

    # Time features
    if 'upload_date' in df.columns:
        dates = pd.to_datetime(df['upload_date'], errors='coerce')
        out['hour_of_day'] = dates.dt.hour
        out['day_of_week'] = dates.dt.dayofweek
        out['is_weekend'] = out['day_of_week'].isin([5, 6]).astype(int)
        out['month'] = dates.dt.month
    else:
        out[['hour_of_day','day_of_week','is_weekend','month']] = 0

    # Caption-related
    captions = df.get('caption', pd.Series([''] * len(df))).fillna('')
    out['caption_length'] = captions.str.len()
    out['word_count'] = captions.str.split().str.len()
    out['hashtag_count'] = captions.str.count('#')
    out['mention_count'] = captions.str.count('@')
    out['emoji_count'] = captions.apply(lambda x: sum(1 for c in x if 0x1F300 < ord(c) < 0x1F9FF))
    out['has_question'] = captions.str.contains(r'\?', regex=True).astype(int)
    out['has_exclamation'] = captions.str.contains('!', regex=False).astype(int)
    out['has_url'] = captions.str.contains('http', regex=False).astype(int)

    # Platform one-hot
    platform_series = df.get('platform', pd.Series(['unknown'] * len(df))).fillna('unknown')
    dummies = pd.get_dummies(platform_series, prefix='platform')
    out = pd.concat([out, dummies], axis=1)

    # Baseline engagement placeholder (can be replaced with historical aggregate)
    out['avg_engagement_rate'] = 0.05

    return out


def align_feature_columns(current: pd.DataFrame, reference_columns: List[str]) -> pd.DataFrame:
    """Ensure current feature frame has same columns as reference (order + missing fill)."""
    for col in reference_columns:
        if col not in current.columns:
            current[col] = 0
    # Drop extraneous columns silently
    return current[reference_columns]
