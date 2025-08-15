/**
 * File: ProgressTracker.tsx
 * 
 * Overview:
 * Upload progress tracking component with cancellation support
 * 
 * Purpose:
 * Provides real-time feedback on file upload progress with user controls
 * 
 * Dependencies:
 * - React (for component state management)
 * - upload.types (for TypeScript interfaces)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import { UploadFile } from '../types/upload.types';
import { formatFileSize } from '../utils/fileValidation';

interface ProgressTrackerProps {
  files: UploadFile[];
  onCancel: (fileId: string) => void;
  onRetry: (fileId: string) => void;
  onRemove: (fileId: string) => void;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  files,
  onCancel,
  onRetry,
  onRemove
}) => {
  if (files.length === 0) {
    return null;
  }

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'uploading':
        return '📤';
      case 'completed':
        return '✅';
      case 'error':
        return '❌';
      case 'cancelled':
        return '🚫';
      default:
        return '📄';
    }
  };

  const getStatusColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-600';
      case 'uploading':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'cancelled':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  const getProgressBarColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'cancelled':
        return 'bg-gray-500';
      default:
        return 'bg-gray-300';
    }
  };

  const formatProgress = (file: UploadFile): string => {
    if (file.status === 'completed') return '100%';
    if (file.status === 'error') return 'Failed';
    if (file.status === 'cancelled') return 'Cancelled';
    if (file.status === 'pending') return 'Waiting...';
    return `${Math.round(file.progress)}%`;
  };

  const canCancel = (status: UploadFile['status']) => {
    return status === 'pending' || status === 'uploading';
  };

  const canRetry = (status: UploadFile['status']) => {
    return status === 'error' || status === 'cancelled';
  };

  const canRemove = (status: UploadFile['status']) => {
    return status === 'completed' || status === 'error' || status === 'cancelled';
  };

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Progress</h3>
      
      <div className="space-y-4">
        {files.map((file) => (
          <div key={file.id} className="border border-gray-200 rounded-lg p-4">
            {/* File Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <span className="text-xl">{getStatusIcon(file.status)}</span>
                <div>
                  <p className="font-medium text-gray-900 truncate max-w-xs">
                    {file.file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(file.file.size)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-medium ${getStatusColor(file.status)}`}>
                  {formatProgress(file)}
                </span>
                
                {/* Action Buttons */}
                <div className="flex space-x-1">
                  {canCancel(file.status) && (
                    <button
                      onClick={() => onCancel(file.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      title="Cancel upload"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                  
                  {canRetry(file.status) && (
                    <button
                      onClick={() => onRetry(file.id)}
                      className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                      title="Retry upload"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                  )}
                  
                  {canRemove(file.status) && (
                    <button
                      onClick={() => onRemove(file.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      title="Remove file"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(file.status)}`}
                style={{ width: `${file.status === 'completed' ? 100 : file.progress}%` }}
              />
            </div>

            {/* Error Message */}
            {file.status === 'error' && file.error && (
              <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                <span className="font-medium">Error:</span> {file.error}
              </div>
            )}

            {/* Upload Speed/Time Info */}
            {file.status === 'uploading' && (
              <div className="mt-2 text-xs text-gray-500">
                Uploading... This may take a moment for large files.
              </div>
            )}

            {/* Completion Info */}
            {file.status === 'completed' && (
              <div className="mt-2 text-xs text-green-600">
                Upload completed successfully
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between text-sm text-gray-600">
          <span>
            {files.filter(f => f.status === 'completed').length} of {files.length} files completed
          </span>
          <span>
            Total size: {formatFileSize(files.reduce((total, file) => total + file.file.size, 0))}
          </span>
        </div>
      </div>
    </div>
  );
};