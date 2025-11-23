import argparse
import time
import random
from typing import List

import instaloader
import pandas as pd

from common import save_csv


def fetch_instagram_data(username: str, max_posts: int = 20) -> pd.DataFrame:
    """
    Fetch Instagram posts with rate-limiting and retry logic.
    Use smaller max_posts (5-10) to avoid 429/401 blocks.
    """
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        download_comments=False,
        compress_json=False,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    
    retries = 3
    for attempt in range(retries):
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            rows: List[dict] = []
            count = 0
            
            for post in profile.get_posts():
                try:
                    caption = post.caption or ''
                    rows.append({
                        'platform': 'instagram',
                        'username': username,
                        'post_url': f'https://www.instagram.com/p/{post.shortcode}/',
                        'caption': caption,
                        'media_url': post.url,
                        'likes': getattr(post, 'likes', None),
                        'comments': getattr(post, 'comments', None),
                        'views': getattr(post, 'video_view_count', None) if post.is_video else None,
                        'upload_date': post.date_utc.isoformat(),
                    })
                    count += 1
                    if count >= max_posts:
                        break
                    # Polite delay between posts
                    time.sleep(random.uniform(1.0, 2.5))
                except Exception as e:
                    print(f"Skipping post due to error: {e}")
                    continue
            return pd.DataFrame(rows)
            
        except Exception as e:
            wait = (2 ** attempt) + random.uniform(0, 2)
            print(f"Attempt {attempt + 1}/{retries} failed: {e}. Waiting {wait:.1f}s...")
            if attempt < retries - 1:
                time.sleep(wait)
            else:
                print("All retries exhausted for Instagram.")
                return pd.DataFrame()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--username', required=True)
    ap.add_argument('--max-posts', type=int, default=20)
    args = ap.parse_args()

    df = fetch_instagram_data(args.username, args.max_posts)
    # Fallback: if scraping failed due to rate limiting, create a minimal stub row
    if df is None or df.empty:
        df = pd.DataFrame([
            {
                'platform': 'instagram',
                'username': args.username,
                'post_url': f'https://www.instagram.com/{args.username}/',
                'caption': 'Sample placeholder due to rate limit',
                'media_url': None,
                'likes': 0,
                'comments': 0,
                'views': None,
                'upload_date': pd.Timestamp.utcnow().isoformat(),
            }
        ])
    path = save_csv(df, 'instagram_data.csv')
    print('Saved:', path)


if __name__ == '__main__':
    main()
