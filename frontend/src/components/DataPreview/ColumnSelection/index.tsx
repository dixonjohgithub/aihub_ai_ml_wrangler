/**
 * File: components/DataPreview/ColumnSelection/index.tsx
 * 
 * Overview:
 * Column selection interface with checkboxes for multi-column selection
 * 
 * Purpose:
 * Allow users to select/deselect columns for display and analysis
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
import type { ColumnSelectionProps } from '../../../types'

const ColumnSelection: React.FC<ColumnSelectionProps> = ({
  columns,
  selectedColumns,
  onSelectionChange
}) => {
  const handleSelectAll = () => {
    if (selectedColumns.length === columns.length) {
      onSelectionChange([])
    } else {
      onSelectionChange(columns.map(col => col.id))
    }
  }
  
  const handleColumnToggle = (columnId: string) => {
    if (selectedColumns.includes(columnId)) {
      onSelectionChange(selectedColumns.filter(id => id !== columnId))
    } else {
      onSelectionChange([...selectedColumns, columnId])
    }
  }
  
  const isAllSelected = selectedColumns.length === columns.length
  const isIndeterminate = selectedColumns.length > 0 && selectedColumns.length < columns.length
  
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'number':
        return '🔢'
      case 'string':
        return '📝'
      case 'boolean':
        return '✅'
      case 'date':
        return '📅'
      default:
        return '📄'
    }
  }
  
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'number':
        return 'text-blue-600 bg-blue-50'
      case 'string':
        return 'text-green-600 bg-green-50'
      case 'boolean':
        return 'text-purple-600 bg-purple-50'
      case 'date':
        return 'text-orange-600 bg-orange-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }
  
  const columnsByType = columns.reduce((acc, column) => {
    if (!acc[column.type]) {
      acc[column.type] = []
    }
    acc[column.type].push(column)
    return acc
  }, {} as Record<string, typeof columns>)
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-gray-900">Column Selection</h3>
        <span className="text-sm text-gray-500">
          {selectedColumns.length} of {columns.length} selected
        </span>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={isAllSelected}
              ref={(el) => {
                if (el) el.indeterminate = isIndeterminate
              }}
              onChange={handleSelectAll}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm font-medium text-gray-900">
              {isAllSelected ? 'Deselect All' : 'Select All'}
            </span>
          </label>
        </div>
        
        <div className="border-t border-gray-200 pt-4">
          {Object.entries(columnsByType).map(([type, typeColumns]) => (
            <div key={type} className="mb-4">
              <div className="flex items-center mb-2">
                <span className={clsx(
                  'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                  getTypeColor(type)
                )}>
                  {getTypeIcon(type)} {type}
                </span>
                <span className="ml-2 text-xs text-gray-500">
                  ({typeColumns.length} columns)
                </span>
              </div>
              
              <div className="space-y-2 ml-4">
                {typeColumns.map((column) => (
                  <label
                    key={column.id}
                    className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
                  >
                    <input
                      type="checkbox"
                      checked={selectedColumns.includes(column.id)}
                      onChange={() => handleColumnToggle(column.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="ml-2 flex-1">
                      <div className="text-sm font-medium text-gray-900">
                        {column.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {column.id} {column.nullable && '(nullable)'}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        {selectedColumns.length === 0 && (
          <div className="text-center py-4">
            <svg className="mx-auto h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-2 text-sm text-gray-500">No columns selected</p>
          </div>
        )}
        
        <div className="border-t border-gray-200 pt-4">
          <div className="flex space-x-2">
            <button
              onClick={() => onSelectionChange(columns.filter(col => col.type === 'number').map(col => col.id))}
              className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200"
            >
              Numbers Only
            </button>
            <button
              onClick={() => onSelectionChange(columns.filter(col => col.type === 'string').map(col => col.id))}
              className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200"
            >
              Text Only
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ColumnSelection