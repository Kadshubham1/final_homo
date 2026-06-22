import { useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card, NoData } from '../components/UI'
import { securityAPI } from '../services/api'
import toast from 'react-hot-toast'

function AdminLogsPage() {
  const [logs, setLogs] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    loadLogs()
    loadStats()
  }, [filter])

  const loadStats = async () => {
    try {
      const response = await securityAPI.getUSBStats()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const loadLogs = async () => {
    try {
      setLoading(true)
      const response = await securityAPI.getSecurityEvents()
      
      const logsData = response.data.results || response.data || []
      
      let filtered = logsData
      if (filter === 'mobile') {
        filtered = logsData.filter(log => log.action?.toLowerCase().includes('mobile'))
      } else if (filter === 'usb') {
        filtered = logsData.filter(log => !log.action?.toLowerCase().includes('mobile'))
      }
      
      setLogs(filtered)
    } catch (error) {
      console.error('Failed to load logs:', error)
      toast.error('Failed to load security events')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50 uppercase-text">
      <Sidebar />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="🛡️ Admin Security Audit Trail" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          
          <div className="bg-gray-900 border-l-4 border-orange-500 rounded-lg p-5 mb-8 shadow-md">
            <h2 className="text-white font-bold text-lg mb-1 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Live Monitoring System Active
            </h2>
            <p className="text-gray-400 text-sm">
              Real-time audit trail capturing USB connections, Mobile Device (MTP) arrivals, and Security Photos.
            </p>
          </div>

          <div className="mb-8 flex flex-wrap gap-3">
            <button onClick={() => setFilter('all')} className={`px-5 py-2.5 rounded-xl font-bold transition-all ${filter === 'all' ? 'bg-orange-600 text-white shadow-lg' : 'bg-white text-gray-700 border hover:bg-gray-100'}`}>
              All Security Events
            </button>
            <button onClick={() => setFilter('usb')} className={`px-5 py-2.5 rounded-xl font-bold transition-all ${filter === 'usb' ? 'bg-blue-600 text-white shadow-lg' : 'bg-white text-gray-700 border hover:bg-gray-100'}`}>
              USB Drive Logs
            </button>
            <button onClick={() => setFilter('mobile')} className={`px-5 py-2.5 rounded-xl font-bold transition-all ${filter === 'mobile' ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white text-gray-700 border hover:bg-gray-100'}`}>
              Mobile / MTP Logs
            </button>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            {loading ? (
              <div className="p-20 text-center text-gray-400 animate-pulse font-medium">Synchronizing Audit Records...</div>
            ) : logs.length === 0 ? (
              <NoData message="No security events captured yet." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50/50 border-b border-gray-100">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Time & Date</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Action</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Security Capture</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Device Details</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Auth Status</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-widest">Face Recon</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {logs.map((log) => (
                      <tr key={log.id} className="hover:bg-blue-50/30 transition-colors">
                        <td className="px-6 py-4 text-sm text-gray-600 font-medium">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1.5 rounded-lg text-xs font-black uppercase tracking-tight ${
                             log.action?.includes('Connected') || log.action?.includes('Inserted') ? 'bg-green-100 text-green-700' :
                             log.action?.includes('Removed') ? 'bg-gray-100 text-gray-600' : 'bg-blue-100 text-blue-700'
                          }`}>
                            {log.action}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {log.image_url ? (
                            <div className="group relative w-16 h-12 bg-gray-200 rounded-lg overflow-hidden border-2 border-white shadow-sm hover:w-48 hover:h-32 transition-all duration-300 z-0 hover:z-50 cursor-zoom-in">
                               <img src={log.image_url} className="w-full h-full object-cover" alt="Capture" />
                            </div>
                          ) : (
                            <span className="text-gray-300 text-xs italic">No Evidence</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-bold text-gray-800">{log.device_name}</div>
                          <div className="text-[10px] text-gray-400 font-mono tracking-tighter truncate max-w-[150px]">{log.device_id}</div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`text-xs font-bold ${log.is_authorized ? 'text-green-500' : 'text-red-500'}`}>
                            {log.is_authorized ? '✔️ VERIFIED' : '❌ UNKNOWN'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${
                            log.face_status === 'Unknown' ? 'bg-orange-50 border-orange-200 text-orange-600' : 'bg-green-50 border-green-200 text-green-600'
                          }`}>
                            {log.face_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default AdminLogsPage
