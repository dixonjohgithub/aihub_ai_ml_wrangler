/**
 * File: pages/NotFoundPage.tsx
 * 
 * Overview:
 * 404 Not Found page for unmatched routes
 * 
 * Purpose:
 * Provides a user-friendly 404 page with navigation options
 * 
 * Dependencies:
 * - React for component structure
 * - React Router for navigation
 * - Button component for actions
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/Button';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center px-6">
      <div className="text-center">
        <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-8">
          <svg className="w-12 h-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Page Not Found</h2>
        <p className="text-gray-600 mb-8 max-w-md mx-auto">
          The page you're looking for doesn't exist. It might have been moved, deleted, 
          or you entered the wrong URL.
        </p>
        
        <div className="space-x-4">
          <Link to="/home">
            <Button variant="primary">
              Go to Dashboard
            </Button>
          </Link>
          <Button variant="secondary" onClick={() => window.history.back()}>
            Go Back
          </Button>
        </div>
        
        <div className="mt-12 text-sm text-gray-500">
          <p>Need help? <a href="#" className="text-primary-600 hover:text-primary-700">Contact Support</a></p>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;