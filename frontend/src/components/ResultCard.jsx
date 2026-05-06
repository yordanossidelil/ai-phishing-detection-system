import { Shield, ShieldAlert, ShieldX, ExternalLink, AlertTriangle } from 'lucide-react'
import { useLang } from '../hooks/useLang'
import clsx from 'clsx'

const RISK_WORDS = [
  'urgent', 'click', 'verify', 'confirm', 'suspended', 'locked', 'winner',
  'free', 'prize', 'password', 'account', 'bank', 'credit', 'immediately',
  'expire', 'warning', 'alert', 'security', 'breach', 'hacked',
  // Amharic
  'አስቸኳይ', 'ይጫኑ', 'ያረጋግጡ', 'ተዘግቷል', 'ነፃ', 'አሸናፊ',
  // Oromo
  'hatattamaan', 'cuqaasi', 'mirkaneessi', 'cufame', 'bilisaan',
]

function highlightText(text) {
  if (!text) return text
  const pattern = new RegExp(`(${RISK_WORDS.join('|')})`, 'gi')
  const parts = text.split(pattern)
  return parts.map((part, i) =>
    pattern.test(part)
      ? <mark key={i} className="bg-red-500/30 text-red-300 rounded px-0.5">{part}</mark>
      : part
  )
}

const ICONS = {
  phishing: <ShieldX className="text-red-400" size={32} />,
  suspicious: <ShieldAlert className="text-yellow-400" size={32} />,
  legitimate: <Shield className="text-green-400" size={32} />,
}

const COLORS = {
  phishing: 'border-red-500/40 bg-red-500/5',
  suspicious: 'border-yellow-500/40 bg-yellow-500/5',
  legitimate: 'border-green-500/40 bg-green-500/5',
}

const BADGE = {
  phishing: 'badge-phishing',
  suspicious: 'badge-suspicious',
  legitimate: 'badge-legitimate',
}

const LABEL = {
  phishing: { en: '❌ PHISHING', am: '❌ ፊሺንግ', or: '❌ PHISHING' },
  suspicious: { en: '⚠️ SUSPICIOUS', am: '⚠️ አጠራጣሪ', or: '⚠️ SHAKKISIISAA' },
  legitimate: { en: '✅ LEGITIMATE', am: '✅ ህጋዊ', or: '✅ SEERAA' },
}

const LABEL_COLOR = {
  phishing: 'text-red-400',
  suspicious: 'text-yellow-400',
  legitimate: 'text-green-400',
}

export default function ResultCard({ result, originalText }) {
  const { lang, t } = useLang()
  const { prediction, confidence_percent, explanation, features, probabilities, language } = result

  return (
    <div className={clsx('card border-2 space-y-5', COLORS[prediction])}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {ICONS[prediction]}
          <div>
            <div className={clsx('text-xl font-bold', LABEL_COLOR[prediction])}>
              {LABEL[prediction][lang] || LABEL[prediction].en}
            </div>
            <div className="text-gray-400 text-sm mt-0.5">
              {t('detectedLang')}: <span className="text-gray-200 capitalize">{language}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-white">{confidence_percent}%</div>
          <div className="text-gray-400 text-sm">{t('confidence')}</div>
        </div>
      </div>

      {/* Confidence Bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>{t('legitimate')}</span>
          <span>{t('suspicious')}</span>
          <span>{t('phishing')}</span>
        </div>
        <div className="h-2 bg-gray-800 rounded-full overflow-hidden flex">
          <div className="bg-green-500 h-full transition-all" style={{ width: `${(probabilities.legitimate || 0) * 100}%` }} />
          <div className="bg-yellow-500 h-full transition-all" style={{ width: `${(probabilities.suspicious || 0) * 100}%` }} />
          <div className="bg-red-500 h-full transition-all" style={{ width: `${(probabilities.phishing || 0) * 100}%` }} />
        </div>
      </div>

      {/* Explanation */}
      {explanation?.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-1">
            <AlertTriangle size={14} className="text-yellow-400" />
            {t('explanation')}
          </h3>
          <ul className="space-y-1">
            {explanation.map((reason, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-yellow-400 mt-0.5">•</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* URLs Found */}
      {features?.urls_found?.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-1">
            <ExternalLink size={14} className="text-blue-400" />
            {t('urlsFound')} ({features.urls_found.length})
          </h3>
          <div className="space-y-1">
            {features.urls_found.map((url, i) => (
              <div key={i} className="text-xs bg-gray-800 rounded px-3 py-1.5 text-blue-300 font-mono break-all">
                {url}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Highlighted Text Preview */}
      {originalText && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Highlighted Text</h3>
          <div className="text-sm text-gray-300 bg-gray-800 rounded-lg p-3 leading-relaxed max-h-32 overflow-y-auto">
            {highlightText(originalText)}
          </div>
        </div>
      )}
    </div>
  )
}
