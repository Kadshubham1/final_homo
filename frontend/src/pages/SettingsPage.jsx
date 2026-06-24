import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card } from '../components/UI'
import useAuthStore from '../context/authStore'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'
import { FiUser, FiLock, FiSettings, FiCheck, FiMoon, FiSun, FiGlobe, FiBell } from 'react-icons/fi'

function SettingsPage() {
  const { user, hydrateUser } = useAuthStore()
  
  // Tab State
  const [activeTab, setActiveTab] = useState('profile') // 'profile', 'security', 'app'

  // Profile Form State
  const [name, setName] = useState('')
  const [mobile, setMobile] = useState('')
  const [bio, setBio] = useState('')
  const [profileLoading, setProfileLoading] = useState(false)

  // Security Form State
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [securityLoading, setSecurityLoading] = useState(false)

  // App Settings State
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('sfs_theme') === 'dark'
  })
  const [defaultScope, setDefaultScope] = useState(() => {
    return localStorage.getItem('sfs_default_scope') || 'private'
  })
  const [emailAlerts, setEmailAlerts] = useState(() => {
    return localStorage.getItem('sfs_email_alerts') !== 'false'
  })
  const [toastAlerts, setToastAlerts] = useState(() => {
    return localStorage.getItem('sfs_toast_alerts') !== 'false'
  })

  // Load User Data
  useEffect(() => {
    if (user) {
      setName(user.name || '')
      setMobile(user.mobile || '')
      setBio(user.bio || '')
    }
  }, [user])

  // Handle Theme Toggle
  const handleThemeChange = (isChecked) => {
    setDarkMode(isChecked)
    if (isChecked) {
      localStorage.setItem('sfs_theme', 'dark')
      document.documentElement.classList.add('dark')
    } else {
      localStorage.setItem('sfs_theme', 'light')
      document.documentElement.classList.remove('dark')
    }
    toast.success(`${isChecked ? 'Dark' : 'Light'} mode theme applied!`)
  }

  // Handle Default Scope Change
  const handleScopeChange = (e) => {
    const value = e.target.value
    setDefaultScope(value)
    localStorage.setItem('sfs_default_scope', value)
    toast.success(`Default upload scope set to: ${value}`)
  }

  // Handle Notification Settings Changes
  const handleNotificationChange = (type, value) => {
    if (type === 'email') {
      setEmailAlerts(value)
      localStorage.setItem('sfs_email_alerts', value.toString())
    } else if (type === 'toast') {
      setToastAlerts(value)
      localStorage.setItem('sfs_toast_alerts', value.toString())
    }
    toast.success('Notification preferences updated')
  }

  // Handle Profile Update Submission
  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    setProfileLoading(true)

    try {
      const response = await authAPI.updateMe({
        name,
        mobile,
        bio
      })
      
      toast.success(response.data.message || 'Profile updated successfully!')
      // Refresh Auth State
      await hydrateUser()
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.error || error.message || 'Failed to update profile'
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Profile update failed. Check fields.')
    } finally {
      setProfileLoading(false)
    }
  }

  // Handle Password Update Submission
  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    
    if (!oldPassword || !newPassword || !confirmPassword) {
      toast.error('All password fields are required')
      return
    }

    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match')
      return
    }

    if (newPassword.length < 8) {
      toast.error('New password must be at least 8 characters long')
      return
    }

    setSecurityLoading(true)
    try {
      const response = await authAPI.changePassword({
        old_password: oldPassword,
        new_password: newPassword,
        new_password2: confirmPassword
      })

      toast.success(response.data.message || 'Password changed successfully!')
      // Clear password fields
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (error) {
      const errorData = error.response?.data
      const errorMsg = errorData?.error || errorData?.detail || errorData?.old_password?.[0] || errorData?.new_password?.[0] || error.message || 'Failed to change password'
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Password change failed')
    } finally {
      setSecurityLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <Sidebar />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="Settings" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-6">System Settings</h2>

            {/* Inner Dashboard Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700 mb-8 overflow-x-auto">
              <button
                onClick={() => setActiveTab('profile')}
                className={`flex items-center gap-2 py-4 px-6 border-b-2 font-semibold text-sm transition duration-300 whitespace-nowrap ${
                  activeTab === 'profile'
                    ? 'border-orange-500 text-orange-500'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                }`}
              >
                <FiUser size={18} />
                Profile Information
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`flex items-center gap-2 py-4 px-6 border-b-2 font-semibold text-sm transition duration-300 whitespace-nowrap ${
                  activeTab === 'security'
                    ? 'border-orange-500 text-orange-500'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                }`}
              >
                <FiLock size={18} />
                Security & Password
              </button>
              <button
                onClick={() => setActiveTab('app')}
                className={`flex items-center gap-2 py-4 px-6 border-b-2 font-semibold text-sm transition duration-300 whitespace-nowrap ${
                  activeTab === 'app'
                    ? 'border-orange-500 text-orange-500'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                }`}
              >
                <FiSettings size={18} />
                Application Preferences
              </button>
            </div>

            {/* Tab Contents */}
            <div className="space-y-6">
              {activeTab === 'profile' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Avatar Profile Card */}
                  <div className="lg:col-span-1">
                    <Card className="h-full flex flex-col items-center justify-center text-center p-6 bg-white dark:bg-gray-800 border dark:border-gray-700 shadow-lg">
                      <div className="w-24 h-24 bg-gradient-to-br from-orange-500 to-pink-500 rounded-full flex items-center justify-center text-white font-extrabold text-3xl shadow-md mb-4 border-4 border-white dark:border-gray-800">
                        {user?.name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || '?'}
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white truncate max-w-full">
                        {user?.name || user?.username}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-3 truncate max-w-full">
                        {user?.email}
                      </p>
                      <div className="inline-flex items-center px-3 py-1 bg-orange-50 dark:bg-orange-500/10 text-orange-600 dark:text-orange-400 text-xs font-bold rounded-full uppercase tracking-wider mb-4 border border-orange-100 dark:border-orange-500/20">
                        {user?.role === 'admin' ? '👑 Admin' : '👤 User'}
                      </div>
                      <div className="w-full pt-4 border-t border-gray-100 dark:border-gray-700 text-left space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-500 dark:text-gray-400">Username:</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200 truncate">{user?.username}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-500 dark:text-gray-400">Joined:</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">
                            {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                          </span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-500 dark:text-gray-400">Status:</span>
                          <span className="inline-flex items-center gap-1 font-semibold text-green-600 dark:text-green-400">
                            <FiCheck size={12} /> Verified Account
                          </span>
                        </div>
                      </div>
                    </Card>
                  </div>

                  {/* Profile Edit Card */}
                  <div className="lg:col-span-2">
                    <Card className="bg-white dark:bg-gray-800 border dark:border-gray-700 shadow-lg">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Profile Settings</h3>
                      <form onSubmit={handleProfileSubmit} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                              Full Name
                            </label>
                            <input
                              type="text"
                              value={name}
                              onChange={(e) => setName(e.target.value)}
                              placeholder="John Doe"
                              className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                              Phone / Mobile
                            </label>
                            <input
                              type="text"
                              value={mobile}
                              onChange={(e) => setMobile(e.target.value)}
                              placeholder="+1 (555) 000-0000"
                              className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Biography
                          </label>
                          <textarea
                            value={bio}
                            onChange={(e) => setBio(e.target.value)}
                            placeholder="Tell us about yourself..."
                            rows={4}
                            className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none"
                          />
                        </div>

                        <div className="flex justify-end">
                          <button
                            type="submit"
                            disabled={profileLoading}
                            className="px-6 py-3 bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
                          >
                            {profileLoading ? 'Saving...' : '💾 Save Profile'}
                          </button>
                        </div>
                      </form>
                    </Card>
                  </div>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="max-w-2xl mx-auto">
                  <Card className="bg-white dark:bg-gray-800 border dark:border-gray-700 shadow-lg">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-3 bg-orange-100 dark:bg-orange-500/20 text-orange-500 rounded-lg">
                        <FiLock size={24} />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">Change Account Password</h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Update your security key periodically to ensure safety.</p>
                      </div>
                    </div>

                    <form onSubmit={handlePasswordSubmit} className="space-y-6">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          Current Password
                        </label>
                        <input
                          type="password"
                          value={oldPassword}
                          onChange={(e) => setOldPassword(e.target.value)}
                          placeholder="••••••••"
                          className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                          required
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            New Password
                          </label>
                          <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            placeholder="•••••••• (Min 8 chars)"
                            className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Confirm New Password
                          </label>
                          <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="••••••••"
                            className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            required
                          />
                        </div>
                      </div>

                      <div className="flex justify-end pt-4">
                        <button
                          type="submit"
                          disabled={securityLoading}
                          className="px-6 py-3 bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
                        >
                          {securityLoading ? 'Updating...' : '🔒 Change Password'}
                        </button>
                      </div>
                    </form>
                  </Card>
                </div>
              )}

              {activeTab === 'app' && (
                <div className="max-w-2xl mx-auto space-y-6">
                  <Card className="bg-white dark:bg-gray-800 border dark:border-gray-700 shadow-lg">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">User Interface & Layout</h3>
                    <div className="space-y-6">
                      {/* Theme Toggle */}
                      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl transition duration-300">
                        <div className="flex items-center gap-3">
                          {darkMode ? (
                            <FiMoon size={22} className="text-orange-500" />
                          ) : (
                            <FiSun size={22} className="text-yellow-500" />
                          )}
                          <div>
                            <span className="font-semibold text-gray-800 dark:text-white block">Theme Mode</span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">Toggle dark styling across layout elements.</span>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={darkMode}
                            onChange={(e) => handleThemeChange(e.target.checked)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-500"></div>
                        </label>
                      </div>

                      {/* Default Scope Selection */}
                      <div className="flex flex-col md:flex-row md:items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl gap-4 transition duration-300">
                        <div className="flex items-center gap-3">
                          <FiGlobe size={22} className="text-orange-500" />
                          <div>
                            <span className="font-semibold text-gray-800 dark:text-white block">Default Upload Scope</span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">Define if uploads are private or public by default.</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <label className="flex items-center gap-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="defaultScope"
                              value="private"
                              checked={defaultScope === 'private'}
                              onChange={handleScopeChange}
                              className="text-orange-500 focus:ring-orange-500"
                            />
                            <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">🔒 Private</span>
                          </label>
                          <label className="flex items-center gap-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="defaultScope"
                              value="public"
                              checked={defaultScope === 'public'}
                              onChange={handleScopeChange}
                              className="text-orange-500 focus:ring-orange-500"
                            />
                            <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">🌐 Public</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </Card>

                  <Card className="bg-white dark:bg-gray-800 border dark:border-gray-700 shadow-lg">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Alerts & System Notifications</h3>
                    <div className="space-y-6">
                      {/* Email Notifications Toggle */}
                      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl transition duration-300">
                        <div className="flex items-center gap-3">
                          <FiBell size={22} className="text-orange-500" />
                          <div>
                            <span className="font-semibold text-gray-800 dark:text-white block">Email Alerts</span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">Receive security alerts and share links in email.</span>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={emailAlerts}
                            onChange={(e) => handleNotificationChange('email', e.target.checked)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-500"></div>
                        </label>
                      </div>

                      {/* Toast Notifications Toggle */}
                      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl transition duration-300">
                        <div className="flex items-center gap-3">
                          <FiBell size={22} className="text-orange-500" />
                          <div>
                            <span className="font-semibold text-gray-800 dark:text-white block">In-App Toast Popups</span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">Show alert popup overlays on real-time activity events.</span>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={toastAlerts}
                            onChange={(e) => handleNotificationChange('toast', e.target.checked)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-500"></div>
                        </label>
                      </div>
                    </div>
                  </Card>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default SettingsPage
