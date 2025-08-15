import React, { useMemo } from 'react';
import { DataRow, ColumnInfo } from '../../types';
import clsx from 'clsx';

interface MissingDataSummaryProps {
  data: DataRow[];
  columns: ColumnInfo[];
  selectedColumns: string[];
  sampleSize?: number;
}

interface MissingDataPoint {
  row: number;
  column: string;
  isMissing: boolean;
}

export const MissingDataSummary: React.FC<MissingDataSummaryProps> = ({
  data,
  columns,
  selectedColumns,
  sampleSize = 100,
}) => {
  const visibleColumns = useMemo(() => 
    columns.filter(col => selectedColumns.includes(col.name)), 
    [columns, selectedColumns]
  );

  const heatmapData = useMemo(() => {
    // Sample data for performance if dataset is large
    const sampledData = data.length > sampleSize 
      ? data.slice(0, sampleSize)
      : data;

    const points: MissingDataPoint[] = [];
    
    sampledData.forEach((row, rowIndex) => {
      visibleColumns.forEach((column) => {
        const value = row[column.name];
        const isMissing = value === null || value === undefined || value === '';
        
        points.push({
          row: rowIndex,
          column: column.name,
          isMissing,
        });
      });
    });

    return points;
  }, [data, visibleColumns, sampleSize]);

  const missingByColumn = useMemo(() => {
    const stats: { [column: string]: { missing: number; total: number; percentage: number } } = {};
    
    visibleColumns.forEach(column => {
      const columnData = heatmapData.filter(point => point.column === column.name);
      const missing = columnData.filter(point => point.isMissing).length;
      const total = columnData.length;
      const percentage = total > 0 ? (missing / total) * 100 : 0;
      
      stats[column.name] = { missing, total, percentage };
    });

    return stats;
  }, [heatmapData, visibleColumns]);

  const missingByRow = useMemo(() => {
    const stats: { [row: number]: { missing: number; total: number; percentage: number } } = {};
    
    const maxRows = Math.min(data.length, sampleSize);
    
    for (let i = 0; i < maxRows; i++) {
      const rowData = heatmapData.filter(point => point.row === i);
      const missing = rowData.filter(point => point.isMissing).length;
      const total = rowData.length;
      const percentage = total > 0 ? (missing / total) * 100 : 0;
      
      stats[i] = { missing, total, percentage };
    }

    return stats;
  }, [heatmapData, data.length, sampleSize]);

  const totalMissing = useMemo(() => {
    const missing = heatmapData.filter(point => point.isMissing).length;
    const total = heatmapData.length;
    return total > 0 ? (missing / total) * 100 : 0;
  }, [heatmapData]);

  const cellSize = 4;
  const maxDisplayRows = Math.min(data.length, sampleSize);

  if (visibleColumns.length === 0 || data.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 bg-white rounded-lg border border-gray-200">
        <div className="text-4xl mb-4">🔍</div>
        <div className="text-lg font-medium mb-2">No Data to Analyze</div>
        <div className="text-sm">Select columns to view missing data patterns</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Missing Data Heatmap</h3>
        <p className="text-sm text-gray-600">
          Visualizing missing data patterns across {maxDisplayRows} rows and {visibleColumns.length} columns
        </p>
        <div className="mt-2 text-sm">
          <span className="font-medium">Overall missing data: </span>
          <span className={clsx(
            'px-2 py-1 rounded',
            totalMissing < 5 ? 'bg-green-100 text-green-800' :
            totalMissing < 15 ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          )}>
            {totalMissing.toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Heatmap */}
        <div className="lg:col-span-2">
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Pattern Matrix</h4>
            <div className="flex items-center space-x-4 text-xs text-gray-600">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-gray-100 border"></div>
                <span>Present</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-red-400"></div>
                <span>Missing</span>
              </div>
            </div>
          </div>
          
          <div className="overflow-auto border border-gray-200 rounded">
            <div className="relative">
              {/* Column headers */}
              <div className="flex sticky top-0 bg-white border-b border-gray-200 z-10">
                <div className="w-12 flex-shrink-0"></div>
                {visibleColumns.map((column) => (
                  <div
                    key={column.name}
                    className="text-xs text-gray-600 p-2 border-r border-gray-100 last:border-r-0"
                    style={{ minWidth: '60px', maxWidth: '80px' }}
                  >
                    <div className="truncate" title={column.name}>
                      {column.name}
                    </div>
                  </div>
                ))}
              </div>

              {/* Heatmap rows */}
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {Array.from({ length: maxDisplayRows }, (_, rowIndex) => (
                  <div key={rowIndex} className="flex border-b border-gray-50 last:border-b-0">
                    {/* Row number */}
                    <div className="w-12 flex-shrink-0 text-xs text-gray-500 p-1 text-right bg-gray-50 border-r border-gray-100">
                      {rowIndex + 1}
                    </div>
                    
                    {/* Row cells */}
                    {visibleColumns.map((column) => {
                      const point = heatmapData.find(p => p.row === rowIndex && p.column === column.name);
                      const isMissing = point?.isMissing || false;
                      
                      return (
                        <div
                          key={column.name}
                          className="border-r border-gray-100 last:border-r-0 p-1"
                          style={{ minWidth: '60px', maxWidth: '80px' }}
                        >
                          <div
                            className={clsx(
                              'w-full h-4 rounded-sm',
                              isMissing ? 'bg-red-400' : 'bg-gray-100'
                            )}
                            title={`Row ${rowIndex + 1}, ${column.name}: ${isMissing ? 'Missing' : 'Present'}`}
                          ></div>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Summary Statistics */}
        <div className="space-y-4">
          {/* Column Summary */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Missing by Column</h4>
            <div className="space-y-2">
              {visibleColumns.map((column) => {
                const stats = missingByColumn[column.name];
                if (!stats) return null;
                
                return (
                  <div key={column.name} className="text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <span className="truncate font-medium" title={column.name}>
                        {column.name}
                      </span>
                      <span className="text-gray-600">
                        {stats.percentage.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className={clsx(
                          'h-1.5 rounded-full',
                          stats.percentage === 0 ? 'bg-green-400' :
                          stats.percentage < 10 ? 'bg-yellow-400' :
                          stats.percentage < 30 ? 'bg-orange-400' :
                          'bg-red-400'
                        )}
                        style={{ width: `${Math.max(stats.percentage, 1)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Row Summary */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Row Completeness</h4>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span>Complete rows:</span>
                <span className="font-medium">
                  {Object.values(missingByRow).filter(r => r.percentage === 0).length}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Partial rows:</span>
                <span className="font-medium">
                  {Object.values(missingByRow).filter(r => r.percentage > 0 && r.percentage < 100).length}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Empty rows:</span>
                <span className="font-medium">
                  {Object.values(missingByRow).filter(r => r.percentage === 100).length}
                </span>
              </div>
            </div>
          </div>

          {/* Pattern Insights */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Insights</h4>
            <div className="text-xs text-gray-600 space-y-1">
              {totalMissing === 0 && (
                <div className="text-green-600">✓ No missing data detected</div>
              )}
              {totalMissing > 0 && totalMissing < 5 && (
                <div className="text-yellow-600">⚠ Low missing data ({totalMissing.toFixed(1)}%)</div>
              )}
              {totalMissing >= 5 && totalMissing < 15 && (
                <div className="text-orange-600">⚠ Moderate missing data ({totalMissing.toFixed(1)}%)</div>
              )}
              {totalMissing >= 15 && (
                <div className="text-red-600">🚨 High missing data ({totalMissing.toFixed(1)}%)</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};