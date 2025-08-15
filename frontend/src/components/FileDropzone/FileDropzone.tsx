/**
 * File: FileDropzone.tsx
 * 
 * Overview:
 * Drag-and-drop file upload component with visual feedback and validation
 * 
 * Purpose:
 * Provides intuitive file upload interface matching Data Wrangler patterns
 * 
 * Dependencies:
 * - react for component functionality
 * - react-dropzone for drag-and-drop behavior
 * - upload.types.ts for type definitions
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileDropzoneProps, ACCEPTED_MIME_TYPES, MAX_FILE_SIZE } from '../../types/upload.types';
import { FileUploadService } from '../../services/fileUpload';

const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFilesAdded,
  acceptedFileTypes = ACCEPTED_MIME_TYPES,
  maxFileSize = MAX_FILE_SIZE,
  multiple = true,
  disabled = false,
}) => {
  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Validate accepted files
      const validFiles = acceptedFiles.filter(file => {
        const validation = FileUploadService.validateFile(file);
        if (!validation.isValid) {
          console.error(`File ${file.name} validation failed:`, validation.errors);
          return false;
        }
        return true;
      });

      // Handle rejected files
      rejectedFiles.forEach(({ file, errors }) => {
        console.error(`File ${file.name} rejected:`, errors);
      });

      if (validFiles.length > 0) {
        onFilesAdded(validFiles);
      }
    },
    [onFilesAdded]
  );

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
    },
    maxSize: maxFileSize,
    multiple,
    disabled,
  });

  const getDropzoneClassName = () => {
    let baseClass = 'w-full h-64 border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ease-in-out cursor-pointer hover:border-blue-400 hover:bg-blue-50';
    
    if (disabled) {
      return `${baseClass} border-gray-300 bg-gray-50 cursor-not-allowed opacity-50`;
    }
    
    if (isDragAccept) {
      return `${baseClass} border-green-400 bg-green-50`;
    }
    
    if (isDragReject) {
      return `${baseClass} border-red-400 bg-red-50`;
    }
    
    if (isDragActive) {
      return `${baseClass} border-blue-400 bg-blue-50`;
    }
    
    return `${baseClass} border-gray-300`;
  };

  const getIconAndText = () => {
    if (isDragAccept) {
      return {
        icon: '✅',
        title: 'Drop files to upload',
        subtitle: 'Release to upload your files',
      };
    }
    
    if (isDragReject) {
      return {
        icon: '❌',
        title: 'Invalid file type',
        subtitle: 'Please upload CSV or JSON files only',
      };
    }
    
    if (isDragActive) {
      return {
        icon: '📂',
        title: 'Drop files here',
        subtitle: 'Release to upload',
      };
    }
    
    return {
      icon: '☁️',
      title: 'Upload Data Files',
      subtitle: 'Drag and drop files here, or click to browse',
    };
  };

  const { icon, title, subtitle } = getIconAndText();

  return (
    <div className="w-full">
      <div {...getRootProps()} className={getDropzoneClassName()}>
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="text-6xl">{icon}</div>
          <div className="space-y-2">
            <h3 className="text-xl font-semibold text-gray-700">{title}</h3>
            <p className="text-sm text-gray-500">{subtitle}</p>
          </div>
          {!disabled && (
            <div className="text-xs text-gray-400 max-w-md">
              <p>
                Supported formats: CSV, JSON
                <br />
                Maximum file size: {FileUploadService.formatFileSize(maxFileSize)}
                <br />
                {multiple ? 'Multiple files allowed' : 'Single file only'}
              </p>
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        <h4 className="font-medium mb-2">Supported Data Wrangler Files:</h4>
        <ul className="list-disc list-inside space-y-1 text-xs">
          <li><code>transformation_file.csv</code> - Data Wrangler export</li>
          <li><code>mapped_data.csv</code> - Transformed data</li>
          <li><code>metadata.json</code> - Statistics and configuration</li>
        </ul>
      </div>
    </div>
  );
};

export default FileDropzone;