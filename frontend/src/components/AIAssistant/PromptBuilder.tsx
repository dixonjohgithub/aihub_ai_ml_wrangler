/**
 * File: PromptBuilder.tsx
 * 
 * Overview:
 * Context-aware prompt builder for AI analysis requests.
 * 
 * Purpose:
 * Provides an intuitive interface for users to select analysis types
 * and configure parameters for AI-powered dataset analysis.
 * 
 * Dependencies:
 * - React for UI components
 * - @heroicons/react for icons
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState } from 'react';
import {
  BeakerIcon,
  CpuChipIcon,
  TagIcon,
  CalculatorIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ExclamationCircleIcon,
  PlayIcon
} from '@heroicons/react/24/outline';
import { AnalysisType } from '../../types/ai';

interface PromptBuilderProps {
  onAnalyze: (type: AnalysisType, options?: any) => void;
  isLoading?: boolean;
}

const PromptBuilder: React.FC<PromptBuilderProps> = ({ onAnalyze, isLoading }) => {
  const [selectedType, setSelectedType] = useState<AnalysisType>(AnalysisType.GENERAL);
  const [targetColumn, setTargetColumn] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');

  const analysisTypes = [
    {
      type: AnalysisType.GENERAL,
      name: 'General Analysis',
      icon: BeakerIcon,
      description: 'Comprehensive dataset overview and recommendations'
    },
    {
      type: AnalysisType.FEATURE_ENGINEERING,
      name: 'Feature Engineering',
      icon: CpuChipIcon,
      description: 'Suggestions for creating new features'
    },
    {
      type: AnalysisType.ENCODING_STRATEGY,
      name: 'Encoding Strategy',
      icon: TagIcon,
      description: 'Categorical variable encoding recommendations'
    },
    {
      type: AnalysisType.IMPUTATION_STRATEGY,
      name: 'Imputation Strategy',
      icon: CalculatorIcon,
      description: 'Missing data handling strategies'
    },
    {
      type: AnalysisType.DATA_QUALITY,
      name: 'Data Quality',
      icon: ShieldCheckIcon,
      description: 'Data quality issues and cleansing'
    },
    {
      type: AnalysisType.CORRELATION_ANALYSIS,
      name: 'Correlation Analysis',
      icon: ChartBarIcon,
      description: 'Feature correlations and multicollinearity'
    },
    {
      type: AnalysisType.OUTLIER_DETECTION,
      name: 'Outlier Detection',
      icon: ExclamationCircleIcon,
      description: 'Identify and handle outliers'
    }
  ];

  const handleAnalyze = () => {
    const options: any = {};
    
    if (targetColumn) {
      options.targetColumn = targetColumn;
    }
    
    if (customPrompt) {
      options.customPrompt = customPrompt;
    }
    
    onAnalyze(selectedType, options);
  };

  return (
    <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
      {/* Analysis Type Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Analysis Type
        </label>
        <div className="grid grid-cols-2 gap-2">
          {analysisTypes.map(({ type, name, icon: Icon, description }) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`p-3 rounded-lg border text-left transition-all ${
                selectedType === type
                  ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                  : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
              }`}
              title={description}
            >
              <div className="flex items-center space-x-2">
                <Icon className="h-5 w-5 flex-shrink-0" />
                <span className="text-sm font-medium truncate">{name}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Target Column (for supervised learning) */}
      {(selectedType === AnalysisType.FEATURE_ENGINEERING ||
        selectedType === AnalysisType.CORRELATION_ANALYSIS) && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Target Column (Optional)
          </label>
          <input
            type="text"
            value={targetColumn}
            onChange={(e) => setTargetColumn(e.target.value)}
            placeholder="Enter target column name"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-600"
          />
        </div>
      )}

      {/* Custom Prompt */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Additional Context (Optional)
        </label>
        <textarea
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          placeholder="Add specific questions or context..."
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-600 resize-none"
          rows={2}
        />
      </div>

      {/* Analyze Button */}
      <button
        onClick={handleAnalyze}
        disabled={isLoading}
        className="w-full py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        <PlayIcon className="h-5 w-5" />
        <span>{isLoading ? 'Analyzing...' : 'Analyze Dataset'}</span>
      </button>
    </div>
  );
};

export default PromptBuilder;