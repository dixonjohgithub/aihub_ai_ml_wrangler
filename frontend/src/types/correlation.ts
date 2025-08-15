/**
 * File: correlation.ts
 * 
 * Overview:
 * TypeScript type definitions for correlation analysis features.
 * 
 * Purpose:
 * Provides type safety for correlation-related data structures.
 * 
 * Dependencies:
 * None
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

export enum CorrelationType {
  PEARSON = 'pearson',
  SPEARMAN = 'spearman',
  KENDALL = 'kendall',
  CRAMERS_V = 'cramers_v',
  POINT_BISERIAL = 'point_biserial'
}

export interface CorrelationConfig {
  method: CorrelationType;
  threshold: number;
  minPeriods: number;
  handleMissing: 'pairwise' | 'listwise';
  includeCategorical: boolean;
}

export interface CorrelationPair {
  feature1: string;
  feature2: string;
  correlation: number;
}

export interface CorrelationResult {
  correlationMatrix: number[][];
  features: string[];
  highCorrelations: CorrelationPair[];
  featureImportance: Record<string, number>;
  clustering: Record<string, string[]>;
  recommendations: string[];
  metadata: {
    nFeatures: number;
    nHighCorrelations: number;
    method: string;
    threshold: number;
    timestamp: string;
  };
}

export interface MulticollinearityResult {
  highCorrelationPairs: CorrelationPair[];
  vifAnalysis: Array<{
    feature: string;
    vif: number;
  }>;
  problematicFeatures: string[];
  recommendation: string;
}

export interface FeatureRelationship {
  feature: string;
  topCorrelations: Record<string, number>;
  mutualInformation?: Record<string, number>;
  statistics: {
    mean?: number;
    std?: number;
    missing: number;
    unique: number;
  };
}

export interface CorrelationNetworkNode {
  id: string;
  label: string;
  group?: string;
  importance?: number;
}

export interface CorrelationNetworkEdge {
  source: string;
  target: string;
  weight: number;
}

export interface CorrelationNetwork {
  nodes: CorrelationNetworkNode[];
  edges: CorrelationNetworkEdge[];
  threshold: number;
}

export interface CorrelationChangeAnalysis {
  significantChanges: Array<{
    feature1: string;
    feature2: string;
    before: number;
    after: number;
    change: number;
  }>;
  maxChange: number;
  meanChange: number;
  nChanges: number;
}

export interface CorrelationExportOptions {
  format: 'csv' | 'json' | 'html';
  threshold?: number;
  includeMetadata: boolean;
}