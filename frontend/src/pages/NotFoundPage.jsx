import { Link } from 'react-router-dom'
import { Shield } from 'lucide-react'

export default function NotFoundPage() {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center text-center px-4 space-y-4">
      <Shield className="text-gray-700" size={64} />
      <h1 className="text-6xl font-bold text-gray-600">404</h1>
      <p className="text-gray-400 text-lg">Page not found</p>
      <Link to="/" className="btn-primary mt-2">Go Home</Link>
    </div>
  )
}
