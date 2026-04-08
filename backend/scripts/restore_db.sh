#!/bin/bash
# CITMS v3.6 - Database Restore Script (SRS §9.2)

set -e

# Environment variables should be provided by Docker
# DB_HOST, DB_NAME, DB_USER, PGPASSWORD
# S3_BUCKET, S3_ENDPOINT, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file_name_in_s3>"
  exit 1
fi

BACKUP_FILE_NAME=$1
S3_PATH="s3://${S3_BUCKET}/backups/${BACKUP_FILE_NAME}"
LOCAL_FILE="/tmp/${BACKUP_FILE_NAME}"

echo "[$(date)] Starting database restore from $S3_PATH..."

# 1. Download from S3
aws --endpoint-url "$S3_ENDPOINT" s3 cp "$S3_PATH" "$LOCAL_FILE"

echo "[$(date)] Backup downloaded: $LOCAL_FILE"

# 2. Restore to DB
# Decompress and pipe to psql
gunzip -c "$LOCAL_FILE" | psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME"

echo "[$(date)] Restore completed successfully."

# 3. Cleanup local file
rm "$LOCAL_FILE"

echo "[$(date)] Restore process completed successfully."
