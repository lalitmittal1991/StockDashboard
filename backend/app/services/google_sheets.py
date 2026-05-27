"""Google Sheets service for fetching stock data.

Hybrid mode:
- If service-account credentials are available, use Google Sheets API.
- Otherwise (or on API access failure), fall back to public CSV sheet fetch.
"""
import json
import base64
import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

import httpx
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


def _parse_stock_rows(rows: list[list[str]]) -> list[StockHolding]:
    stocks: list[StockHolding] = []
    for row in rows:
        if len(row) >= 1:
            symbol = str(row[0]).strip().upper()
            name = str(row[1]).strip() if len(row) > 1 else symbol
            if symbol and symbol not in {"SYMBOL"}:
                stocks.append(StockHolding(symbol=symbol, name=name))
    return stocks


def _extract_sheet_name(stocks_range: str) -> str:
    if "!" in stocks_range:
        return stocks_range.split("!", 1)[0].strip("'")
    return "Stocks"


def _fetch_stocks_with_service_account(
    spreadsheet_id: str,
    creds: Credentials,
    stocks_range: str,
) -> list[StockHolding]:
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=stocks_range,
    ).execute()
    rows = result.get("values", [])
    return _parse_stock_rows(rows)


async def _fetch_stocks_from_public_sheet(
    spreadsheet_id: str,
    stocks_range: str,
) -> list[StockHolding]:
    sheet_name = _extract_sheet_name(stocks_range)
    # Public CSV export for a tab by name. Sheet must be publicly readable.
    csv_url = (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq"
        f"?tqx=out:csv&sheet={sheet_name}"
    )
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(csv_url)
        resp.raise_for_status()
        text = resp.text
    reader = csv.reader(StringIO(text))
    rows = list(reader)
    # Skip header row when reading full tab CSV.
    if rows:
        rows = rows[1:]
    return _parse_stock_rows(rows)


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
    last_updated = datetime.utcnow()

    # Try authenticated Sheets API first if credentials are present.
    if creds:
        try:
            stocks = _fetch_stocks_with_service_account(spreadsheet_id, creds, stocks_range)
            if stocks:
                return stocks, last_updated
        except HttpError:
            # Fallback to public CSV mode below.
            pass

    # Fallback mode: read publicly accessible sheet by Sheet ID only.
    try:
        stocks = await _fetch_stocks_from_public_sheet(spreadsheet_id, stocks_range)
    except httpx.HTTPError as e:
        raise ValueError(
            "Could not read sheet. Either share it with your service account "
            "or make the sheet publicly readable and pass a valid sheet ID."
        ) from e

    if not stocks:
        raise ValueError(
            "No stocks found. Ensure tab name/range is correct and the sheet has rows in Stocks tab."
        )
    return stocks, last_updated
