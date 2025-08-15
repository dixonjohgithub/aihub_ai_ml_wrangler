/**
 * File: components/DataPreview/ColumnStatistics/index.tsx
 * 
 * Overview:
 * Column statistics sidebar component displaying statistical information
 * 
 * Purpose:
 * Show statistical summaries for each column including mean, median, mode, missing data percentage
 * 
 * Dependencies:
 * - react
 * - clsx
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'
import clsx from 'clsx'
import type { ColumnStatisticsProps } from '../../../types'

const ColumnStatistics: React.FC<ColumnStatisticsProps> = ({
  statistics,
  selectedColumns,
  onColumnSelect
}) => {
  const formatNumber = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'N/A'
    if (Number.isInteger(value)) return value.toString()
    return value.toFixed(2)
  }
  
  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`
  }
  
  const getDataTypeIcon = (dataType: string) => {
    switch (dataType) {
      case 'number':
        return (
          <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
          </svg>
        )
      case 'string':
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        )
      case 'boolean':
        return (
          <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      case 'date':
        return (
          <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        )
      default:
        return (
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        )
    }
  }
  
  const getMissingDataColor = (percentage: number) => {
    if (percentage === 0) return 'text-green-600 bg-green-50'
    if (percentage < 5) return 'text-yellow-600 bg-yellow-50'
    if (percentage < 20) return 'text-orange-600 bg-orange-50'
    return 'text-red-600 bg-red-50'
  }
  
  return (
    <div className="space-y-4 max-h-96 overflow-y-auto">
      {statistics.map((stat) => (
        <div
          key={stat.columnId}
          className={clsx(
            'border rounded-lg p-4 transition-all duration-200',
            selectedColumns.includes(stat.columnId)
              ? 'border-blue-200 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          )}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              {getDataTypeIcon(stat.dataType)}
              <h4 className="font-semibold text-gray-900">{stat.columnName}</h4>
            </div>
            <span className="text-xs text-gray-500 uppercase font-medium">
              {stat.dataType}
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-600">Count:</span>
              <span className="ml-2 font-medium">{stat.count.toLocaleString()}</span>
            </div>
            
            <div>
              <span className="text-gray-600">Unique:</span>
              <span className="ml-2 font-medium">{stat.uniqueCount.toLocaleString()}</span>
            </div>
            
            <div className="col-span-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Missing:</span>
                <span className={clsx(
                  'px-2 py-1 rounded-full text-xs font-medium',
                  getMissingDataColor(stat.nullPercentage)
                )}>
                  {stat.nullCount.toLocaleString()} ({formatPercentage(stat.nullPercentage)})
                </span>
              </div>
            </div>
            
            {stat.dataType === 'number' && (
              <>
                <div>
                  <span className="text-gray-600">Mean:</span>
                  <span className="ml-2 font-medium">{formatNumber(stat.mean)}</span>
                </div>
                
                <div>
                  <span className="text-gray-600">Median:</span>
                  <span className="ml-2 font-medium">{formatNumber(stat.median)}</span>
                </div>
                
                <div>
                  <span className="text-gray-600">Min:</span>
                  <span className="ml-2 font-medium">{formatNumber(stat.min)}</span>
                </div>
                
                <div>
                  <span className="text-gray-600">Max:</span>
                  <span className="ml-2 font-medium">{formatNumber(stat.max)}</span>
                </div>
                
                <div>
                  <span className="text-gray-600">Std Dev:</span>
                  <span className="ml-2 font-medium">{formatNumber(stat.standardDeviation)}</span>
                </div>
                
                {stat.quartiles && (
                  <div>
                    <span className="text-gray-600">Q1/Q3:</span>
                    <span className="ml-2 font-medium">
                      {formatNumber(stat.quartiles.q1)}/{formatNumber(stat.quartiles.q3)}
                    </span>
                  </div>
                )}
              </>
            )}
            
            {stat.mode !== null && stat.mode !== undefined && (
              <div className="col-span-2">
                <span className="text-gray-600">Mode:</span>
                <span className="ml-2 font-medium">
                  {typeof stat.mode === 'string' ? `"${stat.mode}"` : String(stat.mode)}
                </span>
              </div>
            )}
          </div>
        </div>
      ))}
      
      {statistics.length === 0 && (
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No columns selected</h3>
          <p className="mt-1 text-sm text-gray-500">Select columns to view statistics</p>
        </div>
      )}
    </div>
  )
}

export default ColumnStatistics