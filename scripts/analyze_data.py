import os
import re
from typing import Dict, List
from collections import Counter

import pandas as pd
import numpy as np

from common import DATA_DIR

PLATFORMS = ['instagram', 'youtube', 'twitter', 'facebook']

# Try to import sentiment analysis libraries
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("Warning: vaderSentiment not installed. Sentiment analysis disabled.")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: textblob not installed. Advanced text analysis disabled.")


def load_csv(platform: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f'{platform}_data.csv')
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def load_all() -> pd.DataFrame:
    frames = [df for p in PLATFORMS if not (df := load_csv(p)).empty]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def extract_hashtags(text: str) -> list:
    """Extract hashtags from text"""
    if not isinstance(text, str):
        return []
    return re.findall(r'#\w+', text, re.UNICODE)


def extract_mentions(text: str) -> list:
    """Extract @mentions from text"""
    if not isinstance(text, str):
        return []
    return re.findall(r'@\w+', text)


def detect_content_type(row: pd.Series) -> str:
    """Detect if post is photo, video, or text-only"""
    media_url = str(row.get('media_url', ''))
    caption = str(row.get('caption', ''))
    platform = str(row.get('platform', '')).lower()
    
    if pd.isna(media_url) or media_url == 'nan' or not media_url:
        return 'text'
    
    # YouTube is always video
    if platform == 'youtube':
        return 'video'
    
    # Check URL patterns
    if any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi', 'video']):
        return 'video'
    elif any(ext in media_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', 'photo', 'image']):
        return 'photo'
    
    # Default to photo if has media
    return 'photo' if media_url else 'text'


def compute_engagement_rate(row: pd.Series, follower_estimate: int = 10000) -> float:
    """
    Compute engagement rate as (likes + comments) / followers * 100
    Since we don't have follower count, use an estimate or return raw engagement
    """
    likes = row.get('likes', 0) or 0
    comments = row.get('comments', 0) or 0
    views = row.get('views', 0) or 0
    
    # For posts with views (YouTube, Twitter), use views as denominator
    if views and views > 0:
        return ((likes + comments) / views) * 100
    
    # Otherwise use follower estimate
    return ((likes + comments) / follower_estimate) * 100


def analyze_sentiment(text: str) -> Dict:
    """Analyze sentiment of text using VADER"""
    if not VADER_AVAILABLE or not isinstance(text, str) or not text:
        return {'sentiment': 'neutral', 'score': 0.0}
    
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        sentiment = 'positive'
    elif compound <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'sentiment': sentiment,
        'score': compound,
        'pos': scores['pos'],
        'neg': scores['neg'],
        'neu': scores['neu']
    }


def compute_summary(df: pd.DataFrame) -> Dict:
    """Compute comprehensive summary statistics"""
    if df.empty:
        return {
            'total_posts': 0,
            'avg_likes': 0.0,
            'avg_comments': 0.0,
            'avg_views': 0.0,
            'total_engagement': 0.0,
            'avg_engagement_rate': 0.0,
        }
    
    # Ensure numeric columns
    for c in ['likes', 'comments', 'views']:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    
    # Calculate total engagement
    total_engagement = df['likes'].sum() + df['comments'].sum()
    
    return {
        'total_posts': int(len(df)),
        'avg_likes': float(df['likes'].mean()),
        'avg_comments': float(df['comments'].mean()),
        'avg_views': float(df['views'].mean()),
        'total_engagement': float(total_engagement),
        'avg_engagement_rate': float(
            ((df['likes'] + df['comments']) / (df['views'].replace(0, np.nan))).mean() * 100
        ) if 'views' in df and df['views'].sum() > 0 else 0.0,
    }


def get_hashtag_stats(df: pd.DataFrame, top_n: int = 20) -> List[Dict]:
    """Extract and count hashtags across all posts"""
    if df.empty or 'caption' not in df.columns:
        return []
    
    all_hashtags = []
    for caption in df['caption'].dropna():
        all_hashtags.extend(extract_hashtags(caption))
    
    counts = Counter(all_hashtags)
    return [
        {'hashtag': tag, 'count': count}
        for tag, count in counts.most_common(top_n)
    ]


def get_content_type_distribution(df: pd.DataFrame) -> Dict:
    """Get distribution of content types (photo, video, text)"""
    if df.empty:
        return {}
    
    df['content_type'] = df.apply(detect_content_type, axis=1)
    dist = df['content_type'].value_counts().to_dict()
    
    return dist


def get_sentiment_distribution(df: pd.DataFrame) -> Dict:
    """Get sentiment distribution across posts"""
    if df.empty or 'caption' not in df.columns or not VADER_AVAILABLE:
        return {'positive': 0, 'neutral': 0, 'negative': 0}
    
    sentiments = []
    for caption in df['caption'].dropna():
        result = analyze_sentiment(caption)
        sentiments.append(result['sentiment'])
    
    dist = Counter(sentiments)
    return {
        'positive': dist.get('positive', 0),
        'neutral': dist.get('neutral', 0),
        'negative': dist.get('negative', 0)
    }


def get_posting_frequency(df: pd.DataFrame) -> Dict:
    """Analyze posting frequency by day of week and hour"""
    if df.empty or 'upload_date' not in df.columns:
        return {}
    
    df = df.copy()
    df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')
    df = df.dropna(subset=['upload_date'])
    
    if df.empty:
        return {}
    
    df['day_of_week'] = df['upload_date'].dt.day_name()
    df['hour'] = df['upload_date'].dt.hour
    
    day_counts = df['day_of_week'].value_counts().to_dict()
    hour_counts = df['hour'].value_counts().to_dict()
    
    return {
        'by_day': day_counts,
        'by_hour': hour_counts,
        'total_days': (df['upload_date'].max() - df['upload_date'].min()).days,
        'posts_per_week': len(df) / max((df['upload_date'].max() - df['upload_date'].min()).days / 7, 1)
    }


def save_analytics_summary(df: pd.DataFrame) -> str:
    """Save comprehensive analytics summary"""
    out = compute_summary(df)
    out_df = pd.DataFrame([out])
    path = os.path.join(DATA_DIR, 'analytics_summary.csv')
    out_df.to_csv(path, index=False)
    return path


def generate_full_report(df: pd.DataFrame) -> Dict:
    """Generate comprehensive analytics report"""
    return {
        'summary': compute_summary(df),
        'hashtags': get_hashtag_stats(df),
        'content_types': get_content_type_distribution(df),
        'sentiment': get_sentiment_distribution(df),
        'posting_frequency': get_posting_frequency(df),
        'platforms': df['platform'].value_counts().to_dict() if 'platform' in df.columns else {}
    }


if __name__ == '__main__':
    df = load_all()
    print('Rows:', len(df))
    print('\n=== Summary ===')
    summary = compute_summary(df)
    for key, val in summary.items():
        print(f'{key}: {val}')
    
    print('\n=== Top Hashtags ===')
    hashtags = get_hashtag_stats(df, 10)
    for ht in hashtags[:10]:
        print(f"{ht['hashtag']}: {ht['count']}")
    
    print('\n=== Content Types ===')
    content = get_content_type_distribution(df)
    for ctype, count in content.items():
        print(f'{ctype}: {count}')
    
    print('\n=== Sentiment ===')
    sentiment = get_sentiment_distribution(df)
    for sent, count in sentiment.items():
        print(f'{sent}: {count}')
    
    print('\nSaved summary to:', save_analytics_summary(df))
