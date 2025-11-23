# 📊 Pulselytics — Professional Social Media Analytics Dashboard

> **Full-stack analytics platform for advertising agencies and social media managers.** Track engagement, analyze trends, and visualize performance across Instagram, Facebook, YouTube, and Twitter/X — all without official APIs.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

---

## ✨ Features

### 📊 **Professional Dashboard**
- **Modern UI** — Clean, data-focused design with Tailwind CSS
- **Real-time Analytics** — Live engagement metrics and trend analysis
- **Interactive Charts** — Recharts visualizations with smooth animations
- **Multi-client Management** — Switch between clients with dynamic data updates
- **Platform Filtering** — View Instagram, Facebook, YouTube, Twitter/X independently
- **Date Range Selection** — Analyze 7/30/90 days or custom ranges
- **Search & Filter** — Find posts by text, hashtags, or platform
- **🌙 Dark Mode** — Complete dark theme with toggle and localStorage persistence

### 📈 **Advanced Analytics**
- **Engagement Trends** — Line charts showing likes, comments, views over time
- **Top Posts** — Ranked grid of highest-performing content
- **Hashtag Insights** — Bar chart of most-used hashtags
- **Platform Distribution** — Compare post count across social channels
- **Sentiment Analysis** — VADER-powered positive/neutral/negative breakdown
- **Content Type Analysis** — Photo vs video vs text-only distribution
- **Posting Frequency** — Heatmap of optimal posting times
- **✨ AI-Powered Insights** — GPT-3.5-turbo analytics with rule-based fallback

### 🤖 **AI & Machine Learning Features** (NEW!)
- **🎯 Predictive Engagement** — Predict post performance before publishing (ML-powered)
- **🚨 Anomaly Detection** — Auto-detect viral posts, engagement drops, and unusual patterns
- **⏰ Optimal Time Predictor** — ML-based recommendations for best posting times
- **📈 Trend Forecasting** — Predict engagement trends 7 days ahead
- **🧠 Custom ML Models** — Train personalized models on each client's historical data
- **📊 Virality Scoring** — Rate content potential on a 0-100 scale
- **💡 Smart Recommendations** — Data-driven content strategy suggestions

### 📄 **Reports & Export**
- **PDF Report Generation** — Professional reports with charts and analytics
- **CSV Export** — Download data for external analysis
- **JSON Export** — API-ready data format
- **Automated Insights** — AI-generated recommendations and trends

### 🔄 **Web Scraping (No APIs Required)**
- **⚡ Lightweight Scraper** — Fast API-based scraping (3-10s total)
  - Instagram: `instaloader` (public profiles)
  - YouTube: `yt-dlp` (channel metadata)
  - Twitter/X: `snscrape` (public tweets)
  - Facebook: Best-effort public page scraping
- **🌐 Playwright Scraper** — Browser automation fallback (15-30s)
  - All platforms with login support
  - Proxy integration for production
  - Anti-detection features

### 🛠️ **Technical Stack**

**Frontend:**
- React 18 + Vite
- Tailwind CSS for styling
- Recharts for data visualization
- React Router for navigation
- Axios for API calls
- Lucide React icons

**Backend:**
- Flask REST API
- Flask-CORS for cross-origin requests
- Pandas for data processing
- VADER Sentiment for NLP
- CSV/JSON data storage

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** with pip
- **Node.js 18+** with npm

### 1️⃣ **Automated Setup** (Recommended)

```powershell
cd c:\pulselytics
.\setup.ps1
```

This script will:
- Create Python virtual environments
- Install all backend and frontend dependencies
- Create `.env` configuration files
- Display next steps

### 2️⃣ **Manual Setup**

#### Backend

```powershell
cd c:\pulselytics\backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env

# Start server
python app.py
```

**Backend runs on:** `http://127.0.0.1:5000`

#### Frontend

```powershell
cd c:\pulselytics\frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env

# Start development server
npm run dev
```

**Frontend runs on:** `http://localhost:5173`

### 3️⃣ **Run Scrapers**

```powershell
cd c:\pulselytics\scripts
..\venv\Scripts\activate

# Scrape YouTube (most reliable)
python scrape_youtube.py --channel NASA --max-videos 20

# Scrape Instagram (small batches to avoid rate limits)
python scrape_instagram.py --username nasa --max-posts 10

# Scrape Twitter/X
python scrape_twitter.py --username NASA --max-posts 30
```

### 4️⃣ **Access Dashboard**

Open `http://localhost:5173` in your browser

---

## 📁 Project Structure

```
pulselytics/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── Layout.jsx     # Main layout with sidebar + header
│   │   │   ├── KPICard.jsx    # Metric cards
│   │   │   ├── ChartTooltip.jsx
│   │   │   ├── LoadingSkeleton.jsx
│   │   │   └── ProfileAutocomplete.jsx
│   │   ├── pages/             # Page components
│   │   │   ├── Overview.jsx   # Dashboard with KPIs and charts
│   │   │   ├── Analytics.jsx  # Detailed analytics
│   │   │   ├── TopPosts.jsx   # Top performing posts
│   │   │   ├── Reports.jsx    # Export functionality
│   │   │   ├── Settings.jsx   # Client management + scraper controls
│   │   │   └── APIKeys.jsx    # API key management
│   │   ├── services/
│   │   │   └── api.js         # Centralized API calls
│   │   ├── utils/
│   │   │   └── exportData.js  # Data export utilities
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # Entry point
│   ├── package.json           # Frontend dependencies
│   ├── vite.config.js         # Vite configuration
│   └── tailwind.config.js     # Tailwind CSS configuration
│
├── backend/                    # Flask API server
│   ├── app.py                 # Main Flask application
│   ├── database.py            # SQLite database utilities
│   ├── encryption.py          # API key encryption
│   ├── requirements.txt       # Python dependencies
│   ├── pulselytics.db         # SQLite database
│   └── data/                  # Client JSON files
│       ├── mrbeast.json       # Sample: MrBeast
│       ├── nike.json          # Sample: Nike
│       ├── adidas.json        # Sample: Adidas
│       ├── redbull.json       # Sample: Red Bull
│       ├── gopro.json         # Sample: GoPro
│       └── nasa_test.json     # Sample: NASA
│
├── scripts/                    # Scraper and utility scripts
│   ├── scrape_instagram.py    # Instagram scraper
│   ├── scrape_instagram_api.py # Instagram Graph API scraper
│   ├── scrape_youtube.py      # YouTube scraper
│   ├── scrape_youtube_api.py  # YouTube Data API v3 scraper
│   ├── scrape_twitter.py      # Twitter/X scraper
│   ├── scrape_twitter_api.py  # Twitter API v2 scraper
│   ├── scrape_facebook.py     # Facebook scraper
│   ├── scrape_facebook_api.py # Facebook Graph API scraper
│   ├── analyze_data.py        # Analytics engine
│   ├── common.py              # Shared utilities
│   ├── seed_demo_data.py      # Demo data generator
│   └── setup.ps1              # Automated setup script
│
├── data/                       # Scraped data (CSV)
│   ├── instagram_data.csv
│   ├── youtube_data.csv
│   ├── twitter_data.csv
│   └── facebook_data.csv
│
├── docs/                       # Documentation
│   ├── API_SETUP.md           # API setup guides
│   ├── API_INTEGRATION_GUIDE.md
│   ├── DATABASE_SETUP.md
│   ├── INSTAGRAM_API_SETUP.md
│   ├── ANALYTICS_ENHANCEMENTS.md
│   ├── NEW_FEATURES.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── SETUP_COMPLETE.md
│   └── SETUP_SUMMARY.md
│
├── venv/                       # Python virtual environment
│
├── README.md                   # This file
├── QUICKSTART.md               # Quick setup guide
├── requirements.txt            # Python dependencies
├── cleanup.ps1                 # Organization script
└── .gitignore                  # Git ignore rules
```

---

## 🔌 API Endpoints

### Client Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/clients` | List all clients |
| `GET` | `/api/clients/:id` | Get client by ID |
| `POST` | `/api/clients` | Create new client |
| `PUT` | `/api/clients/:id` | Update client |
| `DELETE` | `/api/clients/:id` | Delete client |

### Analytics & Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics` | Get analytics (supports `?client=&range=&platform=`) |
| `GET` | `/api/clients/:id/posts` | Get posts for client |
| `GET` | `/api/stats/summary` | Get overall summary stats |

### Reports & Insights
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/reports/generate` | Generate PDF report |
| `GET` | `/api/reports/download/:filename` | Download PDF report |
| `POST` | `/api/insights/generate` | Generate AI insights |
| `POST` | `/api/insights/content-recommendations` | Get content recommendations |

### Scraping
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/scrape` | Trigger scraping for client |
| `GET` | `/api/schedule/status` | Get scraper mode and schedule info |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |

---

## ⚙️ Configuration

### Backend Environment (`backend/.env`)

```bash
# Scraper Mode: 'lightweight' (faster) or 'playwright' (all platforms)
SCRAPER_MODE=lightweight

# Flask Configuration
FLASK_DEBUG=True
PORT=5000

# Auto-scraping interval (minutes)
SCRAPE_INTERVAL_MINUTES=360

# OpenAI API Key (optional - for AI insights)
OPENAI_API_KEY=your-api-key-here

# Playwright Proxies (optional, for production)
# PROXY_SERVER=http://proxy.example.com:8080
# PROXY_USERNAME=your_username
# PROXY_PASSWORD=your_password
```

### Frontend Environment (`frontend/.env`)

```bash
# Backend API URL
VITE_API_URL=http://127.0.0.1:5000/api
```

---

## 📊 Data Flow

```
┌─────────────────────┐
│   Web Scrapers      │  ← Python scripts fetch public posts
│  (Instagram, YouTube,│    from social media platforms
│   Twitter/X, FB)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   CSV Files         │  ← Data stored locally in /data/
│ (instagram_data.csv,│
│  youtube_data.csv)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  analyze_data.py    │  ← Processes data: engagement,
│  (Analytics Engine) │    sentiment, hashtags, trends
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Flask Backend     │  ← Provides REST API endpoints
│   (Port 5000)       │    for frontend consumption
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  React Frontend     │  ← Dashboard displays charts,
│  (Port 5173)        │    KPIs, and top posts
└─────────────────────┘
```

---

## 🛠️ Scraper Details

| Platform | Lightweight Tool | Speed | Reliability | Rate Limits |
|----------|-----------------|-------|-------------|-------------|
| **YouTube** | `yt-dlp` | ⚡ 5-10s | ⭐⭐⭐⭐⭐ Excellent | Low |
| **Instagram** | `instaloader` | ⚡ 3-5s | ⭐⭐⭐ Good | **High** (5-10 posts/hour) |
| **Twitter/X** | `snscrape` | ⚡ 8-12s | ⭐⭐⭐⭐ Very Good | Medium |
| **Facebook** | `requests` + BS4 | ⚡ 10-15s | ⭐⭐ Fair | Very High |

### Best Practices

✅ **Start with YouTube** — Most stable scraper  
✅ **Instagram: Small batches** — Use `--max-posts 5-10` to avoid 401 errors  
✅ **Wait between runs** — 30-60 min cooldown for Instagram  
✅ **Public data only** — No login required, respects ToS  
✅ **Monitor logs** — Check terminal output for errors  

---

## 🧪 Testing

### Test Backend API

```powershell
# Health check
curl http://127.0.0.1:5000/api/health

# Get clients
curl http://127.0.0.1:5000/api/clients

# Get analytics
curl "http://127.0.0.1:5000/api/analytics?range=30days&platform=all"
```

### Test Scrapers

```powershell
# Quick test with NASA
python scrape_youtube.py --channel NASA --max-videos 5

# Check results
cat .\data\youtube_data.csv
```

---

## 📈 Dashboard Features

### Overview Page
- **4 KPI Cards** — Total Posts, Avg Likes, Avg Comments, Avg Views
- **Engagement Trend Chart** — Line graph of engagement over time
- **Platform Distribution** — Bar chart of posts per platform
- **Top Hashtags** — Horizontal bar chart of most-used hashtags
- **Top Posts Grid** — 6 highest-performing posts with thumbnails

### Settings Page
- **Scraper Status** — View current mode (lightweight/playwright)
- **Client Management** — Add, edit, delete clients
- **Scrape Triggers** — Manual scraping with "Scrape Now" button
- **Platform Configuration** — Set Instagram, YouTube, Facebook, Twitter handles

### Analytics Page
- Detailed trend analysis
- Sentiment breakdown (positive/neutral/negative)
- Content type distribution (photo/video/text)
- Posting frequency heatmap

---

## 🚨 Troubleshooting

### Backend won't start
```powershell
# Check Python version
python --version  # Must be 3.9+

# Reinstall dependencies
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt

# Check port availability
netstat -ano | findstr :5000
```

### Frontend won't start
```powershell
# Check Node version
node --version  # Must be 18+

# Clear and reinstall
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

### Instagram 401 Errors
- **Cause:** Rate limiting after 10-15 posts
- **Solution:** Use `--max-posts 5`, wait 30-60 min between runs
- **Alternative:** Switch to Playwright scraper mode

### No data in dashboard
- **Cause:** Scrapers haven't run yet
- **Solution:** Run scrapers to populate `/data/*.csv` files
- **Check:** Backend logs for CSV loading errors

---

## 📅 Automation (Optional)

### Windows Task Scheduler

Create a scheduled task to run scrapers daily:

```powershell
# Create task to run daily at 6 AM
schtasks /create /tn "Pulselytics Daily Scrape" /tr "C:\pulselytics\venv\Scripts\python.exe C:\pulselytics\update_all.py --instagram nasa --youtube NASA --twitter NASA" /sc daily /st 06:00
```

---

## 🔐 Ethics & Legal

- **Public data only** — No login required, no private accounts
- **Rate limiting** — Respects platform limits with delays
- **ToS compliance** — Educational/analytics use only
- **No warranty** — Use at your own risk
- **Personal use** — Not for commercial redistribution

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — 5-minute setup guide
- **[setup.ps1](setup.ps1)** — Automated installation script
- **Backend API** — See docstrings in `backend/app.py`
- **Scraper Guides** — Comments in individual scraper files

---

## 🔮 Roadmap

- [x] Full-stack React + Flask architecture
- [x] Multi-client management
- [x] Real-time scraping with API triggers
- [x] Sentiment analysis with VADER
- [x] Hashtag analytics
I'll start the backend server and verify it's running with sample data.

Starting (1/2) Start backend server


cd c:\pulselytics\backend; ..\venv\Scripts\python.exe app.py
Let me check the terminal output to see if the server started successfully:

Checked background terminal output

The backend can't find common.py because we moved it to the scripts folder. I'll fix the import by updating the path in app.py:

Read app.py, lines 1 to 31

app.py+5-2
Now let me restart the backend server with the fixed imports:


..\venv\Scripts\python.exe app.py
Checked background terminal output


cd c:\pulselytics\backend; & ..\venv\Scripts\python.exe app.py
Checked background terminal output

Perfect! Backend is running. Now let me verify it's responding correctly:

Starting (2/2) Verify server response


Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/health' -UseBasicParsing

Start-Sleep -Seconds 2; try { $health = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/health' -UseBasicParsing; Write-Host "✅ Backend Health: $($health.status)" -ForegroundColor Green; $clients = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/clients' -UseBasicParsing; Write-Host "✅ Clients loaded: $($clients.count)" -ForegroundColor Green } catch { Write-Host "❌ Backend not responding: $_" -ForegroundColor Red }
The server is terminating. Let me check if there's an issue with the data directory path. I notice it's looking for data but the data is in data. Let me fix the common.py path:

Read common.py, lines 1 to 21

common.py+2-1
Now restart the backend:


& ..\venv\Scripts\python.exe app.py

cd c:\pulselytics\backend; Start-Process -NoNewWindow -FilePath '..\venv\Scripts\python.exe' -ArgumentList 'app.py'

Start-Sleep -Seconds 3; try { $health = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/health' -UseBasicParsing; Write-Host "`n✅ Backend Status: $($health.status)" -ForegroundColor Green; Write-Host "✅ Scraper Mode: $($health.scraper_mode)" -ForegroundColor Green; $clients = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/clients' -UseBasicParsing; Write-Host "✅ Sample Clients: $($clients.count)" -ForegroundColor Green; Write-Host "`n🚀 Backend running at http://127.0.0.1:5000" -ForegroundColor Cyan } catch { Write-Host "`n❌ Backend not responding" -ForegroundColor Red; throw }

$health = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/health' -UseBasicParsing; $health | ConvertTo-Json
Excellent! Backend is running. Now let me verify sample data:

Completed (2/2) Verify server response


$clients = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/clients' -UseBasicParsing; Write-Host "`n✅ PULSELYTICS BACKEND RUNNING" -ForegroundColor Green; Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray; Write-Host "Status: OK" -ForegroundColor Cyan; Write-Host "URL: http://127.0.0.1:5000" -ForegroundColor Cyan; Write-Host "Sample Clients: $($clients.count)" -ForegroundColor Cyan; Write-Host "Mode: lightweight" -ForegroundColor Cyan; Write-Host "`nClients:" -ForegroundColor Yellow; $clients.clients | ForEach-Object { Write-Host "  • $($_.name)" -ForegroundColor White }
Perfect! ✅ Backend server is running successfully!

Summary
✅ Backend Server Started

URL: http://127.0.0.1:5000
Status: OK
Mode: lightweight scraper
Sample Clients: 6 loaded (Adidas, GoPro, MrBeast, NASA Test, Nike, Red Bull)
Fixed Issues:

Updated app.py to include scripts folder in Python path
Updated common.py to point DATA_DIR to data (one level up from scripts)
Next Step:
To start the frontend dashboard, run:


- [x] Platform filtering
- [x] PDF report generation
- [x] Dark mode
- [x] AI-powered insights (GPT integration)
- [ ] Email alerts for anomalies
- [ ] Competitor analysis
- [ ] Mobile responsive design

---

## 💡 Pro Tips

1. **Start with sample clients** — Pre-loaded in `backend/data/`
2. **Use lightweight mode** — 3-5x faster than Playwright
3. **YouTube first** — Most reliable for testing
4. **Small Instagram batches** — Avoid rate limits
5. **Check browser console** — F12 for API errors
6. **Monitor backend logs** — Helpful debug messages

---

## 🤝 Contributing

This is a personal analytics tool. Feel free to fork and customize for your needs!

---

## 📄 License

MIT License — Free to use for personal and client projects.

---

## 👨‍💻 Author

Built with ❤️ for social media professionals managing clients at scale.

**Pulselytics** — _Pulse of your social presence._

---

## 🆘 Support

- **Issues:** Check terminal logs (backend and frontend)
- **Scrapers:** Review error messages, adjust rate limits
- **API:** Test endpoints with `curl` or Postman
- **Frontend:** Check browser console (F12) for React errors

For detailed setup help, see **[QUICKSTART.md](QUICKSTART.md)**

---

**Ready to start?** Run `.\setup.ps1` and you'll be analyzing social media data in 5 minutes! 🚀
