import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ColumnSelection } from '../ColumnSelection';
import { ColumnInfo } from '../../../types';

const mockColumns: ColumnInfo[] = [
  { name: 'id', type: 'number', nullable: false },
  { name: 'name', type: 'string', nullable: false },
  { name: 'age', type: 'number', nullable: true },
  { name: 'isActive', type: 'boolean', nullable: false },
];

describe('ColumnSelection', () => {
  const defaultProps = {
    columns: mockColumns,
    selectedColumns: ['id', 'name'],
    onSelectionChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders column list', () => {
    render(<ColumnSelection {...defaultProps} />);
    
    expect(screen.getByText('id')).toBeInTheDocument();
    expect(screen.getByText('name')).toBeInTheDocument();
    expect(screen.getByText('age')).toBeInTheDocument();
    expect(screen.getByText('isActive')).toBeInTheDocument();
  });

  it('shows selection count', () => {
    render(<ColumnSelection {...defaultProps} />);
    
    expect(screen.getByText('2 of 4 columns selected')).toBeInTheDocument();
  });

  it('handles column toggle', () => {
    render(<ColumnSelection {...defaultProps} />);
    
    const ageCheckbox = screen.getByLabelText(/age/);
    fireEvent.click(ageCheckbox);
    
    expect(defaultProps.onSelectionChange).toHaveBeenCalledWith(['id', 'name', 'age']);
  });

  it('handles deselection', () => {
    render(<ColumnSelection {...defaultProps} />);
    
    const nameCheckbox = screen.getByLabelText(/name/);
    fireEvent.click(nameCheckbox);
    
    expect(defaultProps.onSelectionChange).toHaveBeenCalledWith(['id']);
  });

  it('handles search filtering', () => {
    render(<ColumnSelection {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search columns...');
    fireEvent.change(searchInput, { target: { value: 'age' } });
    
    expect(screen.getByText('age')).toBeInTheDocument();
    expect(screen.queryByText('id')).not.toBeInTheDocument();
    expect(screen.queryByText('name')).not.toBeInTheDocument();
  });

  it('handles type filtering', () => {
    render(<ColumnSelection {...defaultProps} />);
    
    const typeFilter = screen.getByDisplayValue('All Types');
    fireEvent.change(typeFilter, { target: { value: 'number' } });
    
    expect(screen.getByText('id')).toBeInTheDocument();
    expect(screen.getByText('age')).toBeInTheDocument();
    expect(screen.queryByText('name')).not.toBeInTheDocument();
    expect(screen.queryByText('isActive')).not.toBeInTheDocument();
  });

  it('handles select all functionality', () => {
    render(<ColumnSelection {...defaultProps} />);
    
    const selectAllButton = screen.getByText('Select All');
    fireEvent.click(selectAllButton);
    
    expect(defaultProps.onSelectionChange).toHaveBeenCalledWith(['id', 'name', 'age', 'isActive']);
  });
});