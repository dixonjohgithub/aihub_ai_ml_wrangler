export type DataType = 'number' | 'string' | 'boolean' | 'date' | 'unknown';

export interface ColumnInfo {
  name: string;
  type: DataType;
  nullable: boolean;
}

export interface ColumnStatistics {
  column: string;
  type: DataType;
  count: number;
  missing: number;
  missingPercentage: number;
  unique?: number;
  mean?: number;
  median?: number;
  mode?: string | number;
  min?: number;
  max?: number;
  std?: number;
  q25?: number;
  q75?: number;
}

export interface DataRow {
  [key: string]: any;
}

export interface DataPreviewProps {
  data: DataRow[];
  columns: ColumnInfo[];
  onColumnSelect?: (columns: string[]) => void;
  onFilter?: (filterText: string, column?: string) => void;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
}

export interface SortState {
  column: string;
  direction: 'asc' | 'desc';
}