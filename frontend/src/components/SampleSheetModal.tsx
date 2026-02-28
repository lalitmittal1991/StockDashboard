import type { SampleSheetFormat } from '../types'

interface Props {
  format: SampleSheetFormat
  isOpen: boolean
  onClose: () => void
}

export default function SampleSheetModal({ format, isOpen, onClose }: Props) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-800 rounded-2xl border border-slate-600 shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-surface-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-white">Google Sheet Input Format</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            ✕
          </button>
        </div>
        <div className="p-6 space-y-6">
          <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-200 text-sm">
            <p className="font-medium mb-1">Quick start</p>
            <p>Create a new sheet at <a href="https://sheets.new" target="_blank" rel="noopener noreferrer" className="underline">sheets.new</a>, add two tabs named &quot;Stocks&quot; and &quot;YouTube&quot;, then copy the format below. Sample CSV files are in the <code className="bg-slate-700 px-1 rounded">sample-sheet/</code> folder of this project.</p>
          </div>
          <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-200 text-sm">
            <p className="font-medium mb-1">Spreadsheet ID</p>
            <p>{format.spreadsheet_id_help}</p>
            <p className="mt-2 text-slate-400">{format.spreadsheet_url_example}</p>
          </div>

          <div>
            <h3 className="font-semibold text-white mb-2">{format.stocks_sheet.sheet_name}</h3>
            <p className="text-slate-400 text-sm mb-3">{format.stocks_sheet.notes}</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr>
                    {format.stocks_sheet.headers.map((h) => (
                      <th
                        key={h}
                        className="border border-slate-600 bg-slate-700/50 px-3 py-2 text-left text-slate-200"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {format.stocks_sheet.sample_rows.map((row, i) => (
                    <tr key={i}>
                      {row.map((cell, j) => (
                        <td
                          key={j}
                          className="border border-slate-600 px-3 py-2 text-slate-300 font-mono"
                        >
                          {String(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-slate-500 text-xs mt-2">Range: {format.stocks_sheet.range}</p>
          </div>

          <div>
            <h3 className="font-semibold text-white mb-2">{format.youtube_sheet.sheet_name}</h3>
            <p className="text-slate-400 text-sm mb-3">{format.youtube_sheet.notes}</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr>
                    {format.youtube_sheet.headers.map((h) => (
                      <th
                        key={h}
                        className="border border-slate-600 bg-slate-700/50 px-3 py-2 text-left text-slate-200"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {format.youtube_sheet.sample_rows.map((row, i) => (
                    <tr key={i}>
                      {row.map((cell, j) => (
                        <td
                          key={j}
                          className="border border-slate-600 px-3 py-2 text-slate-300 font-mono text-xs"
                        >
                          {String(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-slate-500 text-xs mt-2">Range: {format.youtube_sheet.range}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
