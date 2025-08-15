/**
 * File: CorrelationHeatmap.tsx
 * 
 * Overview:
 * Interactive correlation heatmap visualization component.
 * 
 * Purpose:
 * Displays correlation matrix as an interactive heatmap.
 * 
 * Dependencies:
 * - React: UI framework
 * - Plotly.js: Charting library
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { Card, Slider, Select, Button, Space, Tooltip } from 'antd';
import {
  DownloadOutlined,
  FilterOutlined,
  ZoomInOutlined,
  ZoomOutOutlined
} from '@ant-design/icons';

const { Option } = Select;

interface CorrelationHeatmapProps {
  data: number[][];
  features: string[];
  method: string;
  onFeatureSelect?: (feature1: string, feature2: string, correlation: number) => void;
}

const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({
  data,
  features,
  method,
  onFeatureSelect
}) => {
  const [threshold, setThreshold] = useState(0);
  const [colorScale, setColorScale] = useState('RdBu');
  const [showValues, setShowValues] = useState(true);
  const [filteredData, setFilteredData] = useState(data);
  const [filteredFeatures, setFilteredFeatures] = useState(features);
  const [zoomLevel, setZoomLevel] = useState(1);

  useEffect(() => {
    // Apply threshold filtering
    if (threshold > 0) {
      const filtered = data.map((row, i) =>
        row.map((val, j) => {
          if (i === j) return val; // Keep diagonal
          return Math.abs(val) >= threshold ? val : NaN;
        })
      );
      setFilteredData(filtered);
    } else {
      setFilteredData(data);
    }
  }, [data, threshold]);

  const colorScales = [
    { value: 'RdBu', label: 'Red-Blue' },
    { value: 'Viridis', label: 'Viridis' },
    { value: 'Portland', label: 'Portland' },
    { value: 'Picnic', label: 'Picnic' },
    { value: 'Jet', label: 'Jet' }
  ];

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev / 1.2, 0.5));
  };

  const handleExport = () => {
    // Export correlation matrix as CSV
    let csv = 'Feature,' + features.join(',') + '\n';
    features.forEach((feature, i) => {
      csv += feature + ',' + data[i].join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `correlation_matrix_${method}.csv`;
    a.click();
  };

  const plotData: any = [{
    type: 'heatmap',
    z: filteredData,
    x: filteredFeatures,
    y: filteredFeatures,
    colorscale: colorScale,
    zmin: -1,
    zmax: 1,
    colorbar: {
      title: 'Correlation',
      titleside: 'right',
      tickmode: 'linear',
      tick0: -1,
      dtick: 0.2
    },
    hovertemplate: '%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>',
    text: showValues ? filteredData.map(row => row.map(val => val.toFixed(2))) : undefined,
    texttemplate: showValues ? '%{text}' : undefined,
    textfont: {
      size: 10
    }
  }];

  const layout: any = {
    title: {
      text: `${method.charAt(0).toUpperCase() + method.slice(1)} Correlation Matrix`,
      font: { size: 16 }
    },
    width: 800 * zoomLevel,
    height: 800 * zoomLevel,
    xaxis: {
      side: 'bottom',
      tickangle: -45,
      tickfont: { size: 10 }
    },
    yaxis: {
      side: 'left',
      tickfont: { size: 10 }
    },
    paper_bgcolor: 'white',
    plot_bgcolor: 'white',
    margin: {
      l: 100,
      r: 100,
      t: 100,
      b: 100
    }
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToAdd: [],
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    toImageButtonOptions: {
      format: 'png',
      filename: `correlation_heatmap_${method}`,
      height: 800,
      width: 800,
      scale: 1
    }
  };

  return (
    <Card className="correlation-heatmap">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Correlation Heatmap</h3>
          <Space>
            <Tooltip title="Zoom In">
              <Button
                icon={<ZoomInOutlined />}
                onClick={handleZoomIn}
                size="small"
              />
            </Tooltip>
            <Tooltip title="Zoom Out">
              <Button
                icon={<ZoomOutOutlined />}
                onClick={handleZoomOut}
                size="small"
              />
            </Tooltip>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
              size="small"
            >
              Export CSV
            </Button>
          </Space>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              <FilterOutlined /> Threshold Filter
            </label>
            <Slider
              min={0}
              max={1}
              step={0.1}
              value={threshold}
              onChange={setThreshold}
              marks={{
                0: '0',
                0.5: '0.5',
                0.7: '0.7',
                0.9: '0.9',
                1: '1'
              }}
            />
            <p className="text-xs text-gray-500 mt-1">
              Show only correlations ≥ {threshold.toFixed(1)}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Color Scale</label>
            <Select
              value={colorScale}
              onChange={setColorScale}
              className="w-full"
            >
              {colorScales.map(scale => (
                <Option key={scale.value} value={scale.value}>
                  {scale.label}
                </Option>
              ))}
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Display Options</label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showValues}
                  onChange={(e) => setShowValues(e.target.checked)}
                  className="mr-2"
                />
                Show correlation values
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-auto">
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          onHover={(event: any) => {
            if (onFeatureSelect && event.points.length > 0) {
              const point = event.points[0];
              onFeatureSelect(
                point.y as string,
                point.x as string,
                point.z as number
              );
            }
          }}
        />
      </div>

      <div className="mt-4 p-3 bg-gray-50 rounded">
        <h4 className="font-medium mb-2">Interpretation Guide</h4>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="inline-block w-3 h-3 bg-red-500 mr-1"></span>
            <span>Strong Negative (-1 to -0.7)</span>
          </div>
          <div>
            <span className="inline-block w-3 h-3 bg-gray-300 mr-1"></span>
            <span>Weak (-0.3 to 0.3)</span>
          </div>
          <div>
            <span className="inline-block w-3 h-3 bg-blue-500 mr-1"></span>
            <span>Strong Positive (0.7 to 1)</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default CorrelationHeatmap;