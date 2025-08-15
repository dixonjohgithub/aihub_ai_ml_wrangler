/**
 * File: AIAssistantPanel.tsx
 * 
 * Overview:
 * Main AI Assistant panel component that provides an interface for interacting
 * with AI-powered analysis and recommendations.
 * 
 * Purpose:
 * Serves as the container for all AI assistant features including chat interface,
 * suggestions display, and history view.
 * 
 * Dependencies:
 * - React for UI components
 * - axios for API calls
 * - @heroicons/react for icons
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  SparklesIcon, 
  ChevronRightIcon, 
  ChevronLeftIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';
import ChatInterface from './ChatInterface';
import SuggestionCards from './SuggestionCards';
import SuggestionHistory from './SuggestionHistory';
import PromptBuilder from './PromptBuilder';
import { useAIAssistant } from '../../hooks/useAIAssistant';
import { AnalysisType } from '../../types/ai';

interface AIAssistantPanelProps {
  isOpen: boolean;
  onClose: () => void;
  dataset?: any;
  onSuggestionApply?: (suggestion: any) => void;
}

const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
  isOpen,
  onClose,
  dataset,
  onSuggestionApply
}) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'suggestions' | 'history'>('suggestions');
  const [isExpanded, setIsExpanded] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  const {
    suggestions,
    isLoading,
    error,
    history,
    analyzeDataset,
    submitFeedback,
    clearError
  } = useAIAssistant();

  useEffect(() => {
    if (dataset && isOpen) {
      // Automatically analyze dataset when panel opens with new data
      analyzeDataset(dataset, AnalysisType.GENERAL);
    }
  }, [dataset, isOpen]);

  // Handle escape key to close panel
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const panelWidth = isExpanded ? 'w-1/2' : 'w-96';

  return (
    <div
      ref={panelRef}
      className={`fixed right-0 top-0 h-full ${panelWidth} bg-white dark:bg-gray-900 shadow-2xl transform transition-transform duration-300 ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      } z-50 flex flex-col`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <SparklesIcon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            AI Assistant
          </h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? (
              <ChevronRightIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            ) : (
              <ChevronLeftIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            )}
          </button>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            title="Close"
          >
            <XMarkIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('suggestions')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'suggestions'
              ? 'text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          Suggestions
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'chat'
              ? 'text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          Chat
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'history'
              ? 'text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          History
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <div className="flex items-center justify-between">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={clearError}
              className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'suggestions' && (
          <div className="h-full flex flex-col">
            <PromptBuilder
              onAnalyze={(type, options) => analyzeDataset(dataset, type, options)}
              isLoading={isLoading}
            />
            <div className="flex-1 overflow-y-auto">
              <SuggestionCards
                suggestions={suggestions}
                onApply={onSuggestionApply}
                onFeedback={submitFeedback}
                isLoading={isLoading}
              />
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <ChatInterface
            dataset={dataset}
            onSuggestionReceived={(suggestions) => {
              // Handle suggestions from chat
            }}
          />
        )}

        {activeTab === 'history' && (
          <SuggestionHistory
            history={history}
            onSelectAnalysis={(analysis) => {
              // Load historical analysis
            }}
          />
        )}
      </div>

      {/* Footer Status */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-2">
            <div className={`h-2 w-2 rounded-full ${isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`} />
            <span>{isLoading ? 'Analyzing...' : 'Ready'}</span>
          </div>
          <div>
            {suggestions.length} suggestions
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistantPanel;