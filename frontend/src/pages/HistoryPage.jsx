import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { getHistory } from '../utils/api'
import { useLang } from '../hooks/useLang'

const BADGE = { phishing: 'badge-phishing', suspicious: 'badge-suspicious', legitimate: 'badge-legitimate' }

export default function HistoryPage() {
  const { t } = useLang()
  const [data, setData] = useState({ items: [], total: 0, page: 1, limit: 20 })
  const [loading, setLoading] = useState(true)

  const loadPage = (page) => {
    setLoading(true)
    getHistory(page, 20)
      .then(({ data }) => setData(data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadPage(1) }, [])

  const totalPages = Math.ceil(data.total / data.limit)

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">{t('history')}</h1>
        <div className="text-sm text-gray-400">
          {data.total} {data.total === 1 ? t('result') : t('results')}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
        </div>
      ) : data.items.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">{t('noHistory')}</div>
      ) : (
        <>
          <div className="space-y-3">
            {data.items.map((item) => (
              <div key={item.id} className="card hover:border-gray-700 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-200 text-sm mb-2 leading-relaxed">{item.text_preview}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span>{new Date(item.analyzed_at).toLocaleString()}</span>
                      <span>·</span>
                      <span className="capitalize">{item.language}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 shrink-0">
                    <span className={BADGE[item.prediction]}>{item.prediction.toUpperCase()}</span>
                    <span className="text-lg font-bold text-white">{item.confidence_percent}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => loadPage(data.page - 1)}
                disabled={data.page === 1}
                className="btn-secondary disabled:opacity-30"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-sm text-gray-400">
                Page {data.page} of {totalPages}
              </span>
              <button
                onClick={() => loadPage(data.page + 1)}
                disabled={data.page >= totalPages}
                className="btn-secondary disabled:opacity-30"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
