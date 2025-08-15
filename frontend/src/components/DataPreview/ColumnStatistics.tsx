import React from 'react';
import { ColumnStatistics as ColumnStatsType } from '../../types';
import clsx from 'clsx';

interface ColumnStatisticsProps {
  statistics: ColumnStatsType[];
  selectedColumn?: string;
  onColumnSelect?: (column: string) => void;
}

export const ColumnStatistics: React.FC<ColumnStatisticsProps> = ({
  statistics,
  selectedColumn,
  onColumnSelect,
}) => {
  const formatNumber = (num: number | undefined, decimals: number = 2): string => {
    if (num === undefined || num === null) return 'N/A';
    return num.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: decimals });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'number':
        return '🔢';
      case 'string':
        return '📝';
      case 'boolean':
        return '✅';
      case 'date':
        return '📅';
      default:
        return '❓';
    }
  };

  const getMissingDataColor = (percentage: number) => {
    if (percentage === 0) return 'bg-green-100 text-green-800';
    if (percentage < 10) return 'bg-yellow-100 text-yellow-800';
    if (percentage < 30) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="h-full bg-white border-l border-gray-200 overflow-y-auto">
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <h3 className="text-lg font-medium text-gray-900">Column Statistics</h3>
        <p className="text-sm text-gray-600 mt-1">
          Click on a column to view detailed statistics
        </p>
      </div>

      <div className="divide-y divide-gray-100">
        {statistics.map((stat) => {
          const isSelected = selectedColumn === stat.column;
          
          return (
            <div
              key={stat.column}
              className={clsx(
                'p-4 cursor-pointer transition-colors hover:bg-gray-50',
                isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''
              )}
              onClick={() => onColumnSelect?.(stat.column)}
            >
              {/* Column Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getTypeIcon(stat.type)}</span>
                  <h4 className="font-medium text-gray-900 truncate">
                    {stat.column}
                  </h4>
                </div>
                <span className="text-xs text-gray-500 capitalize bg-gray-100 px-2 py-1 rounded">
                  {stat.type}
                </span>
              </div>

              {/* Basic Stats */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <div className="text-xs text-gray-500">Count</div>
                  <div className="font-medium">{formatNumber(stat.count, 0)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Unique</div>
                  <div className="font-medium">{formatNumber(stat.unique, 0)}</div>
                </div>
              </div>

              {/* Missing Data */}
              <div className="mb-3">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                  <span>Missing Data</span>
                  <span>{formatNumber(stat.missing, 0)} rows</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className={clsx(
                      'h-2 rounded-full transition-all duration-300',
                      stat.missingPercentage > 0 ? 'bg-red-400' : 'bg-green-400'
                    )}
                    style={{ width: `${Math.max(stat.missingPercentage, 2)}%` }}
                  ></div>
                </div>
                <span className={clsx(
                  'inline-block px-2 py-1 rounded-full text-xs font-medium',
                  getMissingDataColor(stat.missingPercentage)
                )}>
                  {formatNumber(stat.missingPercentage, 1)}% missing
                </span>
              </div>

              {/* Numeric Statistics */}
              {stat.type === 'number' && (
                <div className="space-y-2">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-xs text-gray-500">Mean</div>
                      <div className="font-medium">{formatNumber(stat.mean)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Median</div>
                      <div className="font-medium">{formatNumber(stat.median)}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-xs text-gray-500">Min</div>
                      <div className="font-medium">{formatNumber(stat.min)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Max</div>
                      <div className="font-medium">{formatNumber(stat.max)}</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-xs text-gray-500">Q25</div>
                      <div className="font-medium">{formatNumber(stat.q25)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Q75</div>
                      <div className="font-medium">{formatNumber(stat.q75)}</div>
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-gray-500">Std Dev</div>
                    <div className="font-medium">{formatNumber(stat.std)}</div>
                  </div>
                </div>
              )}

              {/* Mode for all types */}
              <div className="mt-3 pt-3 border-t border-gray-100">
                <div className="text-xs text-gray-500">Most Common</div>
                <div className="font-medium truncate" title={String(stat.mode)}>
                  {stat.mode !== null && stat.mode !== undefined ? String(stat.mode) : 'N/A'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {statistics.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          <div className="text-4xl mb-4">📊</div>
          <div className="text-lg font-medium mb-2">No Data</div>
          <div className="text-sm">Select columns to view statistics</div>
        </div>
      )}
    </div>
  );
};