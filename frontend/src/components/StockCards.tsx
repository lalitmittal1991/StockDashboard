import type { StockHolding } from '../types'

interface Props {
  stocks: StockHolding[]
}

export default function StockCards({ stocks }: Props) {
  if (!stocks.length) return null

  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-4">Tracked Stocks</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stocks.map((s) => (
          <div
            key={s.symbol}
            className="p-4 rounded-xl bg-surface-800 border border-slate-700/50 hover:border-slate-600 transition"
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono font-bold text-lg text-white">{s.symbol}</span>
                <p className="text-sm text-slate-400 truncate max-w-[180px]">{s.name}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
