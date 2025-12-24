# Database Schema

This document describes the PostgreSQL database schema used by the Data Uploader.

## Tables

### projects

Stores information about projects and their associated S3 buckets.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique project identifier |
| project_name | VARCHAR(255) | Project name |
| bucket_name | VARCHAR(255) UNIQUE | S3 bucket name |
| aws_region | VARCHAR(50) | AWS region |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique constraint on `bucket_name`

### sync_sessions

Tracks individual upload sessions.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique session identifier |
| project_id | INTEGER FK | Reference to projects table |
| local_directory | TEXT | Local directory path |
| s3_prefix | VARCHAR(50) | S3 prefix (cycle: C1, C2, etc.) |
| aws_profile | VARCHAR(100) | AWS profile used |
| max_workers | INTEGER | Number of parallel workers |
| times_to_retry | INTEGER | Number of retry attempts |
| use_find | BOOLEAN | Whether find command was used |
| status | VARCHAR(50) | Session status |
| total_files | INTEGER | Total number of files |
| total_size_bytes | BIGINT | Total size in bytes |
| files_uploaded | INTEGER | Number of files uploaded |
| files_failed | INTEGER | Number of files failed |
| files_skipped | INTEGER | Number of files skipped |
| started_at | TIMESTAMP | Session start time |
| completed_at | TIMESTAMP | Session completion time |
| created_at | TIMESTAMP | Creation timestamp |

**Statuses:**
- `in_progress`: Upload in progress
- `completed`: Successfully completed
- `completed_with_errors`: Completed but some files failed
- `failed`: Session failed

**Indexes:**
- Primary key on `id`
- Index on `project_id`
- Index on `status`

### file_uploads

Tracks individual file upload attempts.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL PRIMARY KEY | Unique file record identifier |
| session_id | INTEGER FK | Reference to sync_sessions |
| local_path | TEXT | Local file path |
| s3_key | TEXT | S3 key (destination path) |
| file_size | BIGINT | File size in bytes |
| file_type | VARCHAR(10) | File type (WAV, JPG, VIDEO) |
| status | VARCHAR(50) | Upload status |
| retry_count | INTEGER | Number of retry attempts |
| error_message | TEXT | Error message if failed |
| uploaded_at | TIMESTAMP | Upload completion time |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Statuses:**
- `pending`: Not yet uploaded
- `uploaded`: Successfully uploaded
- `failed`: Upload failed

**Indexes:**
- Primary key on `id`
- Index on `session_id`
- Index on `status`
- Index on `s3_key`

### config_history

Stores configuration history for each session.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique config record identifier |
| session_id | INTEGER FK | Reference to sync_sessions |
| config_json | JSONB | Configuration as JSON |
| created_at | TIMESTAMP | Creation timestamp |

## Relationships

```
projects (1) ─── (N) sync_sessions
sync_sessions (1) ─── (N) file_uploads
sync_sessions (1) ─── (N) config_history
```

## Common Queries

### Get session statistics

```sql
SELECT
    ss.id,
    p.project_name,
    p.bucket_name,
    ss.s3_prefix,
    ss.total_files,
    ss.files_uploaded,
    ss.files_failed,
    ss.files_skipped,
    ss.status,
    ss.started_at,
    ss.completed_at
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
WHERE ss.id = <session_id>;
```

### Get failed files for a session

```sql
SELECT
    local_path,
    s3_key,
    error_message,
    retry_count
FROM file_uploads
WHERE session_id = <session_id>
  AND status = 'failed'
ORDER BY id;
```

### Get upload statistics by file type

```sql
SELECT
    file_type,
    COUNT(*) as total_files,
    SUM(file_size) as total_size_bytes,
    SUM(CASE WHEN status = 'uploaded' THEN 1 ELSE 0 END) as uploaded,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
FROM file_uploads
WHERE session_id = <session_id>
GROUP BY file_type;
```

### Get all sessions for a project

```sql
SELECT
    ss.id,
    ss.s3_prefix,
    ss.status,
    ss.total_files,
    ss.files_uploaded,
    ss.files_failed,
    ss.started_at,
    ss.completed_at
FROM sync_sessions ss
JOIN projects p ON ss.project_id = p.id
WHERE p.bucket_name = '<bucket_name>'
ORDER BY ss.started_at DESC;
```

## Maintenance

### Cleanup old sessions

```sql
-- Delete sessions older than 90 days (cascade deletes related records)
DELETE FROM sync_sessions
WHERE completed_at < NOW() - INTERVAL '90 days';
```

### Vacuum and analyze

```sql
VACUUM ANALYZE projects;
VACUUM ANALYZE sync_sessions;
VACUUM ANALYZE file_uploads;
VACUUM ANALYZE config_history;
```
