/**
 * File: fileValidation.ts
 * 
 * Overview:
 * Client-side file validation utilities for upload functionality
 * 
 * Purpose:
 * Provides validation functions for file size, type, and Data Wrangler patterns
 * 
 * Dependencies:
 * - upload.types.ts (for type definitions)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import { ValidationResult, UploadConfig } from '../types/upload.types';

export const DEFAULT_CONFIG: UploadConfig = {
  maxFileSize: 100 * 1024 * 1024, // 100MB
  allowedTypes: ['text/csv', 'application/json', 'text/plain'],
  allowedExtensions: ['.csv', '.json'],
  virusScanEnabled: true
};

export function validateFile(file: File, config: UploadConfig = DEFAULT_CONFIG): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  // File size validation
  if (file.size > config.maxFileSize) {
    errors.push(`File size ${formatFileSize(file.size)} exceeds maximum allowed size of ${formatFileSize(config.maxFileSize)}`);
  }

  // File type validation
  const fileExtension = getFileExtension(file.name);
  if (!config.allowedExtensions.includes(fileExtension)) {
    errors.push(`File type "${fileExtension}" is not supported. Allowed types: ${config.allowedExtensions.join(', ')}`);
  }

  // MIME type validation
  if (!config.allowedTypes.includes(file.type) && file.type !== '') {
    warnings.push(`MIME type "${file.type}" may not be supported. Expected: ${config.allowedTypes.join(', ')}`);
  }

  // Data Wrangler pattern validation
  const dwValidation = validateDataWranglerPattern(file.name);
  if (!dwValidation.isValid) {
    warnings.push(...dwValidation.warnings);
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

export function validateDataWranglerPattern(fileName: string): { isValid: boolean; warnings: string[] } {
  const warnings: string[] = [];
  const lowerName = fileName.toLowerCase();

  // Check for Data Wrangler export patterns
  const isTransformationFile = lowerName.includes('transformation_file') && lowerName.endsWith('.csv');
  const isMappedData = lowerName.includes('mapped_data') && lowerName.endsWith('.csv');
  const isMetadata = lowerName.includes('metadata') && lowerName.endsWith('.json');

  if (!isTransformationFile && !isMappedData && !isMetadata) {
    warnings.push('File name does not match Data Wrangler export patterns (transformation_file.csv, mapped_data.csv, metadata.json)');
  }

  return {
    isValid: true, // Always valid, just warnings for pattern matching
    warnings
  };
}

export function getFileExtension(fileName: string): string {
  const lastDot = fileName.lastIndexOf('.');
  return lastDot === -1 ? '' : fileName.substring(lastDot).toLowerCase();
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function isCSVFile(file: File): boolean {
  return file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv');
}

export function isJSONFile(file: File): boolean {
  return file.type === 'application/json' || file.name.toLowerCase().endsWith('.json');
}

export async function validateFileContent(file: File): Promise<ValidationResult> {
  const errors: string[] = [];
  const warnings: string[] = [];

  try {
    if (isCSVFile(file)) {
      await validateCSVContent(file, errors, warnings);
    } else if (isJSONFile(file)) {
      await validateJSONContent(file, errors, warnings);
    }
  } catch (error) {
    errors.push(`Error reading file content: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

async function validateCSVContent(file: File, errors: string[], warnings: string[]): Promise<void> {
  const text = await file.text();
  const lines = text.split('\n').filter(line => line.trim());

  if (lines.length === 0) {
    errors.push('CSV file is empty');
    return;
  }

  if (lines.length === 1) {
    warnings.push('CSV file contains only header row, no data');
  }

  // Check for valid CSV structure
  const header = lines[0];
  if (!header.includes(',')) {
    warnings.push('CSV file may not be properly formatted (no commas detected in header)');
  }
}

async function validateJSONContent(file: File, errors: string[], warnings: string[]): Promise<void> {
  const text = await file.text();

  if (!text.trim()) {
    errors.push('JSON file is empty');
    return;
  }

  try {
    const parsed = JSON.parse(text);
    
    // Check if it's a Data Wrangler metadata file
    if (file.name.toLowerCase().includes('metadata')) {
      validateMetadataStructure(parsed, warnings);
    }
  } catch (parseError) {
    errors.push('Invalid JSON format');
  }
}

function validateMetadataStructure(data: any, warnings: string[]): void {
  const expectedFields = ['statistics', 'transformations', 'columns', 'dataTypes'];
  const missingFields = expectedFields.filter(field => !(field in data));
  
  if (missingFields.length > 0) {
    warnings.push(`Metadata file missing expected fields: ${missingFields.join(', ')}`);
  }
}