/**
 * File: ImportSummary.tsx
 * 
 * Overview:
 * Component for displaying file previews and upload summaries with management controls
 * 
 * Purpose:
 * Shows uploaded file details, data previews, and provides file management options
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
import { ImportSummaryProps, UploadFile } from '../../types/upload.types';
import { FileUploadService } from '../../services/fileUpload';

const ImportSummary: React.FC<ImportSummaryProps> = ({
  files,
  onRemoveFile,
  onRetryUpload,
}) => {
  const completedFiles = files.filter(file => 
    file.status === 'success' || file.status === 'error'
  );

  if (completedFiles.length === 0) {
    return null;
  }

  const renderFilePreview = (file: UploadFile) => {
    if (!file.preview) {
      return (
        <div className="text-sm text-gray-500 italic">
          No preview available
        </div>
      );
    }

    const { preview } = file;
    
    return (
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">File Type:</span>
            <span className="ml-2 capitalize">{preview.fileType}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Rows:</span>
            <span className="ml-2">{preview.rows.toLocaleString()}</span>
          </div>
          <div className="col-span-2">
            <span className="font-medium text-gray-700">Columns:</span>
            <span className="ml-2">{preview.columns.length}</span>
          </div>
        </div>
        
        {preview.columns.length > 0 && (
          <div>
            <h5 className="text-sm font-medium text-gray-700 mb-2">Column Names:</h5>
            <div className="flex flex-wrap gap-1">
              {preview.columns.slice(0, 10).map((column, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                >
                  {column}
                </span>
              ))}
              {preview.columns.length > 10 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  +{preview.columns.length - 10} more
                </span>
              )}
            </div>
          </div>
        )}
        
        {preview.sampleData.length > 0 && (
          <div>
            <h5 className="text-sm font-medium text-gray-700 mb-2">Sample Data:</h5>
            <div className="bg-gray-50 rounded border overflow-x-auto">
              <table className="min-w-full text-xs">
                <thead className="bg-gray-100">
                  <tr>
                    {preview.columns.slice(0, 5).map((column, index) => (
                      <th key={index} className="px-3 py-2 text-left font-medium text-gray-700">
                        {column}
                      </th>
                    ))}
                    {preview.columns.length > 5 && (
                      <th className="px-3 py-2 text-left font-medium text-gray-500">...</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {preview.sampleData.slice(0, 3).map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-t border-gray-200">
                      {preview.columns.slice(0, 5).map((column, colIndex) => (
                        <td key={colIndex} className="px-3 py-2 text-gray-600">
                          {String(row[column] || '').slice(0, 50)}
                          {String(row[column] || '').length > 50 && '...'}
                        </td>
                      ))}
                      {preview.columns.length > 5 && (
                        <td className="px-3 py-2 text-gray-400">...</td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  };

  const getStatusBadge = (status: UploadFile['status']) => {
    const baseClasses = 'px-2 py-1 text-xs font-medium rounded-full';
    
    switch (status) {
      case 'success':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'error':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">
          Import Summary ({completedFiles.length} files)
        </h3>
      </div>
      
      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {completedFiles.map((file) => (
          <div key={file.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start space-x-3 min-w-0 flex-1">
                <span className="text-2xl mt-1">
                  {FileUploadService.getFileIcon(file.type)}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </h4>
                    <span className={getStatusBadge(file.status)}>
                      {file.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {FileUploadService.formatFileSize(file.size)} • {file.type}
                  </p>
                  {file.errorMessage && (
                    <p className="text-xs text-red-600 mt-1">
                      {file.errorMessage}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                {file.status === 'error' && (
                  <button
                    onClick={() => onRetryUpload(file.id)}
                    className="text-xs px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                  >
                    Retry
                  </button>
                )}
                <button
                  onClick={() => onRemoveFile(file.id)}
                  className="text-xs px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
            
            {file.status === 'success' && renderFilePreview(file)}
          </div>
        ))}
      </div>
      
      <div className="p-3 bg-gray-50 border-t border-gray-200">
        <div className="flex justify-between text-xs text-gray-600">
          <span>
            {files.filter(f => f.status === 'success').length} successful uploads
          </span>
          <span>
            Total size: {FileUploadService.formatFileSize(
              completedFiles.reduce((acc, file) => acc + file.size, 0)
            )}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ImportSummary;