"""Dashboard routes - stocks, news, YouTube."""
import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import UserInDB
from app.models.dashboard import (
    StockHolding,
    YouTubeChannel,
    NewsSummary,
    YouTubeRecommendation,
)
from app.services.google_sheets import fetch_sheet_data
from app.services.news_service import fetch_stock_news
from app.services.youtube_service import analyze_channel_for_stocks
from app.core.config import get_settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class SampleSheetFormat(BaseModel):
    """Sample Google Sheet format reference."""

    stocks_sheet: dict = {
        "sheet_name": "Stocks",
        "headers": ["Symbol", "Name", "Avg Price", "Qty"],
        "sample_rows": [
            ["AAPL", "Apple Inc", 175.50, 10],
            ["MSFT", "Microsoft Corporation", 380.25, 5],
            ["GOOGL", "Alphabet Inc", 140.00, 8],
        ],
        "range": "Stocks!A2:E",
        "notes": "Symbol: Stock ticker. Name: Company name. Avg Price: Average buy price. Qty: Quantity held.",
    }
    youtube_sheet: dict = {
        "sheet_name": "YouTube",
        "headers": ["Channel Name", "Channel ID or Handle"],
        "sample_rows": [
            ["@FinancialEducation", "UCnMn36GT_H0d-wsO-2O-ptQ"],
            ["@GrahamStephan", "UCV6KDgJskWaEckne5aPA0aQ"],
            ["@ThePlainBagel", "UCvJJ_dzjViJCoLf5uKUTwoA"],
        ],
        "range": "YouTube!A2:B",
        "notes": "Channel Name: Display name. Channel ID: YouTube channel ID (UC...) or @handle for lookup.",
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
    stocks_range: str = "Stocks!A2:E"
    youtube_range: str = "YouTube!A2:B"


class DashboardResponse(BaseModel):
    stocks: list[StockHolding]
    youtube_channels: list[YouTubeChannel]
    last_updated: str
    news: dict[str, NewsSummary]
    youtube_recommendations: list[YouTubeRecommendation]


@router.post("/fetch", response_model=DashboardResponse)
async def fetch_dashboard(
    request: SheetRequest,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Fetch full dashboard data from Google Sheet, news, and YouTube.
    """
    settings = get_settings()
    try:
        stocks, youtube_channels, last_updated = await fetch_sheet_data(
            spreadsheet_id=request.spreadsheet_id,
            credentials_path=settings.GOOGLE_SHEETS_CREDENTIALS_PATH,
            credentials_json=settings.GOOGLE_SHEETS_CREDENTIALS_JSON,
            stocks_range=request.stocks_range,
            youtube_range=request.youtube_range,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    watch_symbols = {s.symbol for s in stocks}

    # Fetch news for each stock in parallel
    news_tasks = [
        fetch_stock_news(symbol=s.symbol, api_key=settings.GNEWS_API_KEY, days_back=14)
        for s in stocks
    ]
    news_results = await asyncio.gather(*news_tasks, return_exceptions=True)
    news_map: dict[str, NewsSummary] = {}
    for stock, result in zip(stocks, news_results):
        if isinstance(result, Exception):
            news_map[stock.symbol] = NewsSummary(
                symbol=stock.symbol,
                articles=[],
                summary=f"Error: {str(result)}",
                sentiment_overview="Error",
                fetched_at=datetime.utcnow(),
            )
        else:
            news_map[stock.symbol] = result

    # Analyze YouTube channels for stock recommendations
    youtube_recs: list[YouTubeRecommendation] = []
    for ch in youtube_channels:
        recs = await analyze_channel_for_stocks(
            api_key=settings.YOUTUBE_API_KEY,
            channel_name=ch.channel_name,
            channel_id=ch.channel_id,
            watch_symbols=watch_symbols,
            max_videos=5,
            days_back=14,
        )
        youtube_recs.extend(recs)

    return DashboardResponse(
        stocks=stocks,
        youtube_channels=youtube_channels,
        last_updated=last_updated.isoformat(),
        news=news_map,
        youtube_recommendations=youtube_recs,
    )
