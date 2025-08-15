/**
 * File: components/DataPreview/index.tsx
 * 
 * Overview:
 * Main data preview component that orchestrates all sub-components
 * 
 * Purpose:
 * Provides complete data preview functionality with virtualized table, statistics, and visualizations
 * 
 * Dependencies:
 * - react
 * - DataTable, ColumnStatistics, MissingDataSummary, DistributionCharts, ColumnSelection, SearchFilter
 * - utils/dataProcessing, utils/statistics
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useMemo, useCallback } from 'react'
import DataTable from './DataTable'
import ColumnStatistics from './ColumnStatistics'
import MissingDataSummary from './MissingDataSummary'
import DistributionCharts from './DistributionCharts'
import ColumnSelection from './ColumnSelection'
import SearchFilter from './SearchFilter'
import { generateSampleData, generateSampleColumns, sortData, filterData } from '../../utils/dataProcessing'
import { calculateColumnStatistics } from '../../utils/statistics'
import type { DataRow, Column, SortConfig, FilterConfig } from '../../types'

const DataPreview: React.FC = () => {
  const [columns] = useState<Column[]>(generateSampleColumns())
  const [rawData] = useState<DataRow[]>(() => generateSampleData(100000, generateSampleColumns()))
  
  const [selectedColumns, setSelectedColumns] = useState<string[]>(() => 
    columns.slice(0, 5).map(col => col.id)
  )
  
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    columnId: 'id',
    direction: 'asc'
  })
  
  const [filterConfig, setFilterConfig] = useState<FilterConfig>({
    searchTerm: '',
    columnFilters: {}
  })
  
  const [selectedDistributionColumn, setSelectedDistributionColumn] = useState<string>('age')
  
  const visibleColumns = useMemo(() => 
    columns.filter(col => selectedColumns.includes(col.id)),
    [columns, selectedColumns]
  )
  
  const filteredData = useMemo(() => 
    filterData(rawData, filterConfig, columns),
    [rawData, filterConfig, columns]
  )
  
  const sortedData = useMemo(() => 
    sortData(filteredData, sortConfig),
    [filteredData, sortConfig]
  )
  
  const columnStatistics = useMemo(() => 
    visibleColumns.map(column => calculateColumnStatistics(filteredData, column)),
    [visibleColumns, filteredData]
  )
  
  const numericColumns = useMemo(() => 
    visibleColumns.filter(col => col.type === 'number'),
    [visibleColumns]
  )
  
  const handleSort = useCallback((columnId: string) => {
    setSortConfig(prev => ({
      columnId,
      direction: prev.columnId === columnId && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }, [])
  
  const handleColumnSelection = useCallback((newSelectedColumns: string[]) => {
    setSelectedColumns(newSelectedColumns)
  }, [])
  
  const handleFilterChange = useCallback((newFilterConfig: FilterConfig) => {
    setFilterConfig(newFilterConfig)
  }, [])
  
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Data Preview</h2>
        <p className="text-gray-600 mb-6">
          Displaying {filteredData.length.toLocaleString()} of {rawData.length.toLocaleString()} rows
        </p>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <div className="space-y-6">
              <ColumnSelection
                columns={columns}
                selectedColumns={selectedColumns}
                onSelectionChange={handleColumnSelection}
              />
              
              <SearchFilter
                filterConfig={filterConfig}
                onFilterChange={handleFilterChange}
                columns={visibleColumns}
              />
            </div>
          </div>
          
          <div className="lg:col-span-3">
            <DataTable
              data={sortedData}
              columns={visibleColumns}
              sortConfig={sortConfig}
              onSort={handleSort}
              height={600}
            />
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Column Statistics</h3>
          <ColumnStatistics
            statistics={columnStatistics}
            selectedColumns={selectedColumns}
            onColumnSelect={handleColumnSelection}
          />
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Missing Data Summary</h3>
          <MissingDataSummary
            data={filteredData.slice(0, 1000)}
            columns={visibleColumns}
            width={500}
            height={300}
          />
        </div>
      </div>
      
      {numericColumns.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Distribution Charts</h3>
          <DistributionCharts
            data={filteredData.slice(0, 10000)}
            numericColumns={numericColumns}
            selectedColumn={selectedDistributionColumn}
            onColumnSelect={setSelectedDistributionColumn}
          />
        </div>
      )}
    </div>
  )
}

export default DataPreview