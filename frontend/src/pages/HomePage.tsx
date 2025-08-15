/**
 * File: pages/HomePage.tsx
 * 
 * Overview:
 * Main dashboard page showing overview and recent activity
 * 
 * Purpose:
 * Provides users with dashboard overview, quick stats, and navigation
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

const HomePage: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to <span className="text-gradient">AI Hub AI/ML Wrangler</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Transform your data with AI-powered imputation and statistical analysis. 
          Handle missing data intelligently with our comprehensive suite of tools.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card group hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors duration-200">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 ml-4">Import Data</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Upload CSV, JSON, or Data Wrangler export files to start your analysis journey.
          </p>
          <Link to="/import">
            <Button variant="primary" className="w-full">
              Start Import
            </Button>
          </Link>
        </div>

        <div className="card group hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center group-hover:bg-success-200 transition-colors duration-200">
              <svg className="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 ml-4">AI Analysis</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Get intelligent insights and recommendations for your dataset's missing data patterns.
          </p>
          <Link to="/analysis">
            <Button variant="success" className="w-full">
              Analyze Data
            </Button>
          </Link>
        </div>

        <div className="card group hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center group-hover:bg-warning-200 transition-colors duration-200">
              <svg className="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 ml-4">View Results</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Access your completed imputation jobs, reports, and download processed datasets.
          </p>
          <Link to="/results">
            <Button variant="warning" className="w-full">
              View Results
            </Button>
          </Link>
        </div>
      </div>

      {/* Dashboard Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600 mb-2">12</div>
          <div className="text-sm text-gray-600">Active Datasets</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-success-600 mb-2">47</div>
          <div className="text-sm text-gray-600">Completed Jobs</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-warning-600 mb-2">3</div>
          <div className="text-sm text-gray-600">Running Jobs</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-secondary-600 mb-2">98.2%</div>
          <div className="text-sm text-gray-600">Success Rate</div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Datasets</h3>
          <div className="space-y-3">
            {[
              { name: 'customer_survey.csv', size: '2.3 MB', uploaded: '2 hours ago' },
              { name: 'sales_data.json', size: '1.8 MB', uploaded: '5 hours ago' },
              { name: 'product_analytics.csv', size: '954 KB', uploaded: '1 day ago' },
            ].map((dataset, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">{dataset.name}</p>
                  <p className="text-xs text-gray-500">{dataset.size} • {dataset.uploaded}</p>
                </div>
                <Link to="/analysis">
                  <Button size="sm" variant="secondary">
                    Analyze
                  </Button>
                </Link>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Link to="/import">
              <Button variant="secondary" className="w-full">
                View All Datasets
              </Button>
            </Link>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Status</h3>
          <div className="space-y-3">
            {[
              { name: 'ML-based Imputation', status: 'completed', progress: 100 },
              { name: 'Correlation Analysis', status: 'running', progress: 67 },
              { name: 'Statistical Validation', status: 'queued', progress: 0 },
            ].map((job, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-900">{job.name}</p>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                      job.status === 'completed'
                        ? 'bg-success-100 text-success-800'
                        : job.status === 'running'
                        ? 'bg-primary-100 text-primary-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {job.status}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      job.status === 'completed'
                        ? 'bg-success-500'
                        : job.status === 'running'
                        ? 'bg-primary-500'
                        : 'bg-gray-300'
                    }`}
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Link to="/results">
              <Button variant="secondary" className="w-full">
                View All Jobs
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Feature Highlights */}
      <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Powered by Advanced AI
          </h3>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Our AI-powered system analyzes your data patterns and provides intelligent 
            recommendations for the best imputation strategies, ensuring optimal results 
            for your specific dataset characteristics.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Smart Analysis</h4>
              <p className="text-sm text-gray-600">AI-powered pattern recognition</p>
            </div>
            <div>
              <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-8 h-8 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Fast Processing</h4>
              <p className="text-sm text-gray-600">Optimized for large datasets</p>
            </div>
            <div>
              <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-8 h-8 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">High Quality</h4>
              <p className="text-sm text-gray-600">98.2% success rate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;