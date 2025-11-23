import argparse
import re
import time
import random
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd

from common import save_csv

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def _parse_public_posts(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    posts = []
    
    # Try multiple selectors for different FB mobile layouts
    for art in soup.select('article, div[data-ft], div.story_body_container, section'):
        text = ' '.join(t.get_text(strip=True) for t in art.select('p, span, div'))
        if not text or len(text) < 10:
            continue
            
        img = art.find('img')
        media_url = img.get('src') if img and img.has_attr('src') else None
        
        date_el = art.find('abbr') or art.find('span', string=re.compile(r'\d{4}|\d+ hr|\d+ min|Just now'))
        date_text = date_el.get_text(strip=True) if date_el else None
        
        like_count = None
        comments = None
        full_text = art.get_text(' ', strip=True)
        
        m = re.search(r'(\d+[,.]?\d*)\s+(?:like|reaction)', full_text, re.I)
        if m:
            try:
                like_count = int(m.group(1).replace(',', '').replace('.', ''))
            except Exception:
                pass
                
        m2 = re.search(r'(\d+[,.]?\d*)\s+comment', full_text, re.I)
        if m2:
            try:
                comments = int(m2.group(1).replace(',', '').replace('.', ''))
            except Exception:
                pass
                
        posts.append({
            'caption': text[:500],  # truncate long captions
            'media_url': media_url,
            'upload_date': date_text,
            'likes': like_count,
            'comments': comments,
        })
    return posts


def fetch_facebook_data(page: str, max_posts: int = 20) -> pd.DataFrame:
    """
    Fetch Facebook posts with retry logic and multiple URL strategies.
    Best-effort scraping; Facebook may require cookies/login for full data.
    """
    urls_to_try = [
        f'https://m.facebook.com/{page}',
        f'https://www.facebook.com/{page}',
        f'https://mbasic.facebook.com/{page}',
    ]
    
    for url in urls_to_try:
        try:
            print(f"Trying {url}...")
            time.sleep(random.uniform(1, 3))  # polite delay
            r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
            r.raise_for_status()
            
            items = _parse_public_posts(r.text)
            if items:
                print(f"Found {len(items)} posts from {url}")
                items = items[:max_posts]
                break
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
            items = []
    
    if not items:
        print("No posts found from any Facebook URL.")
        return pd.DataFrame()

    rows = []
    for it in items:
        rows.append({
            'platform': 'facebook',
            'username': page,
            'post_url': f'https://facebook.com/{page}',
            'caption': it.get('caption'),
            'media_url': it.get('media_url'),
            'likes': it.get('likes'),
            'comments': it.get('comments'),
            'views': None,
            'upload_date': it.get('upload_date'),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--page', required=True)
    ap.add_argument('--max-posts', type=int, default=20)
    args = ap.parse_args()

    df = fetch_facebook_data(args.page, args.max_posts)
    path = save_csv(df, 'facebook_data.csv')
    print('Saved:', path)


if __name__ == '__main__':
    main()
