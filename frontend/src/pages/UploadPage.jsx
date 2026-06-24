import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card, Alert } from '../components/UI'
import SecurityAlertModal from '../components/SecurityAlertModal'
import { fileAPI } from '../services/api'
import toast from 'react-hot-toast'

function UploadPage() {
  const [file, setFile] = useState(null)
  const [scope, setScope] = useState(() => localStorage.getItem('sfs_default_scope') || 'private')
  const [loading, setLoading] = useState(false)
  const [securityAlert, setSecurityAlert] = useState({ show: false, message: '' })

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) {
      toast.error('Please select a file')
      return
    }

    try {
      setLoading(true)
      const formData = new FormData()
      formData.append('file', file)
      formData.append('original_filename', file.name)
      formData.append('scope', scope)

      await fileAPI.uploadFile(formData)
      toast.success('File uploaded successfully!')
      setFile(null)
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message
      
      // Check if it's a security alert (malware, blocked extension, etc)
      if (errorMsg.includes('SECURITY ALERT') || errorMsg.includes('MALWARE') || errorMsg.includes('CORRUPTION') || errorMsg.includes('INVALID')) {
        setSecurityAlert({ show: true, message: errorMsg })
      } else {
        toast.error('Upload failed: ' + errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <SecurityAlertModal 
        isOpen={securityAlert.show} 
        onClose={() => setSecurityAlert({ ...securityAlert, show: false })}
        message={securityAlert.message}
      />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="Upload Files" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          <div className="max-w-2xl mx-auto">
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload a New File</h2>

              <Alert
                type="info"
                title="Security"
                message="Your files are encrypted before storage using simulated homomorphic encryption."
              />

              <form onSubmit={handleUpload} className="mt-6 space-y-6">
                {/* File Input */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Select File
                  </label>
                  <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-orange-500 transition cursor-pointer bg-gray-50">
                    <input
                      type="file"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="pointer-events-none">
                      <div className="text-4xl mb-2">📁</div>
                      <p className="text-gray-900 font-semibold">Drop file here or click to browse</p>
                      <p className="text-sm text-gray-600 mt-1">Max 100MB</p>
                    </div>
                  </div>
                  {file && (
                    <p className="text-sm text-green-600 mt-2">
                      ✅ Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </p>
                  )}
                </div>

                {/* Scope */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    File Scope
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <label className={`p-4 border-2 rounded-lg cursor-pointer transition ${
                      scope === 'private'
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-gray-300 hover:border-orange-300'
                    }`}>
                      <input
                        type="radio"
                        value="private"
                        checked={scope === 'private'}
                        onChange={(e) => setScope(e.target.value)}
                        className="mr-2"
                      />
                      <span className="font-semibold">🔒 Private</span>
                      <p className="text-sm text-gray-600">Only you can access</p>
                    </label>
                    <label className={`p-4 border-2 rounded-lg cursor-pointer transition ${
                      scope === 'public'
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-gray-300 hover:border-orange-300'
                    }`}>
                      <input
                        type="radio"
                        value="public"
                        checked={scope === 'public'}
                        onChange={(e) => setScope(e.target.value)}
                        className="mr-2"
                      />
                      <span className="font-semibold">🌐 Public</span>
                      <p className="text-sm text-gray-600">Anyone with link can see</p>
                    </label>
                  </div>
                </div>

                {/* Button */}
                <button
                  type="submit"
                  disabled={!file || loading}
                  className="w-full py-3 bg-gradient-to-r from-orange-500 to-pink-500 text-white font-bold rounded-lg disabled:opacity-50"
                >
                  {loading ? 'Uploading...' : '🚀 Upload File'}
                </button>
              </form>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}

export default UploadPage
