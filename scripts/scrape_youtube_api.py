"""
YouTube Data API v3 scraper (FREE - 10,000 requests/day)
Get your API key from: https://console.cloud.google.com/
"""
import os
import argparse
from typing import List, Dict
from datetime import datetime

import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from common import save_csv


def get_youtube_api_key():
    """Get YouTube API key from environment or config"""
    return os.getenv('YOUTUBE_API_KEY', '')


def fetch_channel_videos_api(channel_identifier: str, max_videos: int = 20, api_key: str = None) -> pd.DataFrame:
    """
    Fetch YouTube channel videos using official FREE YouTube Data API v3.
    
    Args:
        channel_identifier: Channel ID, username, or handle (@username)
        max_videos: Maximum number of videos to fetch
        api_key: YouTube Data API key (get free from Google Cloud Console)
    
    Returns:
        DataFrame with video data
    """
    if not api_key:
        api_key = get_youtube_api_key()
    
    if not api_key:
        print("ERROR: YouTube API key not found!")
        print("Set YOUTUBE_API_KEY environment variable or pass --api-key")
        print("Get free API key: https://console.cloud.google.com/")
        return pd.DataFrame()
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Step 1: Get channel ID
        channel_id = None
        
        # Try as channel ID first
        if channel_identifier.startswith('UC'):
            channel_id = channel_identifier
        # Try as username
        elif not channel_identifier.startswith('@'):
            try:
                request = youtube.channels().list(
                    part='id',
                    forUsername=channel_identifier
                )
                response = request.execute()
                if response.get('items'):
                    channel_id = response['items'][0]['id']
            except:
                pass
        
        # Try as handle (@username) more robustly by resolving via search then matching custom URL/title
        if not channel_id:
            handle = channel_identifier.lstrip('@')
            try:
                search_req = youtube.search().list(
                    part='snippet',
                    q=handle,
                    type='channel',
                    maxResults=5,
                    order='relevance'
                )
                search_resp = search_req.execute()
                items = search_resp.get('items', [])
                if items:
                    # Collect candidate channel IDs
                    candidate_ids = [it['snippet']['channelId'] for it in items if 'snippet' in it and 'channelId' in it['snippet']]
                    # Fetch channel details to inspect customUrl/title for exact match
                    chan_req = youtube.channels().list(part='snippet', id=','.join(candidate_ids))
                    chan_resp = chan_req.execute()
                    handle_lower = handle.lower()
                    best_id = None
                    for ch in chan_resp.get('items', []):
                        sn = ch.get('snippet', {})
                        title = (sn.get('title') or '').lower()
                        custom = (sn.get('customUrl') or '').lower()
                        # Prefer exact customUrl match to handle (e.g., '@gopro' vs 'gopro')
                        if custom and ('@' + custom) == ('@' + handle_lower):
                            best_id = ch['id']
                            break
                        # Otherwise prefer exact title match
                        if title == handle_lower:
                            best_id = ch['id']
                            # keep searching for a customUrl match, but remember this
                    if not best_id:
                        # Fall back to first candidate
                        best_id = candidate_ids[0]
                    channel_id = best_id
            except Exception:
                pass
        
        if not channel_id:
            print(f"Could not find channel: {channel_identifier}")
            return pd.DataFrame()
        
        # Step 2: Get uploads playlist ID
        request = youtube.channels().list(
            part='contentDetails,snippet',
            id=channel_id
        )
        response = request.execute()
        
        if not response.get('items'):
            print(f"Channel not found: {channel_id}")
            return pd.DataFrame()
        
        channel_title = response['items'][0]['snippet']['title']
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Step 3: Get videos from uploads playlist
        videos = []
        next_page_token = None
        
        while len(videos) < max_videos:
            request = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_videos - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            video_ids = [item['contentDetails']['videoId'] for item in response.get('items', [])]
            
            if not video_ids:
                break
            
            # Step 4: Get video statistics
            stats_request = youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids)
            )
            stats_response = stats_request.execute()
            
            for item in stats_response.get('items', []):
                try:
                    snippet = item['snippet']
                    stats = item['statistics']
                    
                    # Parse upload date
                    upload_date = snippet.get('publishedAt', '')
                    if upload_date:
                        upload_date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    
                    videos.append({
                        'platform': 'youtube',
                        'username': channel_title,
                        'post_url': f"https://www.youtube.com/watch?v={item['id']}",
                        'caption': snippet.get('title', ''),
                        'media_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'likes': int(stats.get('likeCount', 0)),
                        'comments': int(stats.get('commentCount', 0)),
                        'views': int(stats.get('viewCount', 0)),
                        'upload_date': upload_date.isoformat() if upload_date else None,
                    })
                except Exception as e:
                    print(f"Error parsing video: {e}")
                    continue
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(videos) >= max_videos:
                break
        
        print(f"Successfully fetched {len(videos)} videos from {channel_title}")
        return pd.DataFrame(videos[:max_videos])
        
    except HttpError as e:
        print(f"YouTube API error: {e}")
        if 'quotaExceeded' in str(e):
            print("Daily quota exceeded. Try again tomorrow or use a different API key.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


def main():
    ap = argparse.ArgumentParser(description='Scrape YouTube using FREE YouTube Data API v3')
    ap.add_argument('--channel', required=True, help='Channel ID, username, or @handle')
    ap.add_argument('--max-videos', type=int, default=20, help='Maximum number of videos')
    ap.add_argument('--api-key', help='YouTube Data API key (or set YOUTUBE_API_KEY env var)')
    args = ap.parse_args()

    df = fetch_channel_videos_api(args.channel, args.max_videos, args.api_key)
    
    if df.empty:
        print("No data fetched. Check API key and channel identifier.")
        # Create placeholder
        df = pd.DataFrame([{
            'platform': 'youtube',
            'username': args.channel,
            'post_url': f'https://www.youtube.com/@{args.channel}',
            'caption': 'No data - check API key',
            'media_url': None,
            'likes': 0,
            'comments': 0,
            'views': 0,
            'upload_date': datetime.utcnow().isoformat(),
        }])
    
    path = save_csv(df, 'youtube_data.csv')
    print(f'Saved: {path}')


if __name__ == '__main__':
    main()
