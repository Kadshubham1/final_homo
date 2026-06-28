import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import { securityAPI } from '../services/api';
import { useAuthStore } from '../context/authStore';

export default function SecurityLogsPage() {
  const navigate = useNavigate();
  const { user, token } = useAuthStore();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    action: 'all',
    device_type: 'all',
    timeRange: 'all'
  });
  const [stats, setStats] = useState(null);

  const [activeTab, setActiveTab] = useState('usb');

  // Check admin access
  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/login');
    }
  }, [user, navigate]);

  // Fetch USB logs with polling
  useEffect(() => {
    if (!user || user.role !== 'admin') return;
    
    loadLogs(false);
    const interval = setInterval(() => {
      loadLogs(true);
    }, 3000);
    return () => clearInterval(interval);
  }, [filters, activeTab]);

  const loadLogs = async (isPolling = false) => {
    try {
      if (!isPolling) setLoading(true);
      if (!isPolling) setError('');

      const response = await securityAPI.getLogs();
      
      // Handle paginated response
      const logsData = response.data.results || response.data || [];
      
      // Apply filters in-memory if needed
      let filteredLogs = logsData;
      
      if (activeTab === 'usb') {
        filteredLogs = filteredLogs.filter(log => log.action.includes('USB'));
      }
      
      if (filters.action !== 'all') {
        filteredLogs = filteredLogs.filter(log => log.action === filters.action);
      }
      if (filters.device_type !== 'all') {
        filteredLogs = filteredLogs.filter(log => log.device_type === filters.device_type);
      }
      
      setLogs(filteredLogs);

      // Load stats
      if (!isPolling) loadStats();
    } catch (err) {
      console.error('Error loading USB logs:', err);
      if (!isPolling) setError('Failed to load USB logs. ' + (err.response?.data?.detail || err.message));
    } finally {
      if (!isPolling) setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await securityAPI.getUSBStats();
      setStats(response.data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  const getActionIcon = (action) => {
    if (action === 'USB_INSERTED') return '🔌 Connected';
    if (action === 'USB_REMOVED') return '🔌 Disconnected';
    return action;
  };

  // Compute active devices
  const latestEventsByDevice = {};
  logs.filter(l => l.action.includes('USB') && l.device_id).forEach(log => {
    if (!latestEventsByDevice[log.device_id]) {
      latestEventsByDevice[log.device_id] = log;
    }
  });
  const activeDevices = Object.values(latestEventsByDevice).filter(
    l => l.action === 'USB Inserted' || l.action === 'USB_INSERTED'
  );

  const exportCSV = () => {
    try {
      // Create CSV content
      const headers = ['Timestamp', 'User', 'Action', 'Device', 'Manufacturer', 'VID', 'PID', 'Device Path', 'Hostname', 'System'];
      const rows = logs.map(log => {
        const sysInfo = log.system_info || {};
        return [
          log.timestamp,
          log.user?.username || 'Unknown',
          log.action,
          log.device_name || 'N/A',
          sysInfo.manufacturer || 'N/A',
          sysInfo.vid || 'N/A',
          sysInfo.pid || 'N/A',
          log.device_path || 'N/A',
          log.hostname || 'N/A',
          sysInfo.os || log.system_type || 'N/A'
        ];
      });

      let csv = headers.join(',') + '\n';
      rows.forEach(row => {
        csv += row.map(cell => `"${cell}"`).join(',') + '\n';
      });

      // Download
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `usb-logs-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    } catch (err) {
      console.error('Export error:', err);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="🔐 Security Logs - Live Monitoring" />
        
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            
            {/* Tabs */}
            <div className="flex border-b border-gray-200 mb-6">
              <button
                onClick={() => setActiveTab('usb')}
                className={`py-2 px-4 font-medium text-sm focus:outline-none ${activeTab === 'usb' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                USB Drive Logs
              </button>
              <button
                onClick={() => setActiveTab('all')}
                className={`py-2 px-4 font-medium text-sm focus:outline-none ${activeTab === 'all' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                All Security Events
              </button>
            </div>

            {/* Current Status Banner */}
            <div className={`rounded-lg p-4 mb-6 border ${activeDevices.length > 0 ? 'bg-orange-50 border-orange-200' : 'bg-green-50 border-green-200'}`}>
              <h3 className={`font-bold ${activeDevices.length > 0 ? 'text-orange-800' : 'text-green-800'}`}>
                {activeDevices.length > 0 ? '⚠️ USB Devices Currently Connected:' : '✅ No USB Device Connected'}
              </h3>
              {activeDevices.length > 0 && (
                <ul className="mt-2 text-sm text-orange-700 list-disc list-inside">
                  {activeDevices.map(d => (
                    <li key={d.id}>{d.device_name || 'Unknown Device'} (Serial: {d.device_id})</li>
                  ))}
                </ul>
              )}
            </div>

            {/* Statistics */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <div className="text-sm text-gray-600">Total Events</div>
                  <div className="text-2xl font-bold text-gray-900">{stats.total_events}</div>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <div className="text-sm text-gray-600">Connected</div>
                  <div className="text-2xl font-bold text-green-600">{stats.insertions}</div>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <div className="text-sm text-gray-600">Disconnected</div>
                  <div className="text-2xl font-bold text-red-600">{stats.removals}</div>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <div className="text-sm text-gray-600">Unique Devices</div>
                  <div className="text-2xl font-bold text-blue-600">{stats.unique_devices}</div>
                </div>
              </div>
            )}

            {/* Filters */}
            <div className="bg-white rounded-lg p-4 mb-6 border border-gray-200">
              <h3 className="font-semibold mb-4">Filters</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Action
                  </label>
                  <select
                    value={filters.action}
                    onChange={(e) => setFilters({...filters, action: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Actions</option>
                    <option value="USB_INSERTED">Connected</option>
                    <option value="USB_REMOVED">Disconnected</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Device Type
                  </label>
                  <select
                    value={filters.device_type}
                    onChange={(e) => setFilters({...filters, device_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Types</option>
                    <option value="usb_storage">USB Storage</option>
                    <option value="usb_phone">Mobile Device</option>
                    <option value="usb_other">Other</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <button
                    onClick={exportCSV}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition"
                  >
                    📥 Export CSV
                  </button>
                </div>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {/* Logs Table */}
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Timestamp</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">User</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Action</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Device Name</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Hardware Info</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">System</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Photo</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {loading ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                          Loading logs...
                        </td>
                      </tr>
                    ) : logs.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                          No logs available.
                        </td>
                      </tr>
                    ) : (
                      logs.map((log) => {
                        const sysInfo = log.system_info || {};
                        return (
                          <tr key={log.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm text-gray-900 whitespace-nowrap">
                              {formatTime(log.timestamp)}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {log.user?.username || 'Unknown'}
                            </td>
                            <td className="px-6 py-4 text-sm">
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${log.action.includes('USB') ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                                {getActionIcon(log.action)}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-700">
                              <div className="font-medium">{log.device_name || 'N/A'}</div>
                              {log.device_path && <div className="text-xs text-gray-500">Path: {log.device_path}</div>}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-700 font-mono text-xs">
                              {sysInfo.manufacturer && <div>Mfr: {sysInfo.manufacturer}</div>}
                              {(sysInfo.vid || sysInfo.pid) && <div>VID:PID: {sysInfo.vid}:{sysInfo.pid}</div>}
                              {log.device_id && <div>Serial: {log.device_id}</div>}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-700">
                              <div>{log.hostname || 'N/A'}</div>
                              <div className="text-xs text-gray-500">{sysInfo.os || log.system_type || 'N/A'}</div>
                            </td>
                            <td className="px-6 py-4 text-sm">
                              {log.image ? (
                                <img src={log.image} alt="Security snapshot" className="w-16 h-12 object-cover rounded cursor-pointer hover:opacity-80" onClick={() => window.open(log.image, '_blank')} />
                              ) : (
                                <span className="text-gray-400 italic text-xs">No Photo</span>
                              )}
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
