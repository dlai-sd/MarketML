#!/bin/bash

# Azure resource cleanup script
# Usage: ./scripts/azure-cleanup.sh

set -e

RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-marketml-rg}"

echo "⚠️  WARNING: This will delete all resources in $RESOURCE_GROUP"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Cancelled."
  exit 0
fi

echo "🗑️  Deleting resource group: $RESOURCE_GROUP"
az group delete \
  --name "$RESOURCE_GROUP" \
  --yes \
  --no-wait

echo "✅ Cleanup initiated. Resources will be deleted in the background."
