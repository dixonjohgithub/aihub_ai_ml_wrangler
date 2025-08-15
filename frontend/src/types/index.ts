/**
 * File: types/index.ts
 * 
 * Overview:
 * Type definitions for the AI Hub AI/ML Wrangler frontend application
 * 
 * Purpose:
 * Provides TypeScript interfaces and types for components, API responses, and application state
 * 
 * Dependencies:
 * - None (pure TypeScript types)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

// Data Import Types
export interface ImportedDataset {
  id: string;
  filename: string;
  size: number;
  uploadedAt: string;
  columns: DataColumn[];
  rowCount: number;
  missingDataSummary: MissingDataSummary;
}

export interface DataColumn {
  name: string;
  dataType: 'string' | 'number' | 'boolean' | 'date';
  missingCount: number;
  missingPercentage: number;
  nullable: boolean;
}

export interface MissingDataSummary {
  totalMissing: number;
  missingPercentage: number;
  columnsWithMissing: number;
  pattern: string;
}

// Imputation Types
export interface ImputationStrategy {
  id: string;
  name: string;
  type: 'statistical' | 'ml' | 'correlation' | 'time_series';
  description: string;
  applicableTypes: string[];
  parameters: Record<string, any>;
}

export interface ImputationJob {
  id: string;
  datasetId: string;
  strategies: ImputationStrategy[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  createdAt: string;
  completedAt?: string;
  results?: ImputationResults;
}

export interface ImputationResults {
  imputedDataUrl: string;
  correlationMatrixUrl: string;
  reportUrl: string;
  metadataUrl: string;
  summary: {
    totalImputedValues: number;
    processingTime: number;
    qualityScore: number;
  };
}

// UI Component Types
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export interface LayoutProps {
  children: React.ReactNode;
}

export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon?: string;
  badge?: string;
  disabled?: boolean;
}

// Application State Types
export interface AppState {
  user: User | null;
  datasets: ImportedDataset[];
  currentDataset: ImportedDataset | null;
  jobs: ImputationJob[];
  loading: boolean;
  error: string | null;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

// Route Types
export interface RouteConfig {
  path: string;
  component: React.ComponentType<any>;
  exact?: boolean;
  title: string;
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'file';
  required?: boolean;
  placeholder?: string;
  options?: SelectOption[];
  validation?: ValidationRule[];
}

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface ValidationRule {
  type: 'required' | 'minLength' | 'maxLength' | 'pattern' | 'custom';
  value?: any;
  message: string;
}

// Table Types
export interface TableColumn<T = any> {
  key: keyof T;
  title: string;
  dataIndex?: keyof T;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  width?: number;
}

export interface TableProps<T = any> {
  columns: TableColumn<T>[];
  data: T[];
  loading?: boolean;
  pagination?: boolean;
  pageSize?: number;
  onRowClick?: (record: T, index: number) => void;
}

// Notification Types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

// Workflow Types
export interface WorkflowStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  component?: React.ComponentType<any>;
  optional?: boolean;
}

export interface WorkflowConfig {
  steps: WorkflowStep[];
  currentStep: number;
  canNavigateBackward: boolean;
  canNavigateForward: boolean;
}

// Chart and Visualization Types
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
}

export interface VisualizationConfig {
  type: 'bar' | 'line' | 'pie' | 'scatter' | 'heatmap';
  data: ChartData;
  options?: Record<string, any>;
}

// Export utility type for environment variables
export interface EnvironmentConfig {
  API_BASE_URL: string;
  NODE_ENV: 'development' | 'production' | 'test';
  UPLOAD_MAX_SIZE: number;
  SUPPORTED_FILE_TYPES: string[];
}