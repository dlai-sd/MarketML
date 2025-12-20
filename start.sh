#!/bin/bash
# Quick start script for MarketML

echo "=================================================="
echo "  MarketML - Quick Start"
echo "=================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Start services
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Checking services..."

if docker-compose ps | grep -q "Up"; then
    echo "✓ Services are up"
else
    echo "❌ Some services failed to start"
    docker-compose ps
    exit 1
fi

echo ""
echo "Testing API..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✓ API is responding"
else
    echo "⚠ API might not be ready yet, waiting..."
    sleep 5
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "✓ API is responding"
    else
        echo "❌ API is not responding"
        echo "Check logs with: docker-compose logs api"
        exit 1
    fi
fi

echo ""
echo "=================================================="
echo "  Services Started Successfully!"
echo "=================================================="
echo ""
echo "Access points:"
echo "  • API Docs:    http://localhost:8000/v1/docs"
echo "  • Health:      http://localhost:8000/health"
echo "  • Grafana:     http://localhost:3000 (admin/admin)"
echo "  • Prometheus:  http://localhost:9090"
echo ""
echo "Test the API:"
echo "  python tests/test_api.py"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
echo "=================================================="
