import React, { useState, useEffect, useMemo } from 'react';
import { ColumnInfo, DataType } from '../../types';
import clsx from 'clsx';

interface FilterRule {
  id: string;
  column: string;
  operator: string;
  value: string;
  enabled: boolean;
}

interface SearchFilterProps {
  columns: ColumnInfo[];
  selectedColumns: string[];
  onSearch: (searchTerm: string) => void;
  onFilter: (filters: FilterRule[]) => void;
  globalSearchTerm?: string;
}

const OPERATORS: Record<DataType, Array<{ value: string; label: string }>> = {
  string: [
    { value: 'contains', label: 'Contains' },
    { value: 'equals', label: 'Equals' },
    { value: 'startsWith', label: 'Starts with' },
    { value: 'endsWith', label: 'Ends with' },
    { value: 'isEmpty', label: 'Is empty' },
    { value: 'isNotEmpty', label: 'Is not empty' },
  ],
  number: [
    { value: 'equals', label: 'Equals' },
    { value: 'greaterThan', label: 'Greater than' },
    { value: 'lessThan', label: 'Less than' },
    { value: 'greaterThanOrEqual', label: 'Greater than or equal' },
    { value: 'lessThanOrEqual', label: 'Less than or equal' },
    { value: 'between', label: 'Between' },
    { value: 'isEmpty', label: 'Is empty' },
    { value: 'isNotEmpty', label: 'Is not empty' },
  ],
  boolean: [
    { value: 'equals', label: 'Equals' },
    { value: 'isEmpty', label: 'Is empty' },
    { value: 'isNotEmpty', label: 'Is not empty' },
  ],
  date: [
    { value: 'equals', label: 'Equals' },
    { value: 'after', label: 'After' },
    { value: 'before', label: 'Before' },
    { value: 'between', label: 'Between' },
    { value: 'isEmpty', label: 'Is empty' },
    { value: 'isNotEmpty', label: 'Is not empty' },
  ],
  unknown: [
    { value: 'isEmpty', label: 'Is empty' },
    { value: 'isNotEmpty', label: 'Is not empty' },
  ],
};

export const SearchFilter: React.FC<SearchFilterProps> = ({
  columns,
  selectedColumns,
  onSearch,
  onFilter,
  globalSearchTerm = '',
}) => {
  const [searchTerm, setSearchTerm] = useState(globalSearchTerm);
  const [filters, setFilters] = useState<FilterRule[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const availableColumns = useMemo(() => 
    columns.filter(col => selectedColumns.includes(col.name)),
    [columns, selectedColumns]
  );

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(searchTerm);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm, onSearch]);

  // Update filters when they change
  useEffect(() => {
    onFilter(filters.filter(f => f.enabled));
  }, [filters, onFilter]);

  const addFilter = () => {
    if (availableColumns.length === 0) return;
    
    const newFilter: FilterRule = {
      id: `filter_${Date.now()}`,
      column: availableColumns[0].name,
      operator: 'contains',
      value: '',
      enabled: true,
    };
    
    setFilters([...filters, newFilter]);
  };

  const updateFilter = (id: string, updates: Partial<FilterRule>) => {
    setFilters(filters.map(filter => 
      filter.id === id ? { ...filter, ...updates } : filter
    ));
  };

  const removeFilter = (id: string) => {
    setFilters(filters.filter(filter => filter.id !== id));
  };

  const clearAllFilters = () => {
    setFilters([]);
    setSearchTerm('');
  };

  const getOperatorsForColumn = (columnName: string) => {
    const column = columns.find(col => col.name === columnName);
    return column ? OPERATORS[column.type] : OPERATORS.unknown;
  };

  const needsValue = (operator: string) => {
    return !['isEmpty', 'isNotEmpty'].includes(operator);
  };

  const getInputType = (column: ColumnInfo, operator: string) => {
    if (!needsValue(operator)) return 'text';
    
    switch (column.type) {
      case 'number':
        return 'number';
      case 'date':
        return 'date';
      case 'boolean':
        return 'select';
      default:
        return 'text';
    }
  };

  const renderFilterValue = (filter: FilterRule) => {
    const column = columns.find(col => col.name === filter.column);
    if (!column || !needsValue(filter.operator)) return null;

    const inputType = getInputType(column, filter.operator);

    if (inputType === 'select' && column.type === 'boolean') {
      return (
        <select
          value={filter.value}
          onChange={(e) => updateFilter(filter.id, { value: e.target.value })}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select value</option>
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      );
    }

    return (
      <input
        type={inputType}
        value={filter.value}
        onChange={(e) => updateFilter(filter.id, { value: e.target.value })}
        placeholder={`Enter ${column.type} value`}
        className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
      />
    );
  };

  const activeFiltersCount = filters.filter(f => f.enabled && f.value.trim() !== '').length;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="space-y-4">
        {/* Global Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Global Search
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search across all columns..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Advanced Filters Toggle */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            <svg 
              className={clsx('h-4 w-4 transition-transform', showAdvanced ? 'rotate-90' : '')}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span>Advanced Filters</span>
            {activeFiltersCount > 0 && (
              <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full text-xs font-medium">
                {activeFiltersCount}
              </span>
            )}
          </button>

          {(searchTerm || filters.length > 0) && (
            <button
              onClick={clearAllFilters}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Clear All
            </button>
          )}
        </div>

        {/* Advanced Filters */}
        {showAdvanced && (
          <div className="space-y-3 border-t border-gray-200 pt-4">
            {filters.map((filter) => {
              const column = columns.find(col => col.name === filter.column);
              const operators = getOperatorsForColumn(filter.column);
              
              return (
                <div key={filter.id} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                  {/* Enable/Disable Toggle */}
                  <input
                    type="checkbox"
                    checked={filter.enabled}
                    onChange={(e) => updateFilter(filter.id, { enabled: e.target.checked })}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />

                  {/* Column Selection */}
                  <select
                    value={filter.column}
                    onChange={(e) => updateFilter(filter.id, { column: e.target.value })}
                    className="flex-shrink-0 w-32 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {availableColumns.map(col => (
                      <option key={col.name} value={col.name}>
                        {col.name}
                      </option>
                    ))}
                  </select>

                  {/* Operator Selection */}
                  <select
                    value={filter.operator}
                    onChange={(e) => updateFilter(filter.id, { operator: e.target.value })}
                    className="flex-shrink-0 w-40 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {operators.map(op => (
                      <option key={op.value} value={op.value}>
                        {op.label}
                      </option>
                    ))}
                  </select>

                  {/* Value Input */}
                  <div className="flex-1">
                    {renderFilterValue(filter)}
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => removeFilter(filter.id)}
                    className="flex-shrink-0 p-1 text-gray-400 hover:text-red-600"
                  >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              );
            })}

            {/* Add Filter Button */}
            {availableColumns.length > 0 && (
              <button
                onClick={addFilter}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-blue-600 hover:text-blue-800 border border-blue-200 rounded-md hover:bg-blue-50"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Add Filter</span>
              </button>
            )}

            {availableColumns.length === 0 && (
              <div className="text-center py-4 text-gray-500 text-sm">
                Select columns to add filters
              </div>
            )}
          </div>
        )}

        {/* Active Filters Summary */}
        {activeFiltersCount > 0 && !showAdvanced && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <div className="text-sm text-blue-800">
              <strong>{activeFiltersCount}</strong> filter{activeFiltersCount !== 1 ? 's' : ''} active
            </div>
            <div className="mt-1 space-y-1">
              {filters
                .filter(f => f.enabled && f.value.trim() !== '')
                .slice(0, 3)
                .map(filter => (
                  <div key={filter.id} className="text-xs text-blue-600">
                    {filter.column} {filter.operator} {needsValue(filter.operator) ? filter.value : ''}
                  </div>
                ))}
              {activeFiltersCount > 3 && (
                <div className="text-xs text-blue-600">
                  +{activeFiltersCount - 3} more filters
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};