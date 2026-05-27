import type { NewsSummary } from '../types'

interface Props {
  news: Record<string, NewsSummary>
}

function buildPortfolioSummary(news: Record<string, NewsSummary>) {
  const negativePointers: string[] = []

  for (const [symbol, summary] of Object.entries(news)) {
    const sentiment = summary.sentiment_overview.toLowerCase()
    if (sentiment.includes('negative') || sentiment.includes('error')) {
      const point = summary.summary
        .replace(/\s+/g, ' ')
        .trim()
        .slice(0, 180)
      negativePointers.push(`${symbol}: ${point}${summary.summary.length > 180 ? '...' : ''}`)
    }
  }

  return {
    negativePointers,
  }
}

export default function NewsSection({ news }: Props) {
  const entries = Object.entries(news)
  if (!entries.length) return null
  const summary = buildPortfolioSummary(news)

  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-4">Top Negative News Summary</h2>
      <div className="rounded-xl bg-red-500/10 border border-red-500/30 p-4 mb-8">
        {summary.negativePointers.length ? (
          <ul className="space-y-2 text-sm text-red-100 list-disc pl-5">
            {summary.negativePointers.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-red-100">No major negative signals detected across tracked stocks.</p>
        )}
      </div>

      <h2 className="text-lg font-semibold text-white mb-4">News Summary (Last 7 Days)</h2>
      <div className="space-y-6">
        {entries.map(([symbol, summary]) => (
          <div
            key={symbol}
            className="rounded-xl bg-surface-800 border border-slate-700/50 overflow-hidden"
          >
            <div className="px-4 py-3 bg-slate-800/50 border-b border-slate-700">
              <span className="font-mono font-bold text-accent-blue">{symbol}</span>
              <span className="text-slate-400 text-sm ml-2">
                — {summary.articles.length} articles
              </span>
            </div>
            <div className="p-4">
              <div className="text-slate-300 text-sm whitespace-pre-wrap mb-4">
                {summary.summary}
              </div>
              {summary.articles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Articles
                  </p>
                  {summary.articles.slice(0, 5).map((a, i) => (
                    <a
                      key={i}
                      href={a.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-3 rounded-lg bg-surface-900 hover:bg-slate-800 transition text-sm"
                    >
                      <span className="text-white font-medium line-clamp-2">{a.title}</span>
                      <span className="text-slate-400 text-xs block mt-1">
                        {a.source} • {a.published_at ? new Date(a.published_at).toLocaleDateString() : ''}
                      </span>
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
