# AI Hub AI/ML Wrangler - Product Requirements Document (PRD)

## Introduction/Overview
The AI Hub AI/ML Wrangler is a sophisticated statistical data imputation and analysis tool designed specifically for data scientists and research scientists. This web-based application addresses the critical challenge of handling missing data in large datasets while providing intelligent, AI-powered recommendations for feature engineering, encoding, and imputation strategies. The system leverages OpenAI's API to analyze datasets and suggest optimal approaches based on user goals, making complex statistical operations accessible through an intuitive interface that mirrors the familiar AI Hub Data Wrangler design.

## Goals
1. **Intelligent Data Analysis**: Utilize OpenAI API to assess datasets and provide context-aware suggestions for feature engineering, encoding, and imputation strategies
2. **Comprehensive Imputation**: Support all major imputation methods (statistical, ML-based, correlation-based, and time-series specific) for large datasets (>100MB, >1M rows)
3. **Interactive Guidance**: Provide real-time, interactive suggestions and approaches based on the data characteristics
4. **Correlation Analysis**: Generate correlation matrices in the specific format required (matching yrbs_2021_district_correlation.csv structure)
5. **Complete Documentation**: Produce comprehensive reports with visualizations, statistics, and full transformation audit trails
6. **Seamless Integration**: Import Data Wrangler exports and maintain consistent user experience
7. **Production Ready**: Deploy as a scalable web application with robust error handling and performance optimization

## User Stories

### Primary Users: Data Scientists
1. **As a data scientist**, I want to upload my dataset and receive AI-powered suggestions for handling missing data, so that I can make informed decisions about imputation strategies
2. **As a data scientist**, I want to configure different imputation methods per column based on data type and distribution, so that I can optimize data quality for my ML models
3. **As a data scientist**, I want to preview imputation results before applying them, so that I can validate the approach maintains statistical integrity
4. **As a data scientist**, I want to generate correlation matrices in standard CSV format, so that I can identify multicollinearity issues
5. **As a data scientist**, I want comprehensive reports documenting all transformations, so that I can ensure reproducibility

### Primary Users: Research Scientists
6. **As a research scientist**, I want the system to detect missing data patterns automatically, so that I can understand if data is missing at random or systematically
7. **As a research scientist**, I want to apply multiple imputation strategies and compare results, so that I can choose the most appropriate method for my research
8. **As a research scientist**, I want to export correlation matrices in the exact format I need for publication, so that I can include them in my research papers
9. **As a research scientist**, I want interactive visualizations of before/after imputation, so that I can validate that statistical properties are preserved
10. **As a research scientist**, I want the ability to save and reload imputation configurations, so that I can apply consistent methods across multiple datasets

## Functional Requirements

### Core Functionality
1. **The system must** detect missing data patterns across all columns in uploaded datasets
2. **The system must** integrate with OpenAI API to provide intelligent suggestions for:
   - Feature engineering approaches based on data characteristics
   - Optimal encoding strategies for categorical variables
   - Column-specific imputation strategies aligned with user goals
3. **The system must** support multiple imputation methods:
   - Statistical methods (mean, median, mode, forward/backward fill)
   - Machine learning methods (KNN, Random Forest, iterative imputation)
   - Correlation-based methods (using correlation matrices for informed imputation)
   - Time-series specific methods (interpolation, seasonal decomposition)
4. **The system must** provide interactive configuration allowing users to:
   - Select imputation strategy per column
   - Configure strategy-specific parameters
   - Preview results on sample data before applying
   - Compare multiple strategies side-by-side
5. **The system must** generate comprehensive outputs:
   - Imputed dataset in CSV format
   - Correlation matrix matching the yrbs_2021_district_correlation.csv format
   - Detailed markdown reports with visualizations
   - Complete metadata JSON for reproducibility
6. **The system must** handle large datasets efficiently (>100MB, >1M rows)
7. **The system must** provide real-time progress updates for long-running operations
8. **The system must** allow users to save and reload imputation configurations
9. **The system must** validate data quality post-imputation
10. **The system must** provide clear error messages and recovery options

### AI-Powered Features
11. **The system must** analyze uploaded datasets using OpenAI API to suggest:
    - Optimal feature engineering strategies
    - Appropriate encoding methods for categorical variables
    - Best imputation strategy per column based on data distribution
    - Potential issues or data quality concerns
12. **The system must** provide interactive dialogue where users can:
    - Ask questions about their data
    - Receive contextual suggestions
    - Get explanations for recommended approaches
13. **The system must** learn from user feedback to improve suggestions

### Visualization Requirements
14. **The system must** display missing data patterns through heatmaps
15. **The system must** show before/after distribution plots for imputed columns
16. **The system must** render interactive correlation heatmaps with filtering
17. **The system must** provide statistical summary cards for quick insights
18. **The system must** generate exportable charts for reports

## Non-Goals (Out of Scope)

1. **Data Collection**: This system will NOT collect or scrape data from external sources
2. **Real-time Streaming**: Will NOT support real-time streaming data imputation
3. **Database Management**: Will NOT include database creation, management, or administration features
4. **Advanced ML Training**: Will NOT train custom ML models beyond imputation algorithms
5. **Data Storage**: Will NOT provide long-term data storage solutions
6. **ETL Pipeline**: Will NOT include full ETL pipeline capabilities
7. **Version Control**: Will NOT provide built-in version control for datasets
8. **Collaborative Features**: Will NOT include multi-user collaboration in initial version

## Design Considerations

### User Interface
- **Consistency**: Mirror AI Hub Data Wrangler's design patterns and components
- **Step-based Workflow**: Clear visual progression through import → analyze → configure → apply → export
- **Responsive Tables**: Virtualized data tables for smooth performance with large datasets
- **Inline Editing**: Direct manipulation of imputation configurations in table cells
- **Real-time Feedback**: Immediate validation and preview updates
- **Progress Tracking**: Clear progress bars with time estimates for long operations
- **Error States**: Informative error messages with suggested actions

### OpenAI Integration UI
- **AI Assistant Panel**: Dedicated sidebar for AI-powered suggestions
- **Context-Aware Prompts**: Pre-populated questions based on data characteristics
- **Suggestion Cards**: Visual cards displaying AI recommendations with rationale
- **Interactive Chat**: Allow users to ask follow-up questions about suggestions
- **Feedback Mechanism**: Thumbs up/down for suggestion quality

## Technical Considerations

### Architecture
- **Frontend**: React 18 with TypeScript, Vite, Tailwind CSS (matching Data Wrangler)
- **Backend**: FastAPI (Python 3.10+) for optimal ML library integration
- **ML Integration**: Direct integration with research_pipeline modules
- **Task Queue**: Celery with Redis for asynchronous processing
- **Database**: PostgreSQL for job tracking and metadata
- **Deployment**: Docker containers with docker-compose orchestration

### OpenAI API Integration
- **API Key Management**: Secure storage of API keys in environment variables
- **Rate Limiting**: Implement rate limiting to manage API costs
- **Caching**: Cache API responses for similar datasets/questions
- **Fallback Logic**: Provide default suggestions if API is unavailable
- **Cost Tracking**: Monitor and report API usage costs

### Performance Optimization
- **Chunked Processing**: Process large datasets in manageable chunks
- **Worker Processes**: Utilize multiple workers for parallel processing
- **Memory Management**: Stream large files instead of loading entirely into memory
- **Caching Strategy**: Cache correlation matrices and intermediate results
- **Database Indexing**: Optimize queries with appropriate indexes

### Security Considerations
- **Input Validation**: Sanitize all user inputs and file uploads
- **File Size Limits**: Enforce maximum file size limits
- **Authentication**: Optional authentication for production deployment
- **Data Encryption**: Encrypt sensitive data at rest and in transit
- **API Key Security**: Never expose OpenAI API keys to frontend

## Success Metrics

### Performance Metrics
1. **Processing Speed**: < 30 seconds for 100K row dataset imputation
2. **Preview Response**: < 3 seconds for imputation preview generation
3. **Large Dataset Handling**: Successfully process datasets > 1M rows
4. **Correlation Matrix Generation**: < 10 seconds for 100 variable correlation matrix
5. **API Response Time**: < 5 seconds for OpenAI suggestions

### Quality Metrics
6. **Imputation Accuracy**: Maintain statistical properties (mean, variance, distribution) within 5% of original
7. **Correlation Preservation**: Preserve correlation coefficients within 0.05 of original relationships
8. **Report Completeness**: 100% documentation of all applied transformations
9. **Error Recovery**: Graceful handling of 100% of anticipated error scenarios

### User Experience Metrics
10. **Ease of Use**: Users can complete basic imputation workflow within 10 minutes
11. **Documentation Clarity**: Clear documentation enables self-service for 90% of use cases
12. **AI Suggestion Relevance**: > 80% of AI suggestions rated as helpful by users
13. **Export Success**: 100% successful export of all output formats

## Open Questions

### Technical Questions
1. **OpenAI Model Selection**: Which OpenAI model(s) should be used for different types of analysis?
2. **Cost Management**: What is the acceptable monthly budget for OpenAI API usage?
3. **Caching Duration**: How long should AI suggestions be cached before refreshing?
4. **Dataset Size Limits**: What is the maximum acceptable file size for uploads?
5. **Processing Timeouts**: What timeout values should be set for long-running operations?

### Feature Questions
6. **Authentication Requirements**: Is user authentication required for the initial version?
7. **Multi-user Support**: Should the system support team collaboration features?
8. **Cloud Storage Integration**: Should the system integrate with cloud storage providers?
9. **Custom Imputation Methods**: Should users be able to define custom imputation algorithms?
10. **Versioning**: Should the system track versions of imputation configurations?

### Integration Questions
11. **Data Wrangler Integration**: Should there be direct API integration with Data Wrangler?
12. **Research Pipeline Updates**: How should updates to research_pipeline modules be managed?
13. **Export Formats**: Are additional export formats needed beyond CSV and JSON?
14. **Visualization Libraries**: Should additional visualization libraries be integrated?
15. **Notification System**: Should the system notify users when long operations complete?

## Architecture Decision

This will be a **separate application** from the Data Wrangler to maintain clean separation of concerns, avoid cross-repository complexity, and enable independent deployment cycles. The application will follow a microservices architecture with clear separation between the React frontend, Python backend, and ML processing services.

### Related Repositories
- **Research Pipeline Repository**: https://dev.hsrn.nyu.edu/ai-hub/research_pipeline.git
  - Local Path: `/Users/johndixon/AI_Hub/research_pipeline/`
  - Contains: Core Python ML modules (feature_imputer.py, eda.py, etc.)
  
- **Data Wrangler Repository**: https://github.com/dixonjohgithub/aihub_data_wrangler.git
  - Local Path: `/Users/johndixon/AI_Hub/aihub_data_wrangler/`
  - Produces: Export files that this app will import

### New Repository to Create
- **AI/ML Wrangler Repository**: `aihub_ai_ml_wrangler` (to be created)
  - Suggested URL: `https://github.com/[username]/aihub_ai_ml_wrangler.git`
  - Purpose: Standalone AI/ML analysis and imputation application
  - Interface: Similar design and workflow to AI Hub Data Wrangler

## Technology Stack

### Frontend (Matching Data Wrangler)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (same component library as Data Wrangler)
- **State Management**: React Context API (WorkflowContext pattern)
- **Charts**: Recharts + Plotly.js (for heatmaps)
- **Icons**: Lucide React
- **HTTP Client**: Axios with custom timeout configuration
- **File Handling**: react-dropzone
- **UI Components**: Reuse patterns from Data Wrangler (tables, progress bars, modals)

### Backend (Python for ML Integration)
- **Framework**: FastAPI (Python 3.10+) - Different from Data Wrangler's Node.js for better ML support
- **ASGI Server**: Uvicorn
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **ML Libraries**: Direct integration with research_pipeline modules
- **Task Queue**: Celery with Redis (for long-running operations)
- **File Storage**: Local filesystem with optional S3 support
- **API Documentation**: Auto-generated via FastAPI/Swagger
- **Progress Tracking**: Server-Sent Events (SSE) like Data Wrangler

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL (for job tracking and metadata)
- **Cache**: Redis (for task queue and caching)
- **Reverse Proxy**: Nginx

## Project Directory Structure

```
aihub_ai_ml_wrangler/
├── frontend/                    # Similar structure to Data Wrangler
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileImport/     # Reuse Data Wrangler patterns
│   │   │   │   ├── ImportDropzone.tsx
│   │   │   │   ├── FileValidator.tsx
│   │   │   │   └── ImportSummary.tsx
│   │   │   ├── DataPreview/    # Similar to Data Wrangler
│   │   │   │   ├── DataTable.tsx
│   │   │   │   ├── ColumnStatistics.tsx
│   │   │   │   └── MissingDataSummary.tsx
│   │   │   ├── Imputation/
│   │   │   │   ├── ImputationTable.tsx
│   │   │   │   ├── StrategySelector.tsx
│   │   │   │   ├── ParameterConfig.tsx
│   │   │   │   └── PreviewModal.tsx
│   │   │   ├── Correlation/
│   │   │   │   ├── CorrelationHeatmap.tsx
│   │   │   │   ├── ThresholdSlider.tsx
│   │   │   │   └── HighCorrelationsList.tsx
│   │   │   ├── Reports/
│   │   │   │   ├── ReportViewer.tsx
│   │   │   │   ├── ReportEditor.tsx
│   │   │   │   └── ExportOptions.tsx
│   │   │   ├── WorkflowSteps/  # Similar to Data Wrangler
│   │   │   │   └── StepIndicator.tsx
│   │   │   └── Common/          # Shared with Data Wrangler style
│   │   │       ├── ProgressBar.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       ├── Header.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   ├── pages/              # Similar page structure
│   │   │   ├── HomePage.tsx    # Landing page like Data Wrangler
│   │   │   ├── ImportPage.tsx
│   │   │   ├── ImputationPage.tsx
│   │   │   ├── CorrelationPage.tsx
│   │   │   ├── ReportsPage.tsx
│   │   │   └── ExportSuccessPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── fileService.ts
│   │   │   └── websocket.ts
│   │   ├── stores/
│   │   │   ├── dataStore.ts
│   │   │   ├── imputationStore.ts
│   │   │   └── correlationStore.ts
│   │   ├── types/
│   │   │   ├── data.types.ts
│   │   │   ├── imputation.types.ts
│   │   │   └── api.types.ts
│   │   ├── utils/
│   │   │   ├── validators.ts
│   │   │   ├── formatters.ts
│   │   │   └── constants.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── import.py
│   │   │   │   ├── imputation.py
│   │   │   │   ├── correlation.py
│   │   │   │   ├── reports.py
│   │   │   │   └── health.py
│   │   │   ├── dependencies.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   ├── models/
│   │   │   ├── schemas/
│   │   │   │   ├── import_schema.py
│   │   │   │   ├── imputation_schema.py
│   │   │   │   └── correlation_schema.py
│   │   │   └── database/
│   │   │       ├── base.py
│   │   │       └── models.py
│   │   ├── services/
│   │   │   ├── file_service.py
│   │   │   ├── imputation_service.py
│   │   │   ├── correlation_service.py
│   │   │   ├── report_service.py
│   │   │   └── pipeline_integration.py
│   │   ├── ml_modules/
│   │   │   ├── interactive_imputer.py
│   │   │   ├── correlation_analyzer.py
│   │   │   ├── report_generator.py
│   │   │   └── __init__.py
│   │   ├── tasks/
│   │   │   ├── celery_app.py
│   │   │   ├── imputation_tasks.py
│   │   │   └── report_tasks.py
│   │   ├── utils/
│   │   │   ├── file_handlers.py
│   │   │   ├── validators.py
│   │   │   └── helpers.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/
│   │   └── versions/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   └── .env.example
│
├── research_pipeline_integration/
│   ├── setup.py
│   ├── requirements.txt
│   └── README.md
│
├── docker/
│   ├── frontend/
│   │   └── Dockerfile
│   ├── backend/
│   │   └── Dockerfile
│   └── nginx/
│       ├── Dockerfile
│       └── nginx.conf
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .gitignore
├── .env.example
├── Makefile
└── README.md
```

## Implementation Phases

### Phase 1: Project Setup & Import Interface (Days 1-2)

#### 1.1 Repository Initialization
```bash
# Create new repository with consistent naming
mkdir aihub_ai_ml_wrangler
cd aihub_ai_ml_wrangler
git init

# Setup structure similar to Data Wrangler
mkdir -p packages/frontend packages/backend
mkdir -p docker research_pipeline_integration
mkdir -p sample_data notebooks

# Initialize as npm workspace (like Data Wrangler)
npm init -y
```

#### 1.2 Backend Setup (FastAPI)
```python
# backend/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2
pydantic==2.5.0
python-multipart==0.0.6
celery==5.3.4
redis==5.0.1
sqlalchemy==2.0.23
alembic==1.12.1
python-jose==3.3.0
passlib==1.7.4
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.1
```

#### 1.3 Frontend Setup (React + TypeScript)
```json
// frontend/package.json key dependencies
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "react-dropzone": "^14.2.3",
    "recharts": "^2.10.3",
    "plotly.js": "^2.27.1",
    "react-plotly.js": "^2.6.0",
    "lucide-react": "^0.294.0"
  }
}
```

#### 1.4 Import Interface Implementation (Similar to Data Wrangler)
- **File Upload Component**: Reuse Data Wrangler's drag-and-drop interface
- **Accepted Files**: 
  - `transformation_file.csv` (from Data Wrangler export)
  - `mapped_data.csv` (transformed data)
  - `metadata.json` (complete metadata with statistics)
- **UI Features**:
  - Progress bars during upload (like Data Wrangler)
  - File validation with error messages
  - Preview of imported data in tables
  - Summary cards showing data dimensions
- **Workflow Steps**: Similar visual step indicator as Data Wrangler

### Phase 2: Research Pipeline Integration (Days 3-4)

#### 2.1 Setup Research Pipeline as Git Submodule
```bash
# Add research_pipeline as submodule
git submodule add https://dev.hsrn.nyu.edu/ai-hub/research_pipeline.git research_pipeline_submodule
```

#### 2.2 Python Integration Service
```python
# backend/app/services/pipeline_integration.py
import sys
import os

# Add research_pipeline to Python path
RESEARCH_PIPELINE_PATH = "/Users/johndixon/AI_Hub/research_pipeline"
sys.path.insert(0, RESEARCH_PIPELINE_PATH)

from research_pipeline.feature_imputer import FeatureImputer
from research_pipeline.eda import EDA

class PipelineIntegration:
    """Bridge between FastAPI and research_pipeline modules"""
    
    def __init__(self):
        self.imputer = None
        self.eda = None
    
    def initialize_imputer(self, data_df, numeric_cols, binary_cols, categorical_cols):
        self.imputer = FeatureImputer(
            data=data_df,
            numeric_columns=numeric_cols,
            binary_columns=binary_cols,
            categorical_columns=categorical_cols
        )
    
    def initialize_eda(self, data_df):
        self.eda = EDA(data_df)
```

#### 2.3 Enhanced Research Pipeline Modules
Create new files in research_pipeline repository:
- `/Users/johndixon/AI_Hub/research_pipeline/research_pipeline/interactive_imputer.py`
- `/Users/johndixon/AI_Hub/research_pipeline/research_pipeline/correlation_analyzer.py`
- `/Users/johndixon/AI_Hub/research_pipeline/research_pipeline/report_generator.py`

### Phase 3: Interactive Imputation Configuration (Days 5-7)

#### 3.1 Backend API Endpoints
```python
# backend/app/api/endpoints/imputation.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any

router = APIRouter(prefix="/api/imputation", tags=["imputation"])

@router.post("/analyze-missing")
async def analyze_missing_data(file_id: str):
    """Analyze missing data patterns per column"""
    # Implementation here
    
@router.post("/set-strategy")
async def set_column_strategy(
    column: str,
    strategy: str,
    parameters: Dict[str, Any]
):
    """Set imputation strategy for specific column"""
    # Implementation here

@router.post("/preview")
async def preview_imputation(
    column: str,
    strategy: str,
    sample_size: int = 100
):
    """Preview imputation results without applying"""
    # Implementation here

@router.post("/apply-all")
async def apply_all_strategies(
    background_tasks: BackgroundTasks,
    strategies: List[Dict[str, Any]]
):
    """Apply all configured strategies and generate outputs"""
    # Implementation here
```

#### 3.2 Frontend Imputation Table Component
```typescript
// frontend/src/components/Imputation/ImputationTable.tsx
interface ImputationConfig {
  column: string;
  dataType: 'numeric' | 'categorical' | 'binary';
  missingCount: number;
  missingPercent: number;
  strategy: string;
  parameters: Record<string, any>;
}

export const ImputationTable: React.FC = () => {
  // Interactive table implementation
}
```

### Phase 4: Correlation Analysis (Days 8-9)

#### 4.1 Correlation Analyzer Module
```python
# backend/app/ml_modules/correlation_analyzer.py
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict

class CorrelationAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.correlation_matrix = None
    
    def calculate_correlation_matrix(self, method='pearson') -> pd.DataFrame:
        """Calculate correlation matrix for numeric columns"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        self.correlation_matrix = self.data[numeric_cols].corr(method=method)
        return self.correlation_matrix
    
    def export_correlation_csv(self, filepath: str):
        """Export correlation matrix in required format"""
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        # Format to match yrbs_2021_district_correlation.csv
        self.correlation_matrix.to_csv(filepath, index=True)
    
    def find_high_correlations(self, threshold: float = 0.8) -> List[Tuple[str, str, float]]:
        """Find variable pairs with correlation above threshold"""
        high_corrs = []
        matrix = self.correlation_matrix
        
        for i in range(len(matrix.columns)):
            for j in range(i+1, len(matrix.columns)):
                corr_value = abs(matrix.iloc[i, j])
                if corr_value >= threshold:
                    high_corrs.append((
                        matrix.columns[i],
                        matrix.columns[j],
                        matrix.iloc[i, j]
                    ))
        
        return sorted(high_corrs, key=lambda x: abs(x[2]), reverse=True)
    
    def recommend_feature_drops(self) -> Dict[str, List[str]]:
        """Recommend features to drop based on high correlations"""
        recommendations = {}
        high_corrs = self.find_high_correlations(0.9)
        
        for var1, var2, corr in high_corrs:
            if var1 not in recommendations:
                recommendations[var1] = []
            recommendations[var1].append(f"{var2} (corr={corr:.3f})")
        
        return recommendations
```

#### 4.2 Frontend Correlation Heatmap
```typescript
// frontend/src/components/Correlation/CorrelationHeatmap.tsx
import Plot from 'react-plotly.js';

export const CorrelationHeatmap: React.FC<{data: number[][], labels: string[]}> = ({data, labels}) => {
  return (
    <Plot
      data={[{
        type: 'heatmap',
        z: data,
        x: labels,
        y: labels,
        colorscale: 'RdBu',
        reversescale: true,
        zmin: -1,
        zmax: 1
      }]}
      layout={{
        title: 'Correlation Matrix',
        width: 800,
        height: 800
      }}
    />
  );
};
```

### Phase 5: Report Generation (Days 10-11)

#### 5.1 Report Generator Module
```python
# backend/app/ml_modules/report_generator.py
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
import json

class ReportGenerator:
    def __init__(self, original_data: pd.DataFrame, imputed_data: pd.DataFrame, 
                 imputation_config: Dict, correlation_results: Dict):
        self.original_data = original_data
        self.imputed_data = imputed_data
        self.imputation_config = imputation_config
        self.correlation_results = correlation_results
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report"""
        report = f"""# ML Analysis & Imputation Report

## Executive Summary
- **Dataset:** {self.imputation_config.get('filename', 'Unknown')}
- **Analysis Date:** {datetime.now().isoformat()}
- **Total Columns:** {len(self.original_data.columns)}
- **Columns with Missing Data:** {self._count_missing_columns()}
- **Total Missing Values:** {self.original_data.isnull().sum().sum()}
- **Imputation Strategies Used:** {self._list_strategies()}

## Missing Data Analysis

### Overview
Total missing values: {self.original_data.isnull().sum().sum()}
Percentage missing: {(self.original_data.isnull().sum().sum() / self.original_data.size * 100):.2f}%

### Per-Column Analysis
{self._generate_column_analysis_table()}

## Imputation Details
{self._generate_imputation_details()}

## Correlation Analysis
{self._generate_correlation_section()}

## Quality Metrics
{self._generate_quality_metrics()}

## Recommendations
{self._generate_recommendations()}

## Appendix: Technical Details
- **Python Version:** 3.10+
- **Libraries Used:** pandas, scikit-learn, numpy
- **Random Seed:** 42
"""
        return report
    
    def generate_metadata_json(self) -> Dict:
        """Generate metadata JSON with all transformation details"""
        metadata = {
            "analysis_id": self._generate_uuid(),
            "timestamp": datetime.now().isoformat(),
            "dataset": {
                "source_file": self.imputation_config.get('filename'),
                "rows": len(self.original_data),
                "columns": len(self.original_data.columns),
                "size_mb": self._calculate_size()
            },
            "missing_data": self._generate_missing_summary(),
            "imputation_strategies": self._generate_strategy_summary(),
            "correlations": self._generate_correlation_summary(),
            "outputs": self._generate_output_summary(),
            "configuration": {
                "random_seed": 42,
                "validation_split": 0.2,
                "quality_checks": True
            }
        }
        return metadata
```

### Phase 6: Testing & Deployment (Days 12-15)

#### 6.1 Docker Configuration
```dockerfile
# docker/backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone research_pipeline
RUN git clone https://dev.hsrn.nyu.edu/ai-hub/research_pipeline.git /research_pipeline

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### 6.2 Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mlanalysis
      - REDIS_URL=redis://redis:6379
      - RESEARCH_PIPELINE_PATH=/research_pipeline
    volumes:
      - ./backend:/app
      - /Users/johndixon/AI_Hub/research_pipeline:/research_pipeline:ro
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mlanalysis
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    build:
      context: ./docker/nginx
    ports:
      - "80:80"
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

## Workflow Design (Mirroring Data Wrangler UX)

### User Journey

1. **Import Phase** (Similar to Data Wrangler Import)
   - Landing page with workflow visualization
   - Drag-and-drop file upload area
   - Progress tracking during file processing
   - Data preview tables with virtualization
   - Column statistics sidebar

2. **Configuration Phase** (Like Data Wrangler Prepare)
   - Interactive table with inline editing
   - Column-by-column configuration
   - Batch operations for multiple columns
   - Real-time preview of changes
   - Save/load configuration templates

3. **Analysis Phase** (Processing with Progress)
   - Progress dialog with task breakdown
   - Time estimates for long operations
   - Cancel/pause capabilities
   - Real-time status updates via SSE

4. **Report Phase** (Similar to Data Wrangler Export)
   - Export success page with summary
   - Multiple download options
   - Bundle all files as ZIP
   - Copy shareable links

### API Workflow
```
POST /api/import/upload
  ├── Validates files
  ├── Stores in database
  └── Returns session_id

POST /api/imputation/analyze-missing
  ├── Analyzes patterns
  └── Returns missing data summary

POST /api/imputation/set-strategy
  ├── Configures column strategy
  └── Returns confirmation

POST /api/imputation/preview
  ├── Generates preview
  └── Returns sample results

POST /api/imputation/apply-all
  ├── Applies all strategies
  ├── Triggers background job
  └── Returns job_id

GET /api/correlation/matrix
  ├── Calculates correlations
  └── Returns matrix data

POST /api/reports/generate
  ├── Creates all outputs
  └── Returns download links
```

## Output Files

### 1. Imputed Data CSV
- Filename: `[original_name]_imputed.csv`
- Contains: Complete dataset with all missing values filled
- Format: Same structure as input mapped_data.csv

### 2. Correlation Matrix CSV
- Filename: `[original_name]_correlation.csv`
- Format: Square matrix with variable names as row/column headers
- Values: Pearson correlation coefficients

### 3. Transformation Report
- Filename: `[original_name]_ml_report.md`
- Contains: Comprehensive markdown report
- Includes: Visualizations, statistics, recommendations

### 4. Metadata JSON
- Filename: `[original_name]_ml_metadata.json`
- Contains: Complete audit trail of all transformations
- Purpose: Reproducibility and documentation

## Development Commands

```bash
# Clone and setup
git clone [new_repo_url] aihub_ai_ml_wrangler
cd aihub_ai_ml_wrangler

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev

# Docker setup
docker-compose up -d

# Run tests
pytest backend/tests/
npm test --prefix frontend/

# Database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"
```

## Environment Variables

```bash
# .env.example

# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/ai_ml_wrangler
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
RESEARCH_PIPELINE_PATH=/Users/johndixon/AI_Hub/research_pipeline
UPLOAD_FOLDER=/tmp/ml_analysis_uploads
MAX_UPLOAD_SIZE=104857600  # 100MB

# Frontend (in frontend/.env)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Success Metrics

- ✅ Successfully imports Data Wrangler export files
- ✅ Per-column imputation strategy configuration
- ✅ Real-time preview of imputation results
- ✅ Correlation matrix generation matching required format
- ✅ Comprehensive markdown report with visualizations
- ✅ Complete metadata tracking of all transformations
- ✅ < 3 second response for preview operations
- ✅ < 30 second processing for 100k row datasets
- ✅ 100% test coverage for critical paths
- ✅ Docker deployment ready

## Next Steps

1. Create new GitHub repository: `aihub_ai_ml_wrangler`
2. Initialize project structure matching Data Wrangler patterns
3. Copy and adapt UI components from Data Wrangler
4. Set up Python backend with FastAPI
5. Implement Phase 1: Import interface (reuse Data Wrangler components)
6. Integrate research_pipeline modules
7. Build interactive imputation UI (similar table patterns)
8. Add correlation analysis features
9. Implement report generation
10. Complete testing suite
11. Deploy to production

## Key Features & Design Principles

1. **Consistent User Experience**: Interface mirrors Data Wrangler for familiarity
2. **Standalone Architecture**: Clean separation from Data Wrangler
3. **File-Based Workflow**: Seamless import of Data Wrangler exports
4. **Python-Native Backend**: Optimized for ML/AI operations
5. **Interactive Configuration**: Same inline editing patterns as Data Wrangler
6. **Progress Tracking**: Similar progress bars and status messages
7. **Component Reuse**: Leverage Data Wrangler's UI components where possible
8. **Production Ready**: Docker-based deployment from day one

## UI/UX Consistency with Data Wrangler

### Shared Design Elements
- **Color Scheme**: Same Tailwind CSS classes and color palette
- **Layout**: Similar header, sidebar, and content area structure
- **Navigation**: Step-based workflow with visual indicators
- **Tables**: Same virtualized tables with inline editing
- **Modals**: Consistent modal patterns for editing and configuration
- **Progress Indicators**: Same progress bar styles and animations
- **Error Handling**: Similar error messages and validation feedback
- **Success States**: Export success page pattern

### Component Library
- Copy common components from Data Wrangler:
  - FileDropzone
  - DataTable
  - ProgressBar
  - WorkflowSteps
  - Header/Layout
  - Export dialogs

## Timeline

| Week | Phase | Deliverables |
|------|-------|-------------|
| Week 1 | Setup & Import | Repository created, import interface working |
| Week 2 | Imputation & Analysis | Interactive configuration, correlation analysis |
| Week 3 | Reports & Testing | Report generation, full test coverage, deployment |

## References

- Research Pipeline Documentation: `/Users/johndixon/AI_Hub/research_pipeline/README.md`
- Data Wrangler Export Format: `/Users/johndixon/AI_Hub/aihub_data_wrangler/docs/export-format.md`
- FastAPI Documentation: https://fastapi.tiangolo.com/
- React + Vite Setup: https://vitejs.dev/guide/