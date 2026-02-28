import type { YouTubeChannel, YouTubeRecommendation } from '../types'

interface Props {
  channels: YouTubeChannel[]
  recommendations: YouTubeRecommendation[]
}

const recTypeColors: Record<string, string> = {
  buy: 'bg-green-500/20 text-green-400 border-green-500/40',
  sell: 'bg-red-500/20 text-red-400 border-red-500/40',
  hold: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
  mention: 'bg-slate-500/20 text-slate-400 border-slate-500/40',
}

export default function YouTubeSection({ channels, recommendations }: Props) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-4">YouTube Analysis</h2>

      {channels.length > 0 && (
        <div className="mb-6">
          <p className="text-sm text-slate-400 mb-2">Watching channels:</p>
          <div className="flex flex-wrap gap-2">
            {channels.map((ch) => (
              <span
                key={ch.channel_name}
                className="px-3 py-1 rounded-full bg-slate-700 text-slate-300 text-sm"
              >
                {ch.channel_name}
              </span>
            ))}
          </div>
        </div>
      )}

      {recommendations.length === 0 ? (
        <div className="rounded-xl bg-surface-800 border border-slate-700/50 p-6 text-center text-slate-400">
          <p>No stock recommendations found in recent videos (last 14 days)</p>
          <p className="text-sm mt-2">
            Add YouTube channel names/IDs in your sheet to analyze transcripts
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec, i) => (
            <div
              key={i}
              className="p-4 rounded-xl bg-surface-800 border border-slate-700/50"
            >
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="font-mono font-bold text-accent-blue">{rec.symbol}</span>
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium border ${
                    recTypeColors[rec.recommendation_type] || recTypeColors.mention
                  }`}
                >
                  {rec.recommendation_type}
                </span>
                <span className="text-slate-500 text-xs">({rec.confidence})</span>
              </div>
              <p className="text-slate-300 text-sm mb-3 line-clamp-2">{rec.context}</p>
              <a
                href={rec.video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-accent-blue hover:underline"
              >
                {rec.video.title} — {rec.video.channel_name}
              </a>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
