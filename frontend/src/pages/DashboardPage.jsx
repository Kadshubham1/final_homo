import { useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card, NoData } from '../components/UI'
import { fileAPI, authAPI } from '../services/api'
import { FiUploadCloud, FiFile, FiShare2, FiLock } from 'react-icons/fi'
import toast from 'react-hot-toast'

function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [recentFiles, setRecentFiles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [fileStats, filesData] = await Promise.all([
        fileAPI.getStats(),
        fileAPI.listFiles(),
      ])

      setStats(fileStats.data)
      setRecentFiles(filesData.data.results || [])
    } catch (error) {
      console.error('Error loading dashboard:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (id, defaultFilename) => {
    try {
      const response = await fileAPI.downloadFile(id)
      
      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition']
      let filename = defaultFilename
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1]
        }
      }

      const blob = new Blob([response.data], { type: response.headers['content-type'] })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      window.URL.revokeObjectURL(url)
      toast.success('Download started')
    } catch (error) {
      toast.error('Failed to download file')
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="Dashboard" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
                  <FiFile />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Total Files</p>
                  <p className="text-3xl font-bold text-gray-900">{stats?.total_files || 0}</p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">
                  <FiUploadCloud />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Public Files</p>
                  <p className="text-3xl font-bold text-gray-900">{stats?.public_files || 0}</p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-2xl">
                  <FiLock />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Private Files</p>
                  <p className="text-3xl font-bold text-gray-900">{stats?.private_files || 0}</p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center text-2xl">
                  <FiShare2 />
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Downloads</p>
                  <p className="text-3xl font-bold text-gray-900">{stats?.total_downloads || 0}</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Recent Files */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Files</h3>
            {recentFiles.length === 0 ? (
              <Card>
                <NoData message="No files uploaded yet. Start by uploading a file!" />
              </Card>
            ) : (
              <Card>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">File Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Scope</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Downloads</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentFiles.slice(0, 5).map((file) => (
                        <tr key={file.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4">{file.original_filename}</td>
                          <td className="py-3 px-4">
                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                              file.scope === 'public'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {file.scope}
                            </span>
                          </td>
                          <td className="py-3 px-4">{file.downloads}</td>
                          <td className="py-3 px-4">
                            <button 
                              onClick={() => handleDownload(file.id, file.original_filename)}
                              className="text-orange-500 hover:text-orange-600 font-semibold"
                            >
                              View / Download
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default DashboardPage
