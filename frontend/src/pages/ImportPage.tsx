/**
 * File: ImportPage.tsx
 * 
 * Overview:
 * File import page for uploading data files
 * 
 * Purpose:
 * Allow users to upload CSV files and Data Wrangler exports for processing
 * 
 * Dependencies:
 * - React for component structure
 * - dataService for API communication
 * - Tailwind CSS for styling
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState } from 'react'
import dataService from '../services/dataService'

const ImportPage: React.FC = () => {
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string>('')

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setUploadStatus('Please upload a CSV file.')
      return
    }

    setUploading(true)
    setUploadStatus('Uploading file...')

    try {
      const response = await dataService.uploadFile(file)
      setUploadStatus(`File uploaded successfully! ID: ${response.id}`)
    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Import Data</h1>
        <p className="mt-2 text-gray-600">
          Upload your CSV files or Data Wrangler exports to begin analysis and imputation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card p-8">
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                dragActive
                  ? 'border-primary-400 bg-primary-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    Drop files here or click to upload
                  </span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    accept=".csv"
                    onChange={handleChange}
                    disabled={uploading}
                  />
                </label>
                <p className="mt-2 text-xs text-gray-500">
                  CSV files up to 100MB
                </p>
              </div>
            </div>

            {uploadStatus && (
              <div className={`mt-4 p-4 rounded-md ${
                uploadStatus.includes('success') 
                  ? 'bg-green-50 text-green-700' 
                  : uploadStatus.includes('failed')
                  ? 'bg-red-50 text-red-700'
                  : 'bg-blue-50 text-blue-700'
              }`}>
                {uploadStatus}
              </div>
            )}

            {uploading && (
              <div className="mt-4">
                <div className="bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Supported Formats</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>CSV files (.csv)</span>
              </li>
              <li className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Data Wrangler exports</span>
              </li>
              <li className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                <span>Excel files (coming soon)</span>
              </li>
            </ul>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">File Requirements</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Maximum file size: 100MB</li>
              <li>• Maximum rows: 1M+</li>
              <li>• UTF-8 encoding recommended</li>
              <li>• First row should contain headers</li>
              <li>• Missing values: empty cells or 'NaN'</li>
            </ul>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Data</h3>
            <p className="text-sm text-gray-600 mb-4">
              Try the application with our sample datasets.
            </p>
            <button className="btn-secondary w-full">
              Download Sample CSV
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ImportPage