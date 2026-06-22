/**
 * Reusable UI Components
 */

// Loading Spinner
export function Spinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="spinner" style={{
        borderTopColor: '#ff6b35',
        width: '40px',
        height: '40px',
      }} />
    </div>
  )
}

// Loading Overlay
export function LoadingOverlay() {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 shadow-2xl">
        <Spinner />
        <p className="mt-4 text-gray-600 font-semibold">Loading...</p>
      </div>
    </div>
  )
}

// Modal Component
export function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-2xl',
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className={`modal-content ${sizes[size]}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition"
          >
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

// Alert Component
export function Alert({ type = 'info', title, message, onClose }) {
  const colors = {
    success: 'bg-green-50 border-green-300 text-green-900',
    error: 'bg-red-50 border-red-300 text-red-900',
    warning: 'bg-yellow-50 border-yellow-300 text-yellow-900',
    info: 'bg-blue-50 border-blue-300 text-blue-900',
  }

  return (
    <div className={`border-l-4 p-4 rounded ${colors[type]}`}>
      <div className="flex justify-between items-start">
        <div>
          {title && <h4 className="font-semibold">{title}</h4>}
          <p className="text-sm mt-1">{message}</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="ml-4">
            ✕
          </button>
        )}
      </div>
    </div>
  )
}

// Badge Component
export function Badge({ type = 'info', children }) {
  const styles = {
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
    info: 'bg-blue-100 text-blue-800',
  }

  return (
    <span className={`badge ${styles[type]}`}>
      {children}
    </span>
  )
}

// Card Component
export function Card({ children, className = "", hover = false }) {
  return (
    <div className={`card ${hover ? 'card-hover' : ''} ${className}`}>
      {children}
    </div>
  )
}

// Button Component
export function Button({ variant = 'primary', disabled = false, children, ...props }) {
  const styles = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
  }

  return (
    <button
      className={`${styles[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}

// Input Component
export function Input({ label, error, ...props }) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          {label}
        </label>
      )}
      <input className="input-field" {...props} />
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  )
}

// No Data State
export function NoData({ message = "No data available" }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="text-6xl mb-4">📭</div>
      <p className="text-gray-600 text-lg font-medium">{message}</p>
    </div>
  )
}
