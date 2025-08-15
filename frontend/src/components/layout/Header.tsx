/**
 * File: Header.tsx
 * 
 * Overview:
 * Application header with navigation and branding
 * 
 * Purpose:
 * Provide consistent top navigation and application identity
 * 
 * Dependencies:
 * - React Router for navigation
 * - Tailwind CSS for styling
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'
import { Link } from 'react-router-dom'

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  AI/ML Wrangler
                </h1>
                <p className="text-xs text-gray-500">Data Imputation & Analysis</p>
              </div>
            </Link>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            <Link
              to="/"
              className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/import"
              className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Import
            </Link>
            <Link
              to="/analyze"
              className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Analyze
            </Link>
            <Link
              to="/impute"
              className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Impute
            </Link>
            <Link
              to="/export"
              className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Export
            </Link>
          </nav>

          <div className="flex items-center space-x-4">
            <button className="text-gray-500 hover:text-gray-900 p-2 rounded-md">
              <span className="sr-only">Settings</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header