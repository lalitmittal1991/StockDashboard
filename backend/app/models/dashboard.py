"""Dashboard data models."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StockHolding(BaseModel):
    """Stock from Google Sheet."""
    symbol: str
    name: str
    avg_price: float
    quantity: int
    total_invested: float


class YouTubeChannel(BaseModel):
    """YouTube channel from Google Sheet."""
    channel_name: str
    channel_id: Optional[str] = None
    channel_url: Optional[str] = None


class SheetConfig(BaseModel):
    """Configuration for Google Sheet."""
    spreadsheet_id: str
    stocks_range: str = "Stocks!A2:E"
    youtube_range: str = "YouTube!A2:B"
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


class YouTubeVideo(BaseModel):
    """YouTube video with transcript analysis."""
    video_id: str
    title: str
    channel_name: str
    published_at: str
    url: str
    transcript_preview: Optional[str] = None


class YouTubeRecommendation(BaseModel):
    """Stock recommendation extracted from YouTube."""
    symbol: str
    recommendation_type: str  # buy, sell, hold, mention
    context: str
    confidence: str  # high, medium, low
    video: YouTubeVideo
    extracted_at: datetime
