import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { Card, NoData } from '../components/UI'
import { sharingAPI, fileAPI, authAPI } from '../services/api'
import toast from 'react-hot-toast'

const OtpCountdownToast = ({ otp, expiresAt, t }) => {
  const [timeLeft, setTimeLeft] = useState(() => {
    const now = new Date().getTime()
    const expiryTime = new Date(expiresAt).getTime()
    return Math.max(0, Math.floor((expiryTime - now) / 1000))
  })

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date().getTime()
      const expiryTime = new Date(expiresAt).getTime()
      const left = Math.max(0, Math.floor((expiryTime - now) / 1000))
      setTimeLeft(left)
      
      if (left <= 0) {
        clearInterval(timer)
        toast.dismiss(t.id)
        toast.error('OTP has expired. Please generate a new OTP.', { duration: 4000 })
      }
    }, 1000)
    return () => clearInterval(timer)
  }, [expiresAt, t.id])

  if (timeLeft <= 0) return null

  return (
    <div>
      <p>✅ File shared! OTP: <strong>{otp}</strong></p>
      <p className="mt-1 font-mono text-sm font-bold text-orange-600">
        OTP Expires In: {String(Math.floor(timeLeft / 60)).padStart(2, '0')}:{String(timeLeft % 60).padStart(2, '0')}
      </p>
    </div>
  )
}

const PendingVerifySection = ({ share, otpInput, setOtpInput, handleVerifyOTP, verifying }) => {
  const [timeLeft, setTimeLeft] = useState(() => {
    const now = new Date().getTime()
    const expiryTime = new Date(share.otp_expires_at).getTime()
    return Math.max(0, Math.floor((expiryTime - now) / 1000))
  })

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date().getTime()
      const expiryTime = new Date(share.otp_expires_at).getTime()
      setTimeLeft(Math.max(0, Math.floor((expiryTime - now) / 1000)))
    }, 1000)
    return () => clearInterval(timer)
  }, [share.otp_expires_at])

  const isExpired = timeLeft <= 0 || share.status === 'expired'

  if (isExpired) {
    return (
      <div className="mt-4 pt-4 border-t border-gray-300">
        <p className="text-red-600 font-bold">OTP has expired. Please generate a new OTP.</p>
      </div>
    )
  }

  return (
    <div className="mt-4 pt-4 border-t border-gray-300">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">
          Enter OTP to Verify:
        </label>
        <span className="text-orange-600 font-bold text-sm font-mono">
          OTP Expires In: {String(Math.floor(timeLeft / 60)).padStart(2, '0')}:{String(timeLeft % 60).padStart(2, '0')}
        </span>
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Enter 6-digit OTP"
          value={otpInput[share.id] || ''}
          onChange={(e) => setOtpInput({ ...otpInput, [share.id]: e.target.value })}
          maxLength="6"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={() => handleVerifyOTP(share.id)}
          disabled={verifying[share.id] || !otpInput[share.id]}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
        >
          {verifying[share.id] ? '⏳ Verifying...' : '✅ Verify'}
        </button>
      </div>
    </div>
  )
}

function SharePage() {
  const [files, setFiles] = useState([])
  const [users, setUsers] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedUser, setSelectedUser] = useState(null)
  const [sentShares, setSentShares] = useState([])
  const [receivedShares, setReceivedShares] = useState([])
  const [loading, setLoading] = useState(true)
  const [sharing, setSharing] = useState(false)
  const [otpInput, setOtpInput] = useState({})
  const [verifying, setVerifying] = useState({})
  const [activeTab, setActiveTab] = useState('send') // 'send' or 'received'

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      console.log('[SharePage] Loading data...')
      
      const [filesRes, usersRes, sentRes, receivedRes] = await Promise.all([
        fileAPI.listFiles(),
        authAPI.getUsers(),
        sharingAPI.getSentShares(),
        sharingAPI.getReceivedShares(),
      ])
      
      console.log('[SharePage] Files loaded:', filesRes.data.results?.length)
      console.log('[SharePage] Users response:', usersRes.data)
      console.log('[SharePage] Sent shares:', sentRes.data)
      console.log('[SharePage] Received shares:', receivedRes.data)
      
      setFiles(filesRes.data.results || [])
      
      // Handle both paginated and non-paginated user responses
      const usersList = usersRes.data.results ? usersRes.data.results : 
                        Array.isArray(usersRes.data) ? usersRes.data : []
      setUsers(usersList)
      
      // Handle both paginated and non-paginated share responses
      const sentList = sentRes.data.results ? sentRes.data.results :
                       Array.isArray(sentRes.data) ? sentRes.data : []
      setSentShares(sentList)
      
      const receivedList = receivedRes.data.results ? receivedRes.data.results :
                           Array.isArray(receivedRes.data) ? receivedRes.data : []
      setReceivedShares(receivedList)
    } catch (error) {
      console.error('[SharePage] Error loading data:', error)
      
      if (error.response?.status === 403) {
        toast.error('❌ Permission denied: You cannot access users list')
      } else if (error.response?.status === 401) {
        toast.error('❌ Session expired: Please login again')
      } else {
        toast.error('❌ Failed to load data: ' + (error.response?.data?.detail || error.message))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleShare = async (e) => {
    e.preventDefault()
    
    // Validation
    if (!selectedFile) {
      toast.error('⚠️ Please select a file')
      return
    }
    
    if (!selectedUser) {
      toast.error('⚠️ Please select a user')
      return
    }

    setSharing(true)
    try {
      console.log('[SharePage] Sharing file:', selectedFile, 'with user:', selectedUser)
      
      const response = await sharingAPI.shareFile({
        file_id: selectedFile,
        receiver_id: selectedUser,
      })
      
      toast((t) => (
        <OtpCountdownToast 
          otp={response.data.otp} 
          expiresAt={response.data.share.otp_expires_at} 
          t={t} 
        />
      ), { duration: 55000 })
      setSelectedFile(null)
      setSelectedUser(null)
      loadData()
    } catch (error) {
      console.error('[SharePage] Share error:', error)
      
      if (error.response?.status === 403) {
        toast.error('❌ Cannot share: ' + (error.response?.data?.error || 'Permission denied'))
      } else if (error.response?.status === 400) {
        toast.error('⚠️ ' + (error.response?.data?.error || 'Invalid share request'))
      } else {
        toast.error('❌ Share failed: ' + (error.response?.data?.error || error.message))
      }
    } finally {
      setSharing(false)
    }
  }

  const handleVerifyOTP = async (shareId) => {
    const otp = otpInput[shareId]
    
    if (!otp) {
      toast.error('⚠️ Please enter OTP')
      return
    }
    
    setVerifying({ ...verifying, [shareId]: true })
    try {
      console.log('[SharePage] Verifying OTP for share:', shareId)
      
      const response = await sharingAPI.verifyOTP({
        share_id: shareId,
        otp: otp,
      })
      
      console.log('[SharePage] OTP verified successfully')
      toast.success('✅ OTP verified! File access granted')
      
      // Clear input and reload
      setOtpInput({ ...otpInput, [shareId]: '' })
      loadData()
    } catch (error) {
      console.error('[SharePage] OTP verification error:', error)
      
      if (error.response?.status === 400) {
        toast.error('❌ Invalid OTP: ' + (error.response?.data?.message || 'Please check and try again'))
      } else {
        toast.error('❌ Verification failed: ' + error.message)
      }
    } finally {
      setVerifying({ ...verifying, [shareId]: false })
    }
  }

  const handleDownloadFile = async (fileId, filename) => {
    if (!fileId) {
      toast.error('❌ File ID not found')
      return
    }

    try {
      console.log('[SharePage] Downloading file ID:', fileId, 'Filename:', filename)
      
      const response = await fileAPI.downloadFile(fileId)
      
      console.log('[SharePage] Download response received, size:', response.data.size)
      
      // Create blob and download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename || 'download')
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      console.log('[SharePage] File downloaded successfully')
      toast.success('✅ File downloaded!')
    } catch (error) {
      console.error('[SharePage] Download error:', error)
      
      if (error.response?.status === 403) {
        toast.error('❌ Permission denied: ' + (error.response?.data?.error || 'Cannot download this file'))
      } else if (error.response?.status === 404) {
        toast.error('❌ File not found: Ensure OTP is verified first')
      } else {
        toast.error('❌ Download failed: ' + (error.response?.data?.error || error.message))
      }
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col pt-20 md:pt-0">
          <Header title="Share Files" />
          <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16 flex items-center justify-center">
            <div className="text-gray-500">Loading...</div>
          </main>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col pt-20 md:pt-0">
        <Header title="Share Files" />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 mt-16">
          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('send')}
              className={`px-4 py-2 font-semibold transition-colors ${
                activeTab === 'send'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📤 Send File
            </button>
            <button
              onClick={() => setActiveTab('received')}
              className={`px-4 py-2 font-semibold transition-colors ${
                activeTab === 'received'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📥 Received Files ({receivedShares.length})
            </button>
          </div>

          {/* Send Tab */}
          {activeTab === 'send' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Share Form */}
              <div className="lg:col-span-1">
                <Card>
                  <h3 className="text-xl font-bold mb-4">Share File</h3>
                  <form onSubmit={handleShare} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select File
                      </label>
                      <select
                        value={selectedFile || ''}
                        onChange={(e) => setSelectedFile(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">-- Choose File --</option>
                        {files.filter(f => f.scope === 'public').length === 0 ? (
                          <option disabled>No public files available</option>
                        ) : (
                          files.filter(f => f.scope === 'public').map(f => (
                            <option key={f.id} value={f.id}>
                              {f.original_filename} (Public)
                            </option>
                          ))
                        )}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select User
                      </label>
                      <select
                        value={selectedUser || ''}
                        onChange={(e) => setSelectedUser(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">-- Choose User --</option>
                        {users.length === 0 ? (
                          <option disabled>No users available</option>
                        ) : (
                          users.map(u => (
                            <option key={u.id} value={u.id}>
                              {u.name || u.username} ({u.email})
                            </option>
                          ))
                        )}
                      </select>
                    </div>

                    <button
                      type="submit"
                      disabled={sharing || !selectedFile || !selectedUser}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                    >
                      {sharing ? '⏳ Sharing...' : '🔗 Share File'}
                    </button>
                  </form>
                </Card>
              </div>

              {/* Sent Shares List */}
              <div className="lg:col-span-2">
                <Card>
                  <h3 className="text-xl font-bold mb-4">Files I Shared</h3>
                  {sentShares.length === 0 ? (
                    <div className="text-gray-500 text-center py-8">No files shared yet</div>
                  ) : (
                    <div className="space-y-3">
                      {sentShares.map(share => (
                        <div key={share.id} className="p-3 border border-gray-200 rounded-lg">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <p className="font-semibold text-gray-900">{share.file?.original_filename || 'Unknown File'}</p>
                              <p className="text-sm text-gray-600">
                                📨 To: {share.receiver?.name || share.receiver?.username}
                              </p>
                              <p className={`text-sm font-semibold mt-1 ${
                                share.is_verified ? 'text-green-600' : 'text-orange-600'
                              }`}>
                                {share.is_verified ? '✅ Verified' : '⏳ Awaiting OTP Verification'}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            </div>
          )}

          {/* Received Tab */}
          {activeTab === 'received' && (
            <div>
              <Card>
                <h3 className="text-xl font-bold mb-4">Files Shared With Me</h3>
                {receivedShares.length === 0 ? (
                  <div className="text-gray-500 text-center py-8">No files shared with you yet</div>
                ) : (
                  <div className="space-y-4">
                    {receivedShares.map(share => (
                      <div key={share.id} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900 text-lg">{share.file?.original_filename || 'Unknown File'}</p>
                            <p className="text-sm text-gray-600">
                              👤 From: {share.sender?.name || share.sender?.username}
                            </p>
                            {share.message && (
                              <p className="text-sm text-gray-700 mt-2 italic">💬 {share.message}</p>
                            )}
                          </div>
                          <div>
                            <p className={`text-sm font-bold px-2 py-1 rounded ${
                              share.is_verified 
                                ? 'bg-green-100 text-green-700' 
                                : 'bg-orange-100 text-orange-700'
                            }`}>
                              {share.is_verified ? '✅ Verified' : '⏳ Pending'}
                            </p>
                          </div>
                        </div>

                        {!share.is_verified && (
                          <PendingVerifySection
                            share={share}
                            otpInput={otpInput}
                            setOtpInput={setOtpInput}
                            handleVerifyOTP={handleVerifyOTP}
                            verifying={verifying}
                          />
                        )}

                        {share.is_verified && (
                          <div className="mt-4 pt-4 border-t border-gray-300">
                            <button
                              onClick={() => handleDownloadFile(share.file?.id, share.file?.original_filename)}
                              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                            >
                              📥 Download File
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default SharePage
