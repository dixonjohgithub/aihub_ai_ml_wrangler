/**
 * File: dataService.ts
 * 
 * Overview:
 * Service layer for data-related API operations
 * 
 * Purpose:
 * Handle file uploads, data processing, and imputation requests
 * 
 * Dependencies:
 * - api instance for HTTP requests
 * - TypeScript interfaces for type safety
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import api from './api'

export interface UploadResponse {
  id: string
  filename: string
  size: number
  status: string
}

export interface DataSummary {
  rows: number
  columns: number
  missing_values: number
  data_types: Record<string, string>
}

export const dataService = {
  // Upload file
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },

  // Get data summary
  getDataSummary: async (fileId: string): Promise<DataSummary> => {
    const response = await api.get(`/api/data/${fileId}/summary`)
    return response.data
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default dataService