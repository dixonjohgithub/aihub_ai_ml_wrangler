/**
 * File: ImputationTable.tsx
 * 
 * Overview:
 * Main imputation configuration table component.
 * 
 * Purpose:
 * Provides interface for configuring imputation strategies per column.
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
import { Table, Select, Button, Badge, Tooltip, Progress, Card } from 'antd';
import {
  SettingOutlined,
  PlayCircleOutlined,
  EyeOutlined,
  QuestionCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { ImputationStrategy, ColumnImputationConfig } from '../../types/imputation';
import StrategySelector from './StrategySelector';
import ParameterConfig from './ParameterConfig';
import ImputationPreview from './ImputationPreview';

const { Option } = Select;

interface ImputationTableProps {
  data: any[];
  columns: string[];
  missingStats: Record<string, any>;
  onApplyImputation: (configs: ColumnImputationConfig[]) => void;
}

const ImputationTable: React.FC<ImputationTableProps> = ({
  data,
  columns,
  missingStats,
  onApplyImputation
}) => {
  const [configurations, setConfigurations] = useState<Record<string, ColumnImputationConfig>>({});
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [previewColumn, setPreviewColumn] = useState<string | null>(null);
  const [configColumn, setConfigColumn] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initialize configurations for columns with missing values
    const initialConfigs: Record<string, ColumnImputationConfig> = {};
    columns.forEach(col => {
      if (missingStats[col]?.missingCount > 0) {
        initialConfigs[col] = {
          column: col,
          strategy: ImputationStrategy.MEAN,
          parameters: {},
          enabled: false
        };
      }
    });
    setConfigurations(initialConfigs);
  }, [columns, missingStats]);

  const handleStrategyChange = (column: string, strategy: ImputationStrategy) => {
    setConfigurations(prev => ({
      ...prev,
      [column]: {
        ...prev[column],
        strategy,
        parameters: getDefaultParameters(strategy)
      }
    }));
  };

  const handleParameterChange = (column: string, parameters: any) => {
    setConfigurations(prev => ({
      ...prev,
      [column]: {
        ...prev[column],
        parameters
      }
    }));
  };

  const handleEnableToggle = (column: string, enabled: boolean) => {
    setConfigurations(prev => ({
      ...prev,
      [column]: {
        ...prev[column],
        enabled
      }
    }));

    if (enabled) {
      setSelectedColumns(prev => [...prev, column]);
    } else {
      setSelectedColumns(prev => prev.filter(c => c !== column));
    }
  };

  const getDefaultParameters = (strategy: ImputationStrategy): any => {
    switch (strategy) {
      case ImputationStrategy.KNN:
        return { n_neighbors: 5 };
      case ImputationStrategy.RANDOM_FOREST:
        return { n_estimators: 100, max_iter: 10 };
      case ImputationStrategy.MICE:
        return { max_iter: 10 };
      case ImputationStrategy.CONSTANT:
        return { value: 0 };
      case ImputationStrategy.INTERPOLATION:
        return { method: 'linear' };
      default:
        return {};
    }
  };

  const getStrategyDescription = (strategy: ImputationStrategy): string => {
    const descriptions: Record<ImputationStrategy, string> = {
      [ImputationStrategy.MEAN]: 'Replace with column mean',
      [ImputationStrategy.MEDIAN]: 'Replace with column median',
      [ImputationStrategy.MODE]: 'Replace with most frequent value',
      [ImputationStrategy.FORWARD_FILL]: 'Use previous valid value',
      [ImputationStrategy.BACKWARD_FILL]: 'Use next valid value',
      [ImputationStrategy.INTERPOLATION]: 'Linear interpolation between values',
      [ImputationStrategy.KNN]: 'K-Nearest Neighbors imputation',
      [ImputationStrategy.RANDOM_FOREST]: 'Random Forest prediction',
      [ImputationStrategy.MICE]: 'Multivariate Imputation by Chained Equations',
      [ImputationStrategy.CONSTANT]: 'Replace with constant value',
      [ImputationStrategy.DROP]: 'Remove rows with missing values'
    };
    return descriptions[strategy];
  };

  const handleApplyImputation = () => {
    const enabledConfigs = Object.values(configurations).filter(c => c.enabled);
    onApplyImputation(enabledConfigs);
  };

  const tableColumns = [
    {
      title: 'Column',
      dataIndex: 'column',
      key: 'column',
      width: 150,
      render: (text: string) => (
        <div className="font-medium">{text}</div>
      )
    },
    {
      title: 'Missing Values',
      dataIndex: 'missing',
      key: 'missing',
      width: 150,
      render: (_: any, record: any) => {
        const stats = missingStats[record.column];
        const percentage = ((stats?.missingCount || 0) / data.length) * 100;
        return (
          <div>
            <Progress
              percent={percentage}
              size="small"
              status={percentage > 30 ? 'exception' : 'normal'}
              format={() => `${stats?.missingCount || 0} (${percentage.toFixed(1)}%)`}
            />
          </div>
        );
      }
    },
    {
      title: 'Data Type',
      dataIndex: 'dtype',
      key: 'dtype',
      width: 100,
      render: (_: any, record: any) => {
        const dtype = missingStats[record.column]?.dtype || 'unknown';
        return (
          <Badge
            color={dtype === 'numeric' ? 'blue' : 'green'}
            text={dtype}
          />
        );
      }
    },
    {
      title: 'Strategy',
      dataIndex: 'strategy',
      key: 'strategy',
      width: 200,
      render: (_: any, record: any) => {
        const config = configurations[record.column];
        return (
          <StrategySelector
            value={config?.strategy || ImputationStrategy.MEAN}
            dataType={missingStats[record.column]?.dtype || 'numeric'}
            missingPercentage={((missingStats[record.column]?.missingCount || 0) / data.length) * 100}
            onChange={(strategy) => handleStrategyChange(record.column, strategy)}
          />
        );
      }
    },
    {
      title: 'Parameters',
      dataIndex: 'parameters',
      key: 'parameters',
      width: 100,
      render: (_: any, record: any) => {
        const config = configurations[record.column];
        const hasParams = config?.strategy && [
          ImputationStrategy.KNN,
          ImputationStrategy.RANDOM_FOREST,
          ImputationStrategy.MICE,
          ImputationStrategy.CONSTANT,
          ImputationStrategy.INTERPOLATION
        ].includes(config.strategy);

        return hasParams ? (
          <Button
            size="small"
            icon={<SettingOutlined />}
            onClick={() => setConfigColumn(record.column)}
          >
            Configure
          </Button>
        ) : (
          <span className="text-gray-400">None</span>
        );
      }
    },
    {
      title: 'Preview',
      dataIndex: 'preview',
      key: 'preview',
      width: 100,
      render: (_: any, record: any) => (
        <Button
          size="small"
          icon={<EyeOutlined />}
          onClick={() => setPreviewColumn(record.column)}
        >
          Preview
        </Button>
      )
    },
    {
      title: 'Enable',
      dataIndex: 'enable',
      key: 'enable',
      width: 80,
      render: (_: any, record: any) => {
        const config = configurations[record.column];
        return (
          <input
            type="checkbox"
            checked={config?.enabled || false}
            onChange={(e) => handleEnableToggle(record.column, e.target.checked)}
            className="w-4 h-4"
          />
        );
      }
    }
  ];

  const tableData = columns
    .filter(col => missingStats[col]?.missingCount > 0)
    .map(col => ({ column: col, key: col }));

  return (
    <div className="space-y-4">
      <Card>
        <div className="mb-4 flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Imputation Configuration</h3>
            <p className="text-gray-600">Configure imputation strategies for columns with missing values</p>
          </div>
          <div className="space-x-2">
            <Badge count={selectedColumns.length} showZero>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleApplyImputation}
                disabled={selectedColumns.length === 0}
                loading={loading}
              >
                Apply Imputation
              </Button>
            </Badge>
          </div>
        </div>

        <Table
          columns={tableColumns}
          dataSource={tableData}
          pagination={false}
          size="small"
          scroll={{ y: 400 }}
        />
      </Card>

      {/* Parameter Configuration Modal */}
      {configColumn && configurations[configColumn] && (
        <ParameterConfig
          visible={!!configColumn}
          column={configColumn}
          strategy={configurations[configColumn].strategy}
          parameters={configurations[configColumn].parameters}
          onSave={(params) => {
            handleParameterChange(configColumn, params);
            setConfigColumn(null);
          }}
          onCancel={() => setConfigColumn(null)}
        />
      )}

      {/* Preview Modal */}
      {previewColumn && configurations[previewColumn] && (
        <ImputationPreview
          visible={!!previewColumn}
          column={previewColumn}
          data={data}
          strategy={configurations[previewColumn].strategy}
          parameters={configurations[previewColumn].parameters}
          onClose={() => setPreviewColumn(null)}
        />
      )}
    </div>
  );
};

export default ImputationTable;