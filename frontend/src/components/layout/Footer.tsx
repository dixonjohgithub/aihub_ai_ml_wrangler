/**
 * File: Footer.tsx
 * 
 * Overview:
 * Application footer with project information and links
 * 
 * Purpose:
 * Provide consistent footer with project details and useful links
 * 
 * Dependencies:
 * - React for component structure
 * - Tailwind CSS for styling
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <p className="text-sm text-gray-600">
              © 2025 AI Hub AI/ML Wrangler. Built with ❤️ by the AI Hub Team.
            </p>
          </div>
          
          <div className="flex items-center space-x-6">
            <a
              href="https://github.com/dixonjohgithub/aihub_ai_ml_wrangler"
              className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <a
              href="#"
              className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
            >
              Documentation
            </a>
            <a
              href="#"
              className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
            >
              Support
            </a>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
            <p className="text-xs text-gray-500">
              Statistical data imputation and analysis tool with AI-powered recommendations
            </p>
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>v1.0.0</span>
              <span>•</span>
              <span>MIT License</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer