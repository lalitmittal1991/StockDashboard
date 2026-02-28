"""Google Gemini API service for summarization and analysis."""
import json
import asyncio
from functools import partial

import google.generativeai as genai

from app.core.config import get_settings


def _init_client():
    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        return None
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")


def _summarize_news_sync(symbol: str, articles_text: str) -> tuple[str, str]:
    """Synchronous call to Gemini for news summarization."""
    model = _init_client()
    if not model:
        return "Gemini API key not configured.", "N/A"

    prompt = f"""Summarize the following news articles about stock {symbol} for an investor.
Provide:
1. A concise 2-3 sentence executive summary of the key developments and their potential impact.
2. Overall sentiment: positive, negative, or neutral - with a brief reason.

News articles:
{articles_text}

Respond in this exact JSON format only, no other text:
{{"summary": "your summary here", "sentiment": "positive/negative/neutral", "sentiment_reason": "brief reason"}}"""

    try:
        response = model.generate_content(prompt)
        if response.text:
            data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            summary = data.get("summary", response.text)
            sentiment = data.get("sentiment", "N/A")
            reason = data.get("sentiment_reason", "")
            sentiment_overview = f"{sentiment}: {reason}" if reason else sentiment
            return summary, sentiment_overview
    except Exception as e:
        return f"Summarization failed: {str(e)}", "Error"
    return "No summary generated.", "N/A"


def _analyze_transcript_sync(transcript: str, watch_symbols: list[str], video_title: str) -> str:
    """Synchronous call to Gemini for transcript analysis."""
    model = _init_client()
    if not model:
        return "[]"

    symbols_str = ", ".join(sorted(watch_symbols))
    prompt = f"""Analyze this YouTube video transcript for stock recommendations. The investor watches these symbols: {symbols_str}.

Video title: {video_title}

Transcript:
{transcript[:15000]}

For each stock symbol mentioned that is in the watch list, extract:
- symbol: the ticker
- recommendation_type: one of "buy", "sell", "hold", or "mention"
- context: 1-2 sentences of relevant quote/context
- confidence: "high", "medium", or "low"

Respond with ONLY a JSON array, no other text. Example:
[{{"symbol": "AAPL", "recommendation_type": "buy", "context": "...", "confidence": "high"}}]
If no relevant recommendations, return: []"""

    try:
        response = model.generate_content(prompt)
        if response.text:
            text = response.text.strip().replace("```json", "").replace("```", "")
            return text
    except Exception:
        pass
    return "[]"


async def summarize_news(symbol: str, articles: list[dict]) -> tuple[str, str]:
    """Summarize news articles using Gemini (async)."""
    if not articles:
        return "No articles to summarize.", "N/A"

    articles_text = "\n\n".join(
        f"Title: {a.get('title', '')}\nDescription: {a.get('description', '')}"
        for a in articles[:10]
    )
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, partial(_summarize_news_sync, symbol, articles_text)
    )


async def analyze_transcript_for_stocks(
    transcript: str, watch_symbols: set[str], video_title: str
) -> list[dict]:
    """Analyze transcript for stock recommendations using Gemini (async)."""
    if not transcript or not watch_symbols:
        return []

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(_analyze_transcript_sync, transcript, list(watch_symbols), video_title),
    )
    try:
        data = json.loads(result)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
