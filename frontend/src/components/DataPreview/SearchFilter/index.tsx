/**
 * File: components/DataPreview/SearchFilter/index.tsx
 * 
 * Overview:
 * Search and filter interface for real-time data filtering
 * 
 * Purpose:
 * Provide search functionality and column-specific filters for data exploration
 * 
 * Dependencies:
 * - react
 * - clsx
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useCallback } from 'react'
import clsx from 'clsx'
import type { SearchFilterProps } from '../../../types'

const SearchFilter: React.FC<SearchFilterProps> = ({
  filterConfig,
  onFilterChange,
  columns
}) => {
  const [isExpanded, setIsExpanded] = useState(false)
  
  const handleSearchChange = useCallback((searchTerm: string) => {
    onFilterChange({
      ...filterConfig,
      searchTerm
    })
  }, [filterConfig, onFilterChange])
  
  const handleColumnFilterChange = useCallback((columnId: string, value: any) => {
    onFilterChange({
      ...filterConfig,
      columnFilters: {
        ...filterConfig.columnFilters,
        [columnId]: value
      }
    })
  }, [filterConfig, onFilterChange])
  
  const clearColumnFilter = useCallback((columnId: string) => {
    const newFilters = { ...filterConfig.columnFilters }
    delete newFilters[columnId]
    
    onFilterChange({
      ...filterConfig,
      columnFilters: newFilters
    })
  }, [filterConfig, onFilterChange])
  
  const clearAllFilters = useCallback(() => {
    onFilterChange({
      searchTerm: '',
      columnFilters: {}
    })
  }, [onFilterChange])
  
  const activeFiltersCount = Object.keys(filterConfig.columnFilters).length + 
    (filterConfig.searchTerm ? 1 : 0)
  
  const getFilterInput = (column: any) => {
    const currentValue = filterConfig.columnFilters[column.id] || ''
    
    switch (column.type) {
      case 'number':
        return (
          <input
            type="number"
            placeholder={`Filter ${column.name}...`}
            value={currentValue}
            onChange={(e) => handleColumnFilterChange(column.id, e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          />
        )
      
      case 'boolean':
        return (
          <select
            value={currentValue === true ? 'true' : currentValue === false ? 'false' : ''}
            onChange={(e) => {
              const value = e.target.value
              handleColumnFilterChange(
                column.id, 
                value === 'true' ? true : value === 'false' ? false : ''
              )
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All values</option>
            <option value="true">True</option>
            <option value="false">False</option>
          </select>
        )
      
      case 'date':
        return (
          <input
            type="date"
            value={currentValue}
            onChange={(e) => handleColumnFilterChange(column.id, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          />
        )
      
      default:
        return (
          <input
            type="text"
            placeholder={`Filter ${column.name}...`}
            value={currentValue}
            onChange={(e) => handleColumnFilterChange(column.id, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          />
        )
    }
  }
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-gray-900">Search & Filter</h3>
        {activeFiltersCount > 0 && (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {activeFiltersCount} active
          </span>
        )}
      </div>
      
      <div className="space-y-4">
        {/* Global Search */}
        <div>
          <label htmlFor="global-search" className="block text-sm font-medium text-gray-700 mb-1">
            Global Search
          </label>
          <div className="relative">
            <input
              id="global-search"
              type="text"
              placeholder="Search across all columns..."
              value={filterConfig.searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            {filterConfig.searchTerm && (
              <button
                onClick={() => handleSearchChange('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg className="h-4 w-4 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>
        
        {/* Column Filters Toggle */}
        <div className="border-t border-gray-200 pt-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center justify-between w-full text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            <span>Column Filters</span>
            <svg
              className={clsx(
                'h-4 w-4 transition-transform',
                isExpanded ? 'transform rotate-180' : ''
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {isExpanded && (
            <div className="mt-3 space-y-3">
              {columns.map((column) => (
                <div key={column.id}>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-xs font-medium text-gray-600">
                      {column.name}
                    </label>
                    {filterConfig.columnFilters[column.id] !== undefined && 
                     filterConfig.columnFilters[column.id] !== '' && (
                      <button
                        onClick={() => clearColumnFilter(column.id)}
                        className="text-xs text-red-600 hover:text-red-800"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                  {getFilterInput(column)}
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Active Filters Summary */}
        {activeFiltersCount > 0 && (
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {activeFiltersCount} filter{activeFiltersCount !== 1 ? 's' : ''} applied
              </span>
              <button
                onClick={clearAllFilters}
                className="text-sm text-red-600 hover:text-red-800 font-medium"
              >
                Clear All
              </button>
            </div>
            
            <div className="mt-2 flex flex-wrap gap-1">
              {filterConfig.searchTerm && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800">
                  Search: "{filterConfig.searchTerm}"
                  <button
                    onClick={() => handleSearchChange('')}
                    className="ml-1 text-gray-500 hover:text-gray-700"
                  >
                    ×
                  </button>
                </span>
              )}
              
              {Object.entries(filterConfig.columnFilters).map(([columnId, value]) => {
                const column = columns.find(col => col.id === columnId)
                if (!column || value === '' || value === null || value === undefined) return null
                
                return (
                  <span
                    key={columnId}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                  >
                    {column.name}: {String(value)}
                    <button
                      onClick={() => clearColumnFilter(columnId)}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchFilter