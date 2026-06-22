import { FiSearch, FiBell, FiUser } from 'react-icons/fi'
import { useState } from 'react'

function Header({ title = "Dashboard" }) {
  const [showNotifications, setShowNotifications] = useState(false)

  return (
    <header className="fixed top-0 right-0 left-0 md:left-64 bg-white border-b border-gray-200 shadow-sm z-30">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Title */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <p className="text-sm text-gray-500">Welcome back!</p>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-4">
          {/* Search Bar */}
          <div className="hidden md:flex items-center gap-2 bg-gray-100 rounded-lg px-4 py-2">
            <FiSearch className="text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent outline-none text-sm w-48"
            />
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
            >
              <FiBell size={20} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
          </div>

          {/* User Profile */}
          <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition">
            <FiUser size={20} />
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
