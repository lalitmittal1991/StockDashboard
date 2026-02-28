"""YouTube service for fetching channel videos and analyzing transcripts."""
from datetime import datetime, timedelta
import re
import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app.models.dashboard import YouTubeVideo, YouTubeRecommendation


# Keywords that suggest stock recommendations
RECOMMENDATION_KEYWORDS = {
    "buy": ["buy", "bullish", "accumulate", "strong buy", "outperform", "undervalued"],
    "sell": ["sell", "bearish", "avoid", "reduce", "overvalued", "underperform"],
    "hold": ["hold", "neutral", "wait", "watch"],
    "mention": ["stock", "share", "ticker", "invest", "investment", "earnings"],
}

# Common stock ticker pattern (1-5 uppercase letters)
TICKER_PATTERN = re.compile(r"\b([A-Z]{1,5})\b")


async def get_channel_id_from_name(api_key: str, channel_name: str) -> str | None:
    """Resolve channel name/URL to channel ID using YouTube Data API."""
    if not api_key:
        return None

    # Extract @handle or channel ID from input
    handle = channel_name.strip()
    if handle.startswith("UC") and len(handle) == 24:
        return handle  # Already a channel ID
    if "youtube.com" in handle or "youtu.be" in handle:
        # Could parse URL - for now require channel ID
        pass

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # Search for channel by handle
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "id",
                    "forHandle": handle.lstrip("@") if handle.startswith("@") else handle,
                    "key": api_key,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    return items[0]["id"]
        except Exception:
            pass
    return None


async def get_channel_videos(
    api_key: str,
    channel_id: str,
    channel_name: str,
    max_videos: int = 5,
    days_back: int = 14,
) -> list[YouTubeVideo]:
    """Get latest videos from a YouTube channel."""
    if not api_key:
        return []

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # Get uploads playlist ID
            ch_resp = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "contentDetails",
                    "id": channel_id,
                    "key": api_key,
                },
            )
            if ch_resp.status_code != 200:
                return []
            ch_data = ch_resp.json()
            items = ch_data.get("items", [])
            if not items:
                return []
            uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # Get playlist items
            pl_resp = await client.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": uploads_id,
                    "maxResults": max_videos,
                    "key": api_key,
                },
            )
            if pl_resp.status_code != 200:
                return []
            pl_data = pl_resp.json()

            cutoff = datetime.utcnow() - timedelta(days=days_back)
            videos = []
            for item in pl_data.get("items", []):
                sn = item.get("snippet", {})
                pub = sn.get("publishedAt", "")
                try:
                    pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                    if pub_dt.replace(tzinfo=None) < cutoff:
                        continue
                except Exception:
                    pass
                vid = sn.get("resourceId", {}).get("videoId")
                if vid:
                    videos.append(
                        YouTubeVideo(
                            video_id=vid,
                            title=sn.get("title", ""),
                            channel_name=channel_name,
                            published_at=pub,
                            url=f"https://www.youtube.com/watch?v={vid}",
                        )
                    )
            return videos
        except Exception:
            return []


def fetch_transcript(video_id: str) -> str:
    """Fetch transcript for a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except (TranscriptsDisabled, NoTranscriptFound, Exception):
        return ""


def extract_stock_recommendations(
    transcript: str,
    video: YouTubeVideo,
    watch_symbols: set[str],
) -> list[YouTubeRecommendation]:
    """
    Extract potential stock recommendations from transcript.
    Uses keyword matching and ticker detection - can be enhanced with LLM.
    """
    transcript_lower = transcript.lower()
    recommendations = []

    for symbol in watch_symbols:
        sym_lower = symbol.lower()
        if sym_lower not in transcript_lower:
            continue

        # Find context around symbol
        idx = transcript_lower.find(sym_lower)
        start = max(0, idx - 100)
        end = min(len(transcript), idx + len(symbol) + 100)
        context = transcript[start:end]

        rec_type = "mention"
        confidence = "low"
        for rec_type_key, keywords in RECOMMENDATION_KEYWORDS.items():
            for kw in keywords:
                if kw in context.lower():
                    rec_type = rec_type_key
                    confidence = "medium" if rec_type in ("buy", "sell") else "low"
                    break

        recommendations.append(
            YouTubeRecommendation(
                symbol=symbol,
                recommendation_type=rec_type,
                context=context[:200] + "..." if len(context) > 200 else context,
                confidence=confidence,
                video=video,
                extracted_at=datetime.utcnow(),
            )
        )

    return recommendations


async def analyze_channel_for_stocks(
    api_key: str,
    channel_name: str,
    channel_id: str | None,
    watch_symbols: set[str],
    max_videos: int = 5,
    days_back: int = 14,
) -> list[YouTubeRecommendation]:
    """
    Get channel videos, fetch transcripts, and extract stock recommendations.
    """
    cid = channel_id
    # Resolve to channel ID: UC... is direct ID; @handle or handle needs API lookup
    if cid and cid.startswith("UC") and len(cid) == 24:
        pass  # Already valid channel ID
    elif api_key:
        cid = await get_channel_id_from_name(
            api_key, channel_id if channel_id else channel_name
        )
    if not cid:
        return []

    videos = await get_channel_videos(api_key, cid, channel_name, max_videos, days_back)
    all_recs = []
    for v in videos:
        transcript = fetch_transcript(v.video_id)
        if transcript:
            v.transcript_preview = transcript[:300] + "..." if len(transcript) > 300 else transcript
            recs = extract_stock_recommendations(transcript, v, watch_symbols)
            all_recs.extend(recs)
    return all_recs
