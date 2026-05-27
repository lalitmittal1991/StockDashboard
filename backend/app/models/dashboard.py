"""Dashboard data models."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StockHolding(BaseModel):
    """Stock from Google Sheet."""
    symbol: str
    name: str


class SheetConfig(BaseModel):
    """Configuration for Google Sheet."""
    spreadsheet_id: str
    stocks_range: str = "Stocks!A2:B"
    last_updated: Optional[datetime] = None


class NewsArticle(BaseModel):
    """Single news article."""
    title: str
    description: str
    url: str
    published_at: str
    source: str
    sentiment: Optional[str] = None


class NewsSummary(BaseModel):
    """News summary for a stock."""
    symbol: str
    articles: list[NewsArticle]
    summary: str
    sentiment_overview: str
    fetched_at: datetime

