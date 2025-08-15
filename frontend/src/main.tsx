/**
 * File: main.tsx
 * 
 * Overview:
 * Application entry point that renders the React app and sets up providers
 * 
 * Purpose:
 * Initialize the React application with routing and global providers
 * 
 * Dependencies:
 * - React and ReactDOM for rendering
 * - React Router for routing
 * - CSS imports for styling
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)