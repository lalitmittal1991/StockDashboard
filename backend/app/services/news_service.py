"""News service for fetching and summarizing stock news."""
from datetime import datetime, timedelta
import httpx
from app.models.dashboard import NewsArticle, NewsSummary

# GNews API - https://gnews.io/
GNEWS_BASE = "https://gnews.io/api/v4"


async def fetch_stock_news(
    symbol: str,
    api_key: str,
    days_back: int = 14,
    max_articles: int = 10,
) -> NewsSummary:
    """
    Fetch news for a stock symbol from the last N days.
    Uses GNews API - get free key at https://gnews.io/
    """
    if not api_key:
        return NewsSummary(
            symbol=symbol,
            articles=[],
            summary="News API key not configured. Add GNEWS_API_KEY to environment.",
            sentiment_overview="N/A",
            fetched_at=datetime.utcnow(),
        )

    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                f"{GNEWS_BASE}/search",
                params={
                    "q": symbol,
                    "token": api_key,
                    "lang": "en",
                    "max": max_articles,
                    "from": from_date,
                    "sortby": "publishedAt",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            return NewsSummary(
                symbol=symbol,
                articles=[],
                summary=f"Failed to fetch news: {str(e)}",
                sentiment_overview="Error",
                fetched_at=datetime.utcnow(),
            )

    articles = []
    for item in data.get("articles", [])[:max_articles]:
        articles.append(
            NewsArticle(
                title=item.get("title", ""),
                description=item.get("description", ""),
                url=item.get("url", ""),
                published_at=item.get("publishedAt", ""),
                source=item.get("source", {}).get("name", "Unknown"),
                sentiment=None,
            )
        )

    # Simple summary from titles and descriptions
    summary_parts = []
    for a in articles[:5]:
        summary_parts.append(f"- {a.title}")
    summary = "\n".join(summary_parts) if summary_parts else "No recent news found."

    return NewsSummary(
        symbol=symbol,
        articles=articles,
        summary=summary,
        sentiment_overview="Review articles for sentiment.",
        fetched_at=datetime.utcnow(),
    )
