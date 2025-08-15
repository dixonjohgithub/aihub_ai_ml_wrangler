import React, { useState, useMemo, useCallback } from 'react';
import { DataTable } from './DataTable';
import { ColumnStatistics } from './ColumnStatistics';
import { MissingDataSummary } from './MissingDataSummary';
import { DistributionCharts } from './DistributionCharts';
import { ColumnSelection } from './ColumnSelection';
import { SearchFilter } from './SearchFilter';
import { DataRow, ColumnInfo, SortState, ColumnStatistics as ColumnStatsType } from '../../types';
import { calculateColumnStatistics } from '../../utils/dataUtils';
import clsx from 'clsx';

interface FilterRule {
  id: string;
  column: string;
  operator: string;
  value: string;
  enabled: boolean;
}

interface DataPreviewProps {
  data: DataRow[];
  columns: ColumnInfo[];
  className?: string;
}

export const DataPreview: React.FC<DataPreviewProps> = ({
  data,
  columns,
  className,
}) => {
  const [selectedColumns, setSelectedColumns] = useState<string[]>(
    columns.slice(0, Math.min(5, columns.length)).map(col => col.name)
  );
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<FilterRule[]>([]);
  const [sortState, setSortState] = useState<SortState | undefined>();
  const [activeTab, setActiveTab] = useState<'table' | 'statistics' | 'missing' | 'distribution'>('table');
  const [selectedStatsColumn, setSelectedStatsColumn] = useState<string>();
  const [showColumnSelection, setShowColumnSelection] = useState(false);

  // Apply filters and search
  const filteredData = useMemo(() => {
    let result = [...data];

    // Apply global search
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      result = result.filter(row => 
        selectedColumns.some(colName => {
          const value = row[colName];
          if (value === null || value === undefined) return false;
          return String(value).toLowerCase().includes(searchLower);
        })
      );
    }

    // Apply column filters
    filters.forEach(filter => {
      if (!filter.enabled || !filter.value.trim()) return;

      result = result.filter(row => {
        const cellValue = row[filter.column];
        const filterValue = filter.value.trim();

        switch (filter.operator) {
          case 'contains':
            return String(cellValue).toLowerCase().includes(filterValue.toLowerCase());
          case 'equals':
            return String(cellValue) === filterValue;
          case 'startsWith':
            return String(cellValue).toLowerCase().startsWith(filterValue.toLowerCase());
          case 'endsWith':
            return String(cellValue).toLowerCase().endsWith(filterValue.toLowerCase());
          case 'greaterThan':
            return Number(cellValue) > Number(filterValue);
          case 'lessThan':
            return Number(cellValue) < Number(filterValue);
          case 'greaterThanOrEqual':
            return Number(cellValue) >= Number(filterValue);
          case 'lessThanOrEqual':
            return Number(cellValue) <= Number(filterValue);
          case 'isEmpty':
            return cellValue === null || cellValue === undefined || cellValue === '';
          case 'isNotEmpty':
            return cellValue !== null && cellValue !== undefined && cellValue !== '';
          default:
            return true;
        }
      });
    });

    return result;
  }, [data, selectedColumns, searchTerm, filters]);

  // Apply sorting
  const sortedData = useMemo(() => {
    if (!sortState) return filteredData;

    const sorted = [...filteredData].sort((a, b) => {
      const aVal = a[sortState.column];
      const bVal = b[sortState.column];

      // Handle null/undefined values
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      // Compare values
      if (aVal < bVal) return sortState.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortState.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [filteredData, sortState]);

  // Calculate statistics for selected columns
  const statistics = useMemo(() => {
    return selectedColumns.map(columnName => 
      calculateColumnStatistics(data, columnName)
    );
  }, [data, selectedColumns]);

  const handleSort = useCallback((column: string, direction: 'asc' | 'desc') => {
    setSortState({ column, direction });
  }, []);

  const handleColumnSelectionChange = useCallback((newSelection: string[]) => {
    setSelectedColumns(newSelection);
    // Reset sort if the sorted column is no longer selected
    if (sortState && !newSelection.includes(sortState.column)) {
      setSortState(undefined);
    }
  }, [sortState]);

  const handleSearch = useCallback((term: string) => {
    setSearchTerm(term);
  }, []);

  const handleFilter = useCallback((newFilters: FilterRule[]) => {
    setFilters(newFilters);
  }, []);

  const tabs = [
    { id: 'table', label: 'Data Table', icon: '📊' },
    { id: 'statistics', label: 'Statistics', icon: '📈' },
    { id: 'missing', label: 'Missing Data', icon: '🔍' },
    { id: 'distribution', label: 'Distribution', icon: '📉' },
  ] as const;

  return (
    <div className={clsx('h-full flex flex-col bg-gray-50', className)}>
      {/* Header */}
      <div className="flex-shrink-0 bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Data Preview</h2>
            <p className="text-sm text-gray-600 mt-1">
              {sortedData.length.toLocaleString()} of {data.length.toLocaleString()} rows • {selectedColumns.length} of {columns.length} columns
            </p>
          </div>
          
          <button
            onClick={() => setShowColumnSelection(!showColumnSelection)}
            className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {showColumnSelection ? 'Hide' : 'Show'} Column Selection
          </button>
        </div>

        {/* Search and Filter */}
        <SearchFilter
          columns={columns}
          selectedColumns={selectedColumns}
          onSearch={handleSearch}
          onFilter={handleFilter}
          globalSearchTerm={searchTerm}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Column Selection Sidebar */}
        {showColumnSelection && (
          <div className="w-80 flex-shrink-0 border-r border-gray-200">
            <ColumnSelection
              columns={columns}
              selectedColumns={selectedColumns}
              onSelectionChange={handleColumnSelectionChange}
            />
          </div>
        )}

        {/* Main View */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tabs */}
          <div className="flex-shrink-0 border-b border-gray-200 bg-white">
            <nav className="flex space-x-8 px-4" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={clsx(
                    'py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex items-center space-x-2',
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  )}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'table' && (
              <div className="h-full p-4">
                <DataTable
                  data={sortedData}
                  columns={columns}
                  selectedColumns={selectedColumns}
                  sortState={sortState}
                  onSort={handleSort}
                  height={window.innerHeight - 300}
                />
              </div>
            )}

            {activeTab === 'statistics' && (
              <div className="h-full flex">
                <div className="flex-1 p-4 overflow-auto">
                  <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                    {statistics.map((stat) => (
                      <div
                        key={stat.column}
                        className={clsx(
                          'bg-white rounded-lg border border-gray-200 p-4 cursor-pointer transition-all',
                          selectedStatsColumn === stat.column ? 'border-blue-500 shadow-md' : 'hover:shadow-sm'
                        )}
                        onClick={() => setSelectedStatsColumn(stat.column)}
                      >
                        <h4 className="font-medium text-gray-900 mb-2">{stat.column}</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Type:</span>
                            <span className="capitalize">{stat.type}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Count:</span>
                            <span>{stat.count.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Missing:</span>
                            <span>{stat.missingPercentage.toFixed(1)}%</span>
                          </div>
                          {stat.type === 'number' && (
                            <>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Mean:</span>
                                <span>{stat.mean?.toFixed(2)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Std:</span>
                                <span>{stat.std?.toFixed(2)}</span>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="w-80 border-l border-gray-200">
                  <ColumnStatistics
                    statistics={statistics}
                    selectedColumn={selectedStatsColumn}
                    onColumnSelect={setSelectedStatsColumn}
                  />
                </div>
              </div>
            )}

            {activeTab === 'missing' && (
              <div className="h-full p-4 overflow-auto">
                <MissingDataSummary
                  data={data}
                  columns={columns}
                  selectedColumns={selectedColumns}
                  sampleSize={200}
                />
              </div>
            )}

            {activeTab === 'distribution' && (
              <div className="h-full p-4 overflow-auto">
                <DistributionCharts
                  data={data}
                  columns={columns}
                  statistics={statistics}
                  selectedColumn={selectedStatsColumn}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};