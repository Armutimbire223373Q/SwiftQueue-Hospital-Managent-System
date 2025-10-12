#!/bin/bash

# ==========================================
# DATABASE BACKUP SCRIPT
# Healthcare Queue Management System
# ==========================================

set -e  # Exit on any error

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="queue_management_backup_${TIMESTAMP}"
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-queue_management}"
DB_USER="${DB_USER:-queue_user}"
DB_PASSWORD="${DB_PASSWORD:-secure_password}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup: $BACKUP_NAME"

# Create database backup
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -F c \
    -f "$BACKUP_DIR/${BACKUP_NAME}.backup"

echo "Database backup completed: $BACKUP_DIR/${BACKUP_NAME}.backup"

# Create compressed backup
gzip "$BACKUP_DIR/${BACKUP_NAME}.backup"

echo "Backup compressed: $BACKUP_DIR/${BACKUP_NAME}.backup.gz"

# Clean up old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.backup.gz" -mtime +30 -delete

echo "Old backups cleaned up"

# Verify backup integrity
echo "Verifying backup integrity..."
if gunzip -c "$BACKUP_DIR/${BACKUP_NAME}.backup.gz" | head -1 | grep -q "PGDMP"; then
    echo "✅ Backup integrity check passed"
else
    echo "❌ Backup integrity check failed"
    exit 1
fi

# Log backup completion
echo "$(date): Backup completed successfully - $BACKUP_NAME" >> "$BACKUP_DIR/backup.log"

echo "✅ Database backup completed successfully"