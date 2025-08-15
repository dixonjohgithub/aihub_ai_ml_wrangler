/**
 * File: main.tsx
 * 
 * Overview:
 * Main entry point for the React application
 * 
 * Purpose:
 * Initializes the React app with routing and renders the root component
 * 
 * Dependencies:
 * - React 18 with concurrent features
 * - React Router DOM for routing
 * - Base CSS styles
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

// Get root element
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found. Make sure index.html has a div with id="root"');
}

// Create React 18 root
const root = ReactDOM.createRoot(rootElement);

// Render app with router
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);