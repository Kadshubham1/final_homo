import { useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card, NoData } from '../components/UI'
import apiClient from '../services/api'
import toast from 'react-hot-toast'

function LiveMonitoringPage() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, unauthorized, unknown_face

  const fetchEvents = async () => {
    try {
      const res = await apiClient.get('/admin/live-events/')
      console.log("LIVE DATA:", res.data);
      
      const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
      setEvents([...data]); // force new reference
    } catch (error) {
      console.error("Error fetching live events:", error)
    } finally {
      if (loading) setLoading(false)
    }
  }

  // Poll every 3 seconds
  useEffect(() => {
    fetchEvents()
    const interval = setInterval(() => {
      fetchEvents()
    }, 3000)
    return () => clearInterval(interval)
  }, []) // Empty array for proper interval set

  const filteredEvents = events.filter(e => {
    if (filter === 'unauthorized') return !e.is_authorized;
    if (filter === 'unknown_face') return e.face_status === 'Unknown';
    return true;
  });

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="🔴 Live Security Monitoring" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
              Live Event Feed
            </h2>
            
            <div className="flex gap-2">
              <button onClick={() => setFilter('all')} className={`px-4 py-2 text-sm rounded-lg font-medium ${filter === 'all' ? 'bg-gray-800 text-white' : 'bg-white text-gray-700 border'}`}>
                All Events
              </button>
              <button onClick={() => setFilter('unauthorized')} className={`px-4 py-2 text-sm rounded-lg font-medium ${filter === 'unauthorized' ? 'bg-red-600 text-white' : 'bg-white text-red-600 border border-red-200'}`}>
                Unauthorized USBs
              </button>
              <button onClick={() => setFilter('unknown_face')} className={`px-4 py-2 text-sm rounded-lg font-medium ${filter === 'unknown_face' ? 'bg-orange-600 text-white' : 'bg-white text-orange-600 border border-orange-200'}`}>
                Unknown Faces
              </button>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-20 text-gray-500">Loading live feed...</div>
          ) : filteredEvents.length === 0 ? (
            <NoData message="No events match criteria." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredEvents.map(event => {
                const isCritical = !event.is_authorized || event.face_status === 'Unknown'
                
                return (
                  <div key={event.id} className={`rounded-xl overflow-hidden border ${isCritical ? 'border-red-400 shadow-[0_0_15px_rgba(239,68,68,0.2)]' : 'border-gray-200 bg-white'}`}>
                    {/* Media Header */}
                    <div className="bg-black aspect-video relative">
                      {event.video_url ? (
                        <video 
                          src={event.video_url} 
                          poster={event.image_url || null}
                          controls 
                          className="w-full h-full object-contain"
                        />
                      ) : event.image_url ? (
                        <img 
                          src={event.image_url} 
                          alt="Security Check" 
                          className="w-full h-full object-contain"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-500 bg-gray-900 border border-gray-800 rounded">
                          <span className="text-sm tracking-widest uppercase opacity-70">No Media</span>
                        </div>
                      )}
                      
                      {isCritical && (
                        <div className="absolute top-2 right-2 bg-red-600 text-white text-xs font-bold px-2 py-1 rounded shadow animate-pulse">
                          CRITICAL ALERT
                        </div>
                      )}
                    </div>
                    
                    {/* Body */}
                    <div className={`p-4 ${isCritical ? 'bg-red-50' : 'bg-white'}`}>
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs text-gray-500 font-mono">{new Date(event.timestamp).toLocaleString()}</span>
                        <span className={`px-2 py-1 flex items-center rounded text-[10px] sm:text-xs font-bold whitespace-nowrap overflow-hidden text-ellipsis max-w-[50%] ${
                          event.action.includes('Inserted') ? 'bg-blue-100 text-blue-700' : 
                          event.action.includes('Removed') ? 'bg-gray-200 text-gray-700' :
                          event.action.includes('Activity') || event.action.includes('Copied') || event.action.includes('Modified') ? 'bg-amber-100 text-amber-700' :
                          'bg-indigo-100 text-indigo-700'
                        }`} title={event.action}>
                          {event.action}
                        </span>
                      </div>
                      
                      <h3 className="font-bold text-gray-900 mb-1">{event.device_name || 'Unknown Device'}</h3>
                      <p className="text-xs text-gray-500 font-mono mb-4">ID: {event.device_id || 'N/A'}</p>
                      
                      <div className="space-y-2 text-sm border-t border-gray-100 pt-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600">USB Auth:</span>
                          <span className={event.is_authorized ? 'text-green-600 font-semibold' : 'text-red-600 font-bold'}>
                            {event.is_authorized ? 'AUTHORIZED' : 'UNAUTHORIZED'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Face Recognition:</span>
                          <span className={event.face_status === 'Unknown' ? 'text-orange-600 font-bold' : 'text-green-600 font-semibold'}>
                            {event.face_status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

        </main>
      </div>
    </div>
  )
}

export default LiveMonitoringPage
