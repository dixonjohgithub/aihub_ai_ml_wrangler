# Docker Deployment Guide

This guide explains how to deploy the AI Hub AI/ML Wrangler application using Docker containers.

## Prerequisites

- Docker 20.0+ 
- Docker Compose 2.0+
- 4GB+ RAM available for containers
- 10GB+ disk space

## Quick Start

### Development Environment

1. **Clone and prepare environment**:
```bash
git clone https://github.com/dixonjohgithub/aihub_ai_ml_wrangler.git
cd aihub_ai_ml_wrangler
cp .env.example .env
```

2. **Configure environment variables** in `.env`:
```bash
# Required - Set your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Security - Change these in production
POSTGRES_PASSWORD=your_secure_postgres_password
REDIS_PASSWORD=your_secure_redis_password
SECRET_KEY=your_super_secret_key_here
```

3. **Start development environment**:
```bash
npm run docker:dev
# or directly: docker-compose -f docker-compose.dev.yml up
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production Environment

1. **Prepare environment**:
```bash
cp .env.example .env
# Configure production values in .env
```

2. **Start production environment**:
```bash
npm run docker:prod
# or directly: docker-compose up -d
```

3. **Access via Nginx proxy**:
- Application: http://localhost (port 80)

## Architecture Overview

### Services

- **nginx**: Reverse proxy and load balancer
- **frontend**: React/TypeScript application (Vite)
- **backend**: FastAPI Python application
- **postgres**: PostgreSQL 15 database
- **redis**: Redis cache and message broker
- **celery-worker**: Background task processor
- **celery-beat**: Task scheduler

### Network Architecture

```
Internet → Nginx (80/443) → Frontend (3000) & Backend (8000)
                         ↓
                    PostgreSQL (5432) & Redis (6379)
                         ↓
                    Celery Workers & Beat
```

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |
| `POSTGRES_PASSWORD` | PostgreSQL database password | `secure_password` |
| `REDIS_PASSWORD` | Redis cache password | `secure_password` |
| `SECRET_KEY` | Application secret key | `your_secret_key` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_DB` | `aihub_ml_wrangler` | Database name |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Application log level |

## Docker Commands

### Build and Start
```bash
# Development with hot reload
docker-compose -f docker-compose.dev.yml up --build

# Production optimized
docker-compose up --build -d

# Build specific service
docker-compose build backend
```

### Management
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f --tail=100 celery-worker

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d aihub_ml_wrangler

# Scale services
docker-compose up --scale celery-worker=3
```

### Maintenance
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (destructive)
docker-compose down -v

# Rebuild without cache
docker-compose build --no-cache
```

## Health Checks

### Manual Health Checks
```bash
# Overall health check
./scripts/health-check.sh

# Individual services
./scripts/health-check.sh backend
./scripts/health-check.sh frontend
./scripts/health-check.sh postgres
./scripts/health-check.sh redis
```

### Health Check Endpoints
- Frontend: `http://localhost:3000/health`
- Backend: `http://localhost:8000/health`
- Nginx: `http://localhost/health`

## Data Persistence

### Volumes

- `postgres_data_dev/prod`: PostgreSQL data
- `redis_data_dev/prod`: Redis data persistence

### Backups

```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres aihub_ml_wrangler > backup.sql

# Database restore
docker-compose exec -T postgres psql -U postgres aihub_ml_wrangler < backup.sql
```

## Performance Tuning

### Resource Limits (Production)

- **Backend**: 2GB limit, 1GB reservation
- **Celery Worker**: 4GB limit, 2GB reservation  
- **Frontend**: 512MB limit, 256MB reservation

### Scaling

```bash
# Scale Celery workers
docker-compose up --scale celery-worker=4

# Scale with Docker Swarm (advanced)
docker stack deploy -c docker-compose.yml aihub-stack
```

## Troubleshooting

### Common Issues

1. **Port conflicts**:
```bash
# Check port usage
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Use different ports
FRONTEND_PORT=3001 docker-compose up
```

2. **Permission issues**:
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./data
```

3. **Out of memory**:
```bash
# Monitor resource usage
docker stats
docker system df
docker system prune
```

4. **Database connection errors**:
```bash
# Check database logs
docker-compose logs postgres

# Verify connectivity
docker-compose exec backend python -c "import psycopg2; print('DB OK')"
```

### Debug Mode

```bash
# Enable debug logging
echo "DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
docker-compose restart
```

## Security Considerations

### Production Security

1. **Change default passwords** in `.env`
2. **Use environment-specific secrets**
3. **Enable SSL/TLS** with certificates
4. **Configure firewall rules**
5. **Regular security updates**

### SSL/TLS Setup

```bash
# Place SSL certificates in ./ssl/
mkdir ssl
cp your-cert.pem ssl/
cp your-key.pem ssl/

# Update nginx configuration for HTTPS
# Uncomment SSL sections in nginx/nginx.conf
```

## Monitoring

### Container Health
```bash
# View container status
docker-compose ps

# Resource monitoring
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Application Logs
```bash
# Application logs
docker-compose logs -f backend | grep ERROR
docker-compose logs -f celery-worker | grep CRITICAL

# Nginx access logs
docker-compose logs nginx | grep -v "health"
```

## Development Workflow

### Hot Reload Development

1. **Frontend changes**: Automatically reloaded via Vite HMR
2. **Backend changes**: Automatically reloaded via uvicorn --reload
3. **Database schema**: Use Alembic migrations

### Testing in Docker

```bash
# Run tests in containers
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Migration and Deployment

### Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Zero-Downtime Deployment

```bash
# Blue-green deployment pattern
docker-compose -f docker-compose.blue.yml up -d
# Test new version
docker-compose -f docker-compose.green.yml down
```

## Support

- Check container logs: `docker-compose logs [service]`
- Health check script: `./scripts/health-check.sh`
- GitHub Issues: [Project Issues](https://github.com/dixonjohgithub/aihub_ai_ml_wrangler/issues)

---

For more information, see the main [README.md](../README.md) and [Development Guide](./development.md).