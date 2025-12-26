# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI application for uploading field sensor data (audio recordings, camera trap images/videos) to AWS S3 buckets. The system handles large-scale file uploads (100k+ files) with resume capability, retry logic, and PostgreSQL-backed tracking.

## Data Model Hierarchy

```
Client (Company)
  └── Project (maps to S3 bucket)
      └── Cycle (C1, C2, C3... - used as S3 prefix)
          └── Sensor Serial Number (folder containing files)
              └── Files (.wav, .jpg, .mp4)
```

## Database Architecture

The PostgreSQL database tracks:
- Sync sessions with unique IDs
- File upload status (uploaded/failed) for resume support
- Project/bucket mappings
- Configuration per delivery (stored as JSON in config_files/ and DB)
- Retry attempt counters

Database runs in Docker for local development.

## Configuration System

JSON config files stored in `config_files/` directory with structure:
```json
{
    "local_directory": "project-name-data",
    "bucket_name": "project-name-data",
    "s3_prefix": "C2",
    "max_workers": 15,
    "aws_region": "eu-west-1",
    "times_to_retry": 3,
    "aws_profile": "aws-eos",
    "use_find": "yes"
}
```

Configuration can be overridden via CLI flags.

## File Discovery Strategy

Two modes for file scanning:
- **use_find: "yes"**: Native `find` command for Linux/macOS (faster for large datasets)
- **use_find: "no"**: Python-based directory walking (Windows compatibility)

System must support WAV, JPG, and video files.

## Performance Requirements

- Handle 300k+ files efficiently
- Show progress every 10k files during scanning
- Cache S3 file listings and previously uploaded files from DB
- Progress bar updates in-place (no new lines)
- Track files/sec scan rate and upload speed

## CLI Scripts Structure

Separate scripts for modularity:
1. Upload files script
2. Retry failed files script
3. Call endpoint to register files (trigger downstream processing)
4. Master pipeline script orchestrating above

## Progress Display Format

```
Sync Session ID: 30 (from the DB)
🔄 Auto-retry enabled: 3 attempts with 5s delay
✅ Verified directory: /path/to/data
✅ Using AWS profile: aws-eos
✅ AWS Identity: arn:aws:iam::xxx:user/xxx
🔍 Verifying access to bucket: bucket-name
✅ Bucket access verified
📋 Loading previously uploaded files from database...
⚡ find: Found 10,000 files so far...

Progress bar (updates in place):
| 84.9% | Uploaded: 256,097/301,575 | Skipped: 0 | Size: 2128.24 GB | Successful: 243,436 | Failed: 12,661 | Speed: 0.6 files/s | ETA: 20:57
```

## AWS Integration

- Read credentials from `~/.aws/credentials` using profile-based authentication
- Verify AWS identity and bucket access before upload
- Check bucket listing permissions
- Verify S3 prefix structure exists

## Resume & Retry Logic

- Track each file's upload status in database
- Exclude previously uploaded files from new syncs
- Automatic retry with configurable attempts and delay
- Support manual retry of failed files via separate script

## Documentation

Store all documentation in `doc/` folder including:
- Quick start guide
- Database schema/model documentation
- SQL queries for Grafana dashboards

## Grafana Analytics

SQL queries needed for:
- Total files per project/bucket (table)
- Upload status per project (table)
- Cycle-by-cycle comparison bar chart (quantity of files by type by bucket)
- General file status statistics
