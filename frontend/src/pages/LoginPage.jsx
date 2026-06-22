import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../context/authStore'
import toast from 'react-hot-toast'

function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [errors, setErrors] = useState({})
  const navigate = useNavigate()
  const { login, isLoading, error } = useAuthStore()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const validateForm = () => {
    const newErrors = {}
    if (!formData.username) newErrors.username = 'Username is required'
    if (!formData.password) newErrors.password = 'Password is required'
    return newErrors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const newErrors = validateForm()

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    try {
      await login(formData.username, formData.password)
      toast.success('Login successful!')
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.message || 'Login failed')
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #581c87 50%, #1e293b 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {/* Animated Background */}
      <div style={{
        position: 'fixed',
        inset: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 0
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '400px',
          height: '400px',
          background: '#ff6b35',
          borderRadius: '50%',
          filter: 'blur(80px)',
          opacity: 0.1,
          animation: 'pulse 4s infinite'
        }} />
        <div style={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: '400px',
          height: '400px',
          background: '#ec4899',
          borderRadius: '50%',
          filter: 'blur(80px)',
          opacity: 0.1,
          animation: 'pulse 4s infinite'
        }} />
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: '50%',
          width: '400px',
          height: '400px',
          background: '#3b82f6',
          borderRadius: '50%',
          filter: 'blur(80px)',
          opacity: 0.1,
          animation: 'pulse 4s infinite'
        }} />
      </div>

      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: '450px',
        zIndex: 10
      }}>
        {/* Card */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
          padding: '40px',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '30px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              marginBottom: '20px'
            }}>
              <div style={{
                width: '60px',
                height: '60px',
                background: 'linear-gradient(135deg, #ff6b35, #ec4899)',
                borderRadius: '15px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '35px'
              }}>
                🔐
              </div>
            </div>
            <h1 style={{
              fontSize: '28px',
              fontWeight: 'bold',
              color: '#1f2937',
              margin: '0 0 10px 0'
            }}>Secure File Sharing</h1>
            <p style={{
              color: '#6b7280',
              fontSize: '15px',
              margin: '10px 0 0 0'
            }}>Sign in to your account</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div style={{
              background: '#fee2e2',
              border: '1px solid #fca5a5',
              borderRadius: '10px',
              padding: '15px',
              marginBottom: '20px',
              color: '#991b1b',
              fontSize: '14px'
            }}>
              <strong>Login Failed:</strong> {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
            {/* Username */}
            <div style={{ marginBottom: '15px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                Username or Email
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter your email or username"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '10px',
                  fontSize: '14px',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#ff6b35'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
              {errors.username && (
                <p style={{ color: '#dc2626', fontSize: '12px', marginTop: '4px' }}>
                  {errors.username}
                </p>
              )}
            </div>

            {/* Password */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '10px',
                  fontSize: '14px',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#ff6b35'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
              {errors.password && (
                <p style={{ color: '#dc2626', fontSize: '12px', marginTop: '4px' }}>
                  {errors.password}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '14px',
                background: isLoading ? '#d1d5db' : 'linear-gradient(135deg, #ff6b35, #ff5722)',
                color: 'white',
                fontWeight: 'bold',
                border: 'none',
                borderRadius: '10px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontSize: '15px',
                transition: 'all 0.3s'
              }}
              onMouseOver={(e) => !isLoading && (e.target.style.boxShadow = '0 10px 20px rgba(255, 107, 53, 0.3)')}
              onMouseOut={(e) => e.target.style.boxShadow = 'none'}
            >
              {isLoading ? '⏳ Logging in...' : '✓ Sign In'}
            </button>
          </form>

          {/* Register Link */}
          <p style={{
            textAlign: 'center',
            color: '#6b7280',
            fontSize: '14px',
            margin: 0
          }}>
            Don't have an account?{' '}
            <a href="/register" style={{
              color: '#ff6b35',
              fontWeight: '600',
              textDecoration: 'none',
              cursor: 'pointer'
            }}>
              Sign up here
            </a>
          </p>
        </div>

        {/* Footer */}
        <p style={{
          textAlign: 'center',
          color: 'rgba(255, 255, 255, 0.7)',
          fontSize: '12px',
          marginTop: '30px'
        }}>
          © 2024 Homomorphic Secure File Sharing System
        </p>
      </div>
    </div>
  )
}

export default LoginPage
