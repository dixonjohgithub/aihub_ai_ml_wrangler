import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { DataTable } from '../DataTable';
import { ColumnInfo, DataRow } from '../../../types';

const mockColumns: ColumnInfo[] = [
  { name: 'id', type: 'number', nullable: false },
  { name: 'name', type: 'string', nullable: false },
  { name: 'age', type: 'number', nullable: true },
];

const mockData: DataRow[] = [
  { id: 1, name: 'John Doe', age: 30 },
  { id: 2, name: 'Jane Smith', age: 25 },
  { id: 3, name: 'Bob Johnson', age: null },
];

describe('DataTable', () => {
  const defaultProps = {
    data: mockData,
    columns: mockColumns,
    selectedColumns: ['id', 'name', 'age'],
  };

  it('renders table with data', () => {
    render(<DataTable {...defaultProps} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
  });

  it('displays column headers', () => {
    render(<DataTable {...defaultProps} />);
    
    expect(screen.getByText('id')).toBeInTheDocument();
    expect(screen.getByText('name')).toBeInTheDocument();
    expect(screen.getByText('age')).toBeInTheDocument();
  });

  it('handles sorting when onSort is provided', () => {
    const mockOnSort = jest.fn();
    render(<DataTable {...defaultProps} onSort={mockOnSort} />);
    
    const idHeader = screen.getByText('id');
    fireEvent.click(idHeader);
    
    expect(mockOnSort).toHaveBeenCalledWith('id', 'asc');
  });

  it('displays null values appropriately', () => {
    render(<DataTable {...defaultProps} />);
    
    expect(screen.getByText('null')).toBeInTheDocument();
  });

  it('shows row count in footer', () => {
    render(<DataTable {...defaultProps} />);
    
    expect(screen.getByText('3 rows × 3 columns')).toBeInTheDocument();
  });

  it('handles empty data', () => {
    render(<DataTable {...defaultProps} data={[]} />);
    
    expect(screen.getByText('0 rows × 3 columns')).toBeInTheDocument();
  });

  it('renders only selected columns', () => {
    render(<DataTable {...defaultProps} selectedColumns={['id', 'name']} />);
    
    expect(screen.getByText('id')).toBeInTheDocument();
    expect(screen.getByText('name')).toBeInTheDocument();
    expect(screen.queryByText('age')).not.toBeInTheDocument();
  });
});