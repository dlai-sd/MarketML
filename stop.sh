#!/bin/bash
###############################################################################
# Stop MarketML - Clean shutdown of all services
###############################################################################

echo "🛑 Stopping MarketML..."

# Stop API
echo "  Stopping API server..."
pkill -f "uvicorn app.main:app" || true

# Stop Celery
echo "  Stopping Celery worker..."
pkill -f "celery.*worker" || true

echo "  Stopping Celery beat..."
pkill -f "celery.*beat" || true

# Stop Frontend
echo "  Stopping Frontend server..."
pkill -f "http.server 3000" || true

# Stop Redis (optional - comment out if you want Redis to keep running)
# echo "  Stopping Redis..."
# redis-cli shutdown || true

sleep 2

echo "✅ MarketML stopped!"
