"""Google Sheets service for fetching stock data."""
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models.dashboard import StockHolding

# Required scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _get_credentials(credentials_path: str, credentials_json: Optional[str] = None):
    """Get Google credentials from file or env."""
    if credentials_json:
        try:
            creds_dict = json.loads(base64.b64decode(credentials_json).decode())
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        except Exception:
            pass
    path = Path(credentials_path)
    if path.exists():
        return Credentials.from_service_account_file(str(path), scopes=SCOPES)
    return None


async def fetch_sheet_data(
    spreadsheet_id: str,
    credentials_path: str = "credentials.json",
    credentials_json: Optional[str] = None,
    stocks_range: str = "Stocks!A2:B",
) -> tuple[list[StockHolding], datetime]:
    """
    Fetch stocks from Google Sheet.

    Expected Stocks sheet format:
    | Symbol | Name |
    | AAPL   | Apple Inc |
    """
    creds = _get_credentials(credentials_path, credentials_json)
    if not creds:
        raise ValueError(
            "Google credentials not found. Set GOOGLE_SHEETS_CREDENTIALS_PATH or "
            "GOOGLE_SHEETS_CREDENTIALS_JSON. Use a service account with Sheets API access."
        )

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    stocks: list[StockHolding] = []
    last_updated = datetime.utcnow()

    try:
        # Fetch stocks
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=stocks_range,
        ).execute()
        rows = result.get("values", [])

        for row in rows:
            if len(row) >= 1:
                symbol = str(row[0]).strip().upper()
                name = str(row[1]).strip() if len(row) > 1 else symbol
                if symbol:
                    stocks.append(StockHolding(symbol=symbol, name=name))

    except HttpError as e:
        raise ValueError(f"Google Sheets API error: {e}") from e

    return stocks, last_updated
