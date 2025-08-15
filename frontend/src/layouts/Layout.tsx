/**
 * File: layouts/Layout.tsx
 * 
 * Overview:
 * Main layout component providing the application structure
 * 
 * Purpose:
 * Wraps all pages with consistent header, sidebar, and footer layout
 * 
 * Dependencies:
 * - React Router for outlet rendering
 * - Header, Sidebar, Footer components
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';

const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header />
      
      {/* Main Content Area */}
      <div className="flex">
        {/* Sidebar */}
        <Sidebar />
        
        {/* Main Content */}
        <main className="flex-1 p-6 ml-64">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Layout;