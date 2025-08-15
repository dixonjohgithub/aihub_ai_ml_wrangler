/**
 * File: ParameterConfig.tsx
 * 
 * Overview:
 * Modal component for configuring imputation strategy parameters.
 * 
 * Purpose:
 * Provides forms for setting strategy-specific parameters.
 * 
 * Dependencies:
 * - React: UI framework
 * - antd: UI components
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useEffect } from 'react';
import { Modal, Form, InputNumber, Select, Switch, Slider } from 'antd';
import { ImputationStrategy } from '../../types/imputation';

const { Option } = Select;

interface ParameterConfigProps {
  visible: boolean;
  column: string;
  strategy: ImputationStrategy;
  parameters: Record<string, any>;
  onSave: (parameters: Record<string, any>) => void;
  onCancel: () => void;
}

const ParameterConfig: React.FC<ParameterConfigProps> = ({
  visible,
  column,
  strategy,
  parameters,
  onSave,
  onCancel
}) => {
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue(parameters);
  }, [parameters, form]);

  const renderStrategyFields = () => {
    switch (strategy) {
      case ImputationStrategy.KNN:
        return (
          <>
            <Form.Item
              name="n_neighbors"
              label="Number of Neighbors"
              rules={[{ required: true }]}
            >
              <InputNumber min={1} max={50} step={1} />
            </Form.Item>
            <Form.Item
              name="weights"
              label="Weight Function"
            >
              <Select defaultValue="uniform">
                <Option value="uniform">Uniform</Option>
                <Option value="distance">Distance</Option>
              </Select>
            </Form.Item>
          </>
        );

      case ImputationStrategy.RANDOM_FOREST:
        return (
          <>
            <Form.Item
              name="n_estimators"
              label="Number of Trees"
              rules={[{ required: true }]}
            >
              <InputNumber min={10} max={500} step={10} />
            </Form.Item>
            <Form.Item
              name="max_iter"
              label="Maximum Iterations"
              rules={[{ required: true }]}
            >
              <InputNumber min={1} max={50} step={1} />
            </Form.Item>
            <Form.Item
              name="random_state"
              label="Random State"
            >
              <InputNumber min={0} />
            </Form.Item>
          </>
        );

      case ImputationStrategy.MICE:
        return (
          <>
            <Form.Item
              name="max_iter"
              label="Maximum Iterations"
              rules={[{ required: true }]}
            >
              <InputNumber min={1} max={100} step={1} />
            </Form.Item>
            <Form.Item
              name="sample_posterior"
              label="Sample from Posterior"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
            <Form.Item
              name="random_state"
              label="Random State"
            >
              <InputNumber min={0} />
            </Form.Item>
          </>
        );

      case ImputationStrategy.CONSTANT:
        return (
          <Form.Item
            name="value"
            label="Constant Value"
            rules={[{ required: true }]}
          >
            <InputNumber />
          </Form.Item>
        );

      case ImputationStrategy.INTERPOLATION:
        return (
          <>
            <Form.Item
              name="method"
              label="Interpolation Method"
              rules={[{ required: true }]}
            >
              <Select defaultValue="linear">
                <Option value="linear">Linear</Option>
                <Option value="polynomial">Polynomial</Option>
                <Option value="spline">Spline</Option>
                <Option value="pchip">PCHIP</Option>
                <Option value="akima">Akima</Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="order"
              label="Polynomial Order"
              dependencies={['method']}
              hidden={form.getFieldValue('method') !== 'polynomial'}
            >
              <InputNumber min={1} max={10} step={1} />
            </Form.Item>
          </>
        );

      default:
        return <div>No parameters required for this strategy</div>;
    }
  };

  const handleOk = () => {
    form.validateFields().then(values => {
      onSave(values);
    });
  };

  return (
    <Modal
      title={`Configure ${strategy} Parameters for ${column}`}
      open={visible}
      onOk={handleOk}
      onCancel={onCancel}
      width={500}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={parameters}
      >
        {renderStrategyFields()}
        
        <div className="mt-4 p-3 bg-gray-50 rounded">
          <h4 className="font-medium mb-2">Parameter Guidelines</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {strategy === ImputationStrategy.KNN && (
              <>
                <li>• Lower k-values: More sensitive to local patterns</li>
                <li>• Higher k-values: Smoother imputation</li>
                <li>• Recommended: k = sqrt(n) for n samples</li>
              </>
            )}
            {strategy === ImputationStrategy.RANDOM_FOREST && (
              <>
                <li>• More trees: Better accuracy but slower</li>
                <li>• Higher iterations: Better convergence</li>
                <li>• Set random_state for reproducibility</li>
              </>
            )}
            {strategy === ImputationStrategy.MICE && (
              <>
                <li>• More iterations: Better convergence</li>
                <li>• Sample posterior: Adds uncertainty</li>
                <li>• Good for MAR (Missing At Random) data</li>
              </>
            )}
            {strategy === ImputationStrategy.INTERPOLATION && (
              <>
                <li>• Linear: Simple, fast, works well for regular spacing</li>
                <li>• Spline: Smooth curves, good for continuous data</li>
                <li>• PCHIP: Preserves monotonicity</li>
              </>
            )}
          </ul>
        </div>
      </Form>
    </Modal>
  );
};

export default ParameterConfig;