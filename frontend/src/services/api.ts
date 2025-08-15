/**
 * File: services/api.ts
 * 
 * Overview:
 * Core API service configuration with axios instance and interceptors
 * 
 * Purpose:
 * Provides centralized HTTP client configuration for API communication
 * 
 * Dependencies:
 * - axios: HTTP client library
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, ApiError } from '@/types';

// Get API base URL from environment or default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with base configuration
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens, logging, etc.
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Add authentication token if available
    const token = localStorage.getItem('authToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      if (config.data) {
        console.log('📤 Request Data:', config.data);
      }
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`);
      console.log('📥 Response Data:', response.data);
    }
    
    return response;
  },
  (error) => {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      const apiError: ApiError = {
        message: error.response.data?.message || 'An error occurred',
        code: error.response.data?.code,
        details: error.response.data?.details,
      };
      
      // Handle specific status codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - redirect to login or refresh token
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden - show access denied message
          console.error('❌ Access Denied:', apiError.message);
          break;
        case 404:
          // Not Found
          console.error('❌ Resource Not Found:', error.config?.url);
          break;
        case 500:
          // Server Error
          console.error('❌ Server Error:', apiError.message);
          break;
        default:
          console.error(`❌ API Error (${error.response.status}):`, apiError.message);
      }
      
      return Promise.reject(apiError);
    } else if (error.request) {
      // Request made but no response received
      const networkError: ApiError = {
        message: 'Network error - please check your connection',
        code: 'NETWORK_ERROR',
      };
      console.error('❌ Network Error:', networkError);
      return Promise.reject(networkError);
    } else {
      // Something else happened
      const unknownError: ApiError = {
        message: error.message || 'An unknown error occurred',
        code: 'UNKNOWN_ERROR',
      };
      console.error('❌ Unknown Error:', unknownError);
      return Promise.reject(unknownError);
    }
  }
);

// Helper function to handle file uploads with progress
export const uploadFile = (
  url: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<AxiosResponse<ApiResponse>> => {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiClient.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(progress);
      }
    },
  });
};

// Helper function for downloading files
export const downloadFile = async (
  url: string,
  filename?: string
): Promise<void> => {
  try {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    });
    
    // Create blob URL and trigger download
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error('❌ Download Error:', error);
    throw error;
  }
};

// Health check function
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('❌ Health Check Failed:', error);
    return false;
  }
};

export default apiClient;