export interface StockHolding {
  symbol: string;
  name: string;
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

export interface DashboardData {
  stocks: StockHolding[];
  last_updated: string;
  news: Record<string, NewsSummary>;
}

export interface SampleSheetFormat {
  stocks_sheet: {
    sheet_name: string;
    headers: string[];
    sample_rows: (string | number)[][];
    range: string;
    notes: string;
  };
  spreadsheet_url_example: string;
  spreadsheet_id_help: string;
}
