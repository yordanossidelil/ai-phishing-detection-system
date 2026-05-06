import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Shield, ShieldAlert, ShieldX, Activity } from 'lucide-react'
import { getDashboard } from '../utils/api'
import { useLang } from '../hooks/useLang'
import clsx from 'clsx'

const BADGE = { phishing: 'badge-phishing', suspicious: 'badge-suspicious', legitimate: 'badge-legitimate' }

function StatCard({ icon, label, value, color }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={clsx('p-3 rounded-xl', color)}>{icon}</div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-sm text-gray-400">{label}</div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { t } = useLang()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard()
      .then(({ data }) => setData(data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
    </div>
  )

  if (!data) return <div className="text-center text-gray-400 py-20">{t('loadError') || 'Failed to load dashboard'}</div>

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold text-white">{t('dashboard')}</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Activity className="text-blue-400" size={22} />}
          label={t('totalAnalyzed')}
          value={data.total_analyzed}
          color="bg-blue-500/10"
        />
        <StatCard
          icon={<ShieldX className="text-red-400" size={22} />}
          label={t('phishingDetected')}
          value={`${data.phishing_count} (${data.phishing_percentage}%)`}
          color="bg-red-500/10"
        />
        <StatCard
          icon={<ShieldAlert className="text-yellow-400" size={22} />}
          label={t('suspicious')}
          value={data.suspicious_count}
          color="bg-yellow-500/10"
        />
        <StatCard
          icon={<Shield className="text-green-400" size={22} />}
          label={t('legitimate')}
          value={data.legitimate_count}
          color="bg-green-500/10"
        />
      </div>

      {/* Weekly Chart */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">{t('weeklyActivity')}</h2>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data.weekly_data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <XAxis dataKey="day" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#e5e7eb' }}
            />
            <Bar dataKey="total" name="Total" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="phishing" name="Phishing" fill="#ef4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">{t('recentActivity')}</h2>
        {data.recent_analyses.length === 0 ? (
          <p className="text-gray-500 text-sm">{t('noHistory')}</p>
        ) : (
          <div className="space-y-3">
            {data.recent_analyses.map((item) => (
              <div key={item.id} className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-300 truncate">{item.text_preview}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {new Date(item.analyzed_at).toLocaleString()} · {item.language}
                  </p>
                </div>
                <div className="ml-4 flex items-center gap-2 shrink-0">
                  <span className={BADGE[item.prediction]}>{item.prediction}</span>
                  <span className="text-sm text-gray-400">{item.confidence_percent}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
