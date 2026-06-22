/**
 * Example React Component - Using Firebase Services
 * Copy and modify this as needed for your components
 */

import { useState, useEffect } from 'react';
import { 
  signupWithOTP, 
  loginWithEmail, 
  verifyOTP,
  logout 
} from '@/services/firebaseAuthService';
import { 
  uploadFile, 
  downloadFile 
} from '@/services/firebaseStorageService';
import { 
  getUserFiles, 
  shareFile 
} from '@/services/firestoreService';

// ============================================
// EXAMPLE 1: Signup Component
// ============================================

export const SignupExample = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await signupWithOTP(email, password, name);

    if (result.success) {
      setMessage(`✓ Signup successful! Check console for OTP code.`);
    } else {
      setMessage(`✗ Error: ${result.error}`);
    }

    setLoading(false);
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Sign Up</h2>
      <form onSubmit={handleSignup} className="space-y-4">
        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
      {message && <p className="mt-4 text-sm">{message}</p>}
    </div>
  );
};

// ============================================
// EXAMPLE 2: Verify OTP Component
// ============================================

export const VerifyOTPExample = ({ email, onVerified }) => {
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await verifyOTP(email, otp);

    if (result.success) {
      setMessage('✓ Email verified! You can now login.');
      setTimeout(onVerified, 2000);
    } else {
      setMessage(`✗ Error: ${result.error}`);
    }

    setLoading(false);
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Verify OTP</h2>
      <p className="text-sm text-gray-600 mb-4">
        Check your browser console for the 6-digit OTP code
      </p>
      <form onSubmit={handleVerify} className="space-y-4">
        <input
          type="text"
          placeholder="Enter 6-digit OTP"
          value={otp}
          onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
          maxLength="6"
          className="w-full px-4 py-2 border rounded text-center text-2xl tracking-widest"
          required
        />
        <button
          type="submit"
          disabled={loading || otp.length !== 6}
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? 'Verifying...' : 'Verify OTP'}
        </button>
      </form>
      {message && <p className="mt-4 text-sm">{message}</p>}
    </div>
  );
};

// ============================================
// EXAMPLE 3: Login Component
// ============================================

export const LoginExample = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await loginWithEmail(email, password);

    if (result.success) {
      localStorage.setItem('firebaseToken', result.token);
      localStorage.setItem('firebaseUser', JSON.stringify(result.user));
      onLoginSuccess(result.user);
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Login</h2>
      <form onSubmit={handleLogin} className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
    </div>
  );
};

// ============================================
// EXAMPLE 4: File Upload Component
// ============================================

export const FileUploadExample = ({ userId }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setMessage('');

    const result = await uploadFile(userId, file, (progressPercent) => {
      setProgress(progressPercent);
    });

    if (result.success) {
      setMessage(`✓ File uploaded! URL: ${result.file.downloadUrl}`);
      setFile(null);
      setProgress(0);
    } else {
      setMessage(`✗ Upload failed: ${result.error}`);
    }

    setUploading(false);
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Upload File</h2>
      <form onSubmit={handleUpload} className="space-y-4">
        <input
          type="file"
          onChange={handleFileChange}
          className="w-full px-4 py-2 border rounded"
          disabled={uploading}
        />
        {file && <p className="text-sm">Selected: {file.name}</p>}
        {progress > 0 && progress < 100 && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}
        <button
          type="submit"
          disabled={!file || uploading}
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {uploading ? `Uploading (${progress}%)...` : 'Upload File'}
        </button>
      </form>
      {message && <p className="mt-4 text-sm">{message}</p>}
    </div>
  );
};

// ============================================
// EXAMPLE 5: User Files List Component
// ============================================

export const UserFilesExample = ({ userId }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFiles = async () => {
      const result = await getUserFiles(userId);
      if (result.success) {
        setFiles(result.files);
      }
      setLoading(false);
    };

    fetchFiles();
  }, [userId]);

  if (loading) {
    return <div className="p-6">Loading files...</div>;
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">My Files ({files.length})</h2>
      {files.length === 0 ? (
        <p className="text-gray-600">No files yet</p>
      ) : (
        <div className="space-y-3">
          {files.map((file) => (
            <div key={file.id} className="p-4 border rounded hover:bg-gray-50">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold">{file.originalName}</p>
                  <p className="text-xs text-gray-600">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <p className="text-xs text-gray-600">
                    {file.scope === 'public' ? '🌐 Public' : '🔒 Private'}
                  </p>
                </div>
                <button
                  onClick={() => downloadFile(file.storagePath)}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                >
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// EXAMPLE 6: Share File Component
// ============================================

export const ShareFileExample = ({ fileId, fileName }) => {
  const [recipientEmail, setRecipientEmail] = useState('');
  const [sharing, setSharing] = useState(false);
  const [message, setMessage] = useState('');

  const handleShare = async (e) => {
    e.preventDefault();
    setSharing(true);

    const result = await shareFile(fileId, recipientEmail);

    if (result.success) {
      setMessage(`✓ File shared with ${recipientEmail}`);
      setRecipientEmail('');
    } else {
      setMessage(`✗ Error: ${result.error}`);
    }

    setSharing(false);
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Share File</h2>
      <p className="text-sm text-gray-600 mb-4">{fileName}</p>
      <form onSubmit={handleShare} className="space-y-4">
        <input
          type="email"
          placeholder="Recipient email"
          value={recipientEmail}
          onChange={(e) => setRecipientEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <button
          type="submit"
          disabled={sharing}
          className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 disabled:opacity-50"
        >
          {sharing ? 'Sharing...' : 'Share File'}
        </button>
      </form>
      {message && <p className="mt-4 text-sm">{message}</p>}
    </div>
  );
};

// ============================================
// EXAMPLE 7: Logout Component
// ============================================

export const LogoutExample = ({ onLogoutSuccess }) => {
  const handleLogout = async () => {
    const result = await logout();
    if (result.success) {
      localStorage.removeItem('firebaseToken');
      localStorage.removeItem('firebaseUser');
      onLogoutSuccess();
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700"
    >
      Logout
    </button>
  );
};

export default {
  SignupExample,
  VerifyOTPExample,
  LoginExample,
  FileUploadExample,
  UserFilesExample,
  ShareFileExample,
  LogoutExample,
};
