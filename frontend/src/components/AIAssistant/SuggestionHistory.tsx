/**
 * File: SuggestionHistory.tsx
 * 
 * Overview:
 * Display history of AI analysis sessions and suggestions.
 * 
 * Purpose:
 * Allows users to review past analyses and reload previous suggestions.
 * 
 * Dependencies:
 * - React for UI components
 * - @heroicons/react for icons
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import {
  ClockIcon,
  DocumentTextIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { AnalysisResult } from '../../types/ai';

interface SuggestionHistoryProps {
  history: AnalysisResult[];
  onSelectAnalysis: (analysis: AnalysisResult) => void;
}

const SuggestionHistory: React.FC<SuggestionHistoryProps> = ({
  history,
  onSelectAnalysis
}) => {
  if (history.length === 0) {
    return (
      <div className="p-8 flex flex-col items-center justify-center text-center">
        <ClockIcon className="h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Analysis History
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Your analysis history will appear here after you run analyses.
        </p>
      </div>
    );
  }

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (hours < 1) {
      return 'Just now';
    } else if (hours < 24) {
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (days < 7) {
      return `${days} day${days > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getAnalysisTypeLabel = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
  };

  return (
    <div className="p-4 space-y-2">
      {history.map((analysis, index) => (
        <button
          key={`${analysis.timestamp}-${index}`}
          onClick={() => onSelectAnalysis(analysis)}
          className="w-full p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-purple-300 dark:hover:border-purple-700 hover:shadow-md transition-all text-left group"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <DocumentTextIcon className="h-5 w-5 text-gray-400 dark:text-gray-600" />
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {getAnalysisTypeLabel(analysis.analysisType)}
                </h4>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
                {analysis.summary}
              </p>
              <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-500">
                <span className="flex items-center">
                  <ClockIcon className="h-3 w-3 mr-1" />
                  {formatDate(new Date(analysis.timestamp))}
                </span>
                <span>
                  {analysis.suggestions.length} suggestion{analysis.suggestions.length !== 1 ? 's' : ''}
                </span>
                <span>
                  ${analysis.totalCost.toFixed(4)}
                </span>
              </div>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-gray-400 dark:text-gray-600 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors" />
          </div>
        </button>
      ))}
    </div>
  );
};

export default SuggestionHistory;