/**
 * File: App.tsx
 * 
 * Overview:
 * Main application component that sets up routing and layout structure
 * 
 * Purpose:
 * Define the overall application structure and routing configuration
 * 
 * Dependencies:
 * - React Router for navigation
 * - Layout components for UI structure
 * - Page components for different routes
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import ImportPage from './pages/ImportPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/import" element={<ImportPage />} />
        <Route path="/analyze" element={<div>Analyze Page - Coming Soon</div>} />
        <Route path="/impute" element={<div>Imputation Page - Coming Soon</div>} />
        <Route path="/export" element={<div>Export Page - Coming Soon</div>} />
      </Routes>
    </Layout>
  )
}

export default App