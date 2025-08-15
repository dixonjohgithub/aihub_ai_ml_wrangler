/**
 * File: App.tsx
 * 
 * Overview:
 * Main application component
 * 
 * Purpose:
 * Root component that houses the data preview functionality
 * 
 * Dependencies:
 * - react
 * - ./components/DataPreview
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'
import DataPreview from './components/DataPreview'

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              AI Hub AI/ML Wrangler
            </h1>
            <p className="text-sm text-gray-500">
              Data Preview & Analysis
            </p>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DataPreview />
      </main>
    </div>
  )
}

export default App