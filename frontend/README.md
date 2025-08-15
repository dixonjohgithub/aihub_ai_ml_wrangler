# Data Preview Frontend

A comprehensive React-based data preview interface with virtualization, statistical analysis, and interactive visualizations.

## Features

### Core Components

- **DataTable**: Virtualized table component that efficiently handles 1M+ rows
- **ColumnStatistics**: Sidebar displaying statistical analysis (mean, median, mode, missing %)
- **MissingDataSummary**: Heatmap visualization of missing data patterns
- **DistributionCharts**: Interactive charts showing data distribution for numeric columns
- **ColumnSelection**: Multi-select interface with type-based filtering
- **SearchFilter**: Real-time search and advanced filtering capabilities

### Key Capabilities

✅ **Performance**: Virtualized rendering for smooth handling of large datasets  
✅ **Statistics**: Comprehensive statistical analysis for all column types  
✅ **Visualization**: Missing data heatmaps and distribution charts  
✅ **Interaction**: Column selection, sorting, filtering, and search  
✅ **Responsive**: Mobile-friendly design with adaptive layouts  
✅ **Accessibility**: WCAG compliant with proper ARIA labels  

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Usage

```typescript
import { DataPreview } from './components/DataPreview';

function App() {
  const data = [...]; // Your data rows
  const columns = [...]; // Column definitions
  
  return (
    <DataPreview
      data={data}
      columns={columns}
      className="h-screen"
    />
  );
}
```

## Component Architecture

```
DataPreview/
├── DataPreview.tsx          # Main container component
├── DataTable.tsx            # Virtualized data table
├── ColumnStatistics.tsx     # Statistical analysis sidebar
├── MissingDataSummary.tsx   # Missing data heatmap
├── DistributionCharts.tsx   # Data distribution visualizations
├── ColumnSelection.tsx      # Column selection interface
├── SearchFilter.tsx         # Search and filtering
└── __tests__/              # Component tests
```

## Type Definitions

```typescript
interface DataRow {
  [key: string]: any;
}

interface ColumnInfo {
  name: string;
  type: 'number' | 'string' | 'boolean' | 'date' | 'unknown';
  nullable: boolean;
}

interface ColumnStatistics {
  column: string;
  type: DataType;
  count: number;
  missing: number;
  missingPercentage: number;
  unique?: number;
  mean?: number;
  median?: number;
  mode?: string | number;
  // ... additional numeric stats
}
```

## Performance Features

- **Virtualization**: Only renders visible rows for smooth scrolling
- **Debounced Search**: 300ms debounce prevents excessive filtering
- **Memoized Calculations**: Statistics computed only when data changes
- **Lazy Loading**: Charts render on-demand when tab is active
- **Sample-based Analysis**: Missing data analysis uses sampling for large datasets

## Testing

Comprehensive test suite covering:

- Component rendering and interaction
- Data filtering and sorting logic
- Statistical calculation accuracy
- Performance with large datasets
- Accessibility compliance

```bash
npm test              # Run all tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
```

## Customization

The components are designed to be highly customizable:

```typescript
// Custom styling
<DataPreview 
  className="custom-preview" 
  data={data} 
  columns={columns} 
/>

// Custom callbacks
<DataTable
  data={data}
  columns={columns}
  selectedColumns={selected}
  onSort={(column, direction) => handleSort(column, direction)}
/>
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- **React 18**: Core framework
- **@tanstack/react-virtual**: Virtualization
- **Recharts**: Data visualization
- **Tailwind CSS**: Styling
- **TypeScript**: Type safety
- **Vitest**: Testing framework