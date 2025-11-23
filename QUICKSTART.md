# 🚀 Quick Setup Guide — Pulselytics

## 📋 Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git** (optional)

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ **Backend Setup**

```powershell
# Navigate to backend directory
cd c:\pulselytics\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env

# Start backend server
python app.py
```

**Backend will run on:** `http://127.0.0.1:5000`

---

### 2️⃣ **Frontend Setup**

Open a **new PowerShell window**:

```powershell
# Navigate to frontend directory
cd c:\pulselytics\frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env

# Start development server
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

---

### 3️⃣ **Run Scrapers (Get Data)**

Open a **third PowerShell window**:

```powershell
# Navigate to project root
cd c:\pulselytics

# Activate Python environment
.\venv\Scripts\activate

# Option A: Scrape individual platforms
python scrape_youtube.py --channel NASA --max-videos 20
python scrape_instagram.py --username nasa --max-posts 10
python scrape_twitter.py --username NASA --max-posts 30

# Option B: Scrape all platforms at once
python update_all.py --instagram nasa --youtube NASA --twitter NASA --facebook nasa
```

**Data saved to:** `c:\pulselytics\data\*.csv`

---

### 4️⃣ **View Dashboard**

1. Open browser to `http://localhost:5173`
2. Select a client from dropdown (or "All Clients")
3. View analytics, top posts, and charts
4. Go to **Settings** page to add new clients

---

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```bash
# Scraper Mode: 'lightweight' (faster) or 'playwright' (all platforms)
SCRAPER_MODE=lightweight

# Flask Settings
FLASK_DEBUG=True
PORT=5000

# Auto-scraping interval (minutes)
SCRAPE_INTERVAL_MINUTES=360
```

### Frontend Configuration (`frontend/.env`)

```bash
# Backend API URL
VITE_API_URL=http://127.0.0.1:5000/api
```

---

## 📊 How It Works

```
┌─────────────────┐
│  Web Scrapers   │ ← Python scripts fetch public posts
│  (Instagram,    │   from social media platforms
│   YouTube, X)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   CSV Files     │ ← Data stored locally in /data/
│  (data/*.csv)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask Backend  │ ← Processes data, provides API
│  (Port 5000)    │   endpoints for analytics
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ React Frontend  │ ← Dashboard displays charts,
│  (Port 5173)    │   KPIs, and top posts
└─────────────────┘
```

---

## 🧪 Testing

### Test Backend API

```powershell
# Check health
curl http://127.0.0.1:5000/api/health

# Get clients
curl http://127.0.0.1:5000/api/clients

# Get analytics
curl "http://127.0.0.1:5000/api/analytics?range=30days"
```

### Test Scrapers

```powershell
cd c:\pulselytics
.\venv\Scripts\activate

# Quick test with NASA account
python scrape_youtube.py --channel NASA --max-videos 5
```

Check `data/youtube_data.csv` for results.

---

## 📦 Sample Data

Pre-loaded clients in `backend/data/`:
- **newco.json** — NewCo Startup
- **techbrand.json** — TechBrand Enterprise
- **lifestyle.json** — Lifestyle Living

---

## 🛠️ Troubleshooting

### Backend won't start
- Check Python version: `python --version` (must be 3.9+)
- Reinstall dependencies: `pip install -r backend/requirements.txt`
- Check port 5000 not in use: `netstat -ano | findstr :5000`

### Frontend won't start
- Check Node version: `node --version` (must be 18+)
- Delete `node_modules` and reinstall: `rm -r node_modules; npm install`
- Check port 5173 not in use

### No data showing in dashboard
- Run scrapers first to populate `data/*.csv` files
- Refresh browser after scraping completes
- Check browser console (F12) for API errors

### Instagram rate limits (401 errors)
- Reduce `--max-posts` to 5-10
- Wait 30-60 minutes between runs
- Use smaller batches for testing

---

## 📚 Next Steps

1. **Add your own clients** — Go to Settings page → Add Client
2. **Schedule automatic scraping** — Set up Windows Task Scheduler (see README)
3. **Export reports** — Click "Export" button to download CSV/PDF
4. **Customize visualizations** — Edit frontend components in `frontend/src/pages/`

---

## 🔗 Resources

- **Full README:** `README.md`
- **API Documentation:** `/backend/app.py` (see docstrings)
- **Scraper Guides:** 
  - Lightweight: `/backend/LIGHTWEIGHT_SCRAPER.md`
  - Playwright: `/backend/SCRAPER_CONFIG.md`

---

## 💡 Pro Tips

✅ **Start with YouTube** — Most reliable scraper  
✅ **Use lightweight mode** — 3-5x faster than Playwright  
✅ **Small batches first** — Test with 5-10 posts before scaling  
✅ **Monitor rate limits** — Instagram is most restrictive  
✅ **Check logs** — Backend prints helpful debug messages  

---

**Happy Analyzing! 📊**

For support, check the main `README.md` or review error logs in terminal.
