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

Hybrid access is supported:
- Private sheet: share with service account email (Viewer).
- Public sheet: no sharing needed, just pass Sheet ID.

## Google Sheets Setup (Private Mode - Service Account)

Use this when you want the sheet to stay private.

1. Create a Google Cloud service account
   - Open Google Cloud Console -> IAM & Admin -> Service Accounts
   - Create service account (for example: `stock-dashboard-reader`)
2. Enable Sheets API in the same project
   - APIs & Services -> Library -> enable **Google Sheets API**
3. Create a JSON key
   - Service account -> Keys -> Add key -> Create new key -> JSON
   - Download and place file at:
     - `backend/credentials.json` (local), or
     - use base64 into `GOOGLE_SHEETS_CREDENTIALS_JSON` (cloud)
4. Share your Google Sheet
   - Open the target Google Sheet -> Share
   - Add the service account email (looks like `...@....iam.gserviceaccount.com`)
   - Role: `Viewer`
5. Verify sheet format
   - Tab name must be `Stocks`
   - Data starts from row 2 with columns:
     - A: Symbol
     - B: Name
6. Set env and test
   - Set `GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json`
   - Open dashboard, paste Sheet ID, click `Fetch Dashboard`

## Google Sheets Setup (Public Mode - Sheet ID Only)

Use this when you want zero credential setup for users.

1. Prepare the sheet
   - Tab name: `Stocks`
   - Columns:
     - A: Symbol
     - B: Name
2. Make sheet publicly readable
   - Open Google Sheet -> Share
   - Set **General access** to one of:
     - `Anyone with the link` (Viewer), or
     - `Anyone on the internet` (Viewer)
3. Copy Sheet ID
   - From URL:
     - `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`
4. Leave credentials unset (optional but recommended in this mode)
   - Do not set `GOOGLE_SHEETS_CREDENTIALS_PATH` / `GOOGLE_SHEETS_CREDENTIALS_JSON`, or keep invalid/empty
   - Backend auto-falls back to public CSV fetch
5. Test
   - Paste Sheet ID in dashboard and click `Fetch Dashboard`

### Quick Troubleshooting

- Error: `Could not read sheet...`
  - Private mode: verify service account is shared on the sheet and JSON key is valid
  - Public mode: verify sheet access is public and Sheet ID is correct
- Empty stocks list:
  - Ensure tab is exactly `Stocks`
  - Ensure symbols are in column `A` and not only header row
- Wrong tab name:
  - If you use a different tab name, pass `stocks_range` accordingly from API client

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
If no credentials are provided, make sure the sheet is publicly readable.

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
