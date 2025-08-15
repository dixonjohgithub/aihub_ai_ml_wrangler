/**
 * File: services/dataService.ts
 * 
 * Overview:
 * Data service layer for handling API calls related to data operations
 * 
 * Purpose:
 * Provides methods for dataset import, imputation, and analysis operations
 * 
 * Dependencies:
 * - @/services/api: Core API client
 * - @/types: Type definitions
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import { apiClient, uploadFile, downloadFile } from './api';
import { 
  ApiResponse, 
  ImportedDataset, 
  ImputationStrategy, 
  ImputationJob, 
  ImputationResults 
} from '@/types';

export class DataService {
  // Dataset Management
  static async uploadDataset(file: File, onProgress?: (progress: number) => void): Promise<ImportedDataset> {
    const response = await uploadFile('/api/datasets/upload', file, onProgress);
    return response.data.data;
  }

  static async getDatasets(): Promise<ImportedDataset[]> {
    const response = await apiClient.get<ApiResponse<ImportedDataset[]>>('/api/datasets');
    return response.data.data;
  }

  static async getDataset(id: string): Promise<ImportedDataset> {
    const response = await apiClient.get<ApiResponse<ImportedDataset>>(`/api/datasets/${id}`);
    return response.data.data;
  }

  static async deleteDataset(id: string): Promise<void> {
    await apiClient.delete(`/api/datasets/${id}`);
  }

  static async previewDataset(id: string, limit: number = 100): Promise<any[]> {
    const response = await apiClient.get<ApiResponse<any[]>>(
      `/api/datasets/${id}/preview?limit=${limit}`
    );
    return response.data.data;
  }

  // Imputation Strategies
  static async getImputationStrategies(dataType?: string): Promise<ImputationStrategy[]> {
    const params = dataType ? `?dataType=${dataType}` : '';
    const response = await apiClient.get<ApiResponse<ImputationStrategy[]>>(
      `/api/imputation/strategies${params}`
    );
    return response.data.data;
  }

  static async getRecommendedStrategies(datasetId: string): Promise<ImputationStrategy[]> {
    const response = await apiClient.post<ApiResponse<ImputationStrategy[]>>(
      `/api/imputation/recommend`,
      { datasetId }
    );
    return response.data.data;
  }

  // Imputation Jobs
  static async createImputationJob(
    datasetId: string, 
    strategies: ImputationStrategy[]
  ): Promise<ImputationJob> {
    const response = await apiClient.post<ApiResponse<ImputationJob>>(
      '/api/imputation/jobs',
      { datasetId, strategies }
    );
    return response.data.data;
  }

  static async getImputationJobs(datasetId?: string): Promise<ImputationJob[]> {
    const params = datasetId ? `?datasetId=${datasetId}` : '';
    const response = await apiClient.get<ApiResponse<ImputationJob[]>>(
      `/api/imputation/jobs${params}`
    );
    return response.data.data;
  }

  static async getImputationJob(jobId: string): Promise<ImputationJob> {
    const response = await apiClient.get<ApiResponse<ImputationJob>>(
      `/api/imputation/jobs/${jobId}`
    );
    return response.data.data;
  }

  static async cancelImputationJob(jobId: string): Promise<void> {
    await apiClient.post(`/api/imputation/jobs/${jobId}/cancel`);
  }

  // Results and Downloads
  static async downloadImputedData(jobId: string, filename?: string): Promise<void> {
    await downloadFile(`/api/imputation/jobs/${jobId}/download/data`, filename);
  }

  static async downloadCorrelationMatrix(jobId: string, filename?: string): Promise<void> {
    await downloadFile(`/api/imputation/jobs/${jobId}/download/correlation`, filename);
  }

  static async downloadReport(jobId: string, filename?: string): Promise<void> {
    await downloadFile(`/api/imputation/jobs/${jobId}/download/report`, filename);
  }

  static async downloadMetadata(jobId: string, filename?: string): Promise<void> {
    await downloadFile(`/api/imputation/jobs/${jobId}/download/metadata`, filename);
  }

  static async downloadAll(jobId: string): Promise<void> {
    await downloadFile(`/api/imputation/jobs/${jobId}/download/all`);
  }

  // Analysis and Insights
  static async analyzeDataset(datasetId: string): Promise<any> {
    const response = await apiClient.post<ApiResponse<any>>(
      '/api/analysis/dataset',
      { datasetId }
    );
    return response.data.data;
  }

  static async getCorrelationMatrix(datasetId: string): Promise<any> {
    const response = await apiClient.get<ApiResponse<any>>(
      `/api/analysis/correlation/${datasetId}`
    );
    return response.data.data;
  }

  static async getMissingDataPattern(datasetId: string): Promise<any> {
    const response = await apiClient.get<ApiResponse<any>>(
      `/api/analysis/missing-pattern/${datasetId}`
    );
    return response.data.data;
  }

  // AI-Powered Recommendations
  static async getAIRecommendations(datasetId: string): Promise<any> {
    const response = await apiClient.post<ApiResponse<any>>(
      '/api/ai/recommendations',
      { datasetId }
    );
    return response.data.data;
  }

  static async getFeatureEngineering(datasetId: string): Promise<any> {
    const response = await apiClient.post<ApiResponse<any>>(
      '/api/ai/feature-engineering',
      { datasetId }
    );
    return response.data.data;
  }

  // Validation and Quality Checks
  static async validateDataset(datasetId: string): Promise<any> {
    const response = await apiClient.post<ApiResponse<any>>(
      '/api/validation/dataset',
      { datasetId }
    );
    return response.data.data;
  }

  static async checkDataQuality(datasetId: string): Promise<any> {
    const response = await apiClient.get<ApiResponse<any>>(
      `/api/validation/quality/${datasetId}`
    );
    return response.data.data;
  }

  // Statistics and Summaries
  static async getDatasetStatistics(datasetId: string): Promise<any> {
    const response = await apiClient.get<ApiResponse<any>>(
      `/api/stats/dataset/${datasetId}`
    );
    return response.data.data;
  }

  static async getColumnStatistics(datasetId: string, columnName: string): Promise<any> {
    const response = await apiClient.get<ApiResponse<any>>(
      `/api/stats/column/${datasetId}/${columnName}`
    );
    return response.data.data;
  }

  // Import/Export Utilities
  static async importFromDataWrangler(file: File): Promise<ImportedDataset> {
    const response = await uploadFile('/api/import/data-wrangler', file);
    return response.data.data;
  }

  static async exportToDataWrangler(datasetId: string): Promise<void> {
    await downloadFile(`/api/export/data-wrangler/${datasetId}`);
  }

  // Real-time Updates (WebSocket or Server-Sent Events)
  static subscribeToJobUpdates(jobId: string, callback: (job: ImputationJob) => void): () => void {
    // Implementation would depend on WebSocket or SSE setup
    // For now, using polling as fallback
    const interval = setInterval(async () => {
      try {
        const job = await this.getImputationJob(jobId);
        callback(job);
        
        // Stop polling if job is completed or failed
        if (job.status === 'completed' || job.status === 'failed') {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error polling job status:', error);
      }
    }, 2000); // Poll every 2 seconds
    
    // Return cleanup function
    return () => clearInterval(interval);
  }
}

export default DataService;