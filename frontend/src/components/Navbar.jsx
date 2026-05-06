import { Link, useLocation } from 'react-router-dom'
import { Shield, LayoutDashboard, History, LogOut, LogIn, Settings } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useLang } from '../hooks/useLang'
import { LANGUAGES } from '../i18n/translations'
import clsx from 'clsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { lang, t, changeLang } = useLang()
  const { pathname } = useLocation()

  const navLink = (to, icon, label) => (
    <Link
      to={to}
      className={clsx(
        'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
        pathname === to ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'
      )}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </Link>
  )

  return (
    <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg text-white">
          <Shield className="text-blue-500" size={24} />
          <span className="hidden sm:inline">{t('appName')}</span>
        </Link>

        <div className="flex items-center gap-1">
          {navLink('/', <Shield size={16} />, t('analyze'))}
          {navLink('/dashboard', <LayoutDashboard size={16} />, t('dashboard'))}
          {navLink('/history', <History size={16} />, t('history'))}
          {user?.role === 'admin' && navLink('/admin', <Settings size={16} />, t('adminPanel'))}
        </div>

        <div className="flex items-center gap-2">
          {/* Language Switcher */}
          <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
            {LANGUAGES.map((l) => (
              <button
                key={l.code}
                onClick={() => changeLang(l.code)}
                className={clsx(
                  'px-2 py-1 rounded text-xs font-bold transition-colors',
                  lang === l.code ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
                )}
                title={l.name}
              >
                {l.label}
              </button>
            ))}
          </div>

          {user ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400 hidden sm:inline">{user.username}</span>
              <button onClick={logout} className="btn-secondary flex items-center gap-1 text-sm py-1.5">
                <LogOut size={14} />
                <span className="hidden sm:inline">{t('logout')}</span>
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn-primary flex items-center gap-1 text-sm py-1.5">
              <LogIn size={14} />
              <span>{t('login')}</span>
            </Link>
          )}
        </div>
      </div>
    </nav>
  )
}
