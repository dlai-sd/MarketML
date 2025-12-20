#!/bin/bash

# Database backup script
# Usage: ./scripts/backup-db.sh

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="data/marketml.db"
BACKUP_FILE="$BACKUP_DIR/marketml_$TIMESTAMP.db"

mkdir -p "$BACKUP_DIR"

echo "💾 Backing up database..."

if [ -f "$DB_FILE" ]; then
  cp "$DB_FILE" "$BACKUP_FILE"
  gzip "$BACKUP_FILE"
  echo "✅ Backup created: ${BACKUP_FILE}.gz"
  
  # Keep only last 7 days of backups
  find "$BACKUP_DIR" -name "marketml_*.db.gz" -mtime +7 -delete
  echo "🗑️  Old backups cleaned"
else
  echo "❌ Database file not found: $DB_FILE"
  exit 1
fi

# Upload to Azure Storage if configured
if [ -n "$AZURE_STORAGE_CONNECTION_STRING" ]; then
  echo "☁️  Uploading to Azure Storage..."
  az storage blob upload \
    --container-name backups \
    --file "${BACKUP_FILE}.gz" \
    --name "marketml_$TIMESTAMP.db.gz" \
    --connection-string "$AZURE_STORAGE_CONNECTION_STRING"
  echo "✅ Uploaded to cloud storage"
fi
