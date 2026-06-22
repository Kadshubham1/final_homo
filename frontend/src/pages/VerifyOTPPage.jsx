/**
 * VerifyOTPPage Component
 * OTP code verification form
 * Allows users to verify their email with OTP code
 * Includes resend OTP button with cooldown timer
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { verifyOTP, resendOTP } from '../services/authService';
import './VerifyOTPPage.css';

const VerifyOTPPage = () => {
  const navigate = useNavigate();

  // State
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [resendLoading, setResendLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [otpAttempts, setOtpAttempts] = useState(0);

  /**
   * Load email from localStorage on component mount
   */
  useEffect(() => {
    const storedEmail = localStorage.getItem('signup_email');
    if (storedEmail) {
      setEmail(storedEmail);
    } else {
      // Redirect to signup if no email in localStorage
      setTimeout(() => navigate('/signup'), 1000);
    }
    
    // Auto-fill OTP if available (from development/testing)
    const storedOTP = localStorage.getItem('signup_otp');
    if (storedOTP) {
      setOtp(storedOTP);
      localStorage.removeItem('signup_otp'); // Remove after use
    }
  }, [navigate]);

  /**
   * Countdown timer for resend button
   */
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  /**
   * Auto-submit OTP when all 6 digits are entered
   */
  useEffect(() => {
    if (otp.length === 6 && /^\d{6}$/.test(otp)) {
      handleVerifyOTP();
    }
  }, [otp]);

  /**
   * Handle OTP input - only allow digits
   */
  const handleOtpChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setOtp(value);

    // Clear error when user starts typing
    if (errors.otp) {
      setErrors((prev) => ({
        ...prev,
        otp: '',
      }));
    }
  };

  /**
   * Verify OTP
   */
  const handleVerifyOTP = async () => {
    // Validate OTP
    if (!otp) {
      setErrors({ otp: 'Please enter the OTP code' });
      return;
    }

    if (otp.length !== 6 || !/^\d{6}$/.test(otp)) {
      setErrors({ otp: 'OTP must be 6 digits' });
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const response = await verifyOTP(email, otp);

      if (response.success) {
        setSuccessMessage('✓ Email verified successfully! Redirecting...');

        // Clear stored email
        localStorage.removeItem('signup_email');

        // Redirect to dashboard or home after 2 seconds
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      } else {
        setOtpAttempts((prev) => prev + 1);

        // Show error message
        if (typeof response.error === 'object' && response.error.otp) {
          setErrors({ otp: response.error.otp });
        } else if (typeof response.error === 'object' && response.error.email) {
          setErrors({ email: response.error.email });
        } else {
          setErrors({ otp: response.error || 'Invalid OTP. Please try again.' });
        }

        // Clear OTP input on error
        setOtp('');
      }
    } catch (error) {
      console.error('OTP verification error:', error);
      setErrors({ general: 'An unexpected error occurred. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Resend OTP
   */
  const handleResendOTP = async () => {
    setResendLoading(true);
    setErrors({});

    try {
      const response = await resendOTP(email);

      if (response.success) {
        setSuccessMessage('✓ New OTP sent to your email');
        setOtp('');
        setOtpAttempts(0);
        setResendCooldown(30); // 30 second cooldown

        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setErrors({
          resend: response.error || 'Failed to resend OTP. Please try again.',
        });
      }
    } catch (error) {
      console.error('Resend OTP error:', error);
      setErrors({ resend: 'An unexpected error occurred. Please try again.' });
    } finally {
      setResendLoading(false);
    }
  };

  /**
   * Handle back button - go back to signup
   */
  const handleBackToSignup = () => {
    navigate('/signup');
  };

  return (
    <div className="verify-otp-container">
      <div className="verify-otp-wrapper">
        <div className="verify-otp-header">
          <button className="back-btn" onClick={handleBackToSignup} title="Back to signup">
            ←
          </button>
          <h1>Verify Your Email</h1>
          <p>We've sent a 6-digit code to <strong>{email}</strong></p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="alert alert-success">
            {successMessage}
          </div>
        )}

        {/* General Error Message */}
        {errors.general && (
          <div className="alert alert-error">
            {errors.general}
          </div>
        )}

        {/* Resend Error Message */}
        {errors.resend && (
          <div className="alert alert-error">
            {errors.resend}
          </div>
        )}

        {/* Email Error Message */}
        {errors.email && (
          <div className="alert alert-error">
            {errors.email}
          </div>
        )}

        <form onSubmit={(e) => { e.preventDefault(); handleVerifyOTP(); }} className="verify-form">
          {/* OTP Input */}
          <div className="form-group">
            <label htmlFor="otp">Enter OTP Code</label>
            <div className="otp-input-wrapper">
              <input
                type="text"
                id="otp"
                value={otp}
                onChange={handleOtpChange}
                placeholder="000000"
                maxLength="6"
                className={`otp-input ${errors.otp ? 'input-error' : ''}`}
                disabled={loading}
                autoFocus
                inputMode="numeric"
              />
              <div className="otp-display">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className="otp-digit">
                    {otp[index] || ''}
                  </div>
                ))}
              </div>
            </div>
            {errors.otp && <p className="error-text">{errors.otp}</p>}
            <p className="otp-hint">Code expires in 5 minutes</p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className={`submit-btn ${loading ? 'loading' : ''}`}
            disabled={loading || otp.length !== 6}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Verifying...
              </>
            ) : (
              'Verify OTP'
            )}
          </button>
        </form>

        {/* Resend OTP Section */}
        <div className="resend-section">
          <p className="resend-label">Didn't receive the code?</p>
          <button
            type="button"
            className={`resend-btn ${resendCooldown > 0 ? 'disabled' : ''} ${resendLoading ? 'loading' : ''}`}
            onClick={handleResendOTP}
            disabled={resendCooldown > 0 || resendLoading}
          >
            {resendCooldown > 0 ? (
              <>
                Resend in {resendCooldown}s
              </>
            ) : resendLoading ? (
              <>
                <span className="spinner small"></span>
                Sending...
              </>
            ) : (
              'Resend OTP'
            )}
          </button>
        </div>

        {/* Attempts Counter */}
        {otpAttempts > 0 && otpAttempts < 3 && (
          <div className="attempts-info">
            ⚠️ You have {3 - otpAttempts} attempt(s) remaining
          </div>
        )}

        {/* Footer */}
        <div className="verify-footer">
          <p>
            Wrong email?{' '}
            <button className="change-email-link" onClick={handleBackToSignup}>
              Create new account
            </button>
          </p>
        </div>
      </div>

      {/* Left Side Info */}
      <div className="verify-info">
        <div className="info-content">
          <div className="info-icon">📧</div>
          <h2>Check Your Email</h2>
          <p>We've sent a 6-digit verification code to your email address.</p>
          <p className="info-subtext">
            If you don't see the email, check your spam folder or request a new code.
          </p>
        </div>
      </div>
    </div>
  );
};

export default VerifyOTPPage;
