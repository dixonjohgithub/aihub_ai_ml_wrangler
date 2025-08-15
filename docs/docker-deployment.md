# Docker Deployment Guide

## AI Hub ML Wrangler - Docker Configuration

This document provides comprehensive instructions for deploying the AI Hub ML Wrangler application using Docker containers.

## 🏗️ Architecture

The application consists of the following services:
- **Frontend**: React/TypeScript with Vite (development) or Nginx (production)
- **Backend**: FastAPI Python application
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Reverse Proxy**: Nginx (production only)
- **Background Workers**: Celery workers and scheduler

## 🚀 Quick Start

### Development Environment

1. **Start all services with hot reload:**
   ```bash
   npm run docker:dev
   # or
   docker-compose -f docker-compose.dev.yml up
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432
   - Redis: localhost:6379

### Production Environment

1. **Configure environment:**
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod with your production values
   ```

2. **Start production services:**
   ```bash
   npm run docker:prod
   # or
   docker-compose up -d
   ```

3. **Access the application:**
   - Application: http://localhost
   - Health check: http://localhost/health
   - Flower (monitoring): http://localhost:5555

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- 4GB+ RAM available
- 10GB+ disk space

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to create your environment file:

```bash
# For development
cp .env.example .env.dev

# For production
cp .env.example .env.prod
```

**Key Variables:**
- `POSTGRES_PASSWORD`: Database password
- `REDIS_PASSWORD`: Redis authentication
- `SECRET_KEY`: Application secret key
- `WORKERS`: Number of backend workers

### Service Configuration

#### Frontend (React/Vite)
- **Development**: Hot reload enabled on port 3000
- **Production**: Optimized build served by Nginx
- **Features**: TypeScript, Vite, React Router

#### Backend (FastAPI)
- **Port**: 8000 (internal)
- **Features**: Auto-reload, OpenAPI docs, health checks
- **Dependencies**: PostgreSQL, Redis, Celery

#### Database (PostgreSQL)
- **Version**: PostgreSQL 15 Alpine
- **Port**: 5432
- **Features**: Automatic initialization, health checks
- **Data**: Persistent volumes

#### Cache (Redis)
- **Version**: Redis 7 Alpine
- **Port**: 6379
- **Features**: Authentication, memory optimization
- **Usage**: Session storage, Celery broker

#### Reverse Proxy (Nginx - Production Only)
- **Port**: 80/443
- **Features**: Rate limiting, security headers, SSL ready
- **Routes**: Frontend (/*), API (/api/*)

#### Background Workers (Celery)
- **Workers**: Configurable concurrency
- **Scheduler**: Beat for periodic tasks
- **Monitoring**: Flower web interface
- **Queues**: data_processing, notifications, maintenance

## 🚀 Deployment Commands

### Development
```bash
# Start development environment
npm run docker:dev

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Production
```bash
# Build images
npm run docker:build

# Start production environment
npm run docker:prod

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Monitoring
```bash
# Check service status
docker-compose ps

# Run health checks
./scripts/health-check.sh

# Monitor logs
docker-compose logs -f [service_name]

# Start monitoring services
docker-compose --profile monitoring up -d
```

## 🔍 Health Checks

All services include health checks:

- **Frontend**: HTTP check on /health
- **Backend**: HTTP check on /health endpoint
- **PostgreSQL**: pg_isready check
- **Redis**: PING command
- **Nginx**: HTTP check on /health

Run comprehensive health check:
```bash
chmod +x scripts/health-check.sh
./scripts/health-check.sh
```

## 📊 Monitoring & Debugging

### Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Container Shell Access
```bash
# Backend container
docker exec -it aihub_backend_prod bash

# Database container
docker exec -it aihub_postgres_prod psql -U aihub_user -d aihub_prod

# Redis container
docker exec -it aihub_redis_prod redis-cli
```

### Performance Monitoring
- **Flower**: http://localhost:5555 (Celery monitoring)
- **Health endpoints**: Monitor service health
- **Docker stats**: `docker stats` for resource usage

## 🔒 Security Considerations

### Production Security
- Change all default passwords
- Use strong secret keys
- Enable SSL/TLS certificates
- Configure firewall rules
- Regular security updates

### Environment Files
- Never commit `.env.*` files
- Use secrets management in production
- Rotate credentials regularly

### Network Security
- Internal service communication
- Rate limiting configured
- Security headers enabled
- CORS properly configured

## 🔄 Backup & Recovery

### Database Backup
```bash
# Create backup
docker exec aihub_postgres_prod pg_dump -U aihub_user aihub_prod > backup.sql

# Restore backup
docker exec -i aihub_postgres_prod psql -U aihub_user aihub_prod < backup.sql
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v aihub_postgres_prod_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 80, 3000, 8000, 5432, 6379 are available
2. **Memory issues**: Ensure 4GB+ RAM available
3. **Permission errors**: Check file permissions and user groups
4. **Network issues**: Verify Docker network configuration

### Debug Commands
```bash
# Check Docker status
docker system info

# Check network
docker network ls
docker network inspect aihub_prod_network

# Check volumes
docker volume ls
docker volume inspect aihub_postgres_prod_data

# Rebuild services
docker-compose build --no-cache [service_name]
```

### Performance Optimization

1. **Resource Limits**: Configure memory and CPU limits
2. **Image Optimization**: Multi-stage builds for smaller images
3. **Cache Strategy**: Optimize Redis and application caching
4. **Database**: Configure PostgreSQL for your workload

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://create-react-app.dev/docs/deployment/)
- [PostgreSQL in Docker](https://hub.docker.com/_/postgres)
- [Redis in Docker](https://hub.docker.com/_/redis)

## 🆘 Support

If you encounter issues:
1. Check the health check script output
2. Review service logs
3. Verify environment configuration
4. Check system resources
5. Consult troubleshooting section

For development questions or issues, please refer to the main project documentation.