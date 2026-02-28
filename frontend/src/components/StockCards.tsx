import type { StockHolding } from '../types'

interface Props {
  stocks: StockHolding[]
}

export default function StockCards({ stocks }: Props) {
  if (!stocks.length) return null

  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-4">Your Holdings</h2>
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
            <div className="mt-3 space-y-1 text-sm">
              <div className="flex justify-between text-slate-300">
                <span>Avg Price</span>
                <span className="font-mono">${s.avg_price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Qty</span>
                <span className="font-mono">{s.quantity}</span>
              </div>
              <div className="flex justify-between text-slate-200 font-medium pt-2 border-t border-slate-700">
                <span>Total Invested</span>
                <span className="font-mono text-accent-blue">${s.total_invested.toLocaleString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
