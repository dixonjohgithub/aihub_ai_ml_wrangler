import React, { useMemo, useState } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { DataRow, ColumnInfo, SortState } from '../../types';
import clsx from 'clsx';

interface DataTableProps {
  data: DataRow[];
  columns: ColumnInfo[];
  selectedColumns: string[];
  sortState?: SortState;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  height?: number;
}

export const DataTable: React.FC<DataTableProps> = ({
  data,
  columns,
  selectedColumns,
  sortState,
  onSort,
  height = 600,
}) => {
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);
  
  const visibleColumns = useMemo(() => 
    columns.filter(col => selectedColumns.includes(col.name)), 
    [columns, selectedColumns]
  );

  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
    overscan: 5,
  });

  const handleSort = (columnName: string) => {
    if (!onSort) return;
    
    const newDirection = 
      sortState?.column === columnName && sortState?.direction === 'asc' 
        ? 'desc' 
        : 'asc';
    
    onSort(columnName, newDirection);
  };

  const getSortIcon = (columnName: string) => {
    if (!sortState || sortState.column !== columnName) {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    
    return sortState.direction === 'asc' ? (
      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
      </svg>
    );
  };

  const formatCellValue = (value: any, columnType: string) => {
    if (value === null || value === undefined || value === '') {
      return <span className="text-gray-400 italic">null</span>;
    }
    
    if (columnType === 'boolean') {
      return (
        <span className={clsx(
          'px-2 py-1 rounded text-xs font-medium',
          value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        )}>
          {value ? 'true' : 'false'}
        </span>
      );
    }
    
    if (columnType === 'number') {
      return typeof value === 'number' ? value.toLocaleString() : value;
    }
    
    return String(value);
  };

  return (
    <div className="flex flex-col h-full bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-gray-50">
        <div className="flex" style={{ minWidth: `${visibleColumns.length * 150}px` }}>
          {visibleColumns.map((column) => (
            <div
              key={column.name}
              className="flex-1 min-w-[150px] px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200 last:border-r-0"
            >
              <button
                onClick={() => handleSort(column.name)}
                className="flex items-center space-x-2 hover:text-gray-700 focus:outline-none"
              >
                <span className="truncate">{column.name}</span>
                {getSortIcon(column.name)}
              </button>
              <div className="text-xs text-gray-400 mt-1 capitalize">
                {column.type}
                {column.nullable && <span className="ml-1">• nullable</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Virtualized Body */}
      <div
        ref={parentRef}
        className="flex-1 overflow-auto"
        style={{ height: height - 80 }}
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualItem) => {
            const row = data[virtualItem.index];
            const isHovered = hoveredRow === virtualItem.index;
            
            return (
              <div
                key={virtualItem.index}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: `${virtualItem.size}px`,
                  transform: `translateY(${virtualItem.start}px)`,
                }}
                className={clsx(
                  'flex border-b border-gray-100 transition-colors',
                  isHovered ? 'bg-blue-50' : 'bg-white hover:bg-gray-50',
                  virtualItem.index % 2 === 0 ? 'bg-white' : 'bg-gray-25'
                )}
                onMouseEnter={() => setHoveredRow(virtualItem.index)}
                onMouseLeave={() => setHoveredRow(null)}
              >
                {visibleColumns.map((column) => (
                  <div
                    key={column.name}
                    className="flex-1 min-w-[150px] px-4 py-2 text-sm text-gray-900 border-r border-gray-100 last:border-r-0 truncate"
                    style={{ minWidth: '150px' }}
                  >
                    {formatCellValue(row[column.name], column.type)}
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer with row count */}
      <div className="flex-shrink-0 px-4 py-2 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
        {data.length.toLocaleString()} rows × {visibleColumns.length} columns
      </div>
    </div>
  );
};