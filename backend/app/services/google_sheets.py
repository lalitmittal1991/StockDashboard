"""Google Sheets service for fetching stock and YouTube channel data."""
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models.dashboard import StockHolding, YouTubeChannel, SheetConfig

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
    stocks_range: str = "Stocks!A2:E",
    youtube_range: str = "YouTube!A2:B",
) -> tuple[list[StockHolding], list[YouTubeChannel], datetime]:
    """
    Fetch stocks and YouTube channels from Google Sheet.

    Expected Stocks sheet format:
    | Symbol | Name | Avg Price | Qty | (optional columns) |
    | AAPL   | Apple Inc | 150.5 | 10 |

    Expected YouTube sheet format:
    | Channel Name | Channel ID/URL |
    | @channelname | UCxxxxxx or https://youtube.com/@channel |
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
    youtube_channels: list[YouTubeChannel] = []
    last_updated = datetime.utcnow()

    try:
        # Fetch stocks
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=stocks_range,
        ).execute()
        rows = result.get("values", [])

        for row in rows:
            if len(row) >= 4:
                try:
                    symbol = str(row[0]).strip().upper()
                    name = str(row[1]).strip() if len(row) > 1 else symbol
                    avg_price = float(str(row[2]).replace(",", "").strip())
                    qty = int(float(str(row[3]).replace(",", "").strip()))
                    if symbol and qty > 0:
                        stocks.append(
                            StockHolding(
                                symbol=symbol,
                                name=name,
                                avg_price=avg_price,
                                quantity=qty,
                                total_invested=round(avg_price * qty, 2),
                            )
                        )
                except (ValueError, TypeError):
                    continue

        # Fetch YouTube channels
        yt_result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=youtube_range,
        ).execute()
        yt_rows = yt_result.get("values", [])

        for row in yt_rows:
            if len(row) >= 1:
                channel_name = str(row[0]).strip()
                channel_id = str(row[1]).strip() if len(row) > 1 else None
                if channel_name:
                    youtube_channels.append(
                        YouTubeChannel(
                            channel_name=channel_name,
                            channel_id=channel_id,
                            channel_url=channel_id if channel_id and channel_id.startswith("http") else None,
                        )
                    )

    except HttpError as e:
        raise ValueError(f"Google Sheets API error: {e}") from e

    return stocks, youtube_channels, last_updated
