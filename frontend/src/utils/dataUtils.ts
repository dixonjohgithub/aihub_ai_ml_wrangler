import { DataRow, ColumnInfo, ColumnStatistics, DataType } from '../types';

export function inferDataType(value: any): DataType {
  if (value === null || value === undefined || value === '') {
    return 'unknown';
  }
  
  if (typeof value === 'boolean') {
    return 'boolean';
  }
  
  if (typeof value === 'number' && !isNaN(value)) {
    return 'number';
  }
  
  if (typeof value === 'string') {
    // Check if it's a date
    const dateValue = new Date(value);
    if (!isNaN(dateValue.getTime()) && value.match(/^\d{4}-\d{2}-\d{2}|^\d{2}\/\d{2}\/\d{4}/)) {
      return 'date';
    }
    
    // Check if it's a number string
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && isFinite(numValue)) {
      return 'number';
    }
    
    return 'string';
  }
  
  return 'unknown';
}

export function calculateColumnStatistics(data: DataRow[], column: string): ColumnStatistics {
  const values = data.map(row => row[column]);
  const nonNullValues = values.filter(v => v !== null && v !== undefined && v !== '');
  const missing = values.length - nonNullValues.length;
  const missingPercentage = (missing / values.length) * 100;
  
  const type = nonNullValues.length > 0 ? inferDataType(nonNullValues[0]) : 'unknown';
  const unique = new Set(nonNullValues).size;
  
  const stats: ColumnStatistics = {
    column,
    type,
    count: values.length,
    missing,
    missingPercentage,
    unique,
  };
  
  if (type === 'number') {
    const numericValues = nonNullValues
      .map(v => typeof v === 'string' ? parseFloat(v) : v)
      .filter(v => !isNaN(v));
    
    if (numericValues.length > 0) {
      numericValues.sort((a, b) => a - b);
      
      stats.mean = numericValues.reduce((sum, val) => sum + val, 0) / numericValues.length;
      stats.median = getMedian(numericValues);
      stats.min = numericValues[0];
      stats.max = numericValues[numericValues.length - 1];
      stats.std = getStandardDeviation(numericValues, stats.mean);
      stats.q25 = getPercentile(numericValues, 25);
      stats.q75 = getPercentile(numericValues, 75);
    }
  }
  
  // Calculate mode for all types
  if (nonNullValues.length > 0) {
    stats.mode = getMode(nonNullValues);
  }
  
  return stats;
}

function getMedian(sortedNumbers: number[]): number {
  const mid = Math.floor(sortedNumbers.length / 2);
  return sortedNumbers.length % 2 !== 0
    ? sortedNumbers[mid]
    : (sortedNumbers[mid - 1] + sortedNumbers[mid]) / 2;
}

function getStandardDeviation(numbers: number[], mean: number): number {
  const squaredDifferences = numbers.map(num => Math.pow(num - mean, 2));
  const avgSquaredDiff = squaredDifferences.reduce((sum, diff) => sum + diff, 0) / numbers.length;
  return Math.sqrt(avgSquaredDiff);
}

function getPercentile(sortedNumbers: number[], percentile: number): number {
  const index = (percentile / 100) * (sortedNumbers.length - 1);
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  const weight = index - lower;
  
  if (lower === upper) {
    return sortedNumbers[lower];
  }
  
  return sortedNumbers[lower] * (1 - weight) + sortedNumbers[upper] * weight;
}

function getMode(values: any[]): any {
  const frequency: { [key: string]: number } = {};
  let maxFreq = 0;
  let mode: any = null;
  
  values.forEach(value => {
    const key = String(value);
    frequency[key] = (frequency[key] || 0) + 1;
    if (frequency[key] > maxFreq) {
      maxFreq = frequency[key];
      mode = value;
    }
  });
  
  return mode;
}

export function generateSampleData(rows: number = 1000): DataRow[] {
  const sampleData: DataRow[] = [];
  
  for (let i = 0; i < rows; i++) {
    sampleData.push({
      id: i + 1,
      name: `User ${i + 1}`,
      age: Math.floor(Math.random() * 60) + 18,
      email: `user${i + 1}@example.com`,
      salary: Math.floor(Math.random() * 100000) + 30000,
      department: ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance'][Math.floor(Math.random() * 5)],
      isActive: Math.random() > 0.2,
      joinDate: new Date(2020 + Math.floor(Math.random() * 4), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toISOString().split('T')[0],
      score: Math.random() > 0.1 ? Math.round(Math.random() * 100) : null, // 10% missing
      notes: Math.random() > 0.3 ? `Note for user ${i + 1}` : null, // 30% missing
    });
  }
  
  return sampleData;
}

export function getSampleColumns(): ColumnInfo[] {
  return [
    { name: 'id', type: 'number', nullable: false },
    { name: 'name', type: 'string', nullable: false },
    { name: 'age', type: 'number', nullable: false },
    { name: 'email', type: 'string', nullable: false },
    { name: 'salary', type: 'number', nullable: false },
    { name: 'department', type: 'string', nullable: false },
    { name: 'isActive', type: 'boolean', nullable: false },
    { name: 'joinDate', type: 'date', nullable: false },
    { name: 'score', type: 'number', nullable: true },
    { name: 'notes', type: 'string', nullable: true },
  ];
}