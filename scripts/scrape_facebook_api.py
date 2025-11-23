"""
Facebook Graph API scraper (FREE with rate limits)
Get your access token from: https://developers.facebook.com/
"""
import os
import argparse
from typing import List, Dict
from datetime import datetime

import pandas as pd
import requests

from common import save_csv


def get_facebook_access_token():
    """Get Facebook access token from environment"""
    return os.getenv('FACEBOOK_ACCESS_TOKEN', '')


def fetch_facebook_page_posts(page_id: str, max_posts: int = 20, access_token: str = None) -> pd.DataFrame:
    """
    Fetch Facebook page posts using FREE Facebook Graph API.
    
    Args:
        page_id: Facebook page username or ID
        max_posts: Maximum number of posts to fetch
        access_token: Facebook access token
    
    Returns:
        DataFrame with post data
    """
    if not access_token:
        access_token = get_facebook_access_token()
    
    if not access_token:
        print("ERROR: Facebook access token not found!")
        print("Set FACEBOOK_ACCESS_TOKEN environment variable or pass --access-token")
        print("Get free token: https://developers.facebook.com/tools/explorer/")
        return pd.DataFrame()
    
    try:
        # Get page posts with engagement metrics
        url = f'https://graph.facebook.com/v19.0/{page_id}/posts'
        params = {
            'fields': 'id,message,created_time,full_picture,permalink_url,reactions.type(LIKE).limit(0).summary(total_count),comments.limit(0).summary(total_count),shares',
            'limit': max_posts,
            'access_token': access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Facebook API error: {response.status_code}")
            print(response.text)
            return pd.DataFrame()
        
        data = response.json()
        
        if 'data' not in data:
            print("No posts found")
            return pd.DataFrame()
        
        posts = []
        for item in data['data']:
            try:
                # Parse created time
                created_time = item.get('created_time', '')
                if created_time:
                    created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                
                posts.append({
                    'platform': 'facebook',
                    'username': page_id,
                    'post_url': item.get('permalink_url', ''),
                    'caption': item.get('message', ''),
                    'media_url': item.get('full_picture', ''),
                    'likes': item.get('reactions', {}).get('summary', {}).get('total_count', 0),
                    'comments': item.get('comments', {}).get('summary', {}).get('total_count', 0),
                    'views': item.get('shares', {}).get('count', 0),  # Using shares as views
                    'upload_date': created_time.isoformat() if created_time else None,
                })
            except Exception as e:
                print(f"Error parsing post: {e}")
                continue
        
        print(f"Successfully fetched {len(posts)} posts from {page_id}")
        return pd.DataFrame(posts)
        
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


def main():
    ap = argparse.ArgumentParser(description='Scrape Facebook using FREE Graph API')
    ap.add_argument('--page', required=True, help='Facebook page username or ID')
    ap.add_argument('--max-posts', type=int, default=20, help='Maximum number of posts')
    ap.add_argument('--access-token', help='Facebook access token (or set FACEBOOK_ACCESS_TOKEN env var)')
    args = ap.parse_args()

    df = fetch_facebook_page_posts(args.page, args.max_posts, args.access_token)
    
    if df.empty:
        print("No data fetched. Check access token and page ID.")
        # Create placeholder
        df = pd.DataFrame([{
            'platform': 'facebook',
            'username': args.page,
            'post_url': f'https://facebook.com/{args.page}',
            'caption': 'No data - check access token',
            'media_url': None,
            'likes': 0,
            'comments': 0,
            'views': 0,
            'upload_date': datetime.utcnow().isoformat(),
        }])
    
    path = save_csv(df, 'facebook_data.csv')
    print(f'Saved: {path}')


if __name__ == '__main__':
    main()
