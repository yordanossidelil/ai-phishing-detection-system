import { useState } from 'react'
import { Settings, RefreshCw, CheckCircle } from 'lucide-react'
import { retrainModel } from '../utils/api'
import { useAuth } from '../hooks/useAuth'
import { useLang } from '../hooks/useLang'
import { useNavigate, Navigate } from 'react-router-dom'

export default function AdminPage() {
  const { user } = useAuth()
  const { t } = useLang()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [modelType, setModelType] = useState('logistic')

  if (!user || user.role !== 'admin') return <Navigate to="/" replace />

  const handleRetrain = async () => {
    setLoading(true)
    setError('')
    setSuccess(false)
    try {
      await retrainModel(modelType)
      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Retraining failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center gap-3">
        <Settings className="text-blue-400" size={28} />
        <h1 className="text-2xl font-bold text-white">{t('adminPanel')}</h1>
      </div>

      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-gray-200">Model Management</h2>

        <div>
          <label className="block text-sm text-gray-400 mb-2">Model Type</label>
          <select
            value={modelType}
            onChange={(e) => setModelType(e.target.value)}
            className="input"
          >
            <option value="logistic">Logistic Regression</option>
            <option value="naive_bayes">Naive Bayes</option>
          </select>
        </div>

        {error && <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">{error}</div>}
        {success && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-green-400 text-sm flex items-center gap-2">
            <CheckCircle size={16} />
            {t('retrainSuccess')}
          </div>
        )}

        <button onClick={handleRetrain} disabled={loading} className="btn-primary flex items-center gap-2">
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          {loading ? t('retraining') : t('retrain')}
        </button>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-200 mb-3">System Info</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between py-2 border-b border-gray-800">
            <span className="text-gray-400">Logged in as</span>
            <span className="text-white">{user.username} ({user.role})</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-800">
            <span className="text-gray-400">Supported Languages</span>
            <span className="text-white">English, Amharic, Afaan Oromo</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-400">ML Algorithms</span>
            <span className="text-white">Logistic Regression, Naive Bayes</span>
          </div>
        </div>
      </div>
    </div>
  )
}
