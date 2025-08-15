/**
 * File: fileUpload.ts
 * 
 * Overview:
 * Service layer for handling file uploads, validation, and communication with backend
 * 
 * Purpose:
 * Centralized API calls and file handling logic for upload functionality
 * 
 * Dependencies:
 * - axios for HTTP requests
 * - upload.types.ts for type definitions
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import axios, { AxiosProgressEvent } from 'axios';
import {
  FileValidationResult,
  FileUploadResponse,
  FilePreview,
  ACCEPTED_MIME_TYPES,
  MAX_FILE_SIZE,
} from '../types/upload.types';

const API_BASE_URL = 'http://localhost:8000/api';

export class FileUploadService {
  static validateFile(file: File): FileValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      errors.push(`File size (${(file.size / 1024 / 1024).toFixed(2)}MB) exceeds maximum limit of 100MB`);
    }

    // Check file type
    if (!ACCEPTED_MIME_TYPES.includes(file.type)) {
      errors.push(`File type '${file.type}' is not supported. Please upload CSV or JSON files only.`);
    }

    // Check file extension
    const extension = file.name.toLowerCase().split('.').pop();
    if (extension !== 'csv' && extension !== 'json') {
      errors.push(`File extension '.${extension}' is not supported. Please use .csv or .json files.`);
    }

    // Warning for large files
    if (file.size > 50 * 1024 * 1024) { // 50MB
      warnings.push('Large file detected. Upload may take longer than usual.');
    }

    // Check for empty files
    if (file.size === 0) {
      errors.push('File appears to be empty. Please select a valid file.');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  static async uploadFile(
    file: File,
    onProgress?: (progress: AxiosProgressEvent) => void
  ): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', file.type);
    formData.append('file_name', file.name);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: onProgress,
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Upload failed');
      }
      throw new Error('Network error occurred during upload');
    }
  }

  static async getFilePreview(fileId: string): Promise<FilePreview> {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/${fileId}/preview`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to generate preview');
      }
      throw new Error('Network error occurred while generating preview');
    }
  }

  static async deleteFile(fileId: string): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/files/${fileId}`);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to delete file');
      }
      throw new Error('Network error occurred while deleting file');
    }
  }

  static generateFileId(): string {
    return `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  static getFileIcon(fileType: string): string {
    switch (fileType) {
      case 'text/csv':
        return '📊';
      case 'application/json':
        return '📋';
      default:
        return '📄';
    }
  }
}