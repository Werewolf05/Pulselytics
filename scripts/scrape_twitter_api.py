"""
Twitter API v2 scraper (paid tiers required for production use)
Docs: https://developer.twitter.com/en/docs/twitter-api

Requirements: Bearer token with access to /2/users/by/username and /2/users/:id/tweets
Environment: TWITTER_BEARER_TOKEN (or pass --bearer)
"""
import os
import argparse
from typing import List, Dict

import requests
import pandas as pd

from common import save_csv


API_BASE = "https://api.twitter.com/2"


def _bearer() -> str:
    return (
        os.getenv("TWITTER_BEARER_TOKEN")
        or os.getenv("TWITTER_API_BEARER")
        or ""
    )


essential_tweet_fields = [
    "id",
    "text",
    "created_at",
    "public_metrics",
]


def _headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_user(username: str, token: str) -> Dict:
    url = f"{API_BASE}/users/by/username/{username}"
    params = {"user.fields": "name,username,verified,public_metrics"}
    r = requests.get(url, headers=_headers(token), params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data")


def get_user_tweets(user_id: str, token: str, max_posts: int = 50) -> List[Dict]:
    # Use expansions to pull media previews when available
    url = f"{API_BASE}/users/{user_id}/tweets"
    params = {
        "max_results": min(100, max_posts),
        "exclude": "retweets,replies",
        "tweet.fields": ",".join(["created_at","public_metrics"]),
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url,type",
    }
    r = requests.get(url, headers=_headers(token), params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    tweets = data.get("data", [])

    media_index = {}
    includes = data.get("includes", {})
    for m in includes.get("media", []) or []:
        media_index[m.get("media_key")] = m

    # Map tweets -> a representative media URL if present
    for tw in tweets:
        m_keys = (tw.get("attachments") or {}).get("media_keys") or []
        media_url = None
        for k in m_keys:
            m = media_index.get(k)
            if not m:
                continue
            media_url = m.get("url") or m.get("preview_image_url")
            if media_url:
                break
        tw["_media_url"] = media_url

    return tweets[:max_posts]


def to_rows(username: str, tweets: List[Dict]) -> List[Dict]:
    rows: List[Dict] = []
    for t in tweets:
        pm = t.get("public_metrics") or {}
        likes = pm.get("like_count")
        comments = pm.get("reply_count")
        # Impression counts are not available via public_metrics in most tiers
        views = None
        rows.append({
            "platform": "twitter",
            "username": username,
            "post_url": f"https://x.com/{username}/status/{t.get('id')}",
            "caption": t.get("text", ""),
            "media_url": t.get("_media_url"),
            "likes": likes,
            "comments": comments,
            "views": views,
            "upload_date": t.get("created_at"),
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="Scrape Twitter using official API v2 (Bearer)")
    ap.add_argument("--username", required=True, help="Twitter handle without @")
    ap.add_argument("--max-posts", type=int, default=50)
    ap.add_argument("--bearer", help="Twitter API v2 Bearer token (or set TWITTER_BEARER_TOKEN)")
    args = ap.parse_args()

    token = args.bearer or _bearer()
    if not token:
        print("ERROR: Missing Bearer token. Set TWITTER_BEARER_TOKEN or pass --bearer")
        df = pd.DataFrame([
            {
                "platform": "twitter",
                "username": args.username,
                "post_url": f"https://x.com/{args.username}",
                "caption": "No data - missing Twitter API bearer token",
                "media_url": None,
                "likes": 0,
                "comments": 0,
                "views": 0,
                "upload_date": pd.Timestamp.utcnow().isoformat(),
            }
        ])
        path = save_csv(df, "twitter_data.csv")
        print(f"Saved: {path}")
        return

    try:
        user = get_user(args.username, token)
        if not user:
            print("Could not resolve user by username")
            return
        tweets = get_user_tweets(user["id"], token, args.max_posts)
        rows = to_rows(user.get("username") or args.username, tweets)
        df = pd.DataFrame(rows)
        path = save_csv(df, "twitter_data.csv")
        print(f"Saved: {path}")
    except requests.HTTPError as e:
        print(f"Twitter API error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
