import { useState } from 'react'
import { fetchDashboard, getSampleSheetFormat } from '../api/client'
import type { DashboardData, SampleSheetFormat } from '../types'
import NewsSection from '../components/NewsSection'
import SampleSheetModal from '../components/SampleSheetModal'

export default function DashboardPage() {
  const [spreadsheetId, setSpreadsheetId] = useState('')
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [sampleFormat, setSampleFormat] = useState<SampleSheetFormat | null>(null)
  const [showSampleModal, setShowSampleModal] = useState(false)

  const loadSampleFormat = async () => {
    try {
      const fmt = await getSampleSheetFormat()
      setSampleFormat(fmt)
      setShowSampleModal(true)
    } catch {
      setError('Failed to load sample format')
    }
  }

  const loadDashboard = async () => {
    if (!spreadsheetId.trim()) {
      setError('Please enter a Google Sheet ID')
      return
    }
    setLoading(true)
    setError('')
    try {
      const result = await fetchDashboard(spreadsheetId.trim())
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface-900">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-surface-900/95 backdrop-blur border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-white">Stock News Dashboard</h1>
              <p className="text-sm text-slate-400">
                {data?.last_updated
                  ? `List updated: ${new Date(data.last_updated).toLocaleString()}`
                  : 'Enter your Google Sheet ID to load'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={loadSampleFormat}
                className="text-sm px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 transition"
              >
                Sample Sheet Format
              </button>
            </div>
          </div>

          {/* Sheet ID input */}
          <div className="mt-4 flex flex-wrap gap-3">
            <input
              type="text"
              value={spreadsheetId}
              onChange={(e) => setSpreadsheetId(e.target.value)}
              placeholder="Google Sheet ID (from URL)"
              className="flex-1 min-w-[200px] px-4 py-2 rounded-lg bg-surface-800 border border-slate-600 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <button
              onClick={loadDashboard}
              disabled={loading}
              className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium disabled:opacity-50 transition"
            >
              {loading ? 'Loading...' : 'Fetch Dashboard'}
            </button>
          </div>
          {error && (
            <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!data ? (
          <div className="text-center py-16 text-slate-400">
            <p className="text-lg">Enter your Google Sheet ID and click Fetch Dashboard</p>
            <p className="mt-2 text-sm">
              Click &quot;Sample Sheet Format&quot; to see the expected structure
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            <NewsSection news={data.news} />
          </div>
        )}
      </main>

      {sampleFormat && (
        <SampleSheetModal
          format={sampleFormat}
          onClose={() => setShowSampleModal(false)}
          isOpen={showSampleModal}
        />
      )}
    </div>
  )
}
