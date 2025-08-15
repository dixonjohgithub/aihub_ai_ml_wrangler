/**
 * File: StrategySelector.tsx
 * 
 * Overview:
 * Dropdown component for selecting imputation strategies.
 * 
 * Purpose:
 * Provides strategy selection with recommendations based on data type.
 * 
 * Dependencies:
 * - React: UI framework
 * - antd: UI components
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import { Select, Tag, Tooltip } from 'antd';
import { InfoCircleOutlined, StarFilled } from '@ant-design/icons';
import { ImputationStrategy } from '../../types/imputation';

const { Option } = Select;

interface StrategySelectorProps {
  value: ImputationStrategy;
  dataType: string;
  missingPercentage: number;
  onChange: (strategy: ImputationStrategy) => void;
}

const StrategySelector: React.FC<StrategySelectorProps> = ({
  value,
  dataType,
  missingPercentage,
  onChange
}) => {
  const getRecommendedStrategies = (): ImputationStrategy[] => {
    const recommendations: ImputationStrategy[] = [];

    if (dataType === 'numeric') {
      if (missingPercentage < 5) {
        recommendations.push(ImputationStrategy.MEAN, ImputationStrategy.MEDIAN);
      } else if (missingPercentage < 20) {
        recommendations.push(ImputationStrategy.KNN, ImputationStrategy.MICE);
      } else {
        recommendations.push(ImputationStrategy.RANDOM_FOREST, ImputationStrategy.MICE);
      }
    } else if (dataType === 'categorical') {
      recommendations.push(ImputationStrategy.MODE, ImputationStrategy.CONSTANT);
    } else if (dataType === 'datetime') {
      recommendations.push(ImputationStrategy.FORWARD_FILL, ImputationStrategy.INTERPOLATION);
    }

    return recommendations;
  };

  const getStrategyInfo = (strategy: ImputationStrategy): { description: string; complexity: string } => {
    const info: Record<ImputationStrategy, { description: string; complexity: string }> = {
      [ImputationStrategy.MEAN]: {
        description: 'Simple and fast, good for normally distributed data',
        complexity: 'Low'
      },
      [ImputationStrategy.MEDIAN]: {
        description: 'Robust to outliers, good for skewed distributions',
        complexity: 'Low'
      },
      [ImputationStrategy.MODE]: {
        description: 'Best for categorical data, uses most frequent value',
        complexity: 'Low'
      },
      [ImputationStrategy.FORWARD_FILL]: {
        description: 'Uses previous value, good for time series',
        complexity: 'Low'
      },
      [ImputationStrategy.BACKWARD_FILL]: {
        description: 'Uses next value, good for time series',
        complexity: 'Low'
      },
      [ImputationStrategy.INTERPOLATION]: {
        description: 'Smooth interpolation, good for continuous data',
        complexity: 'Medium'
      },
      [ImputationStrategy.KNN]: {
        description: 'Uses similar records, captures local patterns',
        complexity: 'Medium'
      },
      [ImputationStrategy.RANDOM_FOREST]: {
        description: 'ML-based prediction, handles complex relationships',
        complexity: 'High'
      },
      [ImputationStrategy.MICE]: {
        description: 'Multiple imputation, best for MAR data',
        complexity: 'High'
      },
      [ImputationStrategy.CONSTANT]: {
        description: 'Replace with specific value',
        complexity: 'Low'
      },
      [ImputationStrategy.DROP]: {
        description: 'Remove rows with missing values',
        complexity: 'Low'
      }
    };
    return info[strategy];
  };

  const recommendedStrategies = getRecommendedStrategies();

  const getComplexityColor = (complexity: string): string => {
    switch (complexity) {
      case 'Low': return 'green';
      case 'Medium': return 'orange';
      case 'High': return 'red';
      default: return 'default';
    }
  };

  return (
    <Select
      value={value}
      onChange={onChange}
      className="w-full"
      placeholder="Select strategy"
    >
      {Object.values(ImputationStrategy).map(strategy => {
        const info = getStrategyInfo(strategy);
        const isRecommended = recommendedStrategies.includes(strategy);
        
        return (
          <Option key={strategy} value={strategy}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span>{strategy.replace('_', ' ').toLowerCase()}</span>
                {isRecommended && (
                  <StarFilled className="text-yellow-500" style={{ fontSize: '12px' }} />
                )}
              </div>
              <div className="flex items-center space-x-1">
                <Tag color={getComplexityColor(info.complexity)} className="text-xs">
                  {info.complexity}
                </Tag>
                <Tooltip title={info.description}>
                  <InfoCircleOutlined className="text-gray-400" style={{ fontSize: '12px' }} />
                </Tooltip>
              </div>
            </div>
          </Option>
        );
      })}
    </Select>
  );
};

export default StrategySelector;