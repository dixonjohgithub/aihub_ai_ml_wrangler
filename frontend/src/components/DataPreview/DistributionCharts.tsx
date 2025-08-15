import React, { useMemo } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BoxPlot,
  ComposedChart,
  Line
} from 'recharts';
import { DataRow, ColumnInfo, ColumnStatistics } from '../../types';

interface DistributionChartsProps {
  data: DataRow[];
  columns: ColumnInfo[];
  statistics: ColumnStatistics[];
  selectedColumn?: string;
}

interface HistogramBin {
  bin: string;
  count: number;
  range: string;
}

interface BoxPlotData {
  name: string;
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  outliers: number[];
}

export const DistributionCharts: React.FC<DistributionChartsProps> = ({
  data,
  columns,
  statistics,
  selectedColumn,
}) => {
  const numericColumns = useMemo(() => 
    columns.filter(col => col.type === 'number'),
    [columns]
  );

  const generateHistogramData = (columnName: string, binCount: number = 20): HistogramBin[] => {
    const values = data
      .map(row => row[columnName])
      .filter(val => val !== null && val !== undefined && !isNaN(val))
      .map(val => Number(val))
      .sort((a, b) => a - b);

    if (values.length === 0) return [];

    const min = values[0];
    const max = values[values.length - 1];
    const binWidth = (max - min) / binCount;

    const bins: HistogramBin[] = [];
    
    for (let i = 0; i < binCount; i++) {
      const binStart = min + i * binWidth;
      const binEnd = min + (i + 1) * binWidth;
      const binValues = values.filter(val => 
        i === binCount - 1 ? (val >= binStart && val <= binEnd) : (val >= binStart && val < binEnd)
      );
      
      bins.push({
        bin: `${i + 1}`,
        count: binValues.length,
        range: `${binStart.toFixed(1)} - ${binEnd.toFixed(1)}`,
      });
    }

    return bins;
  };

  const generateBoxPlotData = (columnName: string): BoxPlotData[] => {
    const values = data
      .map(row => row[columnName])
      .filter(val => val !== null && val !== undefined && !isNaN(val))
      .map(val => Number(val))
      .sort((a, b) => a - b);

    if (values.length === 0) return [];

    const q1Index = Math.floor(values.length * 0.25);
    const medianIndex = Math.floor(values.length * 0.5);
    const q3Index = Math.floor(values.length * 0.75);

    const q1 = values[q1Index];
    const median = values[medianIndex];
    const q3 = values[q3Index];
    const iqr = q3 - q1;
    
    const lowerFence = q1 - 1.5 * iqr;
    const upperFence = q3 + 1.5 * iqr;
    
    const min = values.find(v => v >= lowerFence) || values[0];
    const max = values.reverse().find(v => v <= upperFence) || values[0];
    
    const outliers = values.filter(v => v < lowerFence || v > upperFence);

    return [{
      name: columnName,
      min,
      q1,
      median,
      q3,
      max,
      outliers,
    }];
  };

  const formatTooltip = (value: any, name: string) => {
    if (name === 'count') {
      return [`${value} values`, 'Frequency'];
    }
    return [value, name];
  };

  if (numericColumns.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 bg-white rounded-lg border border-gray-200">
        <div className="text-4xl mb-4">📊</div>
        <div className="text-lg font-medium mb-2">No Numeric Columns</div>
        <div className="text-sm">Select numeric columns to view distribution charts</div>
      </div>
    );
  }

  const activeColumn = selectedColumn && numericColumns.find(col => col.name === selectedColumn)
    ? selectedColumn
    : numericColumns[0].name;

  const histogramData = generateHistogramData(activeColumn);
  const boxPlotData = generateBoxPlotData(activeColumn);
  const columnStats = statistics.find(stat => stat.column === activeColumn);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Distribution Analysis</h3>
        <p className="text-sm text-gray-600">
          Statistical distribution and patterns for numeric columns
        </p>
      </div>

      {/* Column Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Column
        </label>
        <select
          value={activeColumn}
          onChange={(e) => {
            // This would be handled by parent component
            console.log('Column selected:', e.target.value);
          }}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
          {numericColumns.map(column => (
            <option key={column.name} value={column.name}>
              {column.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Histogram */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-4">Distribution Histogram</h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={histogramData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="bin" 
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Bins', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={formatTooltip}
                  labelFormatter={(label, payload) => {
                    const data = payload?.[0]?.payload;
                    return data ? `Range: ${data.range}` : `Bin ${label}`;
                  }}
                />
                <Bar 
                  dataKey="count" 
                  fill="#3B82F6" 
                  stroke="#1E40AF" 
                  strokeWidth={1}
                  radius={[2, 2, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Box Plot Simulation */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-4">Box Plot Summary</h4>
          {columnStats && (
            <div className="space-y-4">
              {/* Visual Box Plot */}
              <div className="relative h-32 bg-gray-50 rounded p-4">
                <div className="flex items-center h-full">
                  <div className="flex-1 relative">
                    {/* Box plot visualization */}
                    <div className="relative h-8 mx-8">
                      {/* Min-Max line */}
                      <div 
                        className="absolute top-1/2 h-0.5 bg-gray-600"
                        style={{ 
                          left: '0%', 
                          right: '0%',
                          transform: 'translateY(-50%)'
                        }}
                      ></div>
                      
                      {/* Min whisker */}
                      <div 
                        className="absolute top-2 bottom-2 w-0.5 bg-gray-600"
                        style={{ left: '0%' }}
                      ></div>
                      
                      {/* Q1-Q3 box */}
                      <div 
                        className="absolute top-1 bottom-1 bg-blue-200 border border-blue-400"
                        style={{ 
                          left: '25%', 
                          right: '25%'
                        }}
                      ></div>
                      
                      {/* Median line */}
                      <div 
                        className="absolute top-1 bottom-1 w-0.5 bg-blue-800"
                        style={{ left: '50%', transform: 'translateX(-50%)' }}
                      ></div>
                      
                      {/* Max whisker */}
                      <div 
                        className="absolute top-2 bottom-2 w-0.5 bg-gray-600"
                        style={{ right: '0%' }}
                      ></div>
                    </div>
                    
                    {/* Labels */}
                    <div className="flex justify-between text-xs text-gray-600 mt-2">
                      <span>Min<br/>{columnStats.min?.toFixed(2)}</span>
                      <span>Q1<br/>{columnStats.q25?.toFixed(2)}</span>
                      <span>Median<br/>{columnStats.median?.toFixed(2)}</span>
                      <span>Q3<br/>{columnStats.q75?.toFixed(2)}</span>
                      <span>Max<br/>{columnStats.max?.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Statistics Summary */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="font-medium text-gray-700">Central Tendency</div>
                  <div className="mt-1 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Mean:</span>
                      <span className="font-medium">{columnStats.mean?.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Median:</span>
                      <span className="font-medium">{columnStats.median?.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Mode:</span>
                      <span className="font-medium">{columnStats.mode}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <div className="font-medium text-gray-700">Spread</div>
                  <div className="mt-1 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Std Dev:</span>
                      <span className="font-medium">{columnStats.std?.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Range:</span>
                      <span className="font-medium">{((columnStats.max || 0) - (columnStats.min || 0)).toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">IQR:</span>
                      <span className="font-medium">{((columnStats.q75 || 0) - (columnStats.q25 || 0)).toFixed(3)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Distribution Insights */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Distribution Insights</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-blue-50 p-3 rounded">
            <div className="font-medium text-blue-800">Skewness</div>
            <div className="text-blue-600 mt-1">
              {columnStats && columnStats.mean && columnStats.median ? (
                Math.abs(columnStats.mean - columnStats.median) < (columnStats.std || 0) * 0.1 ? 'Symmetric' :
                columnStats.mean > columnStats.median ? 'Right-skewed' : 'Left-skewed'
              ) : 'Unknown'}
            </div>
          </div>
          
          <div className="bg-green-50 p-3 rounded">
            <div className="font-medium text-green-800">Data Quality</div>
            <div className="text-green-600 mt-1">
              {columnStats ? (
                columnStats.missingPercentage < 5 ? 'High' :
                columnStats.missingPercentage < 15 ? 'Good' : 'Poor'
              ) : 'Unknown'}
            </div>
          </div>
          
          <div className="bg-purple-50 p-3 rounded">
            <div className="font-medium text-purple-800">Uniqueness</div>
            <div className="text-purple-600 mt-1">
              {columnStats ? (
                (columnStats.unique || 0) / columnStats.count > 0.95 ? 'Very High' :
                (columnStats.unique || 0) / columnStats.count > 0.7 ? 'High' :
                (columnStats.unique || 0) / columnStats.count > 0.3 ? 'Medium' : 'Low'
              ) : 'Unknown'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};