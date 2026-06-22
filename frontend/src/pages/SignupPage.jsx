/**
 * SignupPage Component
 * User registration form with email and password validation
 * On successful signup, redirects to OTP verification page
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signupWithOTP } from '../services/authService';
import './SignupPage.css';

const SignupPage = () => {
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password2: '',
    name: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [otpCode, setOtpCode] = useState('');

  /**
   * Handle form input changes
   */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  /**
   * Validate form data
   */
  const validateForm = () => {
    const newErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Confirm password validation
    if (!formData.password2) {
      newErrors.password2 = 'Please confirm your password';
    } else if (formData.password !== formData.password2) {
      newErrors.password2 = 'Passwords do not match';
    }

    // Name validation (optional but if provided)
    if (formData.name && formData.name.length > 255) {
      newErrors.name = 'Name is too long';
    }

    return newErrors;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form
    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    setErrors({});
    setSuccessMessage('');

    try {
      // Call signup API
      const response = await signupWithOTP({
        email: formData.email.toLowerCase(),
        password: formData.password,
        password2: formData.password2,
        name: formData.name,
      });

      if (response.success) {
        // Store email for OTP verification
        localStorage.setItem('signup_email', formData.email.toLowerCase());
        
        // Store OTP if returned (development mode)
        if (response.data?.otp_code) {
          setOtpCode(response.data.otp_code);
          localStorage.setItem('signup_otp', response.data.otp_code);
          console.log('OTP Code:', response.data.otp_code);
        }
        
        setSuccessMessage('Signup successful! Check the OTP code below or check your email.');
        
        // Redirect to OTP verification page after 3 seconds
        setTimeout(() => {
          navigate('/verify-otp');
        }, 3000);
      } else {
        // Handle API errors
        if (typeof response.error === 'object') {
          setErrors(response.error);
        } else {
          setErrors({ general: response.error || 'An error occurred during signup' });
        }
      }
    } catch (error) {
      console.error('Signup error:', error);
      setErrors({ general: 'An unexpected error occurred. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-form-wrapper">
        <div className="signup-header">
          <h1>Create Account</h1>
          <p>Join our secure file sharing platform</p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="alert alert-success">
            <i className="check-icon">✓</i>
            {successMessage}
            {otpCode && (
              <div style={{ marginTop: '15px', padding: '15px', background: 'white', borderRadius: '5px', textAlign: 'center' }}>
                <p style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#666' }}>Your OTP Code (for testing):</p>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2563eb', letterSpacing: '5px', fontFamily: 'monospace' }}>
                  {otpCode}
                </div>
                <p style={{ margin: '10px 0 0 0', fontSize: '12px', color: '#999' }}>This code will expire in 5 minutes</p>
              </div>
            )}
          </div>
        )}

        {/* General Error Message */}
        {errors.general && (
          <div className="alert alert-error">
            <i className="error-icon">!</i>
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="signup-form">
          {/* Full Name Field */}
          <div className="form-group">
            <label htmlFor="name">Full Name (Optional)</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="John Doe"
              className={`form-input ${errors.name ? 'input-error' : ''}`}
              disabled={loading}
            />
            {errors.name && <p className="error-text">{errors.name}</p>}
          </div>

          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="you@example.com"
              className={`form-input ${errors.email ? 'input-error' : ''}`}
              disabled={loading}
              required
            />
            {errors.email && <p className="error-text">{errors.email}</p>}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="At least 8 characters"
              className={`form-input ${errors.password ? 'input-error' : ''}`}
              disabled={loading}
              required
            />
            {errors.password && <p className="error-text">{errors.password}</p>}
            <p className="password-hint">Must be at least 8 characters long</p>
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label htmlFor="password2">Confirm Password</label>
            <input
              type="password"
              id="password2"
              name="password2"
              value={formData.password2}
              onChange={handleInputChange}
              placeholder="Confirm your password"
              className={`form-input ${errors.password2 ? 'input-error' : ''}`}
              disabled={loading}
              required
            />
            {errors.password2 && <p className="error-text">{errors.password2}</p>}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className={`submit-btn ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Login Link */}
        <div className="signup-footer">
          <p>
            Already have an account?{' '}
            <a href="/login" className="login-link">
              Sign in here
            </a>
          </p>
        </div>
      </div>

      {/* Right Side Decoration */}
      <div className="signup-decoration">
        <div className="decoration-content">
          <h2>Why Join Us?</h2>
          <ul className="features-list">
            <li>✓ End-to-end file encryption</li>
            <li>✓ Secure file sharing</li>
            <li>✓ Email OTP verification</li>
            <li>✓ Advanced security monitoring</li>
            <li>✓ USB detection & logs</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
