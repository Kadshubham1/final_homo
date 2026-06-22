/**
 * Auth Store - Global state management using Zustand
 * Handles user authentication and session with JWT tokens
 */
import { create } from 'zustand'
import Cookies from 'js-cookie'
import { authAPI } from '../services/api'

const useAuthStore = create((set, get) => ({
  // State
  user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
  tokens: null,
  isAuthenticated: !!Cookies.get('access_token') || !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  // Actions
  setUser: (user) => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      localStorage.removeItem('user')
    }
    set({ user })
  },
  
  setTokens: (tokens) => {
    // Store in both cookies and localStorage for redundancy
    Cookies.set('access_token', tokens.access, { expires: 1 })
    localStorage.setItem('access_token', tokens.access)
    
    Cookies.set('refresh_token', tokens.refresh, { expires: 7 })
    localStorage.setItem('refresh_token', tokens.refresh)
    
    console.log('[Auth] Tokens stored in cookies and localStorage')
    set({ tokens })
  },
  
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  login: async (username, password) => {
    set({ isLoading: true, error: null })
    try {
      console.log('[Auth] Attempting login for:', username)
      const response = await authAPI.login(username, password)
      const data = response.data

      console.log('[Auth] Login successful, storing tokens')
      Cookies.set('access_token', data.access, { expires: 1 })
      localStorage.setItem('access_token', data.access)
      Cookies.set('refresh_token', data.refresh, { expires: 7 })
      localStorage.setItem('refresh_token', data.refresh)

      set({
        user: data.user,
        tokens: { access: data.access, refresh: data.refresh },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    } catch (error) {
      const errorData = error.response?.data
      const errorMsg = errorData?.error || errorData?.detail || error.message || 'Login failed. Please check backend connection.'
      console.error('[Auth] Login error:', errorMsg)
      set({ error: errorMsg, isLoading: false })
      throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
    }
  },

  register: async (username, email, name, mobile, password, password2) => {
    set({ isLoading: true, error: null })
    try {
      console.log('[Auth] Attempting registration for:', username)
      const response = await authAPI.register({
        username,
        email,
        name,
        mobile,
        password,
        password2,
      })

      const data = response.data
      console.log('[Auth] Registration successful')

      // Store user if returned by the API
      if (data.user) {
        set({ user: data.user })
        localStorage.setItem('user', JSON.stringify(data.user))
      }

      set({ isLoading: false })
      return data
    } catch (error) {
      const errorMsg = error.response?.data || error.message || 'Registration failed'
      console.error('[Auth] Registration error:', errorMsg)
      set({ error: errorMsg, isLoading: false })
      throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
    }
  },

  logout: () => {
    console.log('[Auth] Logging out user')
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    set({
      user: null,
      tokens: null,
      isAuthenticated: false,
    })
  },

  hydrateUser: async () => {
    const token = Cookies.get('access_token') || localStorage.getItem('access_token')
    if (!token) {
      set({ user: null, tokens: null, isAuthenticated: false })
      return null
    }
    set({ isLoading: true, error: null })
    try {
      const response = await authAPI.getMe()
      const userData = response.data
      set({ user: userData, isAuthenticated: true, isLoading: false })
      localStorage.setItem('user', JSON.stringify(userData))
      return userData
    } catch (error) {
      const errorData = error.response?.data
      const errorMsg = errorData?.error || errorData?.detail || error.message || 'Failed to hydrate user session.'
      console.error('[Auth] Hydration failed:', errorMsg)
      Cookies.remove('access_token')
      Cookies.remove('refresh_token')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      set({ user: null, tokens: null, isAuthenticated: false, isLoading: false })
      return null
    }
  },

  getToken: () => {
    return Cookies.get('access_token') || localStorage.getItem('access_token')
  },

  isAdmin: () => {
    const state = get()
    return state.user?.role === 'admin'
  },
}))

export default useAuthStore
