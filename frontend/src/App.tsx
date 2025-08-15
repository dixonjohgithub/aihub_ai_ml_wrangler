/**
 * File: App.tsx
 * 
 * Overview:
 * Main application component integrating file import interface
 * 
 * Purpose:
 * Orchestrates file upload workflow with all components
 * 
 * Dependencies:
 * - React (for component state management)
 * - FileDropzone (drag-and-drop interface)
 * - ProgressTracker (upload progress)
 * - ImportSummary (file preview)
 * - uploadService (API communication)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useCallback } from 'react';
import { FileDropzone } from './components/FileDropzone';
import { ProgressTracker } from './components/ProgressTracker';
import { ImportSummary } from './components/ImportSummary';
import { UploadFile, UploadProgress } from './types/upload.types';
import uploadService from './services/uploadService';
import './App.css';

function App() {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFilesSelected = useCallback(async (newFiles: UploadFile[]) => {
    // Add new files to the list
    setFiles(prevFiles => [...prevFiles, ...newFiles]);
    
    // Start uploading files automatically
    setIsUploading(true);
    
    try {
      // Upload each file
      for (const uploadFile of newFiles) {
        await uploadFile_Internal(uploadFile);
      }
    } finally {
      setIsUploading(false);
    }
  }, []);

  const uploadFile_Internal = async (uploadFile: UploadFile) => {
    // Update file status to uploading
    setFiles(prevFiles =>
      prevFiles.map(f =>
        f.id === uploadFile.id
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      )
    );

    try {
      const response = await uploadService.uploadFile(
        uploadFile.file,
        uploadFile.id,
        (progress: UploadProgress) => {
          // Update progress
          setFiles(prevFiles =>
            prevFiles.map(f =>
              f.id === uploadFile.id
                ? { ...f, progress: progress.percentage }
                : f
            )
          );
        }
      );

      if (response.success && response.data) {
        // Update file status to completed
        setFiles(prevFiles =>
          prevFiles.map(f =>
            f.id === uploadFile.id
              ? { 
                  ...f, 
                  status: 'completed', 
                  progress: 100,
                  preview: response.data!.preview
                }
              : f
          )
        );

        // Start virus scan
        try {
          const scanResult = await uploadService.scanFile(uploadFile.id);
          if (scanResult.success && scanResult.data && !scanResult.data.isClean) {
            // File failed virus scan
            setFiles(prevFiles =>
              prevFiles.map(f =>
                f.id === uploadFile.id
                  ? { 
                      ...f, 
                      status: 'error', 
                      error: `Security scan failed: ${scanResult.data!.threats?.join(', ') || 'Threats detected'}`
                    }
                  : f
              )
            );
          }
        } catch (scanError) {
          console.warn('Virus scan failed:', scanError);
          // Don't fail the upload, just log warning
        }
      } else {
        throw new Error(response.error || 'Upload failed');
      }
    } catch (error) {
      // Update file status to error
      setFiles(prevFiles =>
        prevFiles.map(f =>
          f.id === uploadFile.id
            ? { 
                ...f, 
                status: 'error', 
                error: error instanceof Error ? error.message : 'Upload failed'
              }
            : f
        )
      );
    }
  };

  const handleCancel = useCallback((fileId: string) => {
    const success = uploadService.cancelUpload(fileId);
    if (success) {
      setFiles(prevFiles =>
        prevFiles.map(f =>
          f.id === fileId
            ? { ...f, status: 'cancelled' }
            : f
        )
      );
    }
  }, []);

  const handleRetry = useCallback(async (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    if (file) {
      await uploadFile_Internal(file);
    }
  }, [files]);

  const handleRemove = useCallback(async (fileId: string) => {
    // Remove from backend if uploaded
    const file = files.find(f => f.id === fileId);
    if (file && file.status === 'completed') {
      try {
        await uploadService.deleteFile(fileId);
      } catch (error) {
        console.error('Failed to delete file from backend:', error);
      }
    }

    // Remove from local state
    setFiles(prevFiles => prevFiles.filter(f => f.id !== fileId));
  }, [files]);

  const handleProcessFile = useCallback(async (fileId: string) => {
    console.log('Processing file:', fileId);
    // This would integrate with your data processing pipeline
    alert(`Processing file ${fileId} - integration with data pipeline would go here`);
  }, []);

  const handleDeleteFile = useCallback(async (fileId: string) => {
    if (window.confirm('Are you sure you want to delete this file?')) {
      await handleRemove(fileId);
    }
  }, [handleRemove]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      uploadService.cancelAllUploads();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Hub Data Wrangler</h1>
              <p className="text-sm text-gray-600">File Import Interface</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {uploadService.getActiveUploadCount()} active uploads
              </span>
              {isUploading && (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm text-blue-600">Uploading...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* File Drop Zone */}
          <section>
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Files</h2>
            <FileDropzone
              onFilesSelected={handleFilesSelected}
              disabled={isUploading}
            />
          </section>

          {/* Progress Tracking */}
          {files.length > 0 && (
            <section>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Progress</h2>
              <ProgressTracker
                files={files}
                onCancel={handleCancel}
                onRetry={handleRetry}
                onRemove={handleRemove}
              />
            </section>
          )}

          {/* Import Summary */}
          {files.some(f => f.status === 'completed') && (
            <section>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Imported Files</h2>
              <ImportSummary
                files={files}
                onProcessFile={handleProcessFile}
                onDeleteFile={handleDeleteFile}
              />
            </section>
          )}

          {/* Instructions */}
          {files.length === 0 && (
            <section className="text-center py-12">
              <div className="max-w-md mx-auto">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Import Data Wrangler Files
                </h3>
                <p className="text-gray-600 mb-6">
                  Upload your Data Wrangler export files to continue with data processing.
                  Supported formats include CSV transformation files and JSON metadata.
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">Supported File Types:</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• transformation_file.csv - Data transformations</li>
                    <li>• mapped_data.csv - Processed data</li>
                    <li>• metadata.json - Configuration and statistics</li>
                  </ul>
                </div>
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            AI Hub Data Wrangler - File Import Interface v1.0
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;