#!/bin/bash
###############################################################################
# MarketML One-Command Deployment
# Works everywhere: Codespace, localhost, production - NO CONFIG NEEDED!
###############################################################################

set -e

echo "🚀 Starting MarketML..."

# Auto-detect environment
if [ ! -z "$CODESPACES" ]; then
    ENV="codespace"
    echo "📍 Environment: GitHub Codespaces"
elif [ "$HOSTNAME" = "localhost" ] || [ "$HOSTNAME" = "127.0.0.1" ]; then
    ENV="localhost"
    echo "📍 Environment: Localhost"
else
    ENV="production"
    echo "📍 Environment: Production"
fi

# Start Redis
echo "▶️  Starting Redis..."
redis-server --daemonize yes --port 6379 --maxmemory 256mb --maxmemory-policy allkeys-lru

# Start Celery Worker
echo "▶️  Starting Celery Worker..."
nohup python -m celery -A app.tasks.celery_app worker --loglevel=info --logfile=logs/celery-worker.log > /dev/null 2>&1 &

# Start Celery Beat
echo "▶️  Starting Celery Beat..."
nohup python -m celery -A app.tasks.celery_app beat --loglevel=info --logfile=logs/celery-beat.log > /dev/null 2>&1 &

# Start API (serves both API and Frontend on same port - no CORS!)
echo "▶️  Starting API Server (with Frontend)..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &

sleep 3

# Display access URLs
echo ""
echo "✅ MarketML is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$ENV" = "codespace" ]; then
    echo "🌐 App URL:  https://${CODESPACE_NAME}-8000.app.github.dev"
    echo "📚 API Docs: https://${CODESPACE_NAME}-8000.app.github.dev/v1/docs"
    echo ""
    echo "💡 Frontend + API on SAME PORT (8000) - No CORS issues!"
else
    echo "🌐 App URL:  http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/v1/docs"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ Just open the URL and start generating personas!"
echo "🛑 To stop: ./stop.sh"

