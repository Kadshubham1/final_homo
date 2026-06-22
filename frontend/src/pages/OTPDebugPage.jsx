/**
 * OTP Debugging & Testing Page
 * Shows API connectivity, configuration, and allows manual testing
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const OTPDebugPage = () => {
  const [apiUrl, setApiUrl] = useState('');
  const [status, setStatus] = useState('checking');
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [testEmail, setTestEmail] = useState('test_' + Date.now() + '@example.com');
  const [testPassword, setTestPassword] = useState('TestPassword123!');
  const [testOTP, setTestOTP] = useState('');
  const [testResults, setTestResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const url = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    setApiUrl(url);
    checkBackendStatus(url);
  }, []);

  const checkBackendStatus = async (url) => {
    try {
      const response = await axios.get(`${url}/auth/me/`, {
        headers: { 'Authorization': 'Bearer dummy' },
        timeout: 5000,
      });
      setBackendStatus('connected');
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('disconnected');
      }
    }
  };

  const addResult = (title, success, data) => {
    setTestResults(prev => [...prev, { title, success, data, time: new Date().toLocaleTimeString() }]);
  };

  const testSignup = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${apiUrl}/auth/signup-otp/`, {
        email: testEmail,
        password: testPassword,
        password2: testPassword,
        name: 'Test User',
      });

      if (response.data.otp_code) {
        setTestOTP(response.data.otp_code);
        addResult('✓ Signup Successful', true, `OTP: ${response.data.otp_code}`);
      } else {
        addResult('✗ Signup Failed', false, 'No OTP in response');
      }
    } catch (error) {
      addResult('✗ Signup Failed', false, error.response?.data || error.message);
    }
    setLoading(false);
  };

  const testVerify = async () => {
    if (!testOTP) {
      addResult('✗ Verify OTP', false, 'No OTP available. Run signup first.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${apiUrl}/auth/verify-otp/`, {
        email: testEmail,
        otp: testOTP,
      });

      addResult('✓ OTP Verification Successful', true, {
        verified: response.data.user?.is_verified,
        hasAccessToken: !!response.data.access,
      });
    } catch (error) {
      addResult('✗ OTP Verification Failed', false, error.response?.data || error.message);
    }
    setLoading(false);
  };

  const testResend = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${apiUrl}/auth/resend-otp/`, {
        email: testEmail,
      });

      addResult('✓ Resend OTP Successful', true, response.data.message);
    } catch (error) {
      addResult('✗ Resend OTP Failed', false, error.response?.data || error.message);
    }
    setLoading(false);
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <div style={{ maxWidth: '900px', margin: '40px auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>🔐 OTP System - Debug & Test Panel</h1>

      {/* Configuration */}
      <div style={{ background: '#f5f5f5', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2>Configuration</h2>
        <p><strong>API URL:</strong> {apiUrl}</p>
        <p><strong>Backend Status:</strong> <span style={{ color: backendStatus === 'connected' ? 'green' : 'red' }}>
          {backendStatus === 'connected' ? '✓ Connected' : '✗ Disconnected'}
        </span></p>
        <p><strong>Environment:</strong> {import.meta.env.MODE}</p>
      </div>

      {/* Test Controls */}
      <div style={{ background: '#e8f4f8', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2>Test Configuration</h2>
        <div style={{ marginBottom: '10px' }}>
          <label><strong>Test Email:</strong></label>
          <input
            type="email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label><strong>Test Password:</strong></label>
          <input
            type="password"
            value={testPassword}
            onChange={(e) => setTestPassword(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div>
          <label><strong>OTP Code (auto-filled after signup):</strong></label>
          <input
            type="text"
            value={testOTP}
            onChange={(e) => setTestOTP(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
            placeholder="Will be auto-filled after signup"
          />
        </div>
      </div>

      {/* Test Buttons */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          onClick={testSignup}
          disabled={loading}
          style={{
            padding: '10px 20px',
            background: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? 'Loading...' : '1. Test Signup'}
        </button>
        <button
          onClick={testVerify}
          disabled={loading || !testOTP}
          style={{
            padding: '10px 20px',
            background: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading || !testOTP ? 'not-allowed' : 'pointer',
            opacity: loading || !testOTP ? 0.6 : 1,
          }}
        >
          {loading ? 'Loading...' : '2. Test Verify OTP'}
        </button>
        <button
          onClick={testResend}
          disabled={loading}
          style={{
            padding: '10px 20px',
            background: '#FF9800',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? 'Loading...' : '3. Test Resend OTP'}
        </button>
        <button
          onClick={clearResults}
          style={{
            padding: '10px 20px',
            background: '#757575',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Clear Results
        </button>
      </div>

      {/* Results */}
      <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
        <h2>Test Results ({testResults.length})</h2>
        {testResults.length === 0 ? (
          <p style={{ color: '#999' }}>No tests run yet. Click the buttons above to start testing.</p>
        ) : (
          <div>
            {testResults.map((result, idx) => (
              <div
                key={idx}
                style={{
                  padding: '15px',
                  marginBottom: '10px',
                  background: result.success ? '#e8f5e9' : '#ffebee',
                  border: `1px solid ${result.success ? '#4CAF50' : '#f44336'}`,
                  borderRadius: '4px',
                }}
              >
                <div style={{ fontWeight: 'bold', color: result.success ? '#2e7d32' : '#c62828' }}>
                  {result.title}
                </div>
                <div style={{ fontSize: '0.9em', color: '#666', marginTop: '5px' }}>
                  <strong>Time:</strong> {result.time}
                </div>
                <div style={{ fontSize: '0.9em', color: '#333', marginTop: '5px', whiteSpace: 'pre-wrap' }}>
                  <strong>Details:</strong> {JSON.stringify(result.data, null, 2)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div style={{ background: '#fff3e0', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
        <h3>Instructions</h3>
        <ol>
          <li><strong>Test Signup:</strong> Click "1. Test Signup" to create a test account. The OTP code will auto-fill.</li>
          <li><strong>Test Verify OTP:</strong> Click "2. Test Verify OTP" to verify the account with the OTP.</li>
          <li><strong>Test Resend OTP:</strong> Click "3. Test Resend OTP" to request a new OTP (30-second cooldown).</li>
          <li>All responses will show in the Results section below.</li>
        </ol>
      </div>
    </div>
  );
};

export default OTPDebugPage;
