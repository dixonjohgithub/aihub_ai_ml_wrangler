/**
 * File: components/DataPreview/DataTable/index.tsx
 * 
 * Overview:
 * Virtualized data table component for high-performance display of large datasets
 * 
 * Purpose:
 * Efficiently render 1M+ rows using virtualization with sorting capabilities
 * 
 * Dependencies:
 * - react
 * - @tanstack/react-virtual
 * - clsx
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useMemo, useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import clsx from 'clsx'
import type { DataTableProps } from '../../../types'

const DataTable: React.FC<DataTableProps> = ({
  data,
  columns,
  sortConfig,
  onSort,
  height = 600,
  width
}) => {
  const parentRef = useRef<HTMLDivElement>(null)
  
  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 10,
  })
  
  const columnVirtualizer = useVirtualizer({
    horizontal: true,
    count: columns.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 150,
    overscan: 5,
  })
  
  const virtualRows = rowVirtualizer.getVirtualItems()
  const virtualColumns = columnVirtualizer.getVirtualItems()
  
  const handleHeaderClick = (columnId: string) => {
    onSort(columnId)
  }
  
  const getSortIcon = (columnId: string) => {
    if (!sortConfig || sortConfig.columnId !== columnId) {
      return (
        <svg className="w-4 h-4 ml-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      )
    }
    
    if (sortConfig.direction === 'asc') {
      return (
        <svg className="w-4 h-4 ml-1 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        </svg>
      )
    }
    
    return (
      <svg className="w-4 h-4 ml-1 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    )
  }
  
  const formatCellValue = (value: any, columnType: string) => {
    if (value === null || value === undefined || value === '') {
      return <span className="text-gray-400 italic">null</span>
    }
    
    if (columnType === 'number' && typeof value === 'number') {
      return value.toLocaleString()
    }
    
    if (columnType === 'boolean') {
      return (
        <span className={clsx(
          'px-2 py-1 rounded-full text-xs font-medium',
          value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        )}>
          {String(value)}
        </span>
      )
    }
    
    return String(value)
  }
  
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      <div 
        ref={parentRef}
        className="overflow-auto"
        style={{ height, width: width || '100%' }}
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            width: `${columnVirtualizer.getTotalSize()}px`,
            position: 'relative',
          }}
        >
          {/* Header */}
          <div
            className="sticky top-0 z-10 bg-gray-50 border-b border-gray-200"
            style={{ height: '40px' }}
          >
            {virtualColumns.map((virtualColumn) => {
              const column = columns[virtualColumn.index]
              return (
                <div
                  key={column.id}
                  className="absolute top-0 flex items-center px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  style={{
                    left: `${virtualColumn.start}px`,
                    width: `${virtualColumn.size}px`,
                    height: '40px',
                  }}
                  onClick={() => handleHeaderClick(column.id)}
                >
                  <span className="truncate">{column.name}</span>
                  {getSortIcon(column.id)}
                </div>
              )
            })}
          </div>
          
          {/* Rows */}
          {virtualRows.map((virtualRow) => {
            const row = data[virtualRow.index]
            return (
              <div
                key={virtualRow.index}
                className={clsx(
                  'absolute border-b border-gray-100',
                  virtualRow.index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                )}
                style={{
                  top: `${virtualRow.start + 40}px`,
                  left: 0,
                  height: `${virtualRow.size}px`,
                  width: `${columnVirtualizer.getTotalSize()}px`,
                }}
              >
                {virtualColumns.map((virtualColumn) => {
                  const column = columns[virtualColumn.index]
                  const cellValue = row[column.id]
                  
                  return (
                    <div
                      key={`${virtualRow.index}-${column.id}`}
                      className="absolute flex items-center px-3 py-2 text-sm text-gray-900"
                      style={{
                        left: `${virtualColumn.start}px`,
                        width: `${virtualColumn.size}px`,
                        height: `${virtualRow.size}px`,
                      }}
                    >
                      <div className="truncate w-full">
                        {formatCellValue(cellValue, column.type)}
                      </div>
                    </div>
                  )
                })}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default DataTable