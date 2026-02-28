# Stock Dashboard

A private dashboard that pulls your stock holdings from Google Sheets, fetches the latest news (last 14 days), and analyzes YouTube channel transcripts for stock recommendations. Deployable to Google Cloud Run with username/password login.

## Features

- **Google Sheets integration**: Stock list (symbol, name, avg price, qty) and YouTube channels
- **News aggregation**: Latest news for each stock via GNews API (14-day window)
- **YouTube analysis**: Fetches transcripts from configured channels and extracts stock mentions/recommendations
- **Last updated timestamp**: Shows when the sheet data was fetched
- **Authentication**: Username/password with JWT
- **Sample sheet format**: Reference modal on the dashboard

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Register a user, then enter your Google Sheet ID.

### 3. Google Sheet Setup

Create a Google Sheet with two tabs:

**Stocks** (range `Stocks!A2:E`):

| Symbol | Name | Avg Price | Qty |
|--------|------|-----------|-----|
| AAPL   | Apple Inc | 175.50 | 10 |
| MSFT   | Microsoft | 380.25 | 5 |

**YouTube** (range `YouTube!A2:B`):

| Channel Name | Channel ID |
|--------------|-------------|
| @FinancialEducation | UCnMn36GT_H0d-wsO-2O-ptQ |
| @GrahamStephan | UCV6KDgJskWaEckne5aPA0aQ |

Share the sheet with your **Google Service Account** email (from credentials.json) with "Viewer" access.

### 4. API Keys

- **Google Sheets**: Create a service account in Google Cloud Console, enable Sheets API, download JSON key.
- **Google Gemini**: For AI summarization & YouTube analysis. Free key at [Google AI Studio](https://aistudio.google.com/apikey).
- **GNews**: Free key at [gnews.io](https://gnews.io/) for news fetching.
- **YouTube**: Enable YouTube Data API v3 in Google Cloud Console, create an API key.

## Deploy to Google Cloud Run

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud builds submit --config=cloudbuild.yaml

# Set secrets (recommended)
gcloud run services update stock-dashboard \
  --set-env-vars="SECRET_KEY=xxx,GNEWS_API_KEY=xxx,YOUTUBE_API_KEY=xxx" \
  --region=us-central1

# For Google Sheets credentials, use Secret Manager or base64 in env
```

For private access, use `--no-allow-unauthenticated` in `cloudbuild.yaml` and configure Cloud IAP or restrict by VPC.

**Note**: The default SQLite database does not persist across Cloud Run restarts. For production, consider Cloud SQL or set `DATABASE_URL` to a persistent volume.

## Project Structure

```
StockDashboard/
├── backend/           # FastAPI app
│   ├── app/
│   │   ├── api/       # Auth, dashboard routes
│   │   ├── core/      # Config
│   │   ├── db/        # SQLite, models
│   │   ├── models/    # Pydantic models
│   │   └── services/ # Sheets, news, YouTube
│   └── requirements.txt
├── frontend/          # React + Vite
├── sample-sheet/      # Sample CSV files for Google Sheet import
├── Dockerfile         # Multi-stage for Cloud Run
├── cloudbuild.yaml    # GCP build config
└── .env.example
```

## License

MIT
