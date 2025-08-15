/**
 * File: ProgressTracker.tsx
 * 
 * Overview:
 * Component for tracking and displaying file upload progress with cancellation support
 * 
 * Purpose:
 * Provides real-time feedback on upload status and allows users to cancel uploads
 * 
 * Dependencies:
 * - react for component functionality
 * - upload.types.ts for type definitions
 * - fileUpload.ts for utility functions
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import { ProgressTrackerProps, UploadFile } from '../../types/upload.types';
import { FileUploadService } from '../../services/fileUpload';

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  uploads,
  onCancelUpload,
}) => {
  const activeUploads = uploads.filter(upload => 
    upload.status === 'uploading' || upload.status === 'pending'
  );

  if (activeUploads.length === 0) {
    return null;
  }

  const getProgressBarColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-500';
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'cancelled':
        return 'bg-gray-500';
      default:
        return 'bg-gray-300';
    }
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading':
        return '⏳';
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'cancelled':
        return '⏹️';
      case 'pending':
        return '⏸️';
      default:
        return '📄';
    }
  };

  const getStatusText = (upload: UploadFile) => {
    switch (upload.status) {
      case 'pending':
        return 'Waiting to upload...';
      case 'uploading':
        return `Uploading... ${upload.progress}%`;
      case 'success':
        return 'Upload complete';
      case 'error':
        return `Error: ${upload.errorMessage || 'Upload failed'}`;
      case 'cancelled':
        return 'Upload cancelled';
      default:
        return 'Unknown status';
    }
  };

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">
          Upload Progress ({activeUploads.length} active)
        </h3>
      </div>
      
      <div className="p-4 space-y-4 max-h-64 overflow-y-auto">
        {activeUploads.map((upload) => (
          <div key={upload.id} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-lg">{getStatusIcon(upload.status)}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {FileUploadService.getFileIcon(upload.type)} {upload.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {FileUploadService.formatFileSize(upload.size)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {upload.status === 'uploading' && (
                  <button
                    onClick={() => onCancelUpload(upload.id)}
                    className="text-xs px-2 py-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
                    title="Cancel upload"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-gray-600">
                <span>{getStatusText(upload)}</span>
                {upload.status === 'uploading' && (
                  <span>{upload.progress}%</span>
                )}
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(upload.status)}`}
                  style={{
                    width: `${upload.status === 'pending' ? 0 : upload.progress}%`,
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="p-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
        <div className="flex justify-between">
          <span>
            Total: {uploads.filter(u => u.status === 'success').length} completed, {' '}
            {uploads.filter(u => u.status === 'error').length} failed
          </span>
          <span>
            {activeUploads.reduce((acc, upload) => acc + upload.size, 0) > 0 && 
              `${FileUploadService.formatFileSize(
                activeUploads.reduce((acc, upload) => acc + upload.size, 0)
              )} total`
            }
          </span>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;