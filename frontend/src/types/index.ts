/**
 * File: types/index.ts
 * 
 * Overview:
 * TypeScript type definitions for data preview components
 * 
 * Purpose:
 * Centralized type definitions for data structures and component props
 * 
 * Dependencies:
 * - None (base TypeScript types)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

export interface DataRow {
  [key: string]: any
}

export interface Column {
  id: string
  name: string
  type: 'string' | 'number' | 'boolean' | 'date'
  dataType?: string
  nullable: boolean
}

export interface ColumnStatistics {
  columnId: string
  columnName: string
  dataType: string
  count: number
  nullCount: number
  nullPercentage: number
  uniqueCount: number
  mean?: number
  median?: number
  mode?: any
  min?: number
  max?: number
  standardDeviation?: number
  variance?: number
  quartiles?: {
    q1: number
    q2: number
    q3: number
  }
}

export interface MissingDataPattern {
  row: number
  column: string
  isMissing: boolean
}

export interface SortConfig {
  columnId: string
  direction: 'asc' | 'desc'
}

export interface FilterConfig {
  searchTerm: string
  columnFilters: Record<string, any>
}

export interface DataPreviewProps {
  data?: DataRow[]
  columns?: Column[]
  loading?: boolean
  error?: string
}

export interface DataTableProps {
  data: DataRow[]
  columns: Column[]
  sortConfig?: SortConfig
  onSort: (columnId: string) => void
  height?: number
  width?: number
}

export interface ColumnStatisticsProps {
  statistics: ColumnStatistics[]
  selectedColumns: string[]
  onColumnSelect: (columnIds: string[]) => void
}

export interface MissingDataSummaryProps {
  data: DataRow[]
  columns: Column[]
  width?: number
  height?: number
}

export interface DistributionChartsProps {
  data: DataRow[]
  numericColumns: Column[]
  selectedColumn?: string
  onColumnSelect: (columnId: string) => void
}

export interface ColumnSelectionProps {
  columns: Column[]
  selectedColumns: string[]
  onSelectionChange: (selectedColumnIds: string[]) => void
}

export interface SearchFilterProps {
  filterConfig: FilterConfig
  onFilterChange: (config: FilterConfig) => void
  columns: Column[]
}