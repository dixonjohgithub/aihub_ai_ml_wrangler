/**
 * File: main.tsx
 * 
 * Overview:
 * React application entry point
 * 
 * Purpose:
 * Initialize React app with root component and global styles
 * 
 * Dependencies:
 * - react
 * - react-dom
 * - ./App
 * - ./index.css
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)