import { Link } from 'react-router-dom'

function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-pink-500">
          404
        </div>
        <h1 className="text-4xl font-bold text-white mt-4">Page Not Found</h1>
        <p className="text-gray-400 mt-2 mb-8">The page you're looking for doesn't exist.</p>
        <Link to="/dashboard" className="btn-primary inline-block">
          📍 Back to Dashboard
        </Link>
      </div>
    </div>
  )
}

export default NotFoundPage
