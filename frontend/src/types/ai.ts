/**
 * File: ai.ts
 * 
 * Overview:
 * TypeScript type definitions for AI assistant features.
 * 
 * Purpose:
 * Provides type safety for AI-related data structures and API responses.
 * 
 * Dependencies:
 * None
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

export enum AnalysisType {
  GENERAL = 'general',
  FEATURE_ENGINEERING = 'feature_engineering',
  ENCODING_STRATEGY = 'encoding_strategy',
  IMPUTATION_STRATEGY = 'imputation_strategy',
  DATA_QUALITY = 'data_quality',
  CORRELATION_ANALYSIS = 'correlation_analysis',
  OUTLIER_DETECTION = 'outlier_detection'
}

export enum SuggestionPriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

export interface AISuggestion {
  id: string;
  type: string;
  title: string;
  description: string;
  rationale: string;
  priority: SuggestionPriority;
  impactScore: number;
  confidenceScore: number;
  implementationCode?: string;
  affectedColumns?: string[];
  estimatedImprovement?: string;
}

export interface AnalysisResult {
  analysisType: string;
  summary: string;
  suggestions: AISuggestion[];
  metadata: Record<string, any>;
  timestamp: string;
  modelUsed: string;
  totalCost: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AnalysisOptions {
  targetColumn?: string;
  customPrompt?: string;
  maxSuggestions?: number;
  model?: string;
}

export interface FeedbackData {
  suggestionId: string;
  type: 'positive' | 'negative';
  comment?: string;
}

export interface AIServiceConfig {
  apiKey?: string;
  baseUrl?: string;
  maxTokens?: number;
  temperature?: number;
  model?: string;
}