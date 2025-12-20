#!/bin/bash

# Setup Azure Service Principal for GitHub Actions
# Usage: ./scripts/setup-azure-sp.sh

set -e

SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-marketml-rg}"
SP_NAME="marketml-github-actions"

if [ -z "$SUBSCRIPTION_ID" ]; then
  echo "Error: AZURE_SUBSCRIPTION_ID environment variable not set"
  exit 1
fi

echo "🔐 Creating Azure Service Principal for GitHub Actions..."

# Create service principal
SP_OUTPUT=$(az ad sp create-for-rbac \
  --name "$SP_NAME" \
  --role Contributor \
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
  --sdk-auth)

echo ""
echo "✅ Service Principal created!"
echo ""
echo "📋 Add this as AZURE_CREDENTIALS secret in GitHub:"
echo "=================================================="
echo "$SP_OUTPUT"
echo "=================================================="
echo ""
echo "Also add these secrets to GitHub:"
echo "- AZURE_RESOURCE_GROUP: $RESOURCE_GROUP"
echo "- AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
