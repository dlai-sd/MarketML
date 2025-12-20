#!/bin/bash

###############################################################################
# MarketML CodeSpace Deployment Script
# Deploys MarketML in GitHub Codespaces with proper port forwarding
###############################################################################

set -e  # Exit on error

echo "=================================================="
echo "🚀 MarketML CodeSpace Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Detect if running in Codespaces
if [ -z "$CODESPACES" ]; then
    print_warning "Not running in GitHub Codespaces. Using localhost URLs."
    CODESPACE_NAME="localhost"
else
    print_status "Running in GitHub Codespaces"
    CODESPACE_NAME="${CODESPACE_NAME}"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    
    # Update .env for Codespaces
    sed -i 's/REDIS_HOST=redis/REDIS_HOST=localhost/' .env
    sed -i 's/QDRANT_HOST=qdrant/QDRANT_HOST=localhost/' .env
    sed -i 's|CELERY_BROKER_URL=redis://redis:6379/0|CELERY_BROKER_URL=redis://localhost:6379/0|' .env
    sed -i 's|CELERY_RESULT_BACKEND=redis://redis:6379/0|CELERY_RESULT_BACKEND=redis://localhost:6379/0|' .env
    
    print_status "Created and configured .env for Codespaces"
fi

# Install system dependencies
print_status "Checking Python dependencies..."
pip install -q -r requirements.txt

# Install ML models
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    print_status "Downloading spaCy model..."
    python -m spacy download en_core_web_sm
fi

# Create required directories
print_status "Creating required directories..."
mkdir -p data/enrichment logs models frontend

# Populate enrichment databases
if [ ! -f data/enrichment/locations.db ]; then
    print_status "Populating enrichment databases..."
    python scripts/populate_enrichment.py
else
    print_status "Enrichment databases already exist"
fi

# Start Redis in background
print_status "Starting Redis..."
if ! pgrep redis-server > /dev/null; then
    redis-server --daemonize yes --port 6379
    sleep 2
    print_status "Redis started on port 6379"
else
    print_status "Redis already running"
fi

# Start Celery worker in background
print_status "Starting Celery worker..."
pkill -f "celery -A app.tasks.celery_app worker" 2>/dev/null || true
celery -A app.tasks.celery_app worker --loglevel=info --logfile=logs/celery-worker.log --detach
sleep 3
print_status "Celery worker started"

# Start Celery beat in background
print_status "Starting Celery beat..."
pkill -f "celery -A app.tasks.celery_app beat" 2>/dev/null || true
celery -A app.tasks.celery_app beat --loglevel=info --logfile=logs/celery-beat.log --detach
sleep 2
print_status "Celery beat started"

# Start FastAPI application
print_status "Starting FastAPI application..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true

# Get API port from .env or use default
API_PORT=$(grep API_PORT .env | cut -d '=' -f2 | tr -d ' ' || echo "8000")

# Start uvicorn in background
nohup uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT} --reload > logs/api.log 2>&1 &
API_PID=$!

print_status "FastAPI starting on port ${API_PORT} (PID: ${API_PID})..."
sleep 10

# Check if API is running
if ps -p $API_PID > /dev/null; then
    print_status "API process is running"
else
    print_error "API failed to start. Check logs/api.log"
    exit 1
fi

# Wait for API to be ready
print_status "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:${API_PORT}/health > /dev/null 2>&1; then
        print_status "API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_warning "API health check timeout. It may still be starting..."
    fi
    sleep 2
done

# Generate URLs
if [ "$CODESPACE_NAME" != "localhost" ]; then
    # Codespaces URL format
    BASE_URL="https://${CODESPACE_NAME}-${API_PORT}.app.github.dev"
else
    BASE_URL="http://localhost:${API_PORT}"
fi

# Display URLs and status
echo ""
echo "=================================================="
echo "🎉 CodeSpace Deployment Complete!"
echo "=================================================="
echo ""
echo "📍 Access URLs:"
echo "   API:            ${BASE_URL}"
echo "   API Docs:       ${BASE_URL}/v1/docs"
echo "   Health Check:   ${BASE_URL}/health"
echo "   OpenAPI:        ${BASE_URL}/v1/openapi.json"
echo ""
echo "📊 Service Status:"
echo "   Redis:          ✅ Running on port 6379"
echo "   Celery Worker:  ✅ Running (logs/celery-worker.log)"
echo "   Celery Beat:    ✅ Running (logs/celery-beat.log)"
echo "   FastAPI:        ✅ Running on port ${API_PORT} (logs/api.log)"
echo ""
echo "📁 Log Files:"
echo "   API:            tail -f logs/api.log"
echo "   Celery Worker:  tail -f logs/celery-worker.log"
echo "   Celery Beat:    tail -f logs/celery-beat.log"
echo ""
echo "🛑 Stop Services:"
echo "   pkill -f 'uvicorn app.main:app'"
echo "   pkill -f 'celery -A app.tasks.celery_app'"
echo "   redis-cli shutdown"
echo ""
echo "=================================================="

# Run smoke test
echo ""
echo "🧪 Running smoke test..."
sleep 2
HEALTH_RESPONSE=$(curl -s ${BASE_URL}/health || echo '{"status":"unavailable"}')
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_status "Smoke test passed! API is responding correctly."
    echo ""
    echo "$HEALTH_RESPONSE" | python -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
    echo ""
    
    # Test persona generation endpoint
    echo "🧪 Testing persona generation endpoint..."
    TEST_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/personas/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test User",
            "location": "Pune, India",
            "description": "Test persona generation",
            "confirmed_profiles": []
        }' || echo '{"error":"failed"}')
    
    if echo "$TEST_RESPONSE" | grep -q "job_id"; then
        print_status "Persona generation endpoint is working!"
        JOB_ID=$(echo "$TEST_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null || echo "")
        if [ -n "$JOB_ID" ]; then
            echo "   Job ID: $JOB_ID"
            echo "   Check status: ${BASE_URL}/v1/jobs/${JOB_ID}"
        fi
    else
        print_warning "Persona generation endpoint test failed"
        echo "   Response: $TEST_RESPONSE"
    fi
else
    print_warning "API health check failed. Check logs/api.log for details."
    echo ""
    echo "Last 20 lines of API log:"
    tail -n 20 logs/api.log || true
fi

echo ""
print_status "CodeSpace deployment ready!"
print_info "Share this URL with others: ${BASE_URL}"
echo ""
