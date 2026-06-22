/**
 * Auth API Service
 * Axios-based service for all authentication API calls
 * Handles signup, OTP verification, login, etc.
 */

import axios from 'axios';

// Create axios instance with base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

console.log('[AuthService] API Base URL:', API_BASE_URL);

const authAPI = axios.create({
  baseURL: `${API_BASE_URL}/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Add token to requests if available
authAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle response errors
authAPI.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Signup with OTP
 * @param {Object} userData - { email, password, password2, name }
 * @returns {Promise} Response with user data
 */
export const signupWithOTP = async (userData) => {
  try {
    console.log('[SignupWithOTP] Sending request to:', `${authAPI.defaults.baseURL}/signup-otp/`);
    console.log('[SignupWithOTP] Data:', { ...userData, password: '***', password2: '***' });
    
    const response = await authAPI.post('/signup-otp/', userData);
    
    console.log('[SignupWithOTP] Success:', response.status);
    
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('[SignupWithOTP] Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
      url: error.config?.url,
    });
    
    // Extract error message
    let errorMsg = error.message;
    if (error.response?.data) {
      if (typeof error.response.data === 'object') {
        // If it's an object with field errors
        Object.values(error.response.data).forEach(err => {
          if (Array.isArray(err)) {
            errorMsg = err[0] || errorMsg;
          } else if (typeof err === 'string') {
            errorMsg = err;
          }
        });
      } else {
        errorMsg = error.response.data;
      }
    }
    
    return {
      success: false,
      error: errorMsg,
    };
  }
};

/**
 * Verify OTP
 * @param {string} email - User email
 * @param {string} otp - OTP code
 * @returns {Promise} Response with user data and tokens
 */
export const verifyOTP = async (email, otp) => {
  try {
    console.log('[VerifyOTP] Sending request to:', `${authAPI.defaults.baseURL}/verify-otp/`);
    console.log('[VerifyOTP] Email:', email, 'OTP Length:', otp.length);
    
    const response = await authAPI.post('/verify-otp/', { email, otp });
    
    console.log('[VerifyOTP] Success:', response.status);
    
    // Store tokens
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      console.log('[VerifyOTP] Tokens saved to localStorage');
    }
    
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error('[VerifyOTP] Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
    });
    
    // Extract error message
    let errorMsg = error.message;
    if (error.response?.data) {
      if (typeof error.response.data === 'object') {
        Object.values(error.response.data).forEach(err => {
          if (Array.isArray(err)) {
            errorMsg = err[0] || errorMsg;
          } else if (typeof err === 'string') {
            errorMsg = err;
          }
        });
      }
    }
    
    return {
      success: false,
      error: errorMsg,
    };
  }
};

/**
 * Resend OTP
 * @param {string} email - User email
 * @returns {Promise} Response message
 */
export const resendOTP = async (email) => {
  try {
    const response = await authAPI.post('/resend-otp/', { email });
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.response?.data || error.message,
    };
  }
};

/**
 * Login user
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise} Response with tokens
 */
export const login = async (username, password) => {
  try {
    const response = await authAPI.post('/login/', { username, password });
    
    // Store tokens
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.response?.data?.error || error.response?.data || error.message,
    };
  }
};

/**
 * Logout user
 * @returns {Promise}
 */
export const logout = async () => {
  try {
    await authAPI.post('/logout/');
    
    // Clear tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    return { success: true };
  } catch (error) {
    // Clear tokens anyway
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    return { success: true };
  }
};

/**
 * Get current user profile
 * @returns {Promise}
 */
export const getCurrentUser = async () => {
  try {
    const response = await authAPI.get('/me/');
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data || error.message,
    };
  }
};

export default authAPI;
