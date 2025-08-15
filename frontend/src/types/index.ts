/**
 * File: index.ts
 * 
 * Overview:
 * TypeScript type definitions for the application
 * 
 * Purpose:
 * Central location for all type definitions and interfaces
 * 
 * Dependencies:
 * - TypeScript for type definitions
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

// API Response Types
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
}

// File Upload Types
export interface FileUpload {
  id: string
  filename: string
  originalName: string
  size: number
  mimetype: string
  uploadedAt: string
  status: 'uploading' | 'completed' | 'processing' | 'error'
}

// Data Analysis Types
export interface DataColumn {
  name: string
  dataType: 'numeric' | 'categorical' | 'datetime' | 'boolean'
  missingCount: number
  missingPercentage: number
  uniqueCount: number
  sampleValues: any[]
}

export interface DataSummary {
  id: string
  filename: string
  totalRows: number
  totalColumns: number
  missingValueCount: number
  missingValuePercentage: number
  columns: DataColumn[]
  createdAt: string
}

// Imputation Types
export interface ImputationStrategy {
  columnName: string
  method: 'mean' | 'median' | 'mode' | 'forward_fill' | 'backward_fill' | 'knn' | 'random_forest' | 'custom'
  parameters?: Record<string, any>
}

export interface ImputationJob {
  id: string
  fileId: string
  strategies: ImputationStrategy[]
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  createdAt: string
  completedAt?: string
}

// Correlation Analysis Types
export interface CorrelationMatrix {
  variables: string[]
  values: number[][]
  method: 'pearson' | 'spearman'
}

// AI Recommendation Types
export interface AIRecommendation {
  id: string
  type: 'imputation' | 'encoding' | 'feature_engineering'
  columnName: string
  recommendation: string
  rationale: string
  confidence: number
  parameters?: Record<string, any>
}

// Navigation Types
export interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  current?: boolean
}

// Form Types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'checkbox' | 'file'
  required?: boolean
  options?: { value: string; label: string }[]
  validation?: {
    min?: number
    max?: number
    pattern?: string
  }
}

// Error Types
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: string
}