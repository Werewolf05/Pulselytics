import argparse
import subprocess
import json
from typing import List
from pathlib import Path

import pandas as pd

from common import save_csv

try:
    import snscrape.modules.twitter as sntwitter
except Exception as e:
    sntwitter = None


def fetch_twitter_data_cli(username: str, max_posts: int = 50) -> pd.DataFrame:
    """
    Fallback: use snscrape CLI to avoid Python import issues on Windows.
    """
    try:
        query = f'from:{username}'
        # Locate snscrape executable on Windows venv if available
        import sys, os
        exe = 'snscrape'
        scripts_dir = os.path.join(sys.prefix, 'Scripts')
        candidate = os.path.join(scripts_dir, 'snscrape.exe')
        if os.name == 'nt' and os.path.exists(candidate):
            exe = candidate
        cmd = [exe, '--jsonl', '--max-results', str(max_posts), 'twitter-search', query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"snscrape CLI failed: {result.stderr}")
            return pd.DataFrame()
        
        rows: List[dict] = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                tweet = json.loads(line)
                media_url = None
                if tweet.get('media'):
                    m = tweet['media'][0]
                    media_url = m.get('fullUrl') or m.get('previewUrl')
                    
                rows.append({
                    'platform': 'twitter',
                    'username': username,
                    'post_url': tweet.get('url', f"https://x.com/{username}/status/{tweet.get('id')}"),
                    'caption': tweet.get('content', ''),
                    'media_url': media_url,
                    'likes': tweet.get('likeCount'),
                    'comments': tweet.get('replyCount'),
                    'views': tweet.get('viewCount'),
                    'upload_date': tweet.get('date'),
                })
            except Exception as e:
                print(f"Parse error: {e}")
                continue
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"CLI scraping failed: {e}")
        return pd.DataFrame()


def fetch_twitter_data(username: str, max_posts: int = 50) -> pd.DataFrame:
    """
    Try Python API first, fallback to CLI if import fails.
    """
    if sntwitter is None:
        print("snscrape Python module not available, using CLI fallback...")
        return fetch_twitter_data_cli(username, max_posts)

    try:
        query = f'from:{username}'
        rows: List[dict] = []
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= max_posts:
                break
            media_url = None
            if getattr(tweet, 'media', None):
                m = tweet.media[0]
                media_url = getattr(m, 'fullUrl', None) or getattr(m, 'previewUrl', None)
            rows.append({
                'platform': 'twitter',
                'username': username,
                'post_url': f'https://x.com/{username}/status/{tweet.id}',
                'caption': tweet.content,
                'media_url': media_url,
                'likes': tweet.likeCount,
                'comments': tweet.replyCount,
                'views': getattr(tweet, 'viewCount', None),
                'upload_date': tweet.date.isoformat(),
            })
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Python API failed ({e}), trying CLI fallback...")
        return fetch_twitter_data_cli(username, max_posts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--username', required=True)
    ap.add_argument('--max-posts', type=int, default=50)
    args = ap.parse_args()

    df = fetch_twitter_data(args.username, args.max_posts)
    # Fallback placeholder if snscrape is unavailable or blocked
    if df is None or df.empty:
        df = pd.DataFrame([
            {
                'platform': 'twitter',
                'username': args.username,
                'post_url': f'https://x.com/{args.username}',
                'caption': 'Sample tweet placeholder (scraper unavailable)',
                'media_url': None,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'upload_date': pd.Timestamp.utcnow().isoformat(),
            }
        ])
    path = save_csv(df, 'twitter_data.csv')
    print('Saved:', path)


if __name__ == '__main__':
    main()
