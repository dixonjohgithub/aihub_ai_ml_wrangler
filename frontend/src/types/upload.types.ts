/**
 * File: upload.types.ts
 * 
 * Overview:
 * TypeScript type definitions for file upload and import functionality
 * 
 * Purpose:
 * Provides type safety for file upload operations, validation, and progress tracking
 * 
 * Dependencies:
 * - None (pure TypeScript types)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

export interface UploadFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  status: 'pending' | 'uploading' | 'success' | 'error' | 'cancelled';
  progress: number;
  errorMessage?: string;
  preview?: FilePreview;
}

export interface FilePreview {
  columns: string[];
  rows: number;
  sampleData: Record<string, any>[];
  fileType: 'csv' | 'json';
  metadata?: {
    encoding?: string;
    delimiter?: string;
    hasHeader?: boolean;
  };
}

export interface FileValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface FileUploadResponse {
  success: boolean;
  fileId: string;
  message: string;
  preview?: FilePreview;
  errors?: string[];
}

export interface FileDropzoneProps {
  onFilesAdded: (files: File[]) => void;
  acceptedFileTypes: string[];
  maxFileSize: number;
  multiple?: boolean;
  disabled?: boolean;
}

export interface ImportSummaryProps {
  files: UploadFile[];
  onRemoveFile: (fileId: string) => void;
  onRetryUpload: (fileId: string) => void;
}

export interface ProgressTrackerProps {
  uploads: UploadFile[];
  onCancelUpload: (fileId: string) => void;
}

export type SupportedFileType = 'transformation_file.csv' | 'mapped_data.csv' | 'metadata.json';

export const SUPPORTED_FILE_TYPES: Record<string, SupportedFileType[]> = {
  'text/csv': ['transformation_file.csv', 'mapped_data.csv'],
  'application/json': ['metadata.json'],
};

export const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB in bytes

export const ACCEPTED_MIME_TYPES = ['text/csv', 'application/json'];