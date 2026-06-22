import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { FiMenu, FiX, FiHome, FiUpload, FiFolder, FiShare2, FiLogOut, FiSettings, FiLock, FiBarChart2, FiMonitor } from 'react-icons/fi'
import useAuthStore from '../context/authStore'
import toast from 'react-hot-toast'

function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout, isAdmin } = useAuthStore()

  const handleLogout = () => {
    logout()
    toast.success('Logged out successfully!')
    navigate('/login')
  }

  const isActive = (path) => location.pathname === path

  // Different menu items for admin vs regular users
  const menuItems = isAdmin() 
    ? [
        { path: '/admin', label: 'Admin Panel', icon: FiBarChart2 },
        { path: '/admin/logs', label: 'Security Logs', icon: FiLock },
        { path: '/admin/live', label: 'Live Security Monitoring', icon: FiMonitor },
      ]
    : [
        { path: '/dashboard', label: 'Dashboard', icon: FiHome },
        { path: '/upload', label: 'Upload Files', icon: FiUpload },
        { path: '/my-files', label: 'My Files', icon: FiFolder },
        { path: '/share', label: 'Share Files', icon: FiShare2 },
      ]

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 bg-orange-500 text-white rounded-lg"
      >
        {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      {/* Sidebar Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen w-64 bg-gradient-to-b from-gray-900 to-gray-800 text-white shadow-2xl transform transition-transform duration-300 ease-in-out z-40 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-pink-500 rounded-lg flex items-center justify-center text-xl font-bold">
              🔐
            </div>
            <div>
              <h1 className="text-lg font-bold">SFS</h1>
              <p className="text-xs text-gray-400">Secure File Sharing</p>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-pink-500 rounded-full flex items-center justify-center font-bold text-lg">
              {user?.name?.charAt(0).toUpperCase() || '?'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm truncate">{user?.name || user?.username}</p>
              <p className="text-xs text-gray-400 truncate">{user?.email}</p>
              <span className="inline-block mt-1 px-2 py-0.5 bg-orange-500/20 text-orange-300 text-xs rounded font-semibold">
                {user?.role === 'admin' ? '👑 Admin' : '👤 User'}
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-6 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition duration-300 ${
                  isActive(item.path)
                    ? 'bg-orange-500 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Settings & Logout */}
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-gray-700 space-y-2">
          <Link
            to="/settings"
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-700 transition"
          >
            <FiSettings size={20} />
            <span className="font-medium">Settings</span>
          </Link>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-red-600 transition"
          >
            <FiLogOut size={20} />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Padding */}
      <div className="md:ml-64" />
    </>
  )
}

export default Sidebar
