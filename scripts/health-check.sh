#!/bin/bash

# Health check script for all services
# Usage: ./scripts/health-check.sh

set -e

echo "🏥 AI Hub ML Wrangler - Health Check"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local timeout=${3:-10}
    
    echo -n "Checking $name... "
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Check if running in Docker
if command -v docker-compose &> /dev/null; then
    DOCKER_CMD="docker-compose"
elif command -v docker compose &> /dev/null; then
    DOCKER_CMD="docker compose"
else
    echo -e "${RED}Docker Compose not found${NC}"
    exit 1
fi

# Check if services are running
echo "📊 Service Status:"
echo "==================="

# Main health endpoints
SERVICES=(
    "Frontend:http://localhost:3000:5"
    "Backend API:http://localhost:8000/health:10"
    "Nginx Proxy:http://localhost/health:5"
    "PostgreSQL:pg_isready -h localhost -p 5432 -U aihub_user:direct"
    "Redis:redis-cli -h localhost -p 6379 ping:direct"
)

HEALTHY=0
TOTAL=${#SERVICES[@]}

for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r name url timeout <<< "$service_info"
    
    if [[ "$timeout" == "direct" ]]; then
        # Direct command execution
        echo -n "Checking $name... "
        if eval "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Healthy${NC}"
            ((HEALTHY++))
        else
            echo -e "${RED}✗ Unhealthy${NC}"
        fi
    else
        # HTTP health check
        if check_service "$name" "$url" "$timeout"; then
            ((HEALTHY++))
        fi
    fi
done

echo
echo "📈 Health Summary:"
echo "=================="
echo "Healthy services: $HEALTHY/$TOTAL"

if [[ $HEALTHY -eq $TOTAL ]]; then
    echo -e "${GREEN}🎉 All services are healthy!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some services are unhealthy${NC}"
    
    # Show Docker service status if available
    if $DOCKER_CMD ps > /dev/null 2>&1; then
        echo
        echo "🐳 Docker Service Status:"
        echo "========================="
        $DOCKER_CMD ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    fi
    
    exit 1
fi