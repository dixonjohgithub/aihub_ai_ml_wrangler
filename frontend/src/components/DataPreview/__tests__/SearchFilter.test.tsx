import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchFilter } from '../SearchFilter';
import { ColumnInfo } from '../../../types';

const mockColumns: ColumnInfo[] = [
  { name: 'id', type: 'number', nullable: false },
  { name: 'name', type: 'string', nullable: false },
  { name: 'age', type: 'number', nullable: true },
];

describe('SearchFilter', () => {
  const defaultProps = {
    columns: mockColumns,
    selectedColumns: ['id', 'name', 'age'],
    onSearch: jest.fn(),
    onFilter: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders search input', () => {
    render(<SearchFilter {...defaultProps} />);
    
    expect(screen.getByPlaceholderText('Search across all columns...')).toBeInTheDocument();
  });

  it('handles search input with debouncing', async () => {
    render(<SearchFilter {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search across all columns...');
    fireEvent.change(searchInput, { target: { value: 'test' } });
    
    expect(defaultProps.onSearch).not.toHaveBeenCalled();
    
    jest.advanceTimersByTime(300);
    
    await waitFor(() => {
      expect(defaultProps.onSearch).toHaveBeenCalledWith('test');
    });
  });

  it('shows advanced filters when toggled', () => {
    render(<SearchFilter {...defaultProps} />);
    
    const advancedButton = screen.getByText('Advanced Filters');
    fireEvent.click(advancedButton);
    
    expect(screen.getByText('Add Filter')).toBeInTheDocument();
  });

  it('allows adding filters', () => {
    render(<SearchFilter {...defaultProps} />);
    
    const advancedButton = screen.getByText('Advanced Filters');
    fireEvent.click(advancedButton);
    
    const addFilterButton = screen.getByText('Add Filter');
    fireEvent.click(addFilterButton);
    
    expect(screen.getByDisplayValue('id')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Contains')).toBeInTheDocument();
  });

  it('handles filter removal', () => {
    render(<SearchFilter {...defaultProps} />);
    
    const advancedButton = screen.getByText('Advanced Filters');
    fireEvent.click(advancedButton);
    
    const addFilterButton = screen.getByText('Add Filter');
    fireEvent.click(addFilterButton);
    
    const removeButton = screen.getByRole('button', { name: '' }); // X button
    fireEvent.click(removeButton);
    
    expect(screen.queryByDisplayValue('id')).not.toBeInTheDocument();
  });

  it('clears all filters and search', () => {
    render(<SearchFilter {...defaultProps} globalSearchTerm="test" />);
    
    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);
    
    expect(defaultProps.onSearch).toHaveBeenCalledWith('');
    expect(defaultProps.onFilter).toHaveBeenCalledWith([]);
  });

  it('updates filter column selection', () => {
    render(<SearchFilter {...defaultProps} />);
    
    const advancedButton = screen.getByText('Advanced Filters');
    fireEvent.click(advancedButton);
    
    const addFilterButton = screen.getByText('Add Filter');
    fireEvent.click(addFilterButton);
    
    const columnSelect = screen.getByDisplayValue('id');
    fireEvent.change(columnSelect, { target: { value: 'name' } });
    
    expect(screen.getByDisplayValue('name')).toBeInTheDocument();
  });

  it('shows appropriate operators for different column types', () => {
    render(<SearchFilter {...defaultProps} />);
    
    const advancedButton = screen.getByText('Advanced Filters');
    fireEvent.click(advancedButton);
    
    const addFilterButton = screen.getByText('Add Filter');
    fireEvent.click(addFilterButton);
    
    // Default is string column, should show string operators
    expect(screen.getByText('Contains')).toBeInTheDocument();
    
    // Change to number column
    const columnSelect = screen.getByDisplayValue('id');
    fireEvent.change(columnSelect, { target: { value: 'age' } });
    
    // Should now show number operators
    expect(screen.getByText('Greater than')).toBeInTheDocument();
  });
});