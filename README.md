# Stock News Dashboard

A lightweight private dashboard that reads stock symbols from Google Sheets, fetches recent stock news from GNews, and generates AI summaries with Gemini.

## Current Features

- Google Sheets input (`Stocks` tab with only `Symbol` and `Name`)
- News fetch from GNews for each symbol
- News window: last 7 days
- Max 2 news articles per stock
- Throttled news calls (1s delay between stock requests) to reduce rate-limit errors
- Portfolio Summary section with:
  - Positives
  - Negatives
  - Risky signals
- No login/auth flow in the UI
- Deployable to Google Cloud Run

## Project Structure

```text
StockDashboard/
├── backend/                  # FastAPI app
│   ├── app/
│   │   ├── api/routers/      # Dashboard API routes
│   │   ├── core/             # App settings
│   │   ├── db/               # SQLAlchemy setup
│   │   ├── models/           # Pydantic models
│   │   └── services/         # Google Sheets, GNews, Gemini services
│   ├── requirements.txt
│   └── .env                  # Local backend env
├── frontend/                 # React + Vite + Tailwind
├── sample-sheet/             # Sample CSVs
├── Dockerfile                # Multi-stage frontend+backend image
└── cloudbuild.yaml           # Cloud Build + Cloud Run deploy
```

## Google Sheet Format

Create one tab named `Stocks` with range `Stocks!A2:B`:

| Symbol | Name |
|--------|------|
| AAPL   | Apple Inc |
| MSFT   | Microsoft Corporation |
| GOOGL  | Alphabet Inc |

Share the sheet with your service account email (Viewer access is enough).

## Environment Variables (Backend)

Create `backend/.env`:

```env
ALLOWED_USERNAME=optional
ALLOWED_PASSWORD=optional
SECRET_KEY=change-me-in-production-use-openssl-rand-hex-32

GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json
# OR use base64 json for cloud
# GOOGLE_SHEETS_CREDENTIALS_JSON=<base64-service-account-json>

GNEWS_API_KEY=your_gnews_key
GEMINI_API_KEY=your_gemini_key

DEBUG=false
CORS_ORIGINS=http://localhost:5173,http://localhost:4173,http://localhost:3000
```

Note: login is currently bypassed, so `ALLOWED_USERNAME` and `ALLOWED_PASSWORD` are not required for dashboard access.

## Run Locally

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 4173
```

### 3. Open App

- Frontend: [http://localhost:4173](http://localhost:4173)
- Backend health: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Use Dashboard

1. Paste Google Sheet ID
2. Click `Fetch Dashboard`
3. See Portfolio Summary + per-stock news cards

## Deploy on Public Cloud (Google Cloud Run)

### Prerequisites

- Google Cloud project
- Billing enabled
- `gcloud` CLI authenticated
- APIs enabled:
  - Cloud Run API
  - Cloud Build API
  - Artifact Registry API

### 1. Set project

```bash
gcloud config set project YOUR_PROJECT_ID
```

### 2. Build and deploy

```bash
gcloud builds submit --config=cloudbuild.yaml
```

This builds the container and deploys service `stock-dashboard` to Cloud Run.

### 3. Set environment variables on Cloud Run

```bash
gcloud run services update stock-dashboard \
  --region=us-central1 \
  --set-env-vars="SECRET_KEY=replace_me,GNEWS_API_KEY=your_gnews_key,GEMINI_API_KEY=your_gemini_key,CORS_ORIGINS=https://YOUR_DOMAIN"
```

### 4. Configure Google Sheets credentials for Cloud Run

Use either of these approaches:

1. Secret Manager + mounted file (recommended)
2. Base64 JSON in env var `GOOGLE_SHEETS_CREDENTIALS_JSON`

If using base64:

```bash
base64 -i credentials.json
```

Put output in `GOOGLE_SHEETS_CREDENTIALS_JSON`.

### 5. Access public URL

After deploy, Cloud Run prints service URL (for example `https://stock-dashboard-xxxxx-uc.a.run.app`).

## Operational Notes

- GNews free tiers can rate-limit aggressively.
- Current backend applies 1 second delay per stock request.
- SQLite is local/ephemeral for Cloud Run instances; current app does not depend on persistent DB for dashboard fetches.

## License

MIT
