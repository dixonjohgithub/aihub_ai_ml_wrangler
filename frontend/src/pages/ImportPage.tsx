/**
 * File: pages/ImportPage.tsx
 * 
 * Overview:
 * Data import page for uploading and configuring datasets
 * 
 * Purpose:
 * Allows users to upload files and configure initial dataset settings
 * 
 * Dependencies:
 * - React for component structure
 * - Button component for actions
 * - DataService for API calls
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';

const ImportPage: React.FC = () => {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  const supportedFormats = [
    { name: 'CSV Files', extensions: '.csv', description: 'Comma-separated values' },
    { name: 'JSON Files', extensions: '.json', description: 'JavaScript Object Notation' },
    { name: 'Excel Files', extensions: '.xlsx, .xls', description: 'Microsoft Excel spreadsheets' },
    { name: 'Data Wrangler Export', extensions: '.csv, .json', description: 'AI Hub Data Wrangler output' },
  ];

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 200);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Navigate to analysis page on success
      navigate('/analysis');
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Import Data</h1>
        <p className="text-gray-600">
          Upload your dataset to begin AI-powered analysis and imputation. 
          Supports CSV, JSON, Excel, and Data Wrangler export files.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Dataset</h3>
            
            {/* Drop Zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
                isDragging 
                  ? 'border-primary-400 bg-primary-50' 
                  : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {selectedFile ? (
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto">
                    <svg className="w-8 h-8 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                  <div className="flex space-x-3 justify-center">
                    <Button
                      variant="primary"
                      onClick={handleUpload}
                      loading={isUploading}
                      disabled={isUploading}
                    >
                      {isUploading ? 'Uploading...' : 'Upload & Analyze'}
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => setSelectedFile(null)}
                      disabled={isUploading}
                    >
                      Remove
                    </Button>
                  </div>
                  
                  {isUploading && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto">
                    <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-900">Drop files here</p>
                    <p className="text-sm text-gray-500 mb-4">or click to browse</p>
                  </div>
                  <div>
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      accept=".csv,.json,.xlsx,.xls"
                      onChange={handleFileSelect}
                    />
                    <label htmlFor="file-upload">
                      <Button variant="primary">
                        Choose File
                      </Button>
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* File Requirements */}
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">File Requirements</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Maximum file size: 100MB</li>
                <li>• Maximum rows: 1 million</li>
                <li>• Headers required for CSV files</li>
                <li>• UTF-8 encoding recommended</li>
              </ul>
            </div>
          </div>

          {/* Recent Uploads */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Uploads</h3>
            <div className="space-y-3">
              {[
                { name: 'customer_survey.csv', uploaded: '2 hours ago', status: 'completed' },
                { name: 'sales_data.json', uploaded: '5 hours ago', status: 'processing' },
                { name: 'product_analytics.csv', uploaded: '1 day ago', status: 'completed' },
              ].map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">{file.uploaded}</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        file.status === 'completed'
                          ? 'bg-success-100 text-success-800'
                          : 'bg-primary-100 text-primary-800'
                      }`}
                    >
                      {file.status}
                    </span>
                    {file.status === 'completed' && (
                      <Button size="sm" variant="secondary">
                        View
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Information Section */}
        <div className="space-y-6">
          {/* Supported Formats */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Supported Formats</h3>
            <div className="space-y-3">
              {supportedFormats.map((format, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900">{format.name}</h4>
                    <p className="text-xs text-gray-500">{format.extensions}</p>
                    <p className="text-sm text-gray-600 mt-1">{format.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* What Happens Next */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">What Happens Next?</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 text-primary-600 text-sm font-semibold">
                  1
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">File Analysis</h4>
                  <p className="text-sm text-gray-600">We'll analyze your dataset structure and identify missing data patterns.</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-success-100 rounded-full flex items-center justify-center flex-shrink-0 text-success-600 text-sm font-semibold">
                  2
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">AI Recommendations</h4>
                  <p className="text-sm text-gray-600">Our AI will suggest the best imputation strategies for your data.</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-warning-100 rounded-full flex items-center justify-center flex-shrink-0 text-warning-600 text-sm font-semibold">
                  3
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">Configuration</h4>
                  <p className="text-sm text-gray-600">Review and customize the imputation settings to your needs.</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-error-100 rounded-full flex items-center justify-center flex-shrink-0 text-error-600 text-sm font-semibold">
                  4
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">Processing & Results</h4>
                  <p className="text-sm text-gray-600">Get your imputed data, correlation matrices, and detailed reports.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Data Privacy */}
          <div className="card bg-green-50 border-green-200">
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-green-900 mb-2">Data Privacy & Security</h4>
                <p className="text-sm text-green-800">
                  Your data is processed securely and never shared with third parties. 
                  All files are encrypted and automatically deleted after processing.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportPage;