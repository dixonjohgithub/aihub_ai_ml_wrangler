/**
 * File: components/Footer.tsx
 * 
 * Overview:
 * Application footer with links and project information
 * 
 * Purpose:
 * Provides footer information, links, and branding
 * 
 * Dependencies:
 * - React for component structure
 * - Tailwind CSS for styling
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand and Description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <span className="font-bold text-gray-900">AI Hub AI/ML Wrangler</span>
            </div>
            <p className="text-sm text-gray-600 mb-4 max-w-md">
              A sophisticated statistical data imputation and analysis tool with AI-powered 
              recommendations for feature engineering, encoding, and imputation strategies.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com/dixonjohgithub/aihub_ai_ml_wrangler"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </a>
              <a
                href="#"
                className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Quick Links</h3>
            <ul className="space-y-3">
              <li>
                <a href="/home" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  Dashboard
                </a>
              </li>
              <li>
                <a href="/import" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  Import Data
                </a>
              </li>
              <li>
                <a href="/analysis" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  Analysis
                </a>
              </li>
              <li>
                <a href="/results" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  Results
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Resources</h3>
            <ul className="space-y-3">
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  API Reference
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  Support
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200">
                  Status
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>&copy; {currentYear} AI Hub Team</span>
              <span>•</span>
              <a href="#" className="hover:text-gray-900 transition-colors duration-200">
                Privacy Policy
              </a>
              <span>•</span>
              <a href="#" className="hover:text-gray-900 transition-colors duration-200">
                Terms of Service
              </a>
            </div>
            
            <div className="mt-4 md:mt-0 flex items-center space-x-2 text-sm text-gray-500">
              <span>Built with</span>
              <span className="text-red-500">♥</span>
              <span>by the AI Hub Team</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;