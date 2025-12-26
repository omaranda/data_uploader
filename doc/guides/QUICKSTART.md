# Quick Start Guide

This guide will help you get started with the Data Uploader tool.

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- AWS credentials configured in `~/.aws/credentials`

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd data_uploader
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if you need to customize database settings
   ```

5. **Start PostgreSQL database**
   ```bash
   docker-compose up -d
   ```

6. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

## Configuration

Create a configuration file in the `config_files/` directory:

```json
{
    "local_directory": "/path/to/your/data",
    "bucket_name": "your-s3-bucket-name",
    "s3_prefix": "C1",
    "max_workers": 15,
    "aws_region": "eu-west-1",
    "times_to_retry": 3,
    "aws_profile": "default",
    "use_find": "yes"
}
```

### Configuration Options

- **local_directory**: Path to local directory containing files to upload
- **bucket_name**: S3 bucket name
- **s3_prefix**: S3 prefix (typically the cycle: C1, C2, C3, etc.)
- **max_workers**: Number of parallel upload workers (default: 15)
- **aws_region**: AWS region (default: eu-west-1)
- **times_to_retry**: Number of retry attempts for failed uploads (default: 3)
- **aws_profile**: AWS profile name from ~/.aws/credentials (default: default)
- **use_find**: Use native find command ("yes") or Python scanning ("no")

## Usage

### Upload Files

Upload files using a configuration file:

```bash
python scripts/upload.py --config config_files/your_config.json
```

**CLI Options:**
- `--config, -c`: Path to configuration file (required)
- `--local-directory, -d`: Override local directory
- `--bucket-name, -b`: Override bucket name
- `--s3-prefix, -p`: Override S3 prefix
- `--max-workers, -w`: Override max workers
- `--aws-profile`: Override AWS profile
- `--dry-run`: Analyze files without uploading

**Example with overrides:**
```bash
python scripts/upload.py \
  --config config_files/my_config.json \
  --s3-prefix C2 \
  --max-workers 20
```

### Retry Failed Files

If some files failed to upload, retry them:

```bash
python scripts/retry.py --session-id <session_id>
```

**CLI Options:**
- `--session-id, -s`: Session ID to retry (required)
- `--max-attempts, -m`: Maximum retry attempts per file (default: 3)
- `--delay, -d`: Delay between retries in seconds (default: 5)
- `--auto-retry, -a`: Enable automatic retry with exponential backoff
- `--max-rounds, -r`: Maximum retry rounds for auto-retry (default: 3)

**Example with auto-retry:**
```bash
python scripts/retry.py \
  --session-id 42 \
  --auto-retry \
  --max-rounds 3
```

### Trigger Endpoint

After uploading, trigger an endpoint to register files for processing:

```bash
python scripts/trigger_endpoint.py \
  --session-id <session_id> \
  --endpoint-url https://your-endpoint.com/api/register
```

### Run Complete Pipeline

Run the entire pipeline (upload → retry → trigger endpoint):

```bash
python scripts/master.py \
  --config config_files/your_config.json \
  --endpoint-url https://your-endpoint.com/api/register
```

**CLI Options:**
- `--config, -c`: Path to configuration file (required)
- `--endpoint-url, -e`: Endpoint URL to trigger after upload
- `--skip-retry`: Skip automatic retry of failed files
- `--skip-endpoint`: Skip triggering endpoint
- `--dry-run`: Analyze files without uploading

## File Organization

The tool expects files to be organized in the local directory with sensor serial numbers as folder names:

```
local_directory/
├── SENSOR_001/
│   ├── file1.wav
│   ├── file2.wav
│   └── image1.jpg
├── SENSOR_002/
│   ├── file1.wav
│   └── video1.mp4
└── ...
```

These will be uploaded to S3 as:

```
s3://bucket-name/C1/SENSOR_001/file1.wav
s3://bucket-name/C1/SENSOR_001/file2.wav
s3://bucket-name/C1/SENSOR_001/image1.jpg
s3://bucket-name/C1/SENSOR_002/file1.wav
s3://bucket-name/C1/SENSOR_002/video1.mp4
```

## Supported File Types

- Audio: `.wav`
- Images: `.jpg`, `.jpeg`
- Video: `.mp4`, `.mov`, `.avi`

## Resume Capability

The tool automatically tracks uploaded files in the PostgreSQL database. If an upload is interrupted:

1. The database maintains a record of which files were successfully uploaded
2. On the next run, previously uploaded files are automatically skipped
3. Only new or failed files will be uploaded

## Troubleshooting

### Database Connection Issues

If you can't connect to the database:

```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### AWS Credentials Issues

Verify your AWS credentials:

```bash
aws sts get-caller-identity --profile your-profile-name
```

### Permission Errors

Ensure your AWS IAM user has these permissions:
- `s3:PutObject`
- `s3:GetObject`
- `s3:ListBucket`

## Getting Help

- Check the [Database Schema](DATABASE_SCHEMA.md) for database details
- See [Grafana Queries](GRAFANA_QUERIES.md) for monitoring queries
- Review error messages in the terminal output
- Check session details in the database using the session ID
