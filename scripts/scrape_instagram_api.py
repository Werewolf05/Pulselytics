"""
Instagram Graph API scraper (FREE but limited to business accounts you own)
Get your access token from: https://developers.facebook.com/
"""
import os
import argparse
from typing import List, Dict
from datetime import datetime

import pandas as pd
import requests

from common import save_csv


def get_instagram_access_token():
    """Get Instagram access token from environment"""
    return os.getenv('INSTAGRAM_ACCESS_TOKEN', '')


def fetch_instagram_posts_api(access_token: str = None, max_posts: int = 20) -> pd.DataFrame:
    """
    Fetch Instagram posts using FREE Instagram Graph API.
    Note: Only works for Instagram Business accounts you own.
    
    Args:
        access_token: Instagram/Facebook access token
        max_posts: Maximum number of posts to fetch
    
    Returns:
        DataFrame with post data
    """
    if not access_token:
        access_token = get_instagram_access_token()
    
    if not access_token:
        print("ERROR: Instagram access token not found!")
        print("Set INSTAGRAM_ACCESS_TOKEN environment variable or pass --access-token")
        print("Get token: https://developers.facebook.com/docs/instagram-basic-display-api/")
        return pd.DataFrame()
    
    try:
        # First, get Instagram Business Account ID
        me_url = f'https://graph.facebook.com/v19.0/me/accounts'
        me_params = {'access_token': access_token}
        
        me_response = requests.get(me_url, params=me_params)
        
        if me_response.status_code != 200:
            print(f"Instagram API error: {me_response.status_code}")
            print(me_response.text)
            return pd.DataFrame()
        
        me_data = me_response.json()
        
        if not me_data.get('data'):
            print("No Instagram business account found. Make sure:")
            print("1. You have a Facebook Page")
            print("2. The page is connected to an Instagram Business account")
            print("3. Your access token has the right permissions")
            return pd.DataFrame()
        
        # Get Instagram account from first page
        page_id = me_data['data'][0]['id']
        page_token = me_data['data'][0]['access_token']
        
        # Get Instagram Business Account
        ig_url = f'https://graph.facebook.com/v19.0/{page_id}'
        ig_params = {
            'fields': 'instagram_business_account',
            'access_token': page_token
        }
        
        ig_response = requests.get(ig_url, params=ig_params)
        
        if ig_response.status_code != 200:
            print("No Instagram account linked to this Facebook page")
            return pd.DataFrame()
        
        ig_data = ig_response.json()
        
        if 'instagram_business_account' not in ig_data:
            print("No Instagram business account found")
            return pd.DataFrame()
        
        ig_account_id = ig_data['instagram_business_account']['id']

        # Try to resolve the Instagram username for cleaner CSV rows
        username = 'instagram_business_account'
        try:
            ig_user_url = f'https://graph.facebook.com/v19.0/{ig_account_id}'
            ig_user_params = {
                'fields': 'username',
                'access_token': page_token
            }
            ig_user_resp = requests.get(ig_user_url, params=ig_user_params)
            if ig_user_resp.status_code == 200:
                username = ig_user_resp.json().get('username') or username
        except Exception:
            pass
        
        # Get media posts
        media_url = f'https://graph.facebook.com/v19.0/{ig_account_id}/media'
        media_params = {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count',
            'limit': max_posts,
            'access_token': page_token
        }
        
        media_response = requests.get(media_url, params=media_params)
        
        if media_response.status_code != 200:
            print(f"Error fetching media: {media_response.status_code}")
            print(media_response.text)
            return pd.DataFrame()
        
        media_data = media_response.json()
        
        if 'data' not in media_data:
            print("No posts found")
            return pd.DataFrame()
        
        posts = []
        for item in media_data['data']:
            try:
                # Parse timestamp
                timestamp = item.get('timestamp', '')
                if timestamp:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                # Get media URL (use thumbnail for videos)
                media_url = item.get('media_url', '')
                if item.get('media_type') == 'VIDEO':
                    media_url = item.get('thumbnail_url', media_url)
                
                posts.append({
                    'platform': 'instagram',
                    'username': username,
                    'post_url': item.get('permalink', ''),
                    'caption': item.get('caption', ''),
                    'media_url': media_url,
                    'likes': item.get('like_count', 0),
                    'comments': item.get('comments_count', 0),
                    'views': 0,  # Not available in basic API
                    'upload_date': timestamp.isoformat() if timestamp else None,
                })
            except Exception as e:
                print(f"Error parsing post: {e}")
                continue
        
        print(f"Successfully fetched {len(posts)} Instagram posts")
        return pd.DataFrame(posts)
        
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


def main():
    ap = argparse.ArgumentParser(description='Scrape Instagram using FREE Graph API (Business accounts only)')
    ap.add_argument('--max-posts', type=int, default=20, help='Maximum number of posts')
    ap.add_argument('--access-token', help='Instagram/Facebook access token (or set INSTAGRAM_ACCESS_TOKEN env var)')
    args = ap.parse_args()

    df = fetch_instagram_posts_api(args.access_token, args.max_posts)
    
    if df.empty:
        print("No data fetched. Check access token and Instagram Business account setup.")
        print("\nNote: Instagram Graph API only works for:")
        print("- Instagram Business or Creator accounts")
        print("- Accounts connected to a Facebook Page")
        print("- With proper access token permissions")
        
        # Create placeholder
        df = pd.DataFrame([{
            'platform': 'instagram',
            'username': 'instagram_business_account',
            'post_url': 'https://instagram.com',
            'caption': 'No data - check access token and business account setup',
            'media_url': None,
            'likes': 0,
            'comments': 0,
            'views': 0,
            'upload_date': datetime.utcnow().isoformat(),
        }])
    
    path = save_csv(df, 'instagram_data.csv')
    print(f'Saved: {path}')


if __name__ == '__main__':
    main()
