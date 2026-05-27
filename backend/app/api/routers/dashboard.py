"""Dashboard routes - stocks and news."""
import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import UserInDB
from app.models.dashboard import (
    StockHolding,
    NewsSummary,
)
from app.services.google_sheets import fetch_sheet_data
from app.services.news_service import fetch_stock_news
from app.core.config import get_settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class SampleSheetFormat(BaseModel):
    """Sample Google Sheet format reference."""

    stocks_sheet: dict = {
        "sheet_name": "Stocks",
        "headers": ["Symbol", "Name"],
        "sample_rows": [
            ["AAPL", "Apple Inc"],
            ["MSFT", "Microsoft Corporation"],
            ["GOOGL", "Alphabet Inc"],
        ],
        "range": "Stocks!A2:B",
        "notes": "Symbol: Stock ticker. Name: Company name.",
    }
    spreadsheet_url_example: str = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
    spreadsheet_id_help: str = "Copy the ID from the URL: docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit"


@router.get("/sample-sheet-format", response_model=SampleSheetFormat)
async def get_sample_sheet_format(
    current_user: UserInDB = Depends(get_current_user),
):
    """Get sample Google Sheet format reference for setup."""
    return SampleSheetFormat()


class SheetRequest(BaseModel):
    spreadsheet_id: str
    stocks_range: str = "Stocks!A2:B"


class DashboardResponse(BaseModel):
    stocks: list[StockHolding]
    last_updated: str
    news: dict[str, NewsSummary]


@router.post("/fetch", response_model=DashboardResponse)
async def fetch_dashboard(
    request: SheetRequest,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Fetch dashboard data from Google Sheet and news APIs.
    """
    settings = get_settings()
    try:
        stocks, last_updated = await fetch_sheet_data(
            spreadsheet_id=request.spreadsheet_id,
            credentials_path=settings.GOOGLE_SHEETS_CREDENTIALS_PATH,
            credentials_json=settings.GOOGLE_SHEETS_CREDENTIALS_JSON,
            stocks_range=request.stocks_range,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    news_map: dict[str, NewsSummary] = {}
    # Fetch news sequentially with throttling to reduce API rate-limit issues.
    for i, stock in enumerate(stocks):
        try:
            result = await fetch_stock_news(
                symbol=stock.symbol,
                api_key=settings.GNEWS_API_KEY,
                days_back=7,
                max_articles=2,
            )
            news_map[stock.symbol] = result
        except Exception as e:
            news_map[stock.symbol] = NewsSummary(
                symbol=stock.symbol,
                articles=[],
                summary=f"Error: {str(e)}",
                sentiment_overview="Error",
                fetched_at=datetime.utcnow(),
            )
        if i < len(stocks) - 1:
            await asyncio.sleep(1.0)

    return DashboardResponse(
        stocks=stocks,
        last_updated=last_updated.isoformat(),
        news=news_map,
    )
