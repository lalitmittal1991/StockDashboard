import type { NewsSummary } from '../types'

interface Props {
  news: Record<string, NewsSummary>
}

function buildPortfolioSummary(news: Record<string, NewsSummary>) {
  const positives: string[] = []
  const negatives: string[] = []
  const risky: string[] = []
  const riskTerms = [
    'risk', 'volatile', 'volatility', 'lawsuit', 'investigation',
    'downgrade', 'fraud', 'debt', 'default', 'warning', 'cut guidance',
  ]

  for (const [symbol, summary] of Object.entries(news)) {
    const sentiment = summary.sentiment_overview.toLowerCase()
    const text = `${summary.sentiment_overview} ${summary.summary}`.toLowerCase()

    if (sentiment.includes('positive')) positives.push(symbol)
    if (sentiment.includes('negative') || sentiment.includes('error')) negatives.push(symbol)
    if (riskTerms.some((term) => text.includes(term))) risky.push(symbol)
  }

  return {
    positives: [...new Set(positives)],
    negatives: [...new Set(negatives)],
    risky: [...new Set(risky)],
  }
}

export default function NewsSection({ news }: Props) {
  const entries = Object.entries(news)
  if (!entries.length) return null
  const summary = buildPortfolioSummary(news)

  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-4">Portfolio Summary</h2>
      <div className="grid gap-4 sm:grid-cols-3 mb-8">
        <div className="rounded-xl bg-green-500/10 border border-green-500/30 p-4">
          <p className="text-xs uppercase tracking-wider text-green-300">Positives</p>
          <p className="text-sm text-green-100 mt-2">
            {summary.positives.length ? summary.positives.join(', ') : 'No strong positive signals detected'}
          </p>
        </div>
        <div className="rounded-xl bg-red-500/10 border border-red-500/30 p-4">
          <p className="text-xs uppercase tracking-wider text-red-300">Negatives</p>
          <p className="text-sm text-red-100 mt-2">
            {summary.negatives.length ? summary.negatives.join(', ') : 'No major negative signals detected'}
          </p>
        </div>
        <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-4">
          <p className="text-xs uppercase tracking-wider text-amber-300">Risky</p>
          <p className="text-sm text-amber-100 mt-2">
            {summary.risky.length ? summary.risky.join(', ') : 'No elevated risk signals detected'}
          </p>
        </div>
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
                  {summary.articles.slice(0, 2).map((a, i) => (
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
