/**
 * File: utils/dataProcessing.ts
 * 
 * Overview:
 * Data processing utilities for filtering, sorting, and manipulation
 * 
 * Purpose:
 * Provide data transformation functions for table operations
 * 
 * Dependencies:
 * - lodash
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import { orderBy } from 'lodash'
import type { DataRow, Column, SortConfig, FilterConfig } from '../types'

export const sortData = (
  data: DataRow[],
  sortConfig: SortConfig
): DataRow[] => {
  const { columnId, direction } = sortConfig
  return orderBy(data, [columnId], [direction])
}

export const filterData = (
  data: DataRow[],
  filterConfig: FilterConfig,
  columns: Column[]
): DataRow[] => {
  let filteredData = [...data]
  
  if (filterConfig.searchTerm) {
    const searchTerm = filterConfig.searchTerm.toLowerCase()
    filteredData = filteredData.filter(row =>
      columns.some(column => {
        const value = row[column.id]
        if (value === null || value === undefined) return false
        return String(value).toLowerCase().includes(searchTerm)
      })
    )
  }
  
  Object.entries(filterConfig.columnFilters).forEach(([columnId, filterValue]) => {
    if (filterValue !== null && filterValue !== undefined && filterValue !== '') {
      filteredData = filteredData.filter(row => {
        const value = row[columnId]
        if (typeof filterValue === 'string') {
          return String(value).toLowerCase().includes(filterValue.toLowerCase())
        }
        return value === filterValue
      })
    }
  })
  
  return filteredData
}

export const generateSampleData = (
  numRows: number = 1000,
  columns: Column[]
): DataRow[] => {
  return Array.from({ length: numRows }, (_, index) => {
    const row: DataRow = {}
    
    columns.forEach(column => {
      switch (column.type) {
        case 'number':
          row[column.id] = Math.random() < 0.1 ? null : Math.round(Math.random() * 1000)
          break
        case 'string':
          row[column.id] = Math.random() < 0.05 ? null : `Value ${index}-${column.id}`
          break
        case 'boolean':
          row[column.id] = Math.random() < 0.08 ? null : Math.random() > 0.5
          break
        case 'date':
          row[column.id] = Math.random() < 0.06 ? null : new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          break
        default:
          row[column.id] = `Sample ${index}`
      }
    })
    
    return row
  })
}

export const generateSampleColumns = (): Column[] => [
  { id: 'id', name: 'ID', type: 'number', nullable: false },
  { id: 'name', name: 'Name', type: 'string', nullable: true },
  { id: 'age', name: 'Age', type: 'number', nullable: true },
  { id: 'email', name: 'Email', type: 'string', nullable: true },
  { id: 'active', name: 'Active', type: 'boolean', nullable: true },
  { id: 'createdAt', name: 'Created At', type: 'date', nullable: true },
  { id: 'score', name: 'Score', type: 'number', nullable: true },
  { id: 'category', name: 'Category', type: 'string', nullable: true },
  { id: 'rating', name: 'Rating', type: 'number', nullable: true },
  { id: 'status', name: 'Status', type: 'string', nullable: true }
]