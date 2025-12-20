#!/bin/bash

# Azure deployment script for MarketML
# Usage: ./scripts/azure-deploy.sh

set -e

# Configuration
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-marketml-rg}"
LOCATION="${AZURE_LOCATION:-centralindia}"
APP_NAME="${AZURE_APP_NAME:-marketml-app}"
REGISTRY="${CONTAINER_REGISTRY:-ghcr.io}"
IMAGE="${CONTAINER_IMAGE:-marketml:latest}"

echo "🚀 Deploying MarketML to Azure..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "App Name: $APP_NAME"

# Create resource group if it doesn't exist
echo "📦 Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  || echo "Resource group already exists"

# Create Azure Container Registry (if using ACR)
if [ "$USE_ACR" = "true" ]; then
  ACR_NAME="${APP_NAME}acr"
  echo "📦 Creating Azure Container Registry..."
  az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --admin-enabled true \
    || echo "ACR already exists"
fi

# Create Redis Cache
echo "💾 Creating Redis Cache..."
REDIS_NAME="${APP_NAME}-redis"
az redis create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REDIS_NAME" \
  --location "$LOCATION" \
  --sku Basic \
  --vm-size c0 \
  || echo "Redis already exists"

# Get Redis connection string
REDIS_KEY=$(az redis list-keys \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REDIS_NAME" \
  --query primaryKey -o tsv)

REDIS_HOST="${REDIS_NAME}.redis.cache.windows.net"

# Create Storage Account for SQLite backup
echo "💾 Creating Storage Account..."
STORAGE_NAME="${APP_NAME}storage"
az storage account create \
  --name "$STORAGE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  || echo "Storage account already exists"

# Create File Share for persistent data
az storage share create \
  --name "marketml-data" \
  --account-name "$STORAGE_NAME" \
  || echo "File share already exists"

STORAGE_KEY=$(az storage account keys list \
  --resource-group "$RESOURCE_GROUP" \
  --account-name "$STORAGE_NAME" \
  --query '[0].value' -o tsv)

# Create Container Instance
echo "🐳 Creating Container Instance..."
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --image "$IMAGE" \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --dns-name-label "$APP_NAME" \
  --environment-variables \
    REDIS_HOST="$REDIS_HOST" \
    REDIS_PORT=6380 \
    REDIS_PASSWORD="$REDIS_KEY" \
    DATABASE_URL="sqlite:////data/marketml.db" \
    ENVIRONMENT="production" \
  --azure-file-volume-account-name "$STORAGE_NAME" \
  --azure-file-volume-account-key "$STORAGE_KEY" \
  --azure-file-volume-share-name "marketml-data" \
  --azure-file-volume-mount-path "/data" \
  --restart-policy Always \
  || az container restart \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME"

# Get container FQDN
FQDN=$(az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --query ipAddress.fqdn -o tsv)

echo "✅ Deployment complete!"
echo "📍 Application URL: http://$FQDN:8000"
echo "📊 API Docs: http://$FQDN:8000/v1/docs"
echo "🔍 Health Check: http://$FQDN:8000/health"

# Test deployment
echo "🧪 Testing deployment..."
sleep 10
curl -f "http://$FQDN:8000/health" && echo "✅ Health check passed!" || echo "❌ Health check failed"

# Output connection details
echo ""
echo "Connection Details:"
echo "==================="
echo "Redis Host: $REDIS_HOST"
echo "Redis Port: 6380"
echo "Storage Account: $STORAGE_NAME"
echo "Resource Group: $RESOURCE_GROUP"
