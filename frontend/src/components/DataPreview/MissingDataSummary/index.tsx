/**
 * File: components/DataPreview/MissingDataSummary/index.tsx
 * 
 * Overview:
 * Missing data heatmap visualization component
 * 
 * Purpose:
 * Visualize missing data patterns across columns and rows as an interactive heatmap
 * 
 * Dependencies:
 * - react
 * - recharts
 * - utils/statistics
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useMemo } from 'react'
import { ResponsiveContainer, Cell, Tooltip, Rectangle } from 'recharts'
import { generateMissingDataMatrix } from '../../../utils/statistics'
import type { MissingDataSummaryProps } from '../../../types'

interface HeatmapData {
  row: number
  column: string
  columnIndex: number
  isMissing: boolean
  x: number
  y: number
}

const MissingDataSummary: React.FC<MissingDataSummaryProps> = ({
  data,
  columns,
  width = 500,
  height = 300
}) => {
  const heatmapData = useMemo(() => {
    const matrix = generateMissingDataMatrix(data, columns)
    const maxRows = Math.min(data.length, 100)
    const sampledData = data.slice(0, maxRows)
    
    const result: HeatmapData[] = []
    
    sampledData.forEach((row, rowIndex) => {
      columns.forEach((column, columnIndex) => {
        const isMissing = row[column.id] === null || 
                         row[column.id] === undefined || 
                         row[column.id] === ''
        
        result.push({
          row: rowIndex,
          column: column.name,
          columnIndex,
          isMissing,
          x: columnIndex,
          y: rowIndex
        })
      })
    })
    
    return result
  }, [data, columns])
  
  const missingDataStats = useMemo(() => {
    const totalCells = data.length * columns.length
    const missingCells = heatmapData.filter(cell => cell.isMissing).length
    const missingPercentage = (missingCells / totalCells) * 100
    
    const columnMissing = columns.map(column => {
      const columnData = data.map(row => row[column.id])
      const missing = columnData.filter(value => 
        value === null || value === undefined || value === ''
      ).length
      return {
        column: column.name,
        missing,
        percentage: (missing / data.length) * 100
      }
    })
    
    return {
      totalCells,
      missingCells,
      missingPercentage,
      columnMissing
    }
  }, [data, columns, heatmapData])
  
  const cellWidth = Math.max(2, width / columns.length)
  const cellHeight = Math.max(2, height / Math.min(data.length, 100))
  
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as HeatmapData
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{data.column}</p>
          <p className="text-sm text-gray-600">Row: {data.row + 1}</p>
          <p className={`text-sm font-medium ${
            data.isMissing ? 'text-red-600' : 'text-green-600'
          }`}>
            {data.isMissing ? 'Missing' : 'Present'}
          </p>
        </div>
      )
    }
    return null
  }
  
  const CustomHeatmapCell = (props: any) => {
    const { payload } = props
    const fill = payload.isMissing ? '#ef4444' : '#22c55e'
    const opacity = payload.isMissing ? 0.8 : 0.3
    
    return (
      <Rectangle
        x={payload.x * cellWidth}
        y={payload.y * cellHeight}
        width={cellWidth}
        height={cellHeight}
        fill={fill}
        opacity={opacity}
        stroke="#ffffff"
        strokeWidth={0.5}
      />
    )
  }
  
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="font-medium text-gray-900">Total Missing</div>
          <div className="text-2xl font-bold text-red-600">
            {missingDataStats.missingPercentage.toFixed(1)}%
          </div>
          <div className="text-gray-600">
            {missingDataStats.missingCells.toLocaleString()} of {missingDataStats.totalCells.toLocaleString()} cells
          </div>
        </div>
        
        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="font-medium text-gray-900">Worst Column</div>
          {missingDataStats.columnMissing.length > 0 && (
            <>
              <div className="text-lg font-bold text-orange-600">
                {Math.max(...missingDataStats.columnMissing.map(c => c.percentage)).toFixed(1)}%
              </div>
              <div className="text-gray-600 truncate">
                {missingDataStats.columnMissing.reduce((prev, current) => 
                  prev.percentage > current.percentage ? prev : current
                ).column}
              </div>
            </>
          )}
        </div>
      </div>
      
      <div className="border border-gray-200 rounded-lg p-4 bg-white">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-gray-900">Missing Data Pattern</h4>
          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span>Missing</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-green-500 opacity-30 rounded"></div>
              <span>Present</span>
            </div>
          </div>
        </div>
        
        <div className="relative">
          <ResponsiveContainer width="100%" height={height}>
            <svg viewBox={`0 0 ${width} ${height}`}>
              {heatmapData.map((cell, index) => (
                <CustomHeatmapCell key={index} payload={cell} />
              ))}
            </svg>
          </ResponsiveContainer>
          
          <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 mt-2">
            {columns.map((column, index) => (
              <div
                key={column.id}
                className="transform -rotate-45 origin-bottom-left"
                style={{ 
                  left: `${(index * cellWidth + cellWidth / 2)}px`,
                  position: 'absolute',
                  bottom: '-20px'
                }}
              >
                {column.name}
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="border border-gray-200 rounded-lg p-4 bg-white">
        <h4 className="font-medium text-gray-900 mb-3">Missing Data by Column</h4>
        <div className="space-y-2">
          {missingDataStats.columnMissing
            .sort((a, b) => b.percentage - a.percentage)
            .map((col) => (
              <div key={col.column} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 truncate flex-1">{col.column}</span>
                <div className="flex items-center space-x-2 ml-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${col.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {col.percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}

export default MissingDataSummary