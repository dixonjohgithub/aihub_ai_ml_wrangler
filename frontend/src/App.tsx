/**
 * File: App.tsx
 * 
 * Overview:
 * Main React application component demonstrating file import interface
 * 
 * Purpose:
 * Demo application showcasing the complete file upload workflow
 * 
 * Dependencies:
 * - react for component functionality
 * - components for file upload UI
 * - services for file handling
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useCallback } from 'react';
import FileDropzone from './components/FileDropzone';
import ProgressTracker from './components/ProgressTracker';
import ImportSummary from './components/ImportSummary';
import { UploadFile, ACCEPTED_MIME_TYPES, MAX_FILE_SIZE } from './types/upload.types';
import { FileUploadService } from './services/fileUpload';
import './App.css';

function App() {
  const [uploads, setUploads] = useState<UploadFile[]>([]);

  const handleFilesAdded = useCallback(async (files: File[]) => {
    const newUploads: UploadFile[] = files.map(file => ({
      id: FileUploadService.generateFileId(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
    }));

    setUploads(prev => [...prev, ...newUploads]);

    // Start uploading files
    for (const upload of newUploads) {
      uploadFile(upload);
    }
  }, []);

  const uploadFile = async (upload: UploadFile) => {
    try {
      // Update status to uploading
      setUploads(prev => 
        prev.map(u => 
          u.id === upload.id 
            ? { ...u, status: 'uploading', progress: 0 }
            : u
        )
      );

      // Upload file with progress tracking
      const response = await FileUploadService.uploadFile(
        upload.file,
        (progressEvent) => {
          const percentage = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          );
          
          setUploads(prev => 
            prev.map(u => 
              u.id === upload.id 
                ? { ...u, progress: percentage }
                : u
            )
          );
        }
      );

      if (response.success) {
        // Get file preview if available
        let preview = response.preview;
        if (!preview && response.file_id) {
          try {
            preview = await FileUploadService.getFilePreview(response.file_id);
          } catch (error) {
            console.warn('Could not fetch preview:', error);
          }
        }

        setUploads(prev => 
          prev.map(u => 
            u.id === upload.id 
              ? { 
                  ...u, 
                  status: 'success', 
                  progress: 100,
                  preview: preview || undefined
                }
              : u
          )
        );
      } else {
        throw new Error(response.message || 'Upload failed');
      }

    } catch (error) {
      setUploads(prev => 
        prev.map(u => 
          u.id === upload.id 
            ? { 
                ...u, 
                status: 'error', 
                errorMessage: error instanceof Error ? error.message : 'Upload failed'
              }
            : u
        )
      );
    }
  };

  const handleCancelUpload = useCallback((fileId: string) => {
    setUploads(prev => 
      prev.map(u => 
        u.id === fileId 
          ? { ...u, status: 'cancelled' }
          : u
      )
    );
  }, []);

  const handleRemoveFile = useCallback((fileId: string) => {
    setUploads(prev => prev.filter(u => u.id !== fileId));
  }, []);

  const handleRetryUpload = useCallback((fileId: string) => {
    const upload = uploads.find(u => u.id === fileId);
    if (upload) {
      uploadFile(upload);
    }
  }, [uploads]);

  const stats = {
    total: uploads.length,
    pending: uploads.filter(u => u.status === 'pending').length,
    uploading: uploads.filter(u => u.status === 'uploading').length,
    success: uploads.filter(u => u.status === 'success').length,
    error: uploads.filter(u => u.status === 'error').length,
    cancelled: uploads.filter(u => u.status === 'cancelled').length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI Hub AI/ML Wrangler
          </h1>
          <p className="text-lg text-gray-600">
            File Import Interface Demo - Data Wrangler Integration
          </p>
        </header>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Upload Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Upload Data Files
              </h2>
              <FileDropzone
                onFilesAdded={handleFilesAdded}
                acceptedFileTypes={ACCEPTED_MIME_TYPES}
                maxFileSize={MAX_FILE_SIZE}
                multiple={true}
              />
            </div>

            {/* Upload Statistics */}
            {uploads.length > 0 && (
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <h3 className="text-lg font-medium text-gray-800 mb-3">
                  Upload Statistics
                </h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
                    <div className="text-gray-600">Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{stats.success}</div>
                    <div className="text-gray-600">Success</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{stats.error}</div>
                    <div className="text-gray-600">Errors</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Progress and Results Section */}
          <div className="space-y-6">
            {/* Progress Tracker */}
            <ProgressTracker
              uploads={uploads}
              onCancelUpload={handleCancelUpload}
            />

            {/* Import Summary */}
            <ImportSummary
              files={uploads}
              onRemoveFile={handleRemoveFile}
              onRetryUpload={handleRetryUpload}
            />
          </div>
        </div>

        {/* Information Section */}
        <div className="mt-12 bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            About This Demo
          </h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Features Demonstrated</h4>
              <ul className="list-disc list-inside space-y-1">
                <li>Drag-and-drop file upload</li>
                <li>File validation (type, size)</li>
                <li>Real-time progress tracking</li>
                <li>File preview generation</li>
                <li>Error handling and retry</li>
                <li>Virus scanning integration</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Supported Files</h4>
              <ul className="list-disc list-inside space-y-1">
                <li><code>transformation_file.csv</code> - Data Wrangler export</li>
                <li><code>mapped_data.csv</code> - Transformed data</li>
                <li><code>metadata.json</code> - Statistics and configuration</li>
                <li>Maximum file size: 100MB</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;