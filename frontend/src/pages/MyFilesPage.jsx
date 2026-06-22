import { useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card, NoData, LoadingOverlay } from '../components/UI'
import { fileAPI } from '../services/api'
import { FiDownload, FiTrash2, FiShare2 } from 'react-icons/fi'
import toast from 'react-hot-toast'

function MyFilesPage() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFiles()
  }, [])

  const loadFiles = async () => {
    try {
      const response = await fileAPI.listFiles()
      setFiles(response.data.results || [])
    } catch (error) {
      toast.error('Failed to load files')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Delete this file?')) {
      try {
        await fileAPI.deleteFile(id)
        toast.success('File deleted')
        loadFiles()
      } catch (error) {
        toast.error('Failed to delete file')
      }
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

  if (loading) return <LoadingOverlay />

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="My Files" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          {files.length === 0 ? (
            <Card>
              <NoData message="No files yet. Upload one to get started!" />
            </Card>
          ) : (
            <div className="space-y-4">
              {files.map((file) => (
                <Card key={file.id}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{file.original_filename}</h3>
                      <p className="text-sm text-gray-600">{file.file_size_display} • {file.downloads} downloads</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDownload(file.id, file.original_filename)}
                        className="p-2 text-blue-600 hover:bg-blue-100 rounded transition"
                      >
                        <FiDownload size={20} />
                      </button>
                      <button
                        onClick={() => handleDelete(file.id)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded transition"
                      >
                        <FiTrash2 size={20} />
                      </button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default MyFilesPage
