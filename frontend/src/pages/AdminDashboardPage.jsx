import { useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card } from '../components/UI'
import { authAPI, fileAPI, securityAPI } from '../services/api'
import toast from 'react-hot-toast'

function AdminDashboardPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    console.log('[Admin Dashboard] Dashboard Loaded');
    console.log('[Admin Dashboard] Fetching Admin Stats');
    try {
      setLoading(true)
      const [authStats, fileStats, securityStats] = await Promise.all([
        authAPI.getAdminStats(),
        fileAPI.getStats(),
        securityAPI.getSecurityDashboard(),
      ])
      
      console.log('[Admin Dashboard] API URLs Called:', {
        auth: '/auth/admin/stats/',
        files: '/files/stats/',
        security: '/security/admin/dashboard/'
      });
      console.log('[Admin Dashboard] Response Data:', {
        users: authStats.data,
        files: fileStats.data,
        security: securityStats.data
      });
      
      setStats({
        users: authStats.data,
        files: fileStats.data,
        security: securityStats.data,
      })
    } catch (error) {
      console.error('[Admin Dashboard] Error Stack:', error);
      
      let errMsg = 'Internal Server Error';
      if (error.response) {
        console.error('[Admin Dashboard] Response Status:', error.response.status);
        console.error('[Admin Dashboard] Response Data:', error.response.data);
        if (error.response.status === 401 || error.response.status === 403) {
          errMsg = 'Authentication Failed / Unauthorized';
        } else if (error.response.status === 404) {
          errMsg = 'Endpoint Not Found';
        } else {
          errMsg = 'Database Connection Failed / Backend Error';
        }
      } else {
        errMsg = error.message;
      }
      toast.error(`Failed to load admin stats: ${errMsg}`);
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="Admin Dashboard" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Users Card */}
            <Card>
              <div className="text-center">
                <div className="text-4xl mb-2">👥</div>
                <p className="text-gray-600 text-sm">Total Users</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.users?.total_users || 0}</p>
                <p className="text-xs text-gray-600 mt-2">{stats?.users?.regular_users} regular • {stats?.users?.total_admins} admin</p>
              </div>
            </Card>

            {/* Files Card */}
            <Card>
              <div className="text-center">
                <div className="text-4xl mb-2">📁</div>
                <p className="text-gray-600 text-sm">Total Files</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.files?.total_files || 0}</p>
                <p className="text-xs text-gray-600 mt-2">{stats?.files?.public_files} public • {stats?.files?.private_files} private</p>
              </div>
            </Card>

            {/* USB Events */}
            <Card>
              <div className="text-center">
                <div className="text-4xl mb-2">🔌</div>
                <p className="text-gray-600 text-sm">USB Events</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.security?.usb_stats?.total_events || 0}</p>
                <p className="text-xs text-red-600 mt-2">🚨 {stats?.security?.usb_stats?.high_risk_events} high risk</p>
              </div>
            </Card>

            {/* Alerts */}
            <Card>
              <div className="text-center">
                <div className="text-4xl mb-2">🚨</div>
                <p className="text-gray-600 text-sm">Active Alerts</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.security?.alert_stats?.unresolved_alerts || 0}</p>
                <p className="text-xs text-red-600 mt-2">⚠️ Need attention</p>
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <h3 className="text-xl font-bold mb-4">Security Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Suspicious Activities:</span>
                  <span className="font-bold">{stats?.security?.usb_stats?.suspicious_events || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Unresolved Alerts:</span>
                  <span className="font-bold text-red-600">{stats?.security?.alert_stats?.unresolved_alerts || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>High Severity:</span>
                  <span className="font-bold">{stats?.security?.alert_stats?.high_severity || 0}</span>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="text-xl font-bold mb-4">System Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Failed Operations:</span>
                  <span className="font-bold">{stats?.security?.system_stats?.failed_operations || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Logs:</span>
                  <span className="font-bold">{stats?.security?.system_stats?.total_logs || 0}</span>
                </div>
              </div>
            </Card>
          </div>

          <div className="mt-6">
            <a href="/admin/logs" className="btn-primary inline-block">
              View Detailed Logs 📊
            </a>
          </div>
        </main>
      </div>
    </div>
  )
}

export default AdminDashboardPage
