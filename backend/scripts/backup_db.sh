#!/bin/bash
# CITMS v3.6 - Database Backup Script (SRS §9.2)

set -e

# Environment variables should be provided by Docker
# DB_HOST, DB_NAME, DB_USER, PGPASSWORD
# S3_BUCKET, S3_ENDPOINT, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="/tmp/citms_backup_${TIMESTAMP}.sql.gz"
S3_PATH="s3://${S3_BUCKET}/backups/citms_backup_${TIMESTAMP}.sql.gz"

echo "[$(date)] Starting database backup..."

# 1. Perform pg_dump and compress
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "[$(date)] Backup created: $BACKUP_FILE"

# 2. Upload to S3
aws --endpoint-url "$S3_ENDPOINT" s3 cp "$BACKUP_FILE" "$S3_PATH"

echo "[$(date)] Backup uploaded to $S3_PATH"

# 3. Cleanup local file
rm "$BACKUP_FILE"

# 4. Retention Policy: Delete backups older than 30 days in S3
# This is a simplified version, ideally use S3 Lifecycle Policies
# But for this script, we can list and delete old ones if needed.

echo "[$(date)] Backup process completed successfully."
