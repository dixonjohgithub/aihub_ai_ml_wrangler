# AI Hub AI/ML Wrangler - Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Research Pipeline Integration](#research-pipeline-integration)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.9+ (3.10 recommended)
- **Node.js**: 16+ (18 recommended)
- **PostgreSQL**: 13+
- **Redis**: 6+
- **Git**: 2.30+
- **Docker** (optional): 20.10+ with Docker Compose

### Required Python Packages
- FastAPI
- SQLAlchemy
- Pandas
- NumPy
- Scikit-learn
- Dask
- PyArrow

### Required Node Packages
- React 18+
- TypeScript 4+
- Vite
- Tailwind CSS

## Project Structure

```
aihub_ai_ml_wrangler/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # Request validation
│   │   └── core/           # Core utilities
│   ├── tests/              # Test suites
│   ├── requirements.txt    # Python dependencies
│   └── main.py            # Application entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── pages/        # Page components
│   ├── package.json       # Node dependencies
│   └── vite.config.ts    # Vite configuration
├── docker/                # Docker configurations
├── docs/                  # Documentation
└── RESEARCH_PIPELINE_UPDATES.md  # Research pipeline changes
```

## Backend Setup

### 1. Clone the Repository

```bash
git clone https://github.com/dixonjohgithub/aihub_ai_ml_wrangler.git
cd aihub_ai_ml_wrangler
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Install additional performance packages
pip install dask[complete] pyarrow memory-profiler joblib
```

### 4. Set Up PostgreSQL Database

```bash
# Create database
createdb aihub_wrangler

# Run migrations
alembic upgrade head
```

### 5. Set Up Redis

```bash
# On macOS:
brew install redis
brew services start redis

# On Ubuntu/Debian:
sudo apt-get install redis-server
sudo systemctl start redis

# On Windows:
# Download from https://redis.io/download
```

### 6. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost/aihub_wrangler
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost/aihub_wrangler

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI API (optional)
OPENAI_API_KEY=your_openai_api_key_here

# Security
SECRET_KEY=your_secret_key_here_minimum_32_characters
ALGORITHM=HS256

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# File Upload
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=[".csv", ".json", ".xlsx", ".xls", ".parquet", ".txt", ".tsv"]

# Performance
CHUNK_SIZE=10000
MAX_WORKERS=4
MEMORY_LIMIT_GB=4.0
USE_DASK=true
CACHE_DIR=.cache

# Rate Limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

### 7. Run Backend Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Node Dependencies

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Or using yarn
yarn install
```

### 2. Configure Frontend Environment

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AI Hub AI/ML Wrangler
VITE_APP_VERSION=1.0.0
VITE_ENABLE_MOCK_DATA=false
```

### 3. Run Frontend Development Server

```bash
# Development mode with hot reload
npm run dev

# Or using yarn
yarn dev
```

The frontend will be available at: `http://localhost:5173`

### 4. Build for Production

```bash
# Build production bundle
npm run build

# Preview production build
npm run preview
```

## Research Pipeline Integration

### 1. Clone Research Pipeline Repository

```bash
# Navigate to parent directory
cd /Users/johndixon/AI_Hub/

# Clone research pipeline (if not already present)
git clone [research_pipeline_repo_url] research_pipeline
cd research_pipeline
```

### 2. Install Research Pipeline Dependencies

```bash
# Create virtual environment for research pipeline
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### 3. Configure Research Pipeline Path

The integration is automatic, but ensure the path is correct in:
`backend/app/core/research_pipeline_integration.py`

```python
RESEARCH_PIPELINE_PATH = Path("/Users/johndixon/AI_Hub/research_pipeline")
```

### 4. Verify Research Pipeline Integration

```bash
# Test the integration
cd /Users/johndixon/AI_Hub/aihub_ai_ml_wrangler/backend
python -c "from app.core.research_pipeline_integration import FeatureImputer, EDA; print('Research pipeline integrated successfully!')"
```

## Docker Deployment

### 1. Build Docker Images

```bash
# From project root
cd /Users/johndixon/AI_Hub/aihub_ai_ml_wrangler

# Build all services
docker-compose build
```

### 2. Create Docker Environment File

Create `.env.docker` in the project root:

```env
# PostgreSQL
POSTGRES_USER=aihub_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=aihub_wrangler

# Redis
REDIS_PASSWORD=redis_password

# Application
SECRET_KEY=your_secret_key_here_minimum_32_characters
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Environment Configuration

### Production Environment Variables

For production deployment, set these additional variables:

```env
# Application
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Security
ALLOWED_HOSTS=["your-domain.com"]
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# Performance
WORKERS=4
THREADS=2
WORKER_CONNECTIONS=1000
```

## Running the Application

### Complete Startup Sequence

1. **Start Database and Cache**:
```bash
# Start PostgreSQL
pg_ctl start

# Start Redis
redis-server
```

2. **Start Backend Services**:
```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head

# Start Celery worker (for background tasks)
celery -A app.tasks worker --loglevel=info &

# Start FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. **Start Frontend**:
```bash
cd frontend

# Start development server
npm run dev
```

### Using the Application

1. **Access the Application**:
   - Open browser to `http://localhost:5173`
   - API documentation at `http://localhost:8000/docs`

2. **Upload Data**:
   - Click "Upload Dataset" button
   - Select CSV, JSON, or Excel file
   - Files are validated and processed automatically

3. **Data Imputation**:
   - Select columns with missing values
   - Choose imputation strategy (mean, median, KNN, MICE, etc.)
   - Preview results before applying

4. **Correlation Analysis**:
   - Select correlation method (Pearson, Spearman, Kendall)
   - View correlation heatmap
   - Export correlation matrix

5. **Generate Reports**:
   - Select report sections
   - Choose export format (Markdown, HTML, PDF)
   - Download comprehensive analysis report

## Testing

### Run Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_imputation_service.py

# Run integration tests
pytest tests/integration/
```

### Run Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Performance Testing

```bash
cd backend/tests

# Run performance tests
pytest test_performance.py -v

# Load testing with locust
locust -f locustfile.py --host=http://localhost:8000
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
# Ensure DATABASE_URL is correct
```

#### 2. Redis Connection Error
```bash
# Check Redis is running
redis-cli ping

# Should return "PONG"
```

#### 3. Import Error for Research Pipeline
```bash
# Verify path in research_pipeline_integration.py
# Ensure research_pipeline is installed:
cd /Users/johndixon/AI_Hub/research_pipeline
pip install -e .
```

#### 4. CORS Issues
```bash
# Add frontend URL to BACKEND_CORS_ORIGINS in .env
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

#### 5. File Upload Size Limit
```bash
# Increase MAX_FILE_SIZE_MB in .env
MAX_FILE_SIZE_MB=500
```

#### 6. Memory Issues with Large Datasets
```bash
# Enable Dask for large files
USE_DASK=true

# Increase memory limit
MEMORY_LIMIT_GB=8.0

# Reduce chunk size
CHUNK_SIZE=5000
```

### Logs and Debugging

#### View Backend Logs
```bash
# Application logs
tail -f backend/logs/app.log

# Celery logs
tail -f backend/logs/celery.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-13-main.log
```

#### Enable Debug Mode
```bash
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Monitor Performance
```bash
# Check memory usage
htop

# Monitor database connections
pg_stat_activity

# Redis monitoring
redis-cli monitor
```

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Frontend Dev Tools**: React Developer Tools Chrome Extension
- **Database Admin**: pgAdmin or DBeaver
- **Redis GUI**: RedisInsight

## Support

For issues or questions:
1. Check the [GitHub Issues](https://github.com/dixonjohgithub/aihub_ai_ml_wrangler/issues)
2. Review [RESEARCH_PIPELINE_UPDATES.md](./RESEARCH_PIPELINE_UPDATES.md) for ML functionality
3. See [tasks.md](./tasks.md) for feature status

## Security Notes

- Never commit `.env` files to version control
- Use strong passwords for database and Redis
- Keep OpenAI API key secure
- Enable HTTPS in production
- Regularly update dependencies
- Use rate limiting to prevent abuse

## Production Deployment Checklist

- [ ] Set ENVIRONMENT=production
- [ ] Configure proper database credentials
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring (Sentry, New Relic, etc.)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Load test the application
- [ ] Review security headers
- [ ] Document API endpoints

---

**Version**: 1.0.0  
**Last Updated**: 2025-08-15  
**Author**: AI Hub Team