/**
 * File: utils/statistics.ts
 * 
 * Overview:
 * Statistical calculation utilities for data analysis
 * 
 * Purpose:
 * Provide statistical functions for column analysis and data preview
 * 
 * Dependencies:
 * - lodash
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import { sortBy, uniq, isNumber, isString, isBoolean, isDate } from 'lodash'
import type { DataRow, Column, ColumnStatistics } from '../types'

export const calculateColumnStatistics = (
  data: DataRow[],
  column: Column
): ColumnStatistics => {
  const values = data.map(row => row[column.id])
  const nonNullValues = values.filter(value => value !== null && value !== undefined && value !== '')
  
  const nullCount = values.length - nonNullValues.length
  const nullPercentage = (nullCount / values.length) * 100
  
  const baseStats: ColumnStatistics = {
    columnId: column.id,
    columnName: column.name,
    dataType: column.type,
    count: values.length,
    nullCount,
    nullPercentage,
    uniqueCount: uniq(nonNullValues).length
  }

  if (column.type === 'number' && nonNullValues.length > 0) {
    const numericValues = nonNullValues.filter(isNumber).sort((a, b) => a - b)
    
    if (numericValues.length > 0) {
      const sum = numericValues.reduce((acc, val) => acc + val, 0)
      const mean = sum / numericValues.length
      
      const median = calculateMedian(numericValues)
      const mode = calculateMode(numericValues)
      const min = Math.min(...numericValues)
      const max = Math.max(...numericValues)
      
      const variance = numericValues.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / numericValues.length
      const standardDeviation = Math.sqrt(variance)
      
      const quartiles = calculateQuartiles(numericValues)
      
      return {
        ...baseStats,
        mean,
        median,
        mode,
        min,
        max,
        standardDeviation,
        variance,
        quartiles
      }
    }
  } else {
    const mode = calculateMode(nonNullValues)
    return {
      ...baseStats,
      mode
    }
  }
  
  return baseStats
}

export const calculateMedian = (sortedValues: number[]): number => {
  const mid = Math.floor(sortedValues.length / 2)
  if (sortedValues.length % 2 === 0) {
    return (sortedValues[mid - 1] + sortedValues[mid]) / 2
  }
  return sortedValues[mid]
}

export const calculateMode = (values: any[]): any => {
  const frequency: Record<string, number> = {}
  
  values.forEach(value => {
    const key = String(value)
    frequency[key] = (frequency[key] || 0) + 1
  })
  
  let maxFreq = 0
  let mode: any = null
  
  Object.entries(frequency).forEach(([value, freq]) => {
    if (freq > maxFreq) {
      maxFreq = freq
      mode = values.find(v => String(v) === value)
    }
  })
  
  return mode
}

export const calculateQuartiles = (sortedValues: number[]) => {
  const q1Index = Math.floor(sortedValues.length * 0.25)
  const q2Index = Math.floor(sortedValues.length * 0.5)
  const q3Index = Math.floor(sortedValues.length * 0.75)
  
  return {
    q1: sortedValues[q1Index],
    q2: sortedValues[q2Index],
    q3: sortedValues[q3Index]
  }
}

export const detectColumnType = (values: any[]): Column['type'] => {
  const nonNullValues = values.filter(v => v !== null && v !== undefined && v !== '')
  
  if (nonNullValues.length === 0) return 'string'
  
  const numericCount = nonNullValues.filter(v => isNumber(v) || (!isNaN(Number(v)) && !isNaN(parseFloat(String(v))))).length
  const booleanCount = nonNullValues.filter(v => isBoolean(v) || v === 'true' || v === 'false').length
  const dateCount = nonNullValues.filter(v => isDate(v) || !isNaN(Date.parse(String(v)))).length
  
  const total = nonNullValues.length
  
  if (numericCount / total > 0.8) return 'number'
  if (booleanCount / total > 0.8) return 'boolean'
  if (dateCount / total > 0.8) return 'date'
  
  return 'string'
}

export const generateMissingDataMatrix = (data: DataRow[], columns: Column[]) => {
  return data.map((row, rowIndex) => 
    columns.map(column => ({
      row: rowIndex,
      column: column.id,
      isMissing: row[column.id] === null || row[column.id] === undefined || row[column.id] === ''
    }))
  ).flat()
}