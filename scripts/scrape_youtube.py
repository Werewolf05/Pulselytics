import argparse
from typing import List, Dict

import pandas as pd
from yt_dlp import YoutubeDL

from common import save_csv


def _extract_channel_videos(channel: str, max_videos: int = 30) -> List[Dict]:
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',  # Faster extraction
        'playlistend': max_videos,
        'noplaylist': False,
        'ignoreerrors': True,  # Skip errors
        'no_warnings': True,
    }
    url = channel
    if not (channel.startswith('http://') or channel.startswith('https://')):
        url = f'https://www.youtube.com/@{channel}/videos'

    results: List[Dict] = []
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries') if info else None
            if entries is None:
                entries = [info]
            
            for v in entries:
                if not v:
                    continue
                try:
                    # For flat extraction, we need to get full info
                    if v.get('_type') == 'url':
                        video_url = v.get('url') or f"https://www.youtube.com/watch?v={v.get('id')}"
                        video_info = ydl.extract_info(video_url, download=False)
                        v = video_info if video_info else v
                    
                    results.append({
                        'platform': 'youtube',
                        'username': v.get('channel') or v.get('uploader') or channel,
                        'post_url': v.get('webpage_url') or f"https://www.youtube.com/watch?v={v.get('id')}",
                        'caption': v.get('title'),
                        'media_url': (v.get('thumbnail') or (v.get('thumbnails') or [{}])[-1].get('url')),
                        'likes': v.get('like_count'),
                        'comments': v.get('comment_count'),
                        'views': v.get('view_count'),
                        'upload_date': str(v.get('upload_date')) if v.get('upload_date') else None,
                    })
                    
                    if len(results) >= max_videos:
                        break
                except Exception as e:
                    print(f"Skipping video: {e}")
                    continue
    except Exception as e:
        print(f"Channel extraction error: {e}")
    
    return results


def fetch_youtube_data(channel: str, max_videos: int = 30) -> pd.DataFrame:
    items = _extract_channel_videos(channel, max_videos)
    return pd.DataFrame(items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--channel', required=True)
    ap.add_argument('--max-videos', type=int, default=30)
    args = ap.parse_args()

    df = fetch_youtube_data(args.channel, args.max_videos)
    path = save_csv(df, 'youtube_data.csv')
    print('Saved:', path)


if __name__ == '__main__':
    main()
