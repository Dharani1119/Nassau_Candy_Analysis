# 🍬 Nassau Candy Distributor — Streamlit Dashboard
## Deployment Guide

---

## 📁 Files Needed
- `streamlit_app.py` — Main dashboard app
- `requirements.txt` — Python dependencies
- `Nassau_Candy_Distributor.csv` — Dataset

---

## 🚀 Deploy to Streamlit Cloud (Free — Recommended)

### Step 1 — Create GitHub Repository
1. Go to [github.com](https://github.com) → Sign in / Sign up (free)
2. Click **"New repository"**
3. Name it: `nassau-candy-dashboard`
4. Set to **Public**
5. Click **"Create repository"**

### Step 2 — Upload Files to GitHub
Upload all 3 files to the repository:
- `streamlit_app.py`
- `requirements.txt`
- `Nassau_Candy_Distributor.csv`

### Step 3 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `nassau-candy-dashboard`
5. Main file: `streamlit_app.py`
6. Click **"Deploy!"**

### Step 4 — Share the URL 🎉
Your dashboard will be live at:
`https://your-username-nassau-candy-dashboard-streamlit-app-xxxx.streamlit.app`

Share this URL with your client!

---

## 💻 Run Locally (Testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```
Opens at: http://localhost:8501

---

## 📊 Dashboard Features

| Tab | Content |
|-----|---------|
| 🏆 Product Profitability | Leaderboard, classification matrix, profit per unit |
| 🏭 Division Performance | Revenue vs profit, treemap, regional & factory analysis |
| 📉 Pareto Analysis | 80/20 concentration, dependency risk |
| 🔬 Cost Diagnostics | Margin risk flags, cost vs sales scatter |
| 📅 Time Series | Monthly trends, quarterly charts, heatmap, ship mode |
| 📋 Executive Summary | Auto-generated insights + data download |

## 🎛️ Sidebar Filters
- Date range selector
- Division filter (Chocolate / Sugar / Other)
- Region filter (Atlantic / Gulf / Interior / Pacific)
- Margin threshold slider
- Product search
- Ship mode filter

---

*Nassau Candy Distributor | Product Line Profitability Dashboard*
