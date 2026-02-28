import type { NewsSummary } from '../types'

interface Props {
  news: Record<string, NewsSummary>
}

export default function NewsSection({ news }: Props) {
  const entries = Object.entries(news)
  if (!entries.length) return null

  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-4">News Summary (Last 14 Days)</h2>
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
