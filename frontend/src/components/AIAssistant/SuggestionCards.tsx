/**
 * File: SuggestionCards.tsx
 * 
 * Overview:
 * Display AI suggestions as interactive cards with rationale and actions.
 * 
 * Purpose:
 * Presents analysis suggestions in a user-friendly card format with options
 * to apply, provide feedback, and view implementation details.
 * 
 * Dependencies:
 * - React for UI components
 * - @heroicons/react for icons
 * - react-syntax-highlighter for code display
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState } from 'react';
import {
  LightBulbIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  CodeBracketIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { AISuggestion, SuggestionPriority } from '../../types/ai';
import ConfidenceIndicator from './ConfidenceIndicator';

interface SuggestionCardsProps {
  suggestions: AISuggestion[];
  onApply?: (suggestion: AISuggestion) => void;
  onFeedback?: (suggestionId: string, feedback: 'positive' | 'negative') => void;
  isLoading?: boolean;
}

const SuggestionCards: React.FC<SuggestionCardsProps> = ({
  suggestions,
  onApply,
  onFeedback,
  isLoading
}) => {
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());
  const [appliedSuggestions, setAppliedSuggestions] = useState<Set<string>>(new Set());
  const [feedbackGiven, setFeedbackGiven] = useState<Map<string, 'positive' | 'negative'>>(new Map());

  const toggleExpanded = (id: string) => {
    const newExpanded = new Set(expandedCards);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedCards(newExpanded);
  };

  const handleApply = (suggestion: AISuggestion) => {
    if (onApply) {
      onApply(suggestion);
      setAppliedSuggestions(new Set(appliedSuggestions).add(suggestion.id));
    }
  };

  const handleFeedback = (suggestionId: string, type: 'positive' | 'negative') => {
    if (onFeedback) {
      onFeedback(suggestionId, type);
      setFeedbackGiven(new Map(feedbackGiven).set(suggestionId, type));
    }
  };

  const getPriorityIcon = (priority: SuggestionPriority) => {
    switch (priority) {
      case SuggestionPriority.CRITICAL:
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case SuggestionPriority.HIGH:
        return <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />;
      case SuggestionPriority.MEDIUM:
        return <InformationCircleIcon className="h-5 w-5 text-yellow-600" />;
      case SuggestionPriority.LOW:
        return <InformationCircleIcon className="h-5 w-5 text-blue-600" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const getPriorityColor = (priority: SuggestionPriority) => {
    switch (priority) {
      case SuggestionPriority.CRITICAL:
        return 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20';
      case SuggestionPriority.HIGH:
        return 'border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-900/20';
      case SuggestionPriority.MEDIUM:
        return 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20';
      case SuggestionPriority.LOW:
        return 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20';
      default:
        return 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        <p className="mt-4 text-gray-600 dark:text-gray-400">Analyzing your dataset...</p>
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <div className="p-8 flex flex-col items-center justify-center text-center">
        <LightBulbIcon className="h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Suggestions Yet
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Select an analysis type above to get AI-powered recommendations for your dataset.
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {suggestions.map((suggestion) => {
        const isExpanded = expandedCards.has(suggestion.id);
        const isApplied = appliedSuggestions.has(suggestion.id);
        const feedback = feedbackGiven.get(suggestion.id);

        return (
          <div
            key={suggestion.id}
            className={`border rounded-lg p-4 transition-all ${getPriorityColor(suggestion.priority)} ${
              isApplied ? 'opacity-75' : ''
            }`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start space-x-3">
                {getPriorityIcon(suggestion.priority)}
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {suggestion.title}
                  </h3>
                  <div className="flex items-center space-x-3 mt-1">
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {suggestion.priority} priority
                    </span>
                    <ConfidenceIndicator confidence={suggestion.confidenceScore} />
                  </div>
                </div>
              </div>
              <button
                onClick={() => toggleExpanded(suggestion.id)}
                className="p-1 hover:bg-white/50 dark:hover:bg-gray-700/50 rounded transition-colors"
              >
                {isExpanded ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
              {suggestion.description}
            </p>

            {/* Expanded Content */}
            {isExpanded && (
              <div className="space-y-3 mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                {/* Rationale */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                    Rationale
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {suggestion.rationale}
                  </p>
                </div>

                {/* Affected Columns */}
                {suggestion.affectedColumns && suggestion.affectedColumns.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      Affected Columns
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {suggestion.affectedColumns.map((col) => (
                        <span
                          key={col}
                          className="px-2 py-1 text-xs bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                        >
                          {col}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Implementation Code */}
                {suggestion.implementationCode && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1 flex items-center">
                      <CodeBracketIcon className="h-4 w-4 mr-1" />
                      Implementation
                    </h4>
                    <div className="rounded-md overflow-hidden">
                      <SyntaxHighlighter
                        language="python"
                        style={vscDarkPlus}
                        customStyle={{
                          margin: 0,
                          fontSize: '0.875rem',
                          maxHeight: '200px'
                        }}
                      >
                        {suggestion.implementationCode}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                )}

                {/* Expected Improvement */}
                {suggestion.estimatedImprovement && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      Expected Improvement
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {suggestion.estimatedImprovement}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2">
                {!isApplied ? (
                  <button
                    onClick={() => handleApply(suggestion)}
                    className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md transition-colors"
                  >
                    Apply
                  </button>
                ) : (
                  <div className="flex items-center text-green-600 dark:text-green-400">
                    <CheckCircleIcon className="h-5 w-5 mr-1" />
                    <span className="text-sm">Applied</span>
                  </div>
                )}
              </div>

              {/* Feedback */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleFeedback(suggestion.id, 'positive')}
                  className={`p-1.5 rounded transition-colors ${
                    feedback === 'positive'
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400'
                  }`}
                  title="Helpful"
                >
                  <HandThumbUpIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleFeedback(suggestion.id, 'negative')}
                  className={`p-1.5 rounded transition-colors ${
                    feedback === 'negative'
                      ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400'
                  }`}
                  title="Not helpful"
                >
                  <HandThumbDownIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SuggestionCards;