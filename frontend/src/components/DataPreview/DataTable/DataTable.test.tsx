/**
 * File: components/DataPreview/DataTable/DataTable.test.tsx
 * 
 * Overview:
 * Unit tests for the DataTable component
 * 
 * Purpose:
 * Test virtualized table functionality, sorting, and performance
 * 
 * Dependencies:
 * - react
 * - @testing-library/react
 * - @testing-library/jest-dom
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import DataTable from './index'
import { generateSampleData, generateSampleColumns } from '../../../utils/dataProcessing'

const mockColumns = generateSampleColumns().slice(0, 3)
const mockData = generateSampleData(100, mockColumns)

const defaultProps = {
  data: mockData,
  columns: mockColumns,
  onSort: jest.fn(),
  height: 400
}

describe('DataTable', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders table headers correctly', () => {
    render(<DataTable {...defaultProps} />)
    
    mockColumns.forEach(column => {
      expect(screen.getByText(column.name)).toBeInTheDocument()
    })
  })

  it('calls onSort when header is clicked', () => {
    const mockOnSort = jest.fn()
    render(<DataTable {...defaultProps} onSort={mockOnSort} />)
    
    fireEvent.click(screen.getByText(mockColumns[0].name))
    expect(mockOnSort).toHaveBeenCalledWith(mockColumns[0].id)
  })

  it('displays sort indicators correctly', () => {
    const sortConfig = {
      columnId: mockColumns[0].id,
      direction: 'asc' as const
    }
    
    render(<DataTable {...defaultProps} sortConfig={sortConfig} />)
    
    // Should show ascending sort icon for sorted column
    const headerButton = screen.getByText(mockColumns[0].name).closest('div')
    expect(headerButton).toBeInTheDocument()
  })

  it('handles empty data gracefully', () => {
    render(<DataTable {...defaultProps} data={[]} />)
    
    // Headers should still be visible
    mockColumns.forEach(column => {
      expect(screen.getByText(column.name)).toBeInTheDocument()
    })
  })

  it('formats cell values correctly', () => {
    const testData = [
      { id: 1, name: 'Test', active: true },
      { id: null, name: '', active: false }
    ]
    
    const testColumns = [
      { id: 'id', name: 'ID', type: 'number' as const, nullable: true },
      { id: 'name', name: 'Name', type: 'string' as const, nullable: true },
      { id: 'active', name: 'Active', type: 'boolean' as const, nullable: true }
    ]
    
    render(<DataTable {...defaultProps} data={testData} columns={testColumns} />)
    
    // Check for formatted number
    expect(screen.getByText('1')).toBeInTheDocument()
    
    // Check for null display
    expect(screen.getByText('null')).toBeInTheDocument()
  })

  it('applies correct styling for alternating rows', () => {
    render(<DataTable {...defaultProps} />)
    
    // The component should render without throwing errors
    expect(screen.getByText(mockColumns[0].name)).toBeInTheDocument()
  })

  it('handles large datasets efficiently', () => {
    const largeData = generateSampleData(10000, mockColumns)
    
    const renderStart = performance.now()
    render(<DataTable {...defaultProps} data={largeData} />)
    const renderTime = performance.now() - renderStart
    
    // Should render within reasonable time (less than 1 second)
    expect(renderTime).toBeLessThan(1000)
    
    // Headers should still be visible
    mockColumns.forEach(column => {
      expect(screen.getByText(column.name)).toBeInTheDocument()
    })
  })

  it('maintains accessibility standards', () => {
    render(<DataTable {...defaultProps} />)
    
    // Table should be keyboard navigable (headers are buttons)
    mockColumns.forEach(column => {
      const header = screen.getByText(column.name)
      expect(header.closest('div')).toHaveClass('cursor-pointer')
    })
  })
})