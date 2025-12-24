# Architecture Overview

This document provides a high-level overview of the Data Uploader architecture.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Scripts Layer                        │
├─────────────────────────────────────────────────────────────┤
│  upload.py  │  retry.py  │  trigger_endpoint.py  │ master.py│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Components Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Config  │  FileScanner  │  S3Uploader  │  RetryManager     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌──────────────────┐                    ┌──────────────────────┐
│   PostgreSQL     │                    │      AWS S3          │
│   Database       │                    │   (File Storage)     │
│  - Projects      │                    │                      │
│  - Sessions      │                    │  bucket/prefix/      │
│  - Files         │                    │    sensor/files      │
│  - Config        │                    │                      │
└──────────────────┘                    └──────────────────────┘
```

## Data Flow

### 1. Upload Flow

```
User Config (JSON)
    │
    ▼
Config Loader ──> Validate
    │
    ▼
Database ──> Create Project & Session
    │
    ▼
FileScanner ──> Scan Local Directory
    │              │
    │              ├─> Use find (Linux/macOS)
    │              └─> Use os.walk (Windows)
    │
    ▼
Filter Files ──> Compare with:
    │              ├─> S3 existing files
    │              └─> DB uploaded files
    │
    ▼
Database ──> Insert pending files
    │
    ▼
S3Uploader ──> Upload files in parallel
    │              │
    │              ├─> ThreadPoolExecutor
    │              └─> boto3 upload_file
    │
    ▼
Database ──> Update file status
    │              ├─> uploaded
    │              └─> failed
    │
    ▼
Complete Session
```

### 2. Retry Flow

```
User provides Session ID
    │
    ▼
Database ──> Get failed files
    │
    ▼
RetryManager ──> Retry each file
    │                 │
    │                 ├─> Exponential backoff
    │                 └─> Track retry count
    │
    ▼
Database ──> Update status
    │              ├─> uploaded (success)
    │              └─> failed (still failed)
    │
    ▼
Return statistics
```

### 3. Endpoint Trigger Flow

```
User provides Session ID + URL
    │
    ▼
Database ──> Get session info
    │
    ▼
HTTP POST ──> Send session data
    │              │
    │              ├─> bucket_name
    │              ├─> s3_prefix
    │              ├─> total_files
    │              └─> files_uploaded
    │
    ▼
External System ──> Process files
```

## Module Descriptions

### config.py
- Loads configuration from JSON files
- Merges with environment variables
- Validates configuration parameters
- Provides CLI override support

### file_scanner.py
- Discovers files in local directory
- Supports two modes:
  - Native `find` command (faster, Unix-only)
  - Python `os.walk` (cross-platform)
- Filters by supported extensions (.wav, .jpg, .mp4, etc.)
- Generates S3 keys from relative paths
- Provides progress callbacks

### s3_uploader.py
- Handles S3 uploads using boto3
- Verifies AWS credentials and bucket access
- Parallel uploads using ThreadPoolExecutor
- Automatic retry with configurable attempts
- Lists existing S3 files for comparison

### database.py
- PostgreSQL connection management
- CRUD operations for:
  - Projects
  - Sync sessions
  - File uploads
  - Configuration history
- Batch insert operations
- Transaction management

### retry.py
- Manages retry logic for failed uploads
- Supports manual and automatic retry modes
- Exponential backoff between retry rounds
- Tracks retry counts per file
- Updates database with results

### progress.py
- Real-time progress tracking
- In-place progress bar updates
- Upload speed calculation
- ETA estimation
- Human-readable size formatting

## Database Schema

### Key Relationships

```
projects (1:N) sync_sessions (1:N) file_uploads
              └─────────────> (1:N) config_history
```

### State Machine for Files

```
pending ──upload──> uploaded
   │
   └──fail──> failed ──retry──> uploaded
                │
                └──max retries──> failed (permanent)
```

## Performance Optimizations

1. **Parallel Uploads**
   - Uses ThreadPoolExecutor with configurable workers
   - Default: 15 parallel uploads

2. **Smart File Discovery**
   - Native `find` command for Unix (much faster)
   - Python fallback for Windows
   - Progress updates every 10,000 files

3. **Database Efficiency**
   - Batch inserts for file records
   - Indexes on frequently queried columns
   - Connection pooling via psycopg2

4. **Resume Capability**
   - Tracks uploaded files in database
   - Compares with S3 to skip existing files
   - Avoids re-uploading successful files

5. **Memory Management**
   - Streaming file scanner option
   - Processes files in batches
   - No loading all file paths into memory

## Scalability Considerations

### Current Design
- Handles 300k+ files efficiently
- Single machine, multi-threaded uploads
- PostgreSQL for state management

### Future Improvements
- Distributed uploads across multiple machines
- Message queue for upload tasks (Kafka/RabbitMQ)
- Horizontal scaling of upload workers
- Caching layer for S3 file listings
- Compression of large files before upload

## Error Handling

### Transient Errors
- Network timeouts
- Temporary S3 unavailability
- Handled via automatic retry with backoff

### Permanent Errors
- File not found
- Permission denied
- Invalid credentials
- Logged to database with error message

### Recovery Strategies
1. Automatic retry during upload (configurable attempts)
2. Manual retry script for failed files
3. Auto-retry with exponential backoff
4. Database tracking prevents duplicate uploads

## Monitoring

### Real-time
- Progress bar with speed and ETA
- Console output with emoji indicators
- File-by-file status updates

### Historical
- Grafana dashboards
- PostgreSQL queries
- Session statistics
- File upload history

## Security Considerations

1. **AWS Credentials**
   - Uses AWS profiles from `~/.aws/credentials`
   - No credentials stored in code or database

2. **Database Credentials**
   - Stored in `.env` file (gitignored)
   - Environment variable support

3. **Configuration Files**
   - May contain sensitive paths
   - Gitignored except example

4. **File Access**
   - Read-only access to local files
   - No modification of source data
