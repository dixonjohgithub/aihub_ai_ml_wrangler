/**
 * File: components/Sidebar.tsx
 * 
 * Overview:
 * Application sidebar with workflow navigation and quick actions
 * 
 * Purpose:
 * Provides workflow-based navigation matching Data Wrangler patterns
 * 
 * Dependencies:
 * - React Router for navigation
 * - Tailwind CSS for styling
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const location = useLocation();

  const workflowSteps = [
    {
      id: 'import',
      title: 'Import Data',
      path: '/import',
      description: 'Upload and configure datasets',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      ),
    },
    {
      id: 'analysis',
      title: 'Analyze',
      path: '/analysis',
      description: 'AI-powered data analysis',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      id: 'configure',
      title: 'Configure',
      path: '/analysis',
      description: 'Set imputation strategies',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
        </svg>
      ),
    },
    {
      id: 'process',
      title: 'Process',
      path: '/results',
      description: 'Execute imputation jobs',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      id: 'results',
      title: 'Results',
      path: '/results',
      description: 'View and download outputs',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
  ];

  const quickActions = [
    {
      title: 'Recent Datasets',
      items: [
        { name: 'sample_data.csv', path: '/import', size: '2.3 MB' },
        { name: 'customer_data.json', path: '/import', size: '1.8 MB' },
        { name: 'survey_results.csv', path: '/import', size: '954 KB' },
      ],
    },
    {
      title: 'Running Jobs',
      items: [
        { name: 'Correlation Analysis', path: '/results', status: 'running' },
        { name: 'ML Imputation', path: '/results', status: 'queued' },
      ],
    },
  ];

  const isActiveRoute = (path: string): boolean => {
    return location.pathname === path;
  };

  return (
    <aside className="fixed left-0 top-16 w-64 h-full bg-white border-r border-gray-200 overflow-y-auto">
      <div className="p-6">
        {/* Workflow Section */}
        <div className="mb-8">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Workflow
          </h3>
          <nav className="space-y-2">
            {workflowSteps.map((step) => (
              <Link
                key={step.id}
                to={step.path}
                className={`sidebar-item group ${
                  isActiveRoute(step.path) ? 'active' : ''
                }`}
              >
                <span className="flex-shrink-0">{step.icon}</span>
                <div className="ml-3">
                  <p className="text-sm font-medium">{step.title}</p>
                  <p className="text-xs text-gray-500 group-hover:text-gray-700">
                    {step.description}
                  </p>
                </div>
              </Link>
            ))}
          </nav>
        </div>

        {/* Quick Actions */}
        <div className="space-y-6">
          {quickActions.map((section) => (
            <div key={section.title}>
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                {section.title}
              </h4>
              <div className="space-y-2">
                {section.items.map((item, index) => (
                  <Link
                    key={index}
                    to={item.path}
                    className="block p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.name}
                      </p>
                      {item.size && (
                        <span className="text-xs text-gray-500">{item.size}</span>
                      )}
                      {item.status && (
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            item.status === 'running'
                              ? 'bg-primary-100 text-primary-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {item.status}
                        </span>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
              
              {section.items.length === 0 && (
                <p className="text-sm text-gray-500 italic">No items</p>
              )}
            </div>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="mt-8 p-4 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Quick Stats</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Datasets</span>
              <span className="text-sm font-semibold text-primary-600">12</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Completed Jobs</span>
              <span className="text-sm font-semibold text-success-600">47</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Success Rate</span>
              <span className="text-sm font-semibold text-success-600">98.2%</span>
            </div>
          </div>
        </div>

        {/* Support Link */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <a
            href="#"
            className="flex items-center p-3 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors duration-200"
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M12 2.25a9.75 9.75 0 000 19.5 9.75 9.75 0 000-19.5z" />
            </svg>
            Help & Support
          </a>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;