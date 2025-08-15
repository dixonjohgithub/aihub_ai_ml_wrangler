# AI Hub ML Wrangler Backend

## Overview

This backend infrastructure provides the core database, caching, and task processing capabilities for the AI Hub ML Wrangler application. Built with FastAPI, PostgreSQL, Redis, and Celery for robust, scalable ML data processing.

## Architecture

### Core Technologies

- **FastAPI**: Modern, async web framework for APIs
- **PostgreSQL 15+**: Primary database with async operations
- **Redis 7+**: Caching and task queue backend
- **SQLAlchemy 2.0+**: Modern async ORM
- **Celery 5.3+**: Distributed task queue for background processing
- **Alembic**: Database migration management

### Key Components

#### Database Layer
- **Models**: User, Dataset, Job entities with relationships
- **Connection Pooling**: Optimized database connections (10 base, 20 overflow)
- **Async Operations**: Full async/await support throughout

#### Cache Layer
- **Redis Service**: High-level caching with error handling
- **Session Management**: Connection pooling and retry logic
- **Data Serialization**: JSON serialization with type safety

#### Task Processing
- **Celery Workers**: Background ML task processing
- **Task Routing**: Queue-based task distribution
- **Progress Tracking**: Real-time task progress updates

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 15+
- Redis 7+

### Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   ```

3. **Database Setup**
   ```bash
   # Initialize Alembic
   alembic init migrations
   
   # Create initial migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migrations
   alembic upgrade head
   ```

4. **Start Services**
   ```bash
   # Start FastAPI server
   python main.py
   
   # Start Celery worker (in separate terminal)
   celery -A config.celery worker --loglevel=info
   
   # Start Celery beat (for scheduled tasks)
   celery -A config.celery beat --loglevel=info
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://user:password@localhost:5432/aihub_db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/0` |
| `SECRET_KEY` | Application secret key | Required |
| `DEBUG` | Debug mode | `false` |

### Database Configuration

- **Connection Pool**: 10 base connections, 20 overflow
- **Pool Recycle**: 1 hour (3600 seconds)
- **Pre-ping**: Enabled for connection health checks

### Celery Configuration

- **Task Queues**:
  - `ml_analysis`: Dataset analysis tasks
  - `data_processing`: Data imputation and correlation tasks
- **Worker Settings**: 1000 tasks per child, late acknowledgment
- **Monitoring**: Task tracking and progress updates enabled

## API Endpoints

### Health Checks

- `GET /health` - Overall system health
- `GET /health/database` - Database connectivity
- `GET /health/redis` - Redis connectivity  
- `GET /health/celery` - Celery worker status

### Documentation

- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Database Models

### User
- **Fields**: id, username, email, full_name, is_active, is_admin
- **Relationships**: One-to-many with Dataset and Job

### Dataset
- **Fields**: id, name, description, file_path, file_size, metadata, analysis_results
- **Relationships**: Many-to-one with User, one-to-many with Job

### Job
- **Fields**: id, task_id, job_type, status, progress, parameters, results
- **Relationships**: Many-to-one with User and Dataset
- **Types**: DATASET_ANALYSIS, DATA_IMPUTATION, CORRELATION_ANALYSIS, MODEL_TRAINING
- **Statuses**: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED

## Background Tasks

### Dataset Analysis (`analyze_dataset`)
- Analyzes dataset structure and statistics
- Identifies missing values and data types
- Generates summary statistics for numeric columns
- Queue: `ml_analysis`

### Data Imputation (`impute_missing_data`)
- Performs missing value imputation
- Supports multiple imputation methods (mean, median, mode)
- Validates results and provides summary
- Queue: `data_processing`

### Correlation Analysis (`calculate_correlations`)
- Calculates correlation matrices for numeric data
- Supports Pearson and Spearman correlation methods
- Identifies strong correlations and patterns
- Queue: `data_processing`

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Test Structure
- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: Database and Redis integration
- **Task Tests**: Celery task functionality
- **Coverage**: Comprehensive test coverage across all layers

## Development

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Tasks
1. Define task in `backend/tasks/ml_tasks.py`
2. Update task routing in `config/celery.py`
3. Add task tests in `tests/test_celery_tasks.py`
4. Update documentation

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints throughout
- Comprehensive error handling
- Async/await patterns for I/O operations
- Comprehensive logging

## Monitoring

### Health Monitoring
- Application health endpoints for load balancer integration
- Service-specific health checks for debugging
- Comprehensive error reporting and logging

### Performance
- Connection pooling for database optimization
- Redis connection pooling for cache performance
- Celery worker monitoring and scaling
- Task progress tracking for user feedback

## Security

### Best Practices
- Environment-based configuration
- No hardcoded secrets or credentials
- Secure database connection handling
- Input validation and sanitization
- Proper error handling without information leakage

### Authentication Ready
- User model with authentication fields
- Admin role support
- Extensible for JWT or session-based auth

## Production Deployment

### Requirements
- PostgreSQL database with connection pooling
- Redis cluster for high availability
- Multiple Celery workers for task processing
- Load balancer for FastAPI instances
- Monitoring and logging infrastructure

### Scaling
- Horizontal scaling of FastAPI instances
- Multiple Celery workers across machines
- Database read replicas for heavy read workloads
- Redis clustering for cache scaling