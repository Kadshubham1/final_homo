import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'
import { Toaster } from 'react-hot-toast'

const root = document.getElementById('root')

if (!root) {
  document.body.innerHTML = '<div style="padding:40px; color:red; font-family:monospace; background:#ffebee; font-size:16px;"><strong>ERROR:</strong> Root element not found!</div>'
} else {
  try {
    const reactRoot = ReactDOM.createRoot(root)
    reactRoot.render(
      <React.StrictMode>
        <App />
        <Toaster position="top-right" />
      </React.StrictMode>,
    )
  } catch (error) {
    root.innerHTML = `<div style="padding:40px; color:#d32f2f; font-family:monospace; background:#ffebee; font-size:14px; line-height:1.6;"><strong>React Render Error:</strong><br><br>${error.message || error}</div>`
  }
}
