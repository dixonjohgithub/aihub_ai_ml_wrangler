/**
 * File: ImputationPreview.tsx
 * 
 * Overview:
 * Modal component for previewing imputation results.
 * 
 * Purpose:
 * Shows before/after comparison of imputed data.
 * 
 * Dependencies:
 * - React: UI framework
 * - antd: UI components
 * - recharts: Charts
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useEffect } from 'react';
import { Modal, Table, Tabs, Badge, Statistic, Row, Col, Alert } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ImputationStrategy } from '../../types/imputation';

const { TabPane } = Tabs;

interface ImputationPreviewProps {
  visible: boolean;
  column: string;
  data: any[];
  strategy: ImputationStrategy;
  parameters: Record<string, any>;
  onClose: () => void;
}

const ImputationPreview: React.FC<ImputationPreviewProps> = ({
  visible,
  column,
  data,
  strategy,
  parameters,
  onClose
}) => {
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<any>({});
  const [distributionData, setDistributionData] = useState<any[]>([]);

  useEffect(() => {
    if (visible) {
      generatePreview();
    }
  }, [visible, column, strategy, parameters]);

  const generatePreview = () => {
    // Sample first 100 rows for preview
    const sampleData = data.slice(0, 100);
    const columnData = sampleData.map(row => row[column]);
    
    // Simulate imputation (in real app, this would call backend)
    const imputedData = columnData.map(val => {
      if (val === null || val === undefined || val === '') {
        // Apply strategy simulation
        switch (strategy) {
          case ImputationStrategy.MEAN:
            const validValues = columnData.filter(v => v !== null && v !== undefined && v !== '');
            const mean = validValues.reduce((a, b) => a + b, 0) / validValues.length;
            return mean;
          case ImputationStrategy.MEDIAN:
            const validVals = columnData.filter(v => v !== null && v !== undefined && v !== '').sort((a, b) => a - b);
            const mid = Math.floor(validVals.length / 2);
            return validVals.length % 2 ? validVals[mid] : (validVals[mid - 1] + validVals[mid]) / 2;
          case ImputationStrategy.MODE:
            const frequency: Record<string, number> = {};
            columnData.forEach(v => {
              if (v !== null && v !== undefined && v !== '') {
                frequency[v] = (frequency[v] || 0) + 1;
              }
            });
            return Object.keys(frequency).reduce((a, b) => frequency[a] > frequency[b] ? a : b);
          case ImputationStrategy.CONSTANT:
            return parameters.value || 0;
          default:
            return 0;
        }
      }
      return val;
    });

    // Create preview table data
    const preview = sampleData.map((row, index) => ({
      index,
      original: columnData[index],
      imputed: imputedData[index],
      wasImputed: columnData[index] === null || columnData[index] === undefined || columnData[index] === ''
    }));

    setPreviewData(preview);

    // Calculate statistics
    const stats = {
      originalMissing: columnData.filter(v => v === null || v === undefined || v === '').length,
      imputedMissing: 0,
      meanBefore: calculateMean(columnData.filter(v => v !== null && v !== undefined && v !== '')),
      meanAfter: calculateMean(imputedData),
      stdBefore: calculateStd(columnData.filter(v => v !== null && v !== undefined && v !== '')),
      stdAfter: calculateStd(imputedData)
    };

    setStatistics(stats);

    // Create distribution comparison data
    const bins = createHistogramBins(columnData, imputedData);
    setDistributionData(bins);
  };

  const calculateMean = (values: number[]) => {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  };

  const calculateStd = (values: number[]) => {
    if (values.length === 0) return 0;
    const mean = calculateMean(values);
    const squaredDiffs = values.map(v => Math.pow(v - mean, 2));
    return Math.sqrt(calculateMean(squaredDiffs));
  };

  const createHistogramBins = (original: any[], imputed: any[]) => {
    // Simple binning for numeric data
    const validOriginal = original.filter(v => v !== null && v !== undefined && v !== '' && !isNaN(v));
    const validImputed = imputed.filter(v => v !== null && v !== undefined && v !== '' && !isNaN(v));
    
    if (validOriginal.length === 0) return [];

    const min = Math.min(...validOriginal, ...validImputed);
    const max = Math.max(...validOriginal, ...validImputed);
    const binCount = 10;
    const binSize = (max - min) / binCount;

    const bins = [];
    for (let i = 0; i < binCount; i++) {
      const binStart = min + i * binSize;
      const binEnd = binStart + binSize;
      const binLabel = `${binStart.toFixed(1)}-${binEnd.toFixed(1)}`;
      
      bins.push({
        range: binLabel,
        original: validOriginal.filter(v => v >= binStart && v < binEnd).length,
        imputed: validImputed.filter(v => v >= binStart && v < binEnd).length
      });
    }

    return bins;
  };

  const columns = [
    {
      title: 'Index',
      dataIndex: 'index',
      key: 'index',
      width: 80
    },
    {
      title: 'Original Value',
      dataIndex: 'original',
      key: 'original',
      render: (value: any) => (
        value === null || value === undefined || value === '' ?
          <Badge status="error" text="Missing" /> :
          <span>{value}</span>
      )
    },
    {
      title: 'Imputed Value',
      dataIndex: 'imputed',
      key: 'imputed',
      render: (value: any, record: any) => (
        <span className={record.wasImputed ? 'font-bold text-blue-600' : ''}>
          {typeof value === 'number' ? value.toFixed(3) : value}
        </span>
      )
    },
    {
      title: 'Status',
      dataIndex: 'wasImputed',
      key: 'wasImputed',
      render: (wasImputed: boolean) => (
        wasImputed ?
          <Badge status="processing" text="Imputed" /> :
          <Badge status="success" text="Original" />
      )
    }
  ];

  return (
    <Modal
      title={`Imputation Preview: ${column}`}
      open={visible}
      onCancel={onClose}
      width={900}
      footer={null}
    >
      <Alert
        message={`Strategy: ${strategy.replace('_', ' ').toUpperCase()}`}
        description="Showing preview of first 100 rows. Actual imputation will be applied to entire dataset."
        type="info"
        showIcon
        className="mb-4"
      />

      <Tabs defaultActiveKey="1">
        <TabPane tab="Data Preview" key="1">
          <Table
            columns={columns}
            dataSource={previewData}
            rowKey="index"
            size="small"
            scroll={{ y: 400 }}
            pagination={false}
          />
        </TabPane>

        <TabPane tab="Statistics" key="2">
          <Row gutter={16}>
            <Col span={12}>
              <Statistic
                title="Missing Values (Before)"
                value={statistics.originalMissing}
                suffix={`/ ${previewData.length}`}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="Missing Values (After)"
                value={statistics.imputedMissing}
                suffix={`/ ${previewData.length}`}
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
          </Row>
          <Row gutter={16} className="mt-4">
            <Col span={12}>
              <Statistic
                title="Mean (Before)"
                value={statistics.meanBefore?.toFixed(3) || 'N/A'}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="Mean (After)"
                value={statistics.meanAfter?.toFixed(3) || 'N/A'}
              />
            </Col>
          </Row>
          <Row gutter={16} className="mt-4">
            <Col span={12}>
              <Statistic
                title="Std Dev (Before)"
                value={statistics.stdBefore?.toFixed(3) || 'N/A'}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="Std Dev (After)"
                value={statistics.stdAfter?.toFixed(3) || 'N/A'}
              />
            </Col>
          </Row>
        </TabPane>

        <TabPane tab="Distribution" key="3">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={distributionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="original" fill="#8884d8" name="Original" />
              <Bar dataKey="imputed" fill="#82ca9d" name="After Imputation" />
            </BarChart>
          </ResponsiveContainer>
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default ImputationPreview;