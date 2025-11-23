# Free API Setup Guide

## ✅ YouTube Data API (100% FREE - 10,000 requests/day)

### Get Your Free API Key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Click "Enable APIs and Services"
4. Search for "YouTube Data API v3"
5. Click "Enable"
6. Go to "Credentials" → "Create Credentials" → "API Key"
7. Copy your API key

### Set Environment Variable:

**Windows PowerShell:**
```powershell
$env:YOUTUBE_API_KEY="your_api_key_here"
```

**Or add to `.env` file:**
```
YOUTUBE_API_KEY=your_api_key_here
```

### Usage:
```powershell
python scrape_youtube_api.py --channel "NASA" --max-videos 20
# Or with API key directly:
python scrape_youtube_api.py --channel "NASA" --max-videos 20 --api-key "your_key"
```

---

## ✅ Facebook Graph API (FREE with rate limits)

### Get Your Free Access Token:

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app (or use existing)
3. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
4. Select your app
5. Click "Generate Access Token"
6. Grant permissions: `pages_read_engagement`, `pages_show_list`
7. Copy the access token

### Set Environment Variable:

```powershell
$env:FACEBOOK_ACCESS_TOKEN="your_access_token_here"
```

### Usage:
```powershell
python scrape_facebook_api.py --page "facebook" --max-posts 20
```

---

## ⚠️ Instagram Graph API (FREE but LIMITED)

**Important:** Instagram Graph API only works for:
- Instagram Business or Creator accounts
- Accounts YOU OWN (connected to your Facebook Page)
- Cannot scrape other people's accounts

### Setup:

1. Convert your Instagram account to Business/Creator
2. Connect it to a Facebook Page
3. Go to [Facebook Developers](https://developers.facebook.com/)
4. Create app → Add Instagram Graph API
5. Get access token with permissions: `instagram_basic`, `pages_read_engagement`

### Set Environment Variable:

```powershell
$env:INSTAGRAM_ACCESS_TOKEN="your_access_token_here"
```

### Usage:
```powershell
python scrape_instagram_api.py --max-posts 20
```

---

## 🚀 Quick Test (No API Keys Required)

The existing scrapers will still work for **YouTube** using yt-dlp (slower but no API key needed):

```powershell
# Works without API key (but slower and may hit rate limits)
python scrape_youtube.py --channel "NASA" --max-videos 10
```

---

## 📊 Recommended Approach for 2-Day Demo

### For REAL, RELIABLE Data:

1. **YouTube**: Use official API (best option, 100% free)
   - Get API key (5 minutes)
   - 10,000 requests/day = plenty for demo
   - Fast, reliable, no rate limits

2. **Facebook**: Use Graph API if you have a page
   - Works for public pages
   - Free tier sufficient

3. **Instagram**: Skip or use your own business account
   - Cannot scrape others' accounts with free API
   - Stick with YouTube for demo

### Best Setup for Demo:

```powershell
# 1. Get YouTube API key (5 min setup)
# 2. Set environment variable:
$env:YOUTUBE_API_KEY="your_key"

# 3. Scrape real data:
python scrape_youtube_api.py --channel "NASA" --max-videos 20
python scrape_youtube_api.py --channel "RCBVideos" --max-videos 20

# 4. Refresh dashboard - REAL data will show!
```

---

## 💡 Summary

| Platform | Free API | Setup Time | Data Quality | Recommendation |
|----------|----------|------------|--------------|----------------|
| **YouTube** | ✅ Yes | 5 min | ⭐⭐⭐⭐⭐ | **USE THIS** |
| **Facebook** | ✅ Yes | 10 min | ⭐⭐⭐⭐ | Optional |
| **Instagram** | ⚠️ Limited | 15 min | ⭐⭐ (own account only) | Skip for demo |
| **Twitter** | ❌ No | N/A | N/A | No free option |

**For a 2-day demo**: Just set up YouTube API key and use that. It's the easiest, most reliable, and 100% free!
