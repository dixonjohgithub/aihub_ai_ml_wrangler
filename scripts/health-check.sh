#!/bin/bash

# Health check script for Docker containers
# Usage: ./health-check.sh [service_name]

set -e

SERVICE=${1:-"all"}
API_URL=${API_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}

check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo "Checking $service_name at $url..."
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo "✅ $service_name is healthy"
        return 0
    else
        echo "❌ $service_name is not responding"
        return 1
    fi
}

check_postgres() {
    echo "Checking PostgreSQL..."
    if docker exec aihub-postgres-dev pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is healthy"
        return 0
    else
        echo "❌ PostgreSQL is not responding"
        return 1
    fi
}

check_redis() {
    echo "Checking Redis..."
    if docker exec aihub-redis-dev redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is healthy"
        return 0
    else
        echo "❌ Redis is not responding"
        return 1
    fi
}

case $SERVICE in
    "backend"|"api")
        check_service "Backend API" "$API_URL/health"
        ;;
    "frontend"|"ui")
        check_service "Frontend" "$FRONTEND_URL"
        ;;
    "postgres"|"db")
        check_postgres
        ;;
    "redis"|"cache")
        check_redis
        ;;
    "all")
        echo "🔍 Performing comprehensive health check..."
        echo
        
        OVERALL_STATUS=0
        
        check_postgres || OVERALL_STATUS=1
        check_redis || OVERALL_STATUS=1
        check_service "Backend API" "$API_URL/health" || OVERALL_STATUS=1
        check_service "Frontend" "$FRONTEND_URL" || OVERALL_STATUS=1
        
        echo
        if [ $OVERALL_STATUS -eq 0 ]; then
            echo "🎉 All services are healthy!"
            exit 0
        else
            echo "⚠️  Some services are not healthy"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 [backend|frontend|postgres|redis|all]"
        exit 1
        ;;
esac