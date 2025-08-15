import React, { useMemo } from 'react';
import { DataPreview } from './components/DataPreview/DataPreview';
import { generateSampleData, getSampleColumns } from './utils/dataUtils';

function App() {
  // Generate sample data for demonstration
  // In production, this would come from your data source
  const data = useMemo(() => generateSampleData(100000), []); // 100k rows for performance testing
  const columns = useMemo(() => getSampleColumns(), []);

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="h-screen">
        <DataPreview
          data={data}
          columns={columns}
          className="h-full"
        />
      </div>
    </div>
  );
}

export default App;