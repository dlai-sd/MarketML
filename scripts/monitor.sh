#!/bin/bash

# Monitoring and health check script
# Usage: ./scripts/monitor.sh

set -e

API_URL="${API_URL:-http://localhost:8000}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL}"

echo "🔍 MarketML Health Monitor"
echo "=========================="

# Check API health
echo "Checking API health..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")

if [ "$HEALTH_STATUS" = "200" ]; then
  echo "✅ API is healthy (200)"
else
  echo "❌ API health check failed (${HEALTH_STATUS})"
  MESSAGE="⚠️ MarketML API health check failed with status $HEALTH_STATUS"
  
  # Send Slack notification if webhook configured
  if [ -n "$SLACK_WEBHOOK" ]; then
    curl -X POST "$SLACK_WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d "{\"text\":\"$MESSAGE\"}"
  fi
  exit 1
fi

# Check Redis
echo "Checking Redis..."
if docker exec marketml-redis-1 redis-cli ping > /dev/null 2>&1; then
  echo "✅ Redis is running"
else
  echo "❌ Redis is down"
fi

# Check Celery workers
echo "Checking Celery workers..."
CELERY_STATUS=$(docker exec marketml-celery-worker-1 celery -A app.tasks.celery_app inspect active 2>/dev/null || echo "error")

if [ "$CELERY_STATUS" != "error" ]; then
  echo "✅ Celery workers are running"
else
  echo "❌ Celery workers are down"
fi

# Check disk space
echo "Checking disk space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt 80 ]; then
  echo "⚠️  Disk usage is high: ${DISK_USAGE}%"
else
  echo "✅ Disk usage is normal: ${DISK_USAGE}%"
fi

# Check recent job success rate
echo "Checking job success rate..."
# This would query the database for recent job statistics

echo ""
echo "✅ Monitoring check complete"
