/**
 * File: ConfidenceIndicator.tsx
 * 
 * Overview:
 * Visual indicator for AI confidence scores.
 * 
 * Purpose:
 * Displays the AI's confidence level for suggestions using a visual meter.
 * 
 * Dependencies:
 * - React for UI components
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';

interface ConfidenceIndicatorProps {
  confidence: number; // 0 to 1
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidence,
  showLabel = true,
  size = 'sm'
}) => {
  const percentage = Math.round(confidence * 100);
  
  const getColor = () => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    if (confidence >= 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getTextColor = () => {
    if (confidence >= 0.8) return 'text-green-600 dark:text-green-400';
    if (confidence >= 0.6) return 'text-yellow-600 dark:text-yellow-400';
    if (confidence >= 0.4) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getLabel = () => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    if (confidence >= 0.4) return 'Low';
    return 'Very Low';
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'lg':
        return { bar: 'h-3', text: 'text-sm' };
      case 'md':
        return { bar: 'h-2', text: 'text-xs' };
      case 'sm':
      default:
        return { bar: 'h-1.5', text: 'text-xs' };
    }
  };

  const sizeClasses = getSizeClasses();

  return (
    <div className="flex items-center space-x-2">
      {showLabel && (
        <span className={`${sizeClasses.text} ${getTextColor()} font-medium`}>
          {getLabel()}
        </span>
      )}
      <div className="flex items-center space-x-1">
        <div className={`w-16 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden ${sizeClasses.bar}`}>
          <div
            className={`h-full ${getColor()} transition-all duration-300`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className={`${sizeClasses.text} text-gray-600 dark:text-gray-400`}>
          {percentage}%
        </span>
      </div>
    </div>
  );
};

export default ConfidenceIndicator;