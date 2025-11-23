# 🚀 START HERE - Pulselytics Quick Guide

Welcome to **Pulselytics**! This is your complete social media analytics platform.

## ✅ Current Status

Your workspace is **organized and ready to use** with sample data already loaded:

- ✅ Backend running on http://127.0.0.1:5000
- ✅ 6 sample clients loaded (MrBeast, Nike, Adidas, Red Bull, GoPro, NASA)
- ✅ Sample data available (70+ posts across 4 platforms)
- ✅ All dependencies installed
- ✅ Files organized into proper folders

## 📂 Organized Structure

```
pulselytics/
├── backend/         - Flask API server
├── frontend/        - React dashboard UI
├── scripts/         - All scraper and utility scripts
├── docs/            - Documentation files
├── data/            - CSV data files from scrapers
└── venv/            - Python virtual environment
```

## 🎯 Quick Actions

### 1. Start the Frontend Dashboard

```powershell
cd c:\pulselytics\frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

You'll immediately see:
- Dashboard with 70+ posts from sample data
- Engagement metrics and charts
- Top performing posts
- Platform distribution

### 2. View Sample Clients

The following clients are pre-loaded with data:
- **MrBeast** - @MrBeast (YouTube, Instagram, Twitter)
- **Nike** - @Nike (All platforms)
- **Adidas** - @Adidas (All platforms)
- **Red Bull** - @redbull (All platforms)
- **GoPro** - @GoPro (All platforms)
- **NASA** - @NASA (All platforms)

### 3. Add Your Own Client

1. Open the frontend dashboard
2. Click **Settings** in the sidebar
3. Click **Add Client**
4. Enter client details and social media handles
5. Click **Save**
6. Click **Scrape Now** to fetch data

### 4. Run Scrapers Manually

```powershell
cd c:\pulselytics\scripts
..\venv\Scripts\activate

# YouTube (most reliable)
python scrape_youtube.py --channel @NASA --max-videos 20

# Instagram (use small batches)
python scrape_instagram.py --username nike --max-posts 10

# Twitter/X
python scrape_twitter.py --username nasa --max-posts 30
```

## 🔑 API Integration (Optional)

For production use, you can configure official API keys:

1. Click **API Keys** in the dashboard sidebar
2. Add your API keys for each platform:
   - YouTube Data API v3
   - Instagram Graph API
   - Twitter API v2
   - Facebook Graph API
3. Keys are encrypted and stored securely

See `docs/API_SETUP.md` for detailed setup instructions.

## 📊 Dashboard Features

### Overview Page
- Total posts, avg likes, comments, views
- Engagement trend chart
- Platform distribution
- Top hashtags
- Best performing posts

### Analytics Page
- Sentiment analysis
- Content type breakdown
- Posting frequency heatmap
- Advanced filtering

### Top Posts Page
- Sortable grid of all posts
- Filter by platform
- Search by keywords

### Settings Page
- Manage clients
- Trigger manual scrapes
- View scraper status

## 🛠️ Useful Commands

### Start Backend (if not running)
```powershell
cd c:\pulselytics\backend
..\venv\Scripts\python.exe app.py
```

### Start Frontend
```powershell
cd c:\pulselytics\frontend
npm run dev
```

### Check Backend Health
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/health'
```

### View Sample Data
```powershell
# Check YouTube data
Get-Content c:\pulselytics\data\youtube_data.csv -TotalCount 10

# Check all clients
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/clients'
```

### Re-organize Files (if needed)
```powershell
cd c:\pulselytics
.\cleanup.ps1
```

## 📚 Documentation

- **README.md** - Complete documentation
- **QUICKSTART.md** - Setup guide
- **docs/** - API setup guides and implementation details

## 🚨 Troubleshooting

### Backend Not Running
```powershell
cd c:\pulselytics\backend
..\venv\Scripts\python.exe app.py
```

### No Data in Dashboard
- Sample data is already loaded in `/data/*.csv`
- Check backend is running on port 5000
- Check browser console (F12) for errors

### Scraper Errors
- **Instagram**: Use `--max-posts 5-10` to avoid rate limits
- **YouTube**: Most reliable, use for testing
- **Twitter**: May need API credentials for production

### Port Already in Use
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /F /PID <PID>
```

## 🎓 Next Steps

1. ✅ **Explore the dashboard** - Already has sample data
2. ✅ **Test different filters** - Try date ranges and platforms
3. ✅ **Add your first client** - Use Settings page
4. ✅ **Run your first scrape** - Test with YouTube first
5. ✅ **Set up API keys** - For production use (optional)

## 💡 Pro Tips

- **Start with YouTube** - Most stable for testing
- **Use small batches for Instagram** - 5-10 posts at a time
- **Check the logs** - Backend shows helpful debug info
- **Use API keys for production** - More reliable than web scraping
- **Schedule daily scrapes** - Use Windows Task Scheduler

## 🆘 Need Help?

- Check terminal output for errors
- Review browser console (F12)
- See README.md for detailed documentation
- Check docs/ folder for specific guides

---

**Ready?** Just run `npm run dev` in the frontend folder and start exploring! 🎉

The dashboard is already populated with sample data from Nike, Adidas, MrBeast, and more.
