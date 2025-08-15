/**
 * File: components/DataPreview/DistributionCharts/index.tsx
 * 
 * Overview:
 * Data distribution charts component for numeric columns
 * 
 * Purpose:
 * Display histograms and box plots for numeric column distributions
 * 
 * Dependencies:
 * - react
 * - recharts
 * - lodash
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useMemo } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BoxPlot as RechartsBoxPlot
} from 'recharts'
import { groupBy } from 'lodash'
import type { DistributionChartsProps } from '../../../types'

interface HistogramBin {
  range: string
  count: number
  min: number
  max: number
}

const DistributionCharts: React.FC<DistributionChartsProps> = ({
  data,
  numericColumns,
  selectedColumn,
  onColumnSelect
}) => {
  const histogramData = useMemo(() => {
    if (!selectedColumn) return []
    
    const column = numericColumns.find(col => col.id === selectedColumn)
    if (!column) return []
    
    const values = data
      .map(row => row[selectedColumn])
      .filter(value => value !== null && value !== undefined && !isNaN(Number(value)))
      .map(Number)
      .sort((a, b) => a - b)
    
    if (values.length === 0) return []
    
    const min = Math.min(...values)
    const max = Math.max(...values)
    const binCount = Math.min(20, Math.ceil(Math.sqrt(values.length)))
    const binWidth = (max - min) / binCount
    
    const bins: HistogramBin[] = []
    
    for (let i = 0; i < binCount; i++) {
      const binMin = min + i * binWidth
      const binMax = min + (i + 1) * binWidth
      const count = values.filter(value => value >= binMin && (i === binCount - 1 ? value <= binMax : value < binMax)).length
      
      bins.push({
        range: `${binMin.toFixed(1)}-${binMax.toFixed(1)}`,
        count,
        min: binMin,
        max: binMax
      })
    }
    
    return bins
  }, [data, selectedColumn, numericColumns])
  
  const boxPlotData = useMemo(() => {
    return numericColumns.map(column => {
      const values = data
        .map(row => row[column.id])
        .filter(value => value !== null && value !== undefined && !isNaN(Number(value)))
        .map(Number)
        .sort((a, b) => a - b)
      
      if (values.length === 0) {
        return {
          column: column.name,
          columnId: column.id,
          q1: 0,
          median: 0,
          q3: 0,
          min: 0,
          max: 0,
          outliers: []
        }
      }
      
      const q1Index = Math.floor(values.length * 0.25)
      const medianIndex = Math.floor(values.length * 0.5)
      const q3Index = Math.floor(values.length * 0.75)
      
      const q1 = values[q1Index]
      const median = values[medianIndex]
      const q3 = values[q3Index]
      const iqr = q3 - q1
      
      const lowerFence = q1 - 1.5 * iqr
      const upperFence = q3 + 1.5 * iqr
      
      const outliers = values.filter(value => value < lowerFence || value > upperFence)
      const filteredValues = values.filter(value => value >= lowerFence && value <= upperFence)
      
      return {
        column: column.name,
        columnId: column.id,
        q1,
        median,
        q3,
        min: filteredValues.length > 0 ? Math.min(...filteredValues) : q1,
        max: filteredValues.length > 0 ? Math.max(...filteredValues) : q3,
        outliers
      }
    })
  }, [data, numericColumns])
  
  const summaryStats = useMemo(() => {
    if (!selectedColumn) return null
    
    const values = data
      .map(row => row[selectedColumn])
      .filter(value => value !== null && value !== undefined && !isNaN(Number(value)))
      .map(Number)
    
    if (values.length === 0) return null
    
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length
    const sortedValues = [...values].sort((a, b) => a - b)
    const median = sortedValues[Math.floor(sortedValues.length / 2)]
    const std = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length)
    
    return {
      count: values.length,
      mean: mean.toFixed(2),
      median: median.toFixed(2),
      std: std.toFixed(2),
      min: Math.min(...values).toFixed(2),
      max: Math.max(...values).toFixed(2)
    }
  }, [data, selectedColumn])
  
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as HistogramBin
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">Range: {data.range}</p>
          <p className="text-sm text-gray-600">Count: {data.count}</p>
        </div>
      )
    }
    return null
  }
  
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {numericColumns.map(column => (
          <button
            key={column.id}
            onClick={() => onColumnSelect(column.id)}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedColumn === column.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {column.name}
          </button>
        ))}
      </div>
      
      {selectedColumn && summaryStats && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-600">Count</div>
            <div className="font-semibold">{summaryStats.count}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-600">Mean</div>
            <div className="font-semibold">{summaryStats.mean}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-600">Median</div>
            <div className="font-semibold">{summaryStats.median}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-600">Std Dev</div>
            <div className="font-semibold">{summaryStats.std}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-600">Min</div>
            <div className="font-semibold">{summaryStats.min}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs text-gray-600">Max</div>
            <div className="font-semibold">{summaryStats.max}</div>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-4">Distribution Histogram</h4>
          {selectedColumn && histogramData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={histogramData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="range" 
                  angle={-45}
                  textAnchor="end"
                  height={60}
                  fontSize={10}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-gray-500">
              {selectedColumn ? 'No data available' : 'Select a column to view distribution'}
            </div>
          )}
        </div>
        
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-4">Box Plot Comparison</h4>
          <div className="space-y-3">
            {boxPlotData.map((boxData) => (
              <div key={boxData.columnId} className="flex items-center space-x-3">
                <div className="w-20 text-sm font-medium text-gray-700 truncate">
                  {boxData.column}
                </div>
                <div className="flex-1 relative h-6">
                  <div className="absolute inset-0 bg-gray-100 rounded"></div>
                  <div
                    className="absolute bg-blue-200 h-full rounded"
                    style={{
                      left: `${((boxData.q1 - boxData.min) / (boxData.max - boxData.min)) * 100}%`,
                      width: `${((boxData.q3 - boxData.q1) / (boxData.max - boxData.min)) * 100}%`
                    }}
                  ></div>
                  <div
                    className="absolute bg-blue-600 h-full w-0.5"
                    style={{
                      left: `${((boxData.median - boxData.min) / (boxData.max - boxData.min)) * 100}%`
                    }}
                  ></div>
                  {boxData.outliers.length > 0 && (
                    <div className="absolute -top-1 text-xs text-red-500">
                      •
                    </div>
                  )}
                </div>
                <div className="text-xs text-gray-500 w-16">
                  {boxData.min.toFixed(1)} - {boxData.max.toFixed(1)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DistributionCharts