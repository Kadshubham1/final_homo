import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from './context/authStore'
import LoginPage from './pages/LoginPageSimple'
import RegisterPage from './pages/RegisterPage'
import SignupPage from './pages/SignupPage'
import VerifyOTPPage from './pages/VerifyOTPPage'
import OTPDebugPage from './pages/OTPDebugPage'
import DashboardPage from './pages/DashboardPage'
import UploadPage from './pages/UploadPage'
import MyFilesPage from './pages/MyFilesPage'
import SharePage from './pages/SharePage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import AdminLogsPage from './pages/AdminLogsPage'
import LiveMonitoringPage from './pages/LiveMonitoringPage'
import NotFoundPage from './pages/NotFoundPage'

function ProtectedRoute({ children, isAdmin = false }) {
  const auth = useAuthStore()
  if (!auth?.isAuthenticated) return <Navigate to="/login" replace />
  if (isAdmin && auth?.user?.role !== 'admin') return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)
  const hydrateUser = useAuthStore((state) => state.hydrateUser)

  useEffect(() => {
    if (isAuthenticated && !user) {
      hydrateUser()
    }
  }, [isAuthenticated, user, hydrateUser])
  
  return (
    <Router>
      <Routes>
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />
        <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <RegisterPage />} />
        <Route path="/signup" element={isAuthenticated ? <Navigate to="/dashboard" /> : <SignupPage />} />
        <Route path="/verify-otp" element={<VerifyOTPPage />} />
        <Route path="/otp-debug" element={<OTPDebugPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><UploadPage /></ProtectedRoute>} />
        <Route path="/my-files" element={<ProtectedRoute><MyFilesPage /></ProtectedRoute>} />
        <Route path="/share" element={<ProtectedRoute><SharePage /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute isAdmin><AdminDashboardPage /></ProtectedRoute>} />
        <Route path="/admin/logs" element={<ProtectedRoute isAdmin><AdminLogsPage /></ProtectedRoute>} />
        <Route path="/admin/live" element={<ProtectedRoute isAdmin><LiveMonitoringPage /></ProtectedRoute>} />
        <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  )
}
