# AI Hub AI/ML Wrangler - Frontend

React TypeScript frontend for the AI Hub AI/ML Wrangler application.

## Technology Stack

- **React 18** - Component-based UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components (Header, Sidebar, Footer)
│   │   └── ui/              # Reusable UI components
│   ├── pages/               # Page components
│   ├── services/            # API service layer
│   ├── hooks/               # Custom React hooks
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   └── styles/              # Global styles and Tailwind imports
├── public/                  # Static assets
└── package.json
```

## Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint code
npm run lint
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Development Configuration
VITE_DEV_MODE=true

# Feature Flags
VITE_ENABLE_AI_FEATURES=true
VITE_ENABLE_EXPORT_FEATURES=true
```

## Key Features

- **Responsive Design** - Works on desktop and mobile devices
- **Data Wrangler UI Patterns** - Consistent with AI Hub design system
- **Type Safety** - Full TypeScript coverage
- **API Integration** - Axios-based service layer
- **Modern Routing** - React Router with nested routes
- **Component Library** - Reusable UI components
- **Error Handling** - Comprehensive error boundaries

## API Integration

The frontend communicates with the FastAPI backend through:

- **Health Check**: `GET /health`
- **File Upload**: `POST /api/upload`
- **Data Summary**: `GET /api/data/{id}/summary`

## Component Architecture

### Layout Components
- **Layout** - Main wrapper with header, sidebar, and footer
- **Header** - Top navigation and branding
- **Sidebar** - Workflow navigation
- **Footer** - Project information and links

### Page Components
- **HomePage** - Dashboard with project overview
- **ImportPage** - File upload interface
- **AnalyzePage** - Data analysis interface (coming soon)
- **ImputePage** - Imputation configuration (coming soon)
- **ExportPage** - Data export interface (coming soon)

### UI Components
- **Button** - Standardized button component
- **Input** - Form input components (coming soon)
- **Modal** - Reusable modal dialogs (coming soon)
- **Table** - Data display tables (coming soon)

## Styling

The application uses Tailwind CSS with a custom configuration that includes:

- **Primary Colors** - Blue-based primary palette
- **Secondary Colors** - Gray-based secondary palette
- **Custom Components** - Pre-defined component classes
- **Responsive Design** - Mobile-first approach

## Development Guidelines

1. **Component Structure** - Use functional components with hooks
2. **Type Safety** - Define interfaces for all props and API responses
3. **Error Handling** - Implement proper error boundaries and user feedback
4. **Performance** - Use React.memo and useMemo for optimization
5. **Accessibility** - Follow WCAG guidelines for inclusive design

## Testing

```bash
# Run unit tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## Building for Production

```bash
# Build production bundle
npm run build

# Preview production build locally
npm run preview
```

The build output will be in the `dist/` directory.

## Contributing

1. Follow the established code style
2. Write tests for new components
3. Update documentation for new features
4. Follow the Git commit message conventions

## Related Documentation

- [Project Overview](../README.md)
- [Backend API](../backend/README.md)
- [Development Guide](../docs/development.md)