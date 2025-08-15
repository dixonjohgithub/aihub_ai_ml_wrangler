/**
 * File: Layout.tsx
 * 
 * Overview:
 * Main layout component that wraps all pages with consistent structure
 * 
 * Purpose:
 * Provide consistent header, sidebar, and footer across all pages
 * 
 * Dependencies:
 * - Header, Sidebar, Footer components
 * - React for component structure
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import Footer from './Footer'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  )
}

export default Layout