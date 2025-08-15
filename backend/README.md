# AI Hub AI/ML Wrangler Backend

## Overview

FastAPI backend for the AI Hub AI/ML Wrangler application, providing database infrastructure, background task processing, and API endpoints for data imputation and analysis.

## Architecture

### Core Components

- **FastAPI Application**: Modern Python web framework with automatic API documentation
- **PostgreSQL Database**: Primary data storage with SQLAlchemy ORM
- **Redis Cache**: Caching and Celery task broker
- **Celery Workers**: Background task processing for data analysis and imputation
- **Alembic Migrations**: Database schema version control

### Technology Stack

- **Python 3.10+** - Core runtime
- **FastAPI** - Web framework with automatic OpenAPI documentation
- **SQLAlchemy 2.0+** - Modern async ORM with relationship mapping
- **PostgreSQL 15+** - Primary database with connection pooling
- **Redis 7+** - Cache and task broker
- **Celery 5.3+** - Distributed task queue
- **Alembic** - Database migration management
- **Pytest** - Comprehensive testing framework

## Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 15+
- Redis 7+
- Virtual environment tool (venv, conda, etc.)

### Installation

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize database**
```bash
# Run migrations
alembic upgrade head
```

### Running the Application

**Development Server:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Celery Worker:**
```bash
celery -A celery_app.celery_app worker --loglevel=info
```

**Celery Beat (Optional - for scheduled tasks):**
```bash
celery -A celery_app.celery_app beat --loglevel=info
```

### API Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aihub_ml_wrangler
DB_USER=postgres
DB_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application
SECRET_KEY=your-secret-key-here
DEBUG=false
OPENAI_API_KEY=your-openai-key
```

### Database Configuration

The application uses SQLAlchemy with connection pooling:

- **Pool Size**: 10 connections (configurable)
- **Max Overflow**: 20 additional connections
- **Pool Pre-ping**: Enabled for connection health checks
- **Pool Recycle**: 1 hour connection refresh

### Redis Configuration

Redis is used for:
- Application caching
- Celery task broker
- Session storage
- Task result backend

## Database Models

### Core Entities

**User Model:**
- Authentication and profile management
- Relationships to datasets and jobs
- Email verification and login tracking

**Dataset Model:**
- File metadata and processing status
- Column information and analysis results
- Processing configuration storage

**Job Model:**
- Background task tracking
- Progress monitoring and result storage
- Celery task integration

### Model Features

- **UUID Primary Keys**: For security and distribution
- **Automatic Timestamps**: Created/updated tracking
- **JSON Fields**: Flexible metadata storage
- **Relationship Mapping**: Complete foreign key relationships
- **Status Tracking**: Enumerated status fields

## Background Tasks

### Celery Configuration

**Task Queues:**
- `imputation`: Data imputation tasks
- `analysis`: Dataset analysis tasks
- `default`: General purpose tasks

**Task Types:**
- **Analysis Tasks**: Missing data pattern analysis
- **Imputation Tasks**: Data imputation processing
- **Correlation Tasks**: Correlation matrix generation
- **Maintenance Tasks**: Cleanup and health checks

**Features:**
- Task progress tracking
- Result persistence
- Error handling and retry logic
- Task routing and priorities
- Monitoring and logging

### Task Examples

```python
# Analyze dataset
from app.tasks import analyze_dataset_task
result = analyze_dataset_task.delay(dataset_id, job_id)

# Process imputation
from app.tasks import process_imputation_task
result = process_imputation_task.delay(dataset_id, job_id, config)
```

## API Endpoints

### Health and Admin

- `GET /health` - Application health check
- `GET /admin/database/info` - Database information
- `POST /admin/database/initialize` - Initialize database
- `POST /admin/database/reset` - Reset database
- `GET /admin/redis/info` - Redis information

### Future API Endpoints

The following endpoints will be implemented in subsequent tasks:

- User authentication and management
- Dataset upload and management
- Job creation and monitoring
- Analysis and imputation endpoints

## Development

### Database Migrations

**Create Migration:**
```bash
alembic revision --autogenerate -m "Description"
```

**Run Migrations:**
```bash
alembic upgrade head
```

**Rollback Migration:**
```bash
alembic downgrade -1
```

### Testing

**Run All Tests:**
```bash
pytest
```

**Run with Coverage:**
```bash
pytest --cov=app --cov-report=html
```

**Run Specific Test File:**
```bash
pytest app/tests/test_models.py -v
```

### Code Quality

**Format Code:**
```bash
black app/
```

**Sort Imports:**
```bash
isort app/
```

**Lint Code:**
```bash
flake8 app/
```

**Type Checking:**
```bash
mypy app/
```

## Services

### Database Service

Provides high-level database operations:
- Health checks and monitoring
- Table management
- Query execution utilities
- Size and performance metrics

### Cache Service

Redis integration with:
- Async operations
- JSON serialization
- TTL management
- Connection pooling
- Error handling

## Monitoring and Logging

### Logging Configuration

- **Development**: DEBUG level with console output
- **Production**: INFO level with structured logging
- **Task Logging**: Separate Celery worker logs

### Health Monitoring

- Database connection health
- Redis connection status
- Table existence verification
- Connection pool monitoring

## Security

### Best Practices

- Environment-based configuration
- No hardcoded credentials
- Password hashing with bcrypt
- JWT token authentication (planned)
- CORS configuration
- Input validation with Pydantic

### Database Security

- Connection pooling with limits
- Prepared statements via SQLAlchemy
- No raw SQL execution without validation
- Foreign key constraints

## Deployment

### Docker Configuration

The application is designed for containerized deployment:

```dockerfile
# Example Dockerfile structure
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

- PostgreSQL database server
- Redis server
- Environment variables configuration
- SSL/TLS for production

### Scaling Considerations

- Multiple Celery workers
- Redis clustering
- Database read replicas
- Load balancing

## Troubleshooting

### Common Issues

**Database Connection:**
```bash
# Check database status
curl http://localhost:8000/health

# Verify connection settings
python -c "from app.database import check_database_connection; print(check_database_connection())"
```

**Redis Connection:**
```bash
# Test Redis connection
redis-cli ping

# Check Redis info
curl http://localhost:8000/admin/redis/info
```

**Celery Tasks:**
```bash
# Monitor Celery workers
celery -A celery_app.celery_app inspect active

# Check task status
celery -A celery_app.celery_app inspect stats
```

### Debug Mode

Enable debug mode for development:
```bash
export DEBUG=true
uvicorn app.main:app --reload --port 8000
```

## Contributing

1. Follow the project's coding standards
2. Write tests for new functionality
3. Update documentation as needed
4. Use the TDD workflow from CLAUDE.md
5. Ensure all tests pass before submitting

## Related Documentation

- [Project Plan](../projectplan.md)
- [Development Guidelines](../CLAUDE.md)
- [API Documentation](http://localhost:8000/docs)
- [Frontend Documentation](../frontend/README.md)