# Instagram Graph API Setup Guide 📸

## Prerequisites
✅ Instagram Business or Creator account (not personal)
✅ Facebook Page connected to your Instagram
✅ Facebook Developer account

---

## Step-by-Step Setup

### 1. Convert Instagram to Business Account (If Not Already)

1. Open Instagram mobile app
2. Go to **Settings** → **Account**
3. Tap **Switch to Professional Account**
4. Choose **Business** or **Creator**
5. Connect to a Facebook Page (create new page if needed)

---

### 2. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/apps/)
2. Click **Create App**
3. Choose **Business** as use case
4. Enter app name: "Pulselytics" (or any name)
5. Click **Create App**

---

### 3. Add Instagram Graph API

1. In your app dashboard, click **Add Product**
2. Find **Instagram Graph API** and click **Set Up**
3. Follow the prompts

---

### 4. Get Access Token

**Method 1: Graph API Explorer (Quick Test)**

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from dropdown
3. Click **Generate Access Token**
4. Grant permissions:
   - `instagram_basic`
   - `pages_read_engagement`
   - `pages_show_list`
5. Copy the **Access Token** (starts with EAA...)

**Important:** This token expires in 1-2 hours. For long-term use, see Method 2.

**Method 2: Long-Lived Token (Recommended for Production)**

After getting short-lived token from Graph Explorer:

```powershell
# Replace with your values
$APP_ID = "your_app_id"
$APP_SECRET = "your_app_secret"
$SHORT_TOKEN = "your_short_lived_token"

# Exchange for long-lived token (60 days)
$url = "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=$APP_ID&client_secret=$APP_SECRET&fb_exchange_token=$SHORT_TOKEN"

Invoke-WebRequest -Uri $url
```

---

### 5. Get Your Instagram Business Account ID

```powershell
# Replace YOUR_ACCESS_TOKEN with token from step 4
$TOKEN = "YOUR_ACCESS_TOKEN"

# Get your Facebook Pages
Invoke-WebRequest -Uri "https://graph.facebook.com/v18.0/me/accounts?access_token=$TOKEN"

# Get Instagram Business Account ID from your page
# Replace PAGE_ID with ID from previous response
Invoke-WebRequest -Uri "https://graph.facebook.com/v18.0/PAGE_ID?fields=instagram_business_account&access_token=$TOKEN"
```

Save the **Instagram Business Account ID** (will be a number like `17841401234567890`)

---

### 6. Save to Pulselytics

1. Go to http://localhost:5173/api-keys
2. Paste your **Access Token** in the Instagram field
3. Click **Save**

---

### 7. Test Your Setup

```powershell
cd c:\pulselytics

# Test with API
.\venv\Scripts\python scrape_instagram_api.py --max-posts 10
```

Check `data/instagram_data.csv` for your posts!

---

## 🎯 What You Can Get

With Instagram Graph API, you can retrieve:

- ✅ Your posts (photos, videos, carousels)
- ✅ Likes, comments count
- ✅ Reach, impressions
- ✅ Saves, shares (if available)
- ✅ Hashtag performance
- ✅ Story metrics (if enabled)
- ✅ Follower demographics

---

## ⚠️ Limitations

❌ **Cannot access:**
- Other people's accounts (competitors, influencers)
- Personal (non-business) Instagram accounts
- DMs or private content
- Detailed follower lists

For analyzing competitors, use web scraping: `scrape_instagram.py`

---

## 🔄 Alternative: Web Scraping for Any Public Profile

If you want to analyze accounts you don't own:

```powershell
# Scrape any public profile (use sparingly!)
.\venv\Scripts\python scrape_instagram.py --username "nike" --max-posts 10
```

**Pros:** Works for any public account
**Cons:** Rate limits, may get blocked, less reliable

---

## 📊 Recommended Approach

**For Demo:**
1. Use **YouTube API** for main demo (most reliable)
2. Use **Instagram web scraping** for competitor analysis
3. Use **Instagram Graph API** only if you have your own business account to showcase

**For Production (Client Work):**
1. Get client's Instagram Business credentials
2. Use Graph API for official, accurate metrics
3. Avoid web scraping (against Instagram ToS)

---

## 🆘 Troubleshooting

**"Invalid OAuth access token"**
- Token expired, get new one
- Wrong permissions, regenerate with correct scopes

**"Unsupported get request"**
- Not a business account
- Account not properly connected to Facebook Page

**"Rate limit exceeded"**
- Wait 1 hour
- Use smaller max-posts value

**"Permission denied"**
- Grant all required permissions when generating token
- Check if Instagram is connected to Facebook Page

---

## 💡 Quick Decision Tree

**Do you own the Instagram business account?**
- ✅ YES → Use Graph API (this guide)
- ❌ NO → Use web scraping (`scrape_instagram.py`)

**Is this for a client?**
- ✅ YES → Ask for their Graph API access
- ❌ NO → Use YouTube instead (easier for demo)

**Is this just for demo purposes?**
- ✅ YES → Stick with YouTube API (simplest, most reliable)
- ❌ NO → Set up proper Graph API for production

---

Ready to set up? Start at Step 1 above! 🚀
