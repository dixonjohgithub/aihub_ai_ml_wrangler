/**
 * File: imputation.ts
 * 
 * Overview:
 * TypeScript type definitions for imputation features.
 * 
 * Purpose:
 * Provides type safety for imputation-related data structures.
 * 
 * Dependencies:
 * None
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

export enum ImputationStrategy {
  MEAN = 'mean',
  MEDIAN = 'median',
  MODE = 'mode',
  FORWARD_FILL = 'forward_fill',
  BACKWARD_FILL = 'backward_fill',
  INTERPOLATION = 'interpolation',
  KNN = 'knn',
  RANDOM_FOREST = 'random_forest',
  MICE = 'mice',
  CONSTANT = 'constant',
  DROP = 'drop'
}

export interface ImputationConfig {
  strategy: ImputationStrategy;
  columns: string[];
  parameters: Record<string, any>;
  validate: boolean;
  previewRows: number;
}

export interface ColumnImputationConfig {
  column: string;
  strategy: ImputationStrategy;
  parameters: Record<string, any>;
  enabled: boolean;
}

export interface ImputationResult {
  strategy: string;
  columnsImputed: string[];
  valuesImputed: number;
  qualityMetrics: {
    completeness: number;
    distributionPreservation?: number;
    variancePreservation?: number;
  };
  executionTime: number;
  warnings: string[];
}

export interface ImputationPreviewData {
  original: any[];
  imputed: any[];
  differences: Array<{
    index: number;
    original: any;
    imputed: any;
  }>;
}

export interface ImputationStrategyRecommendation {
  strategy: ImputationStrategy;
  recommended: boolean;
  reason: string;
  score?: number;
}

export interface ImputationQualityMetrics {
  completeness: number;
  distributionSimilarity: number;
  varianceRatio: number;
  patternPreservation: number;
}

export interface BatchImputationConfig {
  configurations: ColumnImputationConfig[];
  validateAll: boolean;
  stopOnError: boolean;
}