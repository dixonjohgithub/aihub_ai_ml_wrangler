/**
 * File: ImportSummary.tsx
 * 
 * Overview:
 * File preview component showing data structure and content summary
 * 
 * Purpose:
 * Provides detailed preview of uploaded files with data analysis
 * 
 * Dependencies:
 * - React (for component state management)
 * - upload.types (for TypeScript interfaces)
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useEffect } from 'react';
import { UploadFile, FilePreview } from '../types/upload.types';
import { formatFileSize, isCSVFile, isJSONFile } from '../utils/fileValidation';

interface ImportSummaryProps {
  files: UploadFile[];
  onProcessFile?: (fileId: string) => void;
  onDeleteFile?: (fileId: string) => void;
}

export const ImportSummary: React.FC<ImportSummaryProps> = ({
  files,
  onProcessFile,
  onDeleteFile
}) => {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [previews, setPreviews] = useState<Map<string, FilePreview>>(new Map());

  const completedFiles = files.filter(f => f.status === 'completed');

  useEffect(() => {
    // Generate previews for completed files
    completedFiles.forEach(async (file) => {
      if (!previews.has(file.id)) {
        const preview = await generatePreview(file.file);
        setPreviews(prev => new Map(prev.set(file.id, preview)));
      }
    });
  }, [completedFiles]);

  const generatePreview = async (file: File): Promise<FilePreview> => {
    const preview: FilePreview = {
      name: file.name,
      size: file.size,
      type: file.type || 'unknown'
    };

    try {
      if (isCSVFile(file)) {
        const csvPreview = await generateCSVPreview(file);
        Object.assign(preview, csvPreview);
      } else if (isJSONFile(file)) {
        const jsonPreview = await generateJSONPreview(file);
        Object.assign(preview, jsonPreview);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
    }

    return preview;
  };

  const generateCSVPreview = async (file: File): Promise<Partial<FilePreview>> => {
    const text = await file.text();
    const lines = text.split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
      return { rows: 0, columns: [] };
    }

    const header = lines[0].split(',').map(col => col.trim().replace(/"/g, ''));
    const dataRows = lines.slice(1);
    
    // Generate sample data (first 5 rows)
    const sampleData = dataRows.slice(0, 5).map(row => {
      const values = row.split(',').map(val => val.trim().replace(/"/g, ''));
      const rowObj: any = {};
      header.forEach((col, idx) => {
        rowObj[col] = values[idx] || '';
      });
      return rowObj;
    });

    return {
      rows: dataRows.length,
      columns: header,
      sampleData
    };
  };

  const generateJSONPreview = async (file: File): Promise<Partial<FilePreview>> => {
    const text = await file.text();
    const data = JSON.parse(text);
    
    let metadata: Record<string, any> = {};
    let columns: string[] = [];
    let rows = 0;

    if (Array.isArray(data)) {
      rows = data.length;
      if (data.length > 0 && typeof data[0] === 'object') {
        columns = Object.keys(data[0]);
      }
      metadata.type = 'array';
      metadata.sampleRecord = data[0];
    } else if (typeof data === 'object') {
      columns = Object.keys(data);
      metadata.type = 'object';
      
      // Check if it's a Data Wrangler metadata file
      if (file.name.toLowerCase().includes('metadata')) {
        metadata.isDataWranglerMetadata = true;
        metadata.hasStatistics = 'statistics' in data;
        metadata.hasTransformations = 'transformations' in data;
        metadata.hasDataTypes = 'dataTypes' in data;
      }
    }

    return {
      rows,
      columns,
      metadata,
      sampleData: Array.isArray(data) ? data.slice(0, 5) : [data]
    };
  };

  const getFileTypeIcon = (fileName: string) => {
    if (fileName.toLowerCase().endsWith('.csv')) return '📊';
    if (fileName.toLowerCase().endsWith('.json')) return '📋';
    return '📄';
  };

  const getDataWranglerType = (fileName: string) => {
    const lowerName = fileName.toLowerCase();
    if (lowerName.includes('transformation_file')) return 'Transformation Data';
    if (lowerName.includes('mapped_data')) return 'Mapped Data';
    if (lowerName.includes('metadata')) return 'Metadata';
    return 'Unknown Type';
  };

  if (completedFiles.length === 0) {
    return (
      <div className="w-full p-8 text-center text-gray-500">
        <p>No files uploaded yet. Use the dropzone above to upload files.</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Import Summary</h3>
        <p className="text-sm text-gray-600 mt-1">
          {completedFiles.length} file{completedFiles.length !== 1 ? 's' : ''} ready for processing
        </p>
      </div>

      <div className="divide-y divide-gray-200">
        {completedFiles.map((file) => {
          const preview = previews.get(file.id);
          const isExpanded = selectedFile === file.id;

          return (
            <div key={file.id} className="p-4">
              {/* File Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getFileTypeIcon(file.file.name)}</span>
                  <div>
                    <h4 className="font-medium text-gray-900">{file.file.name}</h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{formatFileSize(file.file.size)}</span>
                      <span>{getDataWranglerType(file.file.name)}</span>
                      {preview && (
                        <>
                          {preview.rows !== undefined && <span>{preview.rows} rows</span>}
                          {preview.columns && <span>{preview.columns.length} columns</span>}
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setSelectedFile(isExpanded ? null : file.id)}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                  >
                    {isExpanded ? 'Hide' : 'Preview'}
                  </button>
                  {onProcessFile && (
                    <button
                      onClick={() => onProcessFile(file.id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                    >
                      Process
                    </button>
                  )}
                  {onDeleteFile && (
                    <button
                      onClick={() => onDeleteFile(file.id)}
                      className="px-3 py-1 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50 transition-colors"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>

              {/* Expanded Preview */}
              {isExpanded && preview && (
                <div className="mt-4 space-y-4">
                  {/* Columns */}
                  {preview.columns && preview.columns.length > 0 && (
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Columns ({preview.columns.length})</h5>
                      <div className="flex flex-wrap gap-2">
                        {preview.columns.map((column, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded font-mono"
                          >
                            {column}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sample Data */}
                  {preview.sampleData && preview.sampleData.length > 0 && (
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Sample Data</h5>
                      <div className="bg-gray-50 rounded p-3 overflow-x-auto">
                        <pre className="text-xs text-gray-800">
                          {JSON.stringify(preview.sampleData, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* Metadata */}
                  {preview.metadata && Object.keys(preview.metadata).length > 0 && (
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Metadata</h5>
                      <div className="bg-gray-50 rounded p-3">
                        {Object.entries(preview.metadata).map(([key, value]) => (
                          <div key={key} className="flex justify-between py-1 text-sm">
                            <span className="font-medium text-gray-600">{key}:</span>
                            <span className="text-gray-800">
                              {typeof value === 'boolean' ? (value ? '✓' : '✗') : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action Footer */}
      {completedFiles.length > 0 && (
        <div className="p-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Total data: {formatFileSize(completedFiles.reduce((sum, f) => sum + f.file.size, 0))}
          </div>
          <div className="space-x-2">
            <button className="px-4 py-2 text-sm border border-gray-300 rounded hover:bg-white transition-colors">
              Export Summary
            </button>
            <button className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors">
              Process All Files
            </button>
          </div>
        </div>
      )}
    </div>
  );
};