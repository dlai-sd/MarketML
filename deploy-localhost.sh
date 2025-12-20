#!/bin/bash

###############################################################################
# MarketML Localhost Deployment Script
# Deploys the complete MarketML stack on localhost using Docker Compose
###############################################################################

set -e  # Exit on error

echo "=================================================="
echo "🚀 MarketML Localhost Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_status "Created .env file. Please configure it if needed."
fi

# Create required directories
print_status "Creating required directories..."
mkdir -p data/enrichment logs models frontend

# Check if enrichment databases exist
if [ ! -f data/enrichment/locations.db ]; then
    print_warning "Enrichment databases not found. Populating..."
    python scripts/populate_enrichment.py
    print_status "Enrichment databases populated"
else
    print_status "Enrichment databases found"
fi

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build Docker images
print_status "Building Docker images..."
docker-compose build --no-cache

# Start services
print_status "Starting services..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to start (30 seconds)..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_status "Redis is healthy"
else
    print_warning "Redis health check failed"
fi

# Check API
API_PORT=$(grep API_PORT .env | cut -d '=' -f2 | tr -d ' ' || echo "8000")
if curl -f http://localhost:${API_PORT}/health > /dev/null 2>&1; then
    print_status "API is healthy"
else
    print_warning "API health check failed (may still be starting...)"
fi

# Display URLs
echo ""
echo "=================================================="
echo "🎉 Deployment Complete!"
echo "=================================================="
echo ""
echo "📍 Access URLs:"
echo "   API:            http://localhost:${API_PORT}"
echo "   API Docs:       http://localhost:${API_PORT}/v1/docs"
echo "   Health Check:   http://localhost:${API_PORT}/health"
echo "   Prometheus:     http://localhost:9090"
echo "   Grafana:        http://localhost:3000"
echo "   Frontend:       http://localhost:3001"
echo ""
echo "📊 Quick Commands:"
echo "   View logs:      docker-compose logs -f"
echo "   View API logs:  docker-compose logs -f api"
echo "   Stop services:  docker-compose down"
echo "   Restart:        docker-compose restart"
echo ""
echo "🧪 Test the API:"
echo '   curl http://localhost:'${API_PORT}'/health'
echo ""
echo "=================================================="

# Run a quick smoke test
echo ""
echo "🧪 Running smoke test..."
sleep 5
HEALTH_RESPONSE=$(curl -s http://localhost:${API_PORT}/health || echo '{"status":"unavailable"}')
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_status "Smoke test passed! API is responding correctly."
    echo ""
    echo "$HEALTH_RESPONSE" | python -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    print_warning "API may still be initializing. Check logs with: docker-compose logs -f api"
fi

echo ""
print_status "Localhost deployment ready!"
