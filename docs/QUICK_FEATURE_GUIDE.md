# 🚀 Quick Feature Guide - New Features

This guide covers the three newly implemented features in Pulselytics.

---

## 📄 PDF Report Generation

### How to Use:
1. Navigate to **Reports** page (left sidebar)
2. Select a client from the dropdown
3. Choose a date range
4. Click **"Generate PDF Report"** button
5. PDF downloads automatically

### What's Included:
- Executive summary with key metrics
- Engagement trend chart
- Platform distribution pie chart
- Top 10 performing posts
- Professional formatting

### Technical Details:
- **Backend:** `backend/report_generator.py`
- **Endpoint:** `POST /api/reports/generate`
- **Download:** `GET /api/reports/download/:filename`
- **Charts:** Matplotlib + Seaborn
- **Format:** PDF via ReportLab

---

## 🌙 Dark Mode

### How to Use:
1. Click the **moon icon** 🌙 in the top-right header
2. Theme switches instantly
3. Toggle back with the **sun icon** ☀️

### Features:
- ✅ Persists across browser sessions
- ✅ Smooth color transitions
- ✅ Optimized for readability
- ✅ All charts adapted for dark backgrounds
- ✅ Proper contrast ratios

### Technical Details:
- **Component:** `frontend/src/components/DarkModeToggle.jsx`
- **Storage:** localStorage ('dark-mode' key)
- **Strategy:** Tailwind class-based (`dark:` prefix)
- **CSS:** `frontend/src/index.css`

---

## ✨ AI-Powered Insights

### How to Use:

#### Option 1: Dedicated Tab (Recommended)
1. Go to **Analytics** page
2. Click the **"✨ AI Insights"** tab at the top
3. Click **"Refresh"** button
4. View insights in two sub-tabs:
   - **Analytics Insights** - Data analysis and trends
   - **Content Strategy** - Posting recommendations

#### Option 2: Overview Section
1. Go to **Analytics** page
2. Stay on **"📊 Overview"** tab
3. Scroll to the bottom
4. Find AI Insights section
5. Click **"Refresh"**

### What You'll See:

#### 💡 Key Insights (Blue)
- Content output analysis
- Engagement performance
- Platform activity levels
- Community interaction

#### 📈 Trends & Patterns (Green)
- Posting consistency tracking
- Engagement trajectory (up/down/stable)
- Audience participation trends
- Platform diversity analysis

#### ✨ Recommendations (Purple)
- Posting frequency optimization
- Best posting times
- Hashtag strategies
- Content mix suggestions
- Platform expansion tips

#### ⚠️ Areas of Concern (Orange)
- Low engagement warnings
- Declining trend alerts
- Limited platform presence notifications

### Two Modes:

#### 🤖 AI-Powered (with OpenAI API)
- Uses GPT-3.5-turbo
- Advanced natural language insights
- Context-aware recommendations
- Shows: "Powered by AI" badge

#### 📊 Rule-Based (Fallback)
- Automatic fallback when:
  - No API key configured
  - API quota exceeded
  - Network issues
- Data-driven analysis
- 8+ actionable recommendations
- Shows: "Generated using analytics rules"

### Technical Details:
- **Backend:** `backend/ai_insights.py` (365 lines)
- **Component:** `frontend/src/components/AIInsights.jsx` (259 lines)
- **Endpoints:**
  - `POST /api/insights/generate` - Analytics insights
  - `POST /api/insights/content-recommendations` - Content strategy
- **AI Model:** GPT-3.5-turbo (OpenAI)
- **Fallback:** Comprehensive rule-based system

---

## 🔧 Configuration

### Enable AI Insights with OpenAI:

1. Get an API key from https://platform.openai.com/api-keys
2. Edit `backend/.env`:
   ```bash
   OPENAI_API_KEY=sk-proj-your-api-key-here
   ```
3. Restart backend server
4. AI insights will use GPT-3.5-turbo

### Without OpenAI API Key:
- No configuration needed!
- Rule-based insights work automatically
- Still provides valuable recommendations

---

## 🎯 Tips & Best Practices

### PDF Reports:
- Generate weekly/monthly reports for clients
- Compare different date ranges
- Use as presentation materials
- Archive for performance tracking

### Dark Mode:
- Reduces eye strain during night work
- Better for OLED screens (battery saving)
- Professional appearance
- Personal preference

### AI Insights:
- Refresh regularly (weekly recommended)
- Compare insights over time
- Implement recommended changes
- Track recommendation effectiveness
- Use with different date ranges for trends

---

## 🐛 Troubleshooting

### PDF Generation Issues:
- **Problem:** "Failed to generate report"
- **Solution:** Check backend logs, ensure client has data

### Dark Mode Not Persisting:
- **Problem:** Theme resets on reload
- **Solution:** Check browser localStorage settings
- **Clear cache** if needed

### AI Insights Errors:

#### "Error code: 429 - Quota exceeded"
- **Cause:** OpenAI API quota exceeded
- **Solution:** Automatic fallback to rule-based insights
- **Action:** No action needed, or add more credits to OpenAI account

#### "Error code: 404 - Model not found"
- **Cause:** API key doesn't have access to GPT-4
- **Solution:** Updated to use GPT-3.5-turbo (available on all keys)
- **Status:** ✅ Fixed

#### "No insights showing"
- **Cause:** No data for selected client/date range
- **Solution:** Select different client or date range
- **Check:** Ensure data has been scraped for client

---

## 📊 Feature Comparison

| Feature | Free (Rule-Based) | With OpenAI API |
|---------|-------------------|-----------------|
| PDF Reports | ✅ Full access | ✅ Full access |
| Dark Mode | ✅ Full access | ✅ Full access |
| AI Insights | ✅ Rule-based | ✅ GPT-3.5-turbo |
| Key Insights | ✅ Yes | ✅ Enhanced |
| Trends | ✅ Yes | ✅ Enhanced |
| Recommendations | ✅ 8+ items | ✅ Contextual |
| Warnings | ✅ Yes | ✅ Enhanced |
| Content Strategy | ✅ Best practices | ✅ Custom advice |

---

## 🚀 Next Steps

1. **Try all three features** to familiarize yourself
2. **Generate a PDF report** for your best-performing client
3. **Toggle dark mode** to see the difference
4. **Check AI insights** for actionable recommendations
5. **Implement suggestions** and track improvements

---

## 📞 Need Help?

- Check `FEATURE_STATUS.md` for implementation details
- Review `README.md` for full documentation
- Check backend logs for errors: `backend/app.py` output
- Check browser console for frontend errors (F12)

---

**All features are production-ready and fully tested!** 🎉
