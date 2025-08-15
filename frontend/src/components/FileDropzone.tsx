/**
 * File: FileDropzone.tsx
 * 
 * Overview:
 * Drag-and-drop file upload component with validation and visual feedback
 * 
 * Purpose:
 * Provides intuitive file upload interface matching Data Wrangler patterns
 * 
 * Dependencies:
 * - react-dropzone (for drag-and-drop functionality)
 * - fileValidation utils (for client-side validation)
 * - upload.types (for TypeScript interfaces)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadFile, ValidationResult } from '../types/upload.types';
import { validateFile, formatFileSize, DEFAULT_CONFIG } from '../utils/fileValidation';

interface FileDropzoneProps {
  onFilesSelected: (files: UploadFile[]) => void;
  disabled?: boolean;
  maxFiles?: number;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFilesSelected,
  disabled = false,
  maxFiles = 10
}) => {
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setValidationErrors([]);
    const errors: string[] = [];

    // Handle rejected files
    rejectedFiles.forEach(({ file, errors: fileErrors }) => {
      fileErrors.forEach((error: any) => {
        errors.push(`${file.name}: ${error.message}`);
      });
    });

    // Validate accepted files
    const uploadFiles: UploadFile[] = [];
    acceptedFiles.forEach((file) => {
      const validation = validateFile(file);
      
      if (validation.isValid) {
        uploadFiles.push({
          id: generateFileId(),
          file,
          status: 'pending',
          progress: 0
        });
      } else {
        errors.push(...validation.errors.map(error => `${file.name}: ${error}`));
      }

      // Add warnings as info (not blocking)
      if (validation.warnings.length > 0) {
        console.warn(`File warnings for ${file.name}:`, validation.warnings);
      }
    });

    if (errors.length > 0) {
      setValidationErrors(errors);
    }

    if (uploadFiles.length > 0) {
      onFilesSelected(uploadFiles);
    }
  }, [onFilesSelected]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json']
    },
    maxSize: DEFAULT_CONFIG.maxFileSize,
    maxFiles,
    disabled
  });

  const generateFileId = (): string => {
    return `file_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  };

  const getDropzoneStyle = (): string => {
    let baseStyle = 'border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer';
    
    if (disabled) {
      return `${baseStyle} border-gray-300 bg-gray-50 text-gray-400 cursor-not-allowed`;
    }

    if (isDragReject) {
      return `${baseStyle} border-red-500 bg-red-50 text-red-600`;
    }

    if (isDragAccept) {
      return `${baseStyle} border-green-500 bg-green-50 text-green-600`;
    }

    if (isDragActive) {
      return `${baseStyle} border-blue-500 bg-blue-50 text-blue-600`;
    }

    return `${baseStyle} border-gray-400 hover:border-blue-500 hover:bg-blue-50 text-gray-600`;
  };

  const getDropzoneContent = () => {
    if (disabled) {
      return (
        <div>
          <p className="text-lg font-medium mb-2">Upload Disabled</p>
          <p className="text-sm">File upload is currently disabled</p>
        </div>
      );
    }

    if (isDragReject) {
      return (
        <div>
          <p className="text-lg font-medium mb-2">❌ Invalid Files</p>
          <p className="text-sm">Some files are not supported</p>
        </div>
      );
    }

    if (isDragAccept) {
      return (
        <div>
          <p className="text-lg font-medium mb-2">✅ Drop Files Here</p>
          <p className="text-sm">Release to upload your files</p>
        </div>
      );
    }

    if (isDragActive) {
      return (
        <div>
          <p className="text-lg font-medium mb-2">📁 Drop Files Here</p>
          <p className="text-sm">Release to upload</p>
        </div>
      );
    }

    return (
      <div>
        <div className="mb-4">
          <svg
            className="mx-auto w-12 h-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
        <p className="text-lg font-medium mb-2">Drag & Drop Files Here</p>
        <p className="text-sm mb-4">or click to browse</p>
        <div className="text-xs text-gray-500">
          <p>Supported: CSV, JSON files</p>
          <p>Max size: {formatFileSize(DEFAULT_CONFIG.maxFileSize)}</p>
          <p>Data Wrangler exports: transformation_file.csv, mapped_data.csv, metadata.json</p>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full">
      <div {...getRootProps()} className={getDropzoneStyle()}>
        <input {...getInputProps()} />
        {getDropzoneContent()}
      </div>

      {validationErrors.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="text-red-800 font-medium mb-2">Validation Errors:</h4>
          <ul className="text-red-700 text-sm space-y-1">
            {validationErrors.map((error, index) => (
              <li key={index} className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                {error}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-blue-800 font-medium mb-1">Data Wrangler File Patterns:</h4>
        <ul className="text-blue-700 text-sm space-y-1">
          <li><code className="bg-blue-100 px-1 rounded">transformation_file.csv</code> - Original data transformations</li>
          <li><code className="bg-blue-100 px-1 rounded">mapped_data.csv</code> - Processed and mapped data</li>
          <li><code className="bg-blue-100 px-1 rounded">metadata.json</code> - Statistics and configuration</li>
        </ul>
      </div>
    </div>
  );
};