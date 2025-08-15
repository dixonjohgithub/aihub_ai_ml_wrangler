/**
 * File: upload.types.ts
 * 
 * Overview:
 * TypeScript type definitions for file upload functionality
 * 
 * Purpose:
 * Provides type safety and interfaces for file import operations
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
  status: 'pending' | 'uploading' | 'completed' | 'error' | 'cancelled';
  progress: number;
  error?: string;
  preview?: FilePreview;
}

export interface FilePreview {
  name: string;
  size: number;
  type: string;
  rows?: number;
  columns?: string[];
  sampleData?: any[];
  metadata?: Record<string, any>;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface UploadConfig {
  maxFileSize: number; // in bytes
  allowedTypes: string[];
  allowedExtensions: string[];
  virusScanEnabled: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadResponse {
  fileId: string;
  fileName: string;
  fileSize: number;
  uploadedAt: string;
  preview: FilePreview;
}

export interface ScanResult {
  isClean: boolean;
  scanEngine: string;
  threats?: string[];
  scanTime: string;
}