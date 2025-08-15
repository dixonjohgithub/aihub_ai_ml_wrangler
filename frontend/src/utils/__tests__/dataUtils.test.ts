import { inferDataType, calculateColumnStatistics, generateSampleData } from '../dataUtils';
import { DataRow } from '../../types';

describe('dataUtils', () => {
  describe('inferDataType', () => {
    it('identifies number type', () => {
      expect(inferDataType(42)).toBe('number');
      expect(inferDataType(3.14)).toBe('number');
      expect(inferDataType('123')).toBe('number');
    });

    it('identifies string type', () => {
      expect(inferDataType('hello')).toBe('string');
      expect(inferDataType('abc123')).toBe('string');
    });

    it('identifies boolean type', () => {
      expect(inferDataType(true)).toBe('boolean');
      expect(inferDataType(false)).toBe('boolean');
    });

    it('identifies date type', () => {
      expect(inferDataType('2023-01-01')).toBe('date');
      expect(inferDataType('01/01/2023')).toBe('date');
    });

    it('identifies unknown type for null/undefined', () => {
      expect(inferDataType(null)).toBe('unknown');
      expect(inferDataType(undefined)).toBe('unknown');
      expect(inferDataType('')).toBe('unknown');
    });
  });

  describe('calculateColumnStatistics', () => {
    const testData: DataRow[] = [
      { id: 1, name: 'Alice', age: 25, score: 85.5 },
      { id: 2, name: 'Bob', age: 30, score: 92.0 },
      { id: 3, name: 'Charlie', age: 35, score: null },
      { id: 4, name: 'Diana', age: 28, score: 88.2 },
    ];

    it('calculates basic statistics', () => {
      const stats = calculateColumnStatistics(testData, 'age');
      
      expect(stats.column).toBe('age');
      expect(stats.type).toBe('number');
      expect(stats.count).toBe(4);
      expect(stats.missing).toBe(0);
      expect(stats.missingPercentage).toBe(0);
      expect(stats.unique).toBe(4);
    });

    it('calculates numeric statistics', () => {
      const stats = calculateColumnStatistics(testData, 'age');
      
      expect(stats.mean).toBeCloseTo(29.5);
      expect(stats.median).toBe(29);
      expect(stats.min).toBe(25);
      expect(stats.max).toBe(35);
      expect(stats.std).toBeGreaterThan(0);
    });

    it('handles missing data', () => {
      const stats = calculateColumnStatistics(testData, 'score');
      
      expect(stats.missing).toBe(1);
      expect(stats.missingPercentage).toBe(25);
    });

    it('calculates mode', () => {
      const dataWithMode: DataRow[] = [
        { value: 'A' },
        { value: 'B' },
        { value: 'A' },
        { value: 'C' },
        { value: 'A' },
      ];
      
      const stats = calculateColumnStatistics(dataWithMode, 'value');
      expect(stats.mode).toBe('A');
    });

    it('handles empty data', () => {
      const stats = calculateColumnStatistics([], 'age');
      
      expect(stats.count).toBe(0);
      expect(stats.missing).toBe(0);
      expect(stats.unique).toBe(0);
    });
  });

  describe('generateSampleData', () => {
    it('generates correct number of rows', () => {
      const data = generateSampleData(100);
      expect(data).toHaveLength(100);
    });

    it('generates data with expected properties', () => {
      const data = generateSampleData(10);
      
      data.forEach(row => {
        expect(row).toHaveProperty('id');
        expect(row).toHaveProperty('name');
        expect(row).toHaveProperty('age');
        expect(row).toHaveProperty('email');
        expect(row).toHaveProperty('salary');
        expect(row).toHaveProperty('department');
        expect(row).toHaveProperty('isActive');
        expect(row).toHaveProperty('joinDate');
      });
    });

    it('generates realistic data ranges', () => {
      const data = generateSampleData(100);
      
      data.forEach(row => {
        expect(row.age).toBeGreaterThanOrEqual(18);
        expect(row.age).toBeLessThanOrEqual(77);
        expect(row.salary).toBeGreaterThanOrEqual(30000);
        expect(row.salary).toBeLessThanOrEqual(129999);
        expect(typeof row.isActive).toBe('boolean');
      });
    });
  });
});