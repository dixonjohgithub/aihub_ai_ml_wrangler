/**
 * File: useAIAssistant.ts
 * 
 * Overview:
 * Custom React hook for managing AI assistant state and operations.
 * 
 * Purpose:
 * Provides a centralized interface for all AI assistant functionality including
 * analysis, suggestions, and chat interactions.
 * 
 * Dependencies:
 * - React hooks
 * - axios for API calls
 * - AI types
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import {
  AnalysisType,
  AISuggestion,
  AnalysisResult,
  AnalysisOptions,
  FeedbackData
} from '../types/ai';

interface UseAIAssistantReturn {
  // State
  suggestions: AISuggestion[];
  isLoading: boolean;
  error: string | null;
  history: AnalysisResult[];
  currentAnalysis: AnalysisResult | null;
  
  // Actions
  analyzeDataset: (data: any, type: AnalysisType, options?: AnalysisOptions) => Promise<void>;
  submitFeedback: (suggestionId: string, type: 'positive' | 'negative') => Promise<void>;
  clearSuggestions: () => void;
  clearError: () => void;
  loadHistoricalAnalysis: (analysis: AnalysisResult) => void;
  exportSuggestions: (format: 'json' | 'markdown') => Promise<string>;
}

export const useAIAssistant = (): UseAIAssistantReturn => {
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await axios.get('/api/ai-analysis/history', {
        params: { limit: 20 }
      });
      if (response.data.success) {
        setHistory(response.data.data.history);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const analyzeDataset = useCallback(async (
    data: any,
    type: AnalysisType,
    options?: AnalysisOptions
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/ai-analysis/analyze', {
        data,
        analysis_type: type,
        target_column: options?.targetColumn,
        context: options?.customPrompt ? { custom_prompt: options.customPrompt } : undefined,
        model: options?.model || 'gpt-4-turbo-preview'
      });

      if (response.data) {
        const analysisResult: AnalysisResult = {
          analysisType: response.data.analysis_type,
          summary: response.data.summary,
          suggestions: response.data.suggestions.map((s: any) => ({
            id: s.id,
            type: s.type,
            title: s.title,
            description: s.description,
            rationale: s.rationale,
            priority: s.priority,
            impactScore: s.impact_score,
            confidenceScore: s.confidence_score,
            implementationCode: s.implementation_code,
            affectedColumns: s.affected_columns,
            estimatedImprovement: s.estimated_improvement
          })),
          metadata: response.data.metadata,
          timestamp: response.data.timestamp,
          modelUsed: response.data.model_used,
          totalCost: response.data.total_cost
        };

        setSuggestions(analysisResult.suggestions);
        setCurrentAnalysis(analysisResult);
        
        // Add to history
        setHistory(prev => [analysisResult, ...prev].slice(0, 20));
      }
    } catch (err: any) {
      console.error('Analysis failed:', err);
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const submitFeedback = useCallback(async (
    suggestionId: string,
    type: 'positive' | 'negative'
  ) => {
    try {
      await axios.post('/api/ai-analysis/feedback', {
        suggestion_id: suggestionId,
        feedback_type: type
      });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  }, []);

  const clearSuggestions = useCallback(() => {
    setSuggestions([]);
    setCurrentAnalysis(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const loadHistoricalAnalysis = useCallback((analysis: AnalysisResult) => {
    setSuggestions(analysis.suggestions);
    setCurrentAnalysis(analysis);
  }, []);

  const exportSuggestions = useCallback(async (format: 'json' | 'markdown'): Promise<string> => {
    if (!currentAnalysis) {
      throw new Error('No analysis to export');
    }

    try {
      const response = await axios.get(`/api/ai-analysis/export/${format}`);
      return response.data.data.content;
    } catch (err) {
      console.error('Export failed:', err);
      throw err;
    }
  }, [currentAnalysis]);

  return {
    suggestions,
    isLoading,
    error,
    history,
    currentAnalysis,
    analyzeDataset,
    submitFeedback,
    clearSuggestions,
    clearError,
    loadHistoricalAnalysis,
    exportSuggestions
  };
};