/**
 * File: uploadService.ts
 * 
 * Overview:
 * API service for file upload operations with progress tracking
 * 
 * Purpose:
 * Handles communication with backend upload endpoints
 * 
 * Dependencies:
 * - axios (for HTTP requests)
 * - upload.types (for TypeScript interfaces)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import axios, { AxiosProgressEvent, CancelTokenSource } from 'axios';
import { ApiResponse, UploadResponse, ScanResult, UploadProgress } from '../types/upload.types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class UploadService {
  private cancelTokens: Map<string, CancelTokenSource> = new Map();

  async uploadFile(
    file: File,
    fileId: string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileId', fileId);

    // Create cancel token for this upload
    const cancelToken = axios.CancelToken.source();
    this.cancelTokens.set(fileId, cancelToken);

    try {
      const response = await axios.post<ApiResponse<UploadResponse>>(
        `${API_BASE_URL}/api/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          cancelToken: cancelToken.token,
          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            if (onProgress && progressEvent.total) {
              const progress: UploadProgress = {
                loaded: progressEvent.loaded,
                total: progressEvent.total,
                percentage: Math.round((progressEvent.loaded * 100) / progressEvent.total)
              };
              onProgress(progress);
            }
          },
        }
      );

      // Remove cancel token after successful upload
      this.cancelTokens.delete(fileId);
      
      return response.data;
    } catch (error) {
      // Remove cancel token
      this.cancelTokens.delete(fileId);
      
      if (axios.isCancel(error)) {
        throw new Error('Upload cancelled');
      }
      
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.error || error.message;
        throw new Error(errorMessage);
      }
      
      throw error;
    }
  }

  cancelUpload(fileId: string): boolean {
    const cancelToken = this.cancelTokens.get(fileId);
    if (cancelToken) {
      cancelToken.cancel('Upload cancelled by user');
      this.cancelTokens.delete(fileId);
      return true;
    }
    return false;
  }

  async getUploadStatus(fileId: string): Promise<ApiResponse<any>> {
    try {
      const response = await axios.get<ApiResponse<any>>(
        `${API_BASE_URL}/api/upload/${fileId}/status`
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.error || error.message;
        throw new Error(errorMessage);
      }
      throw error;
    }
  }

  async scanFile(fileId: string): Promise<ApiResponse<ScanResult>> {
    try {
      const response = await axios.post<ApiResponse<ScanResult>>(
        `${API_BASE_URL}/api/upload/${fileId}/scan`
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.error || error.message;
        throw new Error(errorMessage);
      }
      throw error;
    }
  }

  async deleteFile(fileId: string): Promise<ApiResponse<void>> {
    try {
      const response = await axios.delete<ApiResponse<void>>(
        `${API_BASE_URL}/api/upload/${fileId}`
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.error || error.message;
        throw new Error(errorMessage);
      }
      throw error;
    }
  }

  async getFilePreview(fileId: string): Promise<ApiResponse<any>> {
    try {
      const response = await axios.get<ApiResponse<any>>(
        `${API_BASE_URL}/api/upload/${fileId}/preview`
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.error || error.message;
        throw new Error(errorMessage);
      }
      throw error;
    }
  }

  async validateFileContent(file: File): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<ApiResponse<any>>(
        `${API_BASE_URL}/api/upload/validate`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.error || error.message;
        throw new Error(errorMessage);
      }
      throw error;
    }
  }

  // Batch operations
  async uploadMultipleFiles(
    files: File[],
    fileIds: string[],
    onProgress?: (fileId: string, progress: UploadProgress) => void
  ): Promise<Map<string, ApiResponse<UploadResponse>>> {
    const results = new Map<string, ApiResponse<UploadResponse>>();
    
    // Upload files sequentially to avoid overwhelming the server
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileId = fileIds[i];
      
      try {
        const result = await this.uploadFile(
          file,
          fileId,
          onProgress ? (progress) => onProgress(fileId, progress) : undefined
        );
        results.set(fileId, result);
      } catch (error) {
        results.set(fileId, {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
    
    return results;
  }

  async scanMultipleFiles(fileIds: string[]): Promise<Map<string, ApiResponse<ScanResult>>> {
    const results = new Map<string, ApiResponse<ScanResult>>();
    
    // Scan files in parallel
    const scanPromises = fileIds.map(async (fileId) => {
      try {
        const result = await this.scanFile(fileId);
        results.set(fileId, result);
      } catch (error) {
        results.set(fileId, {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    });
    
    await Promise.all(scanPromises);
    return results;
  }

  // Cleanup method to cancel all pending uploads
  cancelAllUploads(): void {
    this.cancelTokens.forEach((cancelToken, fileId) => {
      cancelToken.cancel('All uploads cancelled');
    });
    this.cancelTokens.clear();
  }

  // Get active upload count
  getActiveUploadCount(): number {
    return this.cancelTokens.size;
  }
}

// Export singleton instance
export const uploadService = new UploadService();
export default uploadService;