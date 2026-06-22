/**
 * API Service - Axios configuration and API endpoints with JWT Auth
 */
import axios from 'axios'
import Cookies from 'js-cookie'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: Add JWT token to all requests
apiClient.interceptors.request.use(
  (config) => {
    // Try to get token from cookies first, then localStorage
    let token = Cookies.get('access_token')
    if (!token) {
      token = localStorage.getItem('access_token')
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('[API] Added Authorization header')
    } else {
      console.warn('[API] No access token found')
    }
    
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor: Handle token expiration and errors
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API] ${response.config.method.toUpperCase()} ${response.config.url} - ${response.status}`)
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    console.error(`[API Error] ${error.response?.status} - ${error.response?.data?.detail || error.message}`)
    
    // Handle 403 Forbidden - likely permission issue
    if (error.response?.status === 403) {
      console.error('[API] 403 Forbidden - Check user permissions or token validity')
    }
    
    // Handle 401 Unauthorized - token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = Cookies.get('refresh_token') || localStorage.getItem('refresh_token')
        
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }
        
        console.log('[API] Attempting to refresh token...')
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        })
        
        const { access } = response.data
        
        // Update token in both storage locations
        Cookies.set('access_token', access, { expires: 1 })
        localStorage.setItem('access_token', access)
        
        console.log('[API] Token refreshed successfully')
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        console.error('[API] Token refresh failed, redirecting to login')
        
        // Clear all auth data
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// ============ Auth APIs ============
export const authAPI = {
  login: (username, password) =>
    apiClient.post('/auth/login/', { username, password }),
  
  register: (data) =>
    apiClient.post('/auth/register/', data),
  
  getMe: () =>
    apiClient.get('/auth/me/'),
  
  updateMe: (data) =>
    apiClient.put('/auth/me/', data),
  
  changePassword: (data) =>
    apiClient.post('/auth/change-password/', data),
  
  getUsers: () =>
    apiClient.get('/auth/users/'),
  
  getAdminStats: () =>
    apiClient.get('/auth/admin/stats/'),
}

// ============ File APIs ============
export const fileAPI = {
  listFiles: (page = 1) =>
    apiClient.get(`/files/?page=${page}`),
  
  uploadFile: (formData) =>
    apiClient.post('/files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  getFileDetails: (id) =>
    apiClient.get(`/files/${id}/`),
  
  downloadFile: (id) =>
    apiClient.get(`/files/${id}/download/`, { responseType: 'blob' }),
  
  deleteFile: (id) =>
    apiClient.delete(`/files/${id}/`),
  
  searchFiles: (query) =>
    apiClient.get(`/files/search/?q=${query}`),
  
  getStats: () =>
    apiClient.get('/files/stats/'),
  
  getAllFiles: () =>
    apiClient.get('/files/admin/all/'),
}

// ============ Sharing APIs ============
export const sharingAPI = {
  shareFile: (data) =>
    apiClient.post('/sharing/', data),
  
  getSentShares: () =>
    apiClient.get('/sharing/sent/'),
  
  getReceivedShares: () =>
    apiClient.get('/sharing/received/'),
  
  verifyOTP: (data) =>
    apiClient.post('/sharing/verify_otp/', data),
  
  resendOTP: (data) =>
    apiClient.post('/sharing/resend_otp/', data),
  
  getNotifications: () =>
    apiClient.get('/sharing/notifications/'),
  
  getAllShares: () =>
    apiClient.get('/sharing/admin/all/'),
}

// ============ Security Logs APIs ============
// Transparent USB Detection - Event logging only
export const securityAPI = {
  // Advanced Security Events (Photos, Face Rec, MTP)
  getSecurityEvents: () =>
    apiClient.get('/security/event/'),

  // USB Activity Logs
  getLogs: () =>
    apiClient.get('/security/usb-log/'),
  
  getUSBStats: () =>
    apiClient.get('/security/usb-log/summary/'),
  
  logUSBEvent: (data) =>
    apiClient.post('/security/usb-log/', data),
  
  // Security Alerts
  getAlerts: () =>
    apiClient.get('/security/alerts/'),
  
  getUnresolvedAlerts: () =>
    apiClient.get('/security/alerts/unresolved/'),
  
  resolveAlert: (id, notes) =>
    apiClient.post(`/security/alerts/${id}/resolve/`, { notes }),
  
  // System Logs
  getSystemLogs: () =>
    apiClient.get('/security/system-logs/'),
}

export default apiClient
