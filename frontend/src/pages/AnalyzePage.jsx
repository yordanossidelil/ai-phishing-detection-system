import { useState } from 'react'
import { Shield, Loader2, Trash2, Zap } from 'lucide-react'
import { analyzeText } from '../utils/api'
import { useLang } from '../hooks/useLang'
import ResultCard from '../components/ResultCard'

const EXAMPLES = {
  phishing: "URGENT: Your bank account has been suspended! Verify immediately at http://secure-bank-login.xyz or lose access forever. Click NOW!",
  legitimate: "Hi team, the quarterly report is ready. Please review the attached document before our meeting on Friday.",
  amharic: "አካውንትዎ ተዘግቷል እባክዎ እዚህ ይጫኑ http://fake-ethiopian-bank.com/verify አስቸኳይ ነው!",
  oromo: "Herregaa! Lakkoofsi iccitii kee jijjiirameera. Yoo ati hintaane ta'e asitti cuqaasi: http://iccitii-haaromsi.fake.com",
}

export default function AnalyzePage() {
  const { t } = useLang()
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleAnalyze = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const { data } = await analyzeText(text)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleFile = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => setText(ev.target.result)
    reader.readAsText(file)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      {/* Hero */}
      <div className="text-center space-y-2">
        <div className="flex justify-center">
          <div className="bg-blue-600/20 p-4 rounded-2xl">
            <Shield className="text-blue-400" size={40} />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-white">{t('appName')}</h1>
        <p className="text-gray-400">{t('tagline')}</p>
      </div>

      {/* Input Card */}
      <div className="card space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t('placeholder')}
          rows={6}
          className="input resize-none text-sm leading-relaxed"
        />

        {/* Quick Examples */}
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-500 self-center">{t('tryExample')}:</span>
          {Object.entries(EXAMPLES).map(([key, val]) => (
            <button
              key={key}
              onClick={() => { setText(val); setResult(null) }}
              className="text-xs px-2.5 py-1 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
            >
              {key}
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className="btn-primary flex items-center gap-2 flex-1 justify-center"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
            {loading ? t('analyzing') : t('analyze')}
          </button>

          <label className="btn-secondary cursor-pointer flex items-center gap-1 text-sm">
            📎 {t('uploadFile')}
            <input type="file" accept=".txt,.eml,.msg" onChange={handleFile} className="hidden" />
          </label>

          {text && (
            <button onClick={() => { setText(''); setResult(null) }} className="btn-secondary">
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold text-gray-200">{t('result')}</h2>
          <ResultCard result={result.result} originalText={text} />
        </div>
      )}
    </div>
  )
}
