# AI Hub AI/ML Wrangler Frontend

React TypeScript frontend application for the AI Hub AI/ML Wrangler project.

## 🚀 Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Configure your environment variables in `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📁 Project Structure

```
src/
├── components/         # Reusable UI components
│   ├── Header.tsx     # Application header
│   ├── Sidebar.tsx    # Navigation sidebar
│   ├── Footer.tsx     # Application footer
│   └── Button.tsx     # Reusable button component
├── layouts/           # Layout components
│   └── Layout.tsx     # Main application layout
├── pages/            # Page components
│   ├── HomePage.tsx   # Dashboard page
│   ├── ImportPage.tsx # Data import page
│   ├── AnalysisPage.tsx # Analysis configuration
│   ├── ResultsPage.tsx # Results and downloads
│   └── NotFoundPage.tsx # 404 page
├── services/         # API service layer
│   ├── api.ts        # Axios configuration
│   └── dataService.ts # Data operations
├── types/           # TypeScript type definitions
│   └── index.ts     # Main type definitions
├── App.tsx          # Main app component
├── main.tsx         # Application entry point
└── index.css        # Global styles with Tailwind
```

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type safety and better DX
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **ESLint** - Code linting and formatting

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (`primary-*` classes)
- **Secondary**: Gray scale (`secondary-*` classes)
- **Success**: Green (`success-*` classes)
- **Warning**: Yellow (`warning-*` classes)  
- **Error**: Red (`error-*` classes)

### Components
- **Button**: Multiple variants (primary, secondary, success, warning, error)
- **Card**: Consistent container styling
- **Navigation**: Header and sidebar navigation
- **Forms**: Styled input components

## 📊 Features

### Import Workflow
- Drag & drop file upload
- Multiple format support (CSV, JSON, Excel)
- File validation and preview
- Upload progress tracking

### Analysis Dashboard
- Dataset overview and statistics
- Missing data pattern visualization
- AI-powered recommendations
- Configuration interface

### Results Management
- Job status monitoring
- Download management
- Report generation
- Correlation matrices

## 🔌 API Integration

The frontend communicates with the FastAPI backend through:

- **Base URL**: Configured via `VITE_API_BASE_URL`
- **Authentication**: JWT token support
- **File Upload**: Multipart form data with progress
- **Real-time Updates**: Job status polling
- **Error Handling**: Comprehensive error responses

### API Endpoints

```typescript
// Dataset operations
POST /api/datasets/upload
GET  /api/datasets
GET  /api/datasets/{id}
DELETE /api/datasets/{id}

// Imputation operations  
GET  /api/imputation/strategies
POST /api/imputation/jobs
GET  /api/imputation/jobs/{id}

// Results and downloads
GET  /api/imputation/jobs/{id}/download/data
GET  /api/imputation/jobs/{id}/download/correlation
GET  /api/imputation/jobs/{id}/download/report
```

## 🧪 Development

### Adding New Components

1. Create component in appropriate directory
2. Add TypeScript interfaces in `types/index.ts`
3. Import and use in parent components
4. Follow existing naming conventions

### Styling Guidelines

- Use Tailwind utility classes
- Follow component-based architecture
- Maintain consistent spacing (multiples of 4)
- Use semantic color classes
- Ensure responsive design

### State Management

Currently using React's built-in state management:
- Local state with `useState` for component state
- Context API for global state (if needed)
- Consider adding Redux Toolkit for complex state

## 📱 Responsive Design

- **Mobile First**: Designed for mobile-first experience
- **Breakpoints**: Following Tailwind's responsive system
- **Navigation**: Collapsible mobile navigation
- **Tables**: Horizontally scrollable on mobile
- **Cards**: Stack vertically on smaller screens

## 🔧 Configuration

### Vite Configuration
- Path aliases (`@/` for `src/`)
- Development server on port 3000
- Build optimizations enabled
- Source maps for debugging

### TypeScript Configuration
- Strict mode enabled
- Modern target (ES2020)
- Path mapping for imports
- React JSX transform

### Tailwind Configuration
- Custom color palette
- Extended spacing and sizing
- Custom animations
- Component-specific utilities

## 🚀 Deployment

### Build Process

```bash
# Production build
npm run build

# Preview build locally
npm run preview
```

### Environment Variables

Required for production:
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_APP_NAME` - Application name
- `VITE_APP_VERSION` - Version number

### Static Hosting

The built application can be deployed to:
- Vercel
- Netlify  
- AWS S3 + CloudFront
- Docker container with nginx

## 🤝 Contributing

1. Follow the existing code style
2. Add proper TypeScript types
3. Include component documentation
4. Test across different screen sizes
5. Ensure accessibility compliance

## 📄 License

MIT License - see the [LICENSE](../LICENSE) file for details.