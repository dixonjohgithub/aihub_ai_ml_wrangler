import React, { useState, useMemo } from 'react';
import { ColumnInfo, DataType } from '../../types';
import clsx from 'clsx';

interface ColumnSelectionProps {
  columns: ColumnInfo[];
  selectedColumns: string[];
  onSelectionChange: (selectedColumns: string[]) => void;
}

const TYPE_COLORS: Record<DataType, string> = {
  number: 'bg-blue-100 text-blue-800',
  string: 'bg-green-100 text-green-800',
  boolean: 'bg-purple-100 text-purple-800',
  date: 'bg-orange-100 text-orange-800',
  unknown: 'bg-gray-100 text-gray-800',
};

const TYPE_ICONS: Record<DataType, string> = {
  number: '🔢',
  string: '📝',
  boolean: '✅',
  date: '📅',
  unknown: '❓',
};

export const ColumnSelection: React.FC<ColumnSelectionProps> = ({
  columns,
  selectedColumns,
  onSelectionChange,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<DataType | 'all'>('all');

  const filteredColumns = useMemo(() => {
    return columns.filter(column => {
      const matchesSearch = column.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = filterType === 'all' || column.type === filterType;
      return matchesSearch && matchesType;
    });
  }, [columns, searchTerm, filterType]);

  const columnsByType = useMemo(() => {
    const grouped: Record<DataType, ColumnInfo[]> = {
      number: [],
      string: [],
      boolean: [],
      date: [],
      unknown: [],
    };

    filteredColumns.forEach(column => {
      grouped[column.type].push(column);
    });

    return grouped;
  }, [filteredColumns]);

  const handleSelectAll = () => {
    const allColumnNames = filteredColumns.map(col => col.name);
    const areAllSelected = allColumnNames.every(name => selectedColumns.includes(name));
    
    if (areAllSelected) {
      // Deselect all filtered columns
      const remaining = selectedColumns.filter(name => !allColumnNames.includes(name));
      onSelectionChange(remaining);
    } else {
      // Select all filtered columns
      const newSelection = [...new Set([...selectedColumns, ...allColumnNames])];
      onSelectionChange(newSelection);
    }
  };

  const handleSelectType = (type: DataType) => {
    const typeColumns = columnsByType[type].map(col => col.name);
    const areAllTypeSelected = typeColumns.every(name => selectedColumns.includes(name));
    
    if (areAllTypeSelected) {
      // Deselect all columns of this type
      const remaining = selectedColumns.filter(name => !typeColumns.includes(name));
      onSelectionChange(remaining);
    } else {
      // Select all columns of this type
      const newSelection = [...new Set([...selectedColumns, ...typeColumns])];
      onSelectionChange(newSelection);
    }
  };

  const handleColumnToggle = (columnName: string) => {
    const isSelected = selectedColumns.includes(columnName);
    
    if (isSelected) {
      onSelectionChange(selectedColumns.filter(name => name !== columnName));
    } else {
      onSelectionChange([...selectedColumns, columnName]);
    }
  };

  const getSelectionStats = () => {
    const total = columns.length;
    const selected = selectedColumns.length;
    const filtered = filteredColumns.length;
    
    return { total, selected, filtered };
  };

  const stats = getSelectionStats();

  return (
    <div className="bg-white border border-gray-200 rounded-lg h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Column Selection</h3>
        <div className="text-sm text-gray-600">
          {stats.selected} of {stats.total} columns selected
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="p-4 border-b border-gray-200 space-y-3">
        {/* Search */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search columns..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Type Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Filter by Type</label>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as DataType | 'all')}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Types</option>
            <option value="number">Number</option>
            <option value="string">String</option>
            <option value="boolean">Boolean</option>
            <option value="date">Date</option>
            <option value="unknown">Unknown</option>
          </select>
        </div>

        {/* Bulk Actions */}
        <div className="flex space-x-2">
          <button
            onClick={handleSelectAll}
            className="flex-1 px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {filteredColumns.every(col => selectedColumns.includes(col.name)) ? 'Deselect All' : 'Select All'}
          </button>
        </div>
      </div>

      {/* Column List */}
      <div className="flex-1 overflow-y-auto">
        {Object.entries(columnsByType).map(([type, typeColumns]) => {
          if (typeColumns.length === 0) return null;
          
          const dataType = type as DataType;
          const allTypeSelected = typeColumns.every(col => selectedColumns.includes(col.name));
          const someTypeSelected = typeColumns.some(col => selectedColumns.includes(col.name));
          
          return (
            <div key={type} className="border-b border-gray-100 last:border-b-0">
              {/* Type Header */}
              <div className="sticky top-0 bg-gray-50 px-4 py-2 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{TYPE_ICONS[dataType]}</span>
                    <span className="text-sm font-medium text-gray-700 capitalize">{type}</span>
                    <span className={clsx('px-2 py-0.5 rounded-full text-xs font-medium', TYPE_COLORS[dataType])}>
                      {typeColumns.length}
                    </span>
                  </div>
                  <button
                    onClick={() => handleSelectType(dataType)}
                    className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {allTypeSelected ? 'Deselect All' : 'Select All'}
                  </button>
                </div>
              </div>

              {/* Type Columns */}
              <div className="space-y-1 p-2">
                {typeColumns.map((column) => {
                  const isSelected = selectedColumns.includes(column.name);
                  
                  return (
                    <label
                      key={column.name}
                      className={clsx(
                        'flex items-center p-2 rounded cursor-pointer transition-colors',
                        isSelected ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'
                      )}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleColumnToggle(column.name)}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <div className="ml-3 flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className={clsx(
                            'text-sm font-medium truncate',
                            isSelected ? 'text-blue-900' : 'text-gray-900'
                          )}>
                            {column.name}
                          </span>
                          {column.nullable && (
                            <span className="ml-2 text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                              nullable
                            </span>
                          )}
                        </div>
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>
          );
        })}

        {filteredColumns.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-4">🔍</div>
            <div className="text-lg font-medium mb-2">No Columns Found</div>
            <div className="text-sm">
              {searchTerm ? `No columns match "${searchTerm}"` : 'No columns available'}
            </div>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
              >
                Clear search
              </button>
            )}
          </div>
        )}
      </div>

      {/* Footer Summary */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex justify-between items-center text-sm">
          <div className="text-gray-600">
            Showing {stats.filtered} of {stats.total} columns
          </div>
          <div className="font-medium text-gray-900">
            {stats.selected} selected
          </div>
        </div>
        
        {/* Selected Columns Preview */}
        {selectedColumns.length > 0 && (
          <div className="mt-2">
            <div className="text-xs text-gray-500 mb-1">Selected:</div>
            <div className="flex flex-wrap gap-1">
              {selectedColumns.slice(0, 3).map(columnName => (
                <span
                  key={columnName}
                  className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {columnName}
                </span>
              ))}
              {selectedColumns.length > 3 && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600">
                  +{selectedColumns.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};