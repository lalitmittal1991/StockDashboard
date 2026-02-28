export interface StockHolding {
  symbol: string;
  name: string;
  avg_price: number;
  quantity: number;
  total_invested: number;
}

export interface YouTubeChannel {
  channel_name: string;
  channel_id?: string;
  channel_url?: string;
}

export interface NewsArticle {
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
  sentiment?: string;
}

export interface NewsSummary {
  symbol: string;
  articles: NewsArticle[];
  summary: string;
  sentiment_overview: string;
  fetched_at: string;
}

export interface YouTubeVideo {
  video_id: string;
  title: string;
  channel_name: string;
  published_at: string;
  url: string;
  transcript_preview?: string;
}

export interface YouTubeRecommendation {
  symbol: string;
  recommendation_type: string;
  context: string;
  confidence: string;
  video: YouTubeVideo;
  extracted_at: string;
}

export interface DashboardData {
  stocks: StockHolding[];
  youtube_channels: YouTubeChannel[];
  last_updated: string;
  news: Record<string, NewsSummary>;
  youtube_recommendations: YouTubeRecommendation[];
}

export interface SampleSheetFormat {
  stocks_sheet: {
    sheet_name: string;
    headers: string[];
    sample_rows: (string | number)[][];
    range: string;
    notes: string;
  };
  youtube_sheet: {
    sheet_name: string;
    headers: string[];
    sample_rows: (string | number)[][];
    range: string;
    notes: string;
  };
  spreadsheet_url_example: string;
  spreadsheet_id_help: string;
}
