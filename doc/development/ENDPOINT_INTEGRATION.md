# Endpoint Integration Guide

This guide explains how to use the `trigger_endpoint.py` script to integrate with the MadXXX API for downstream processing.

## Overview

After uploading files to S3, you can trigger the MadXXX API endpoint to register the files for processing. The script supports:

- API key authentication
- Environment variable configuration
- CLI overrides for all settings
- Two modes: prefix-only or complete file list

## Security: API Key Management

**IMPORTANT:** API keys and endpoint URLs should NEVER be hardcoded or committed to git. Always use environment variables.

### Setup

**Add all configuration to .env file** (this file is gitignored):

```bash
# Edit .env
# Required: API credentials
MADXXX_API_KEY=your-api-key-here
MADXXX_API_URL=https://your-api-endpoint.com/api/v1/madxxx_tasks/job

# Optional: API timeout
MADXXX_API_TIMEOUT=30

# Optional: Job configuration (has defaults)
MADXXX_FUNCTION_NAME=register_audiofiles
MADXXX_MODULE_NAME=madxxx_workbench.audio.register_audio
MADXXX_SQS_QUEUE=madXXX_tasks_data_registration
MADXXX_SQS_REGION=eu-west-1
```

## Usage

### Basic Usage

Trigger endpoint using environment variables from .env:

```bash
python scripts/trigger_endpoint.py --session-id 42
```

This will:
- Read API key from `MADXXX_API_KEY` env variable
- Read endpoint URL from `MADXXX_API_URL` env variable
- Read job settings from `MADXXX_*` env variables (or use defaults)
- Send prefix-only mode (API lists files)

### File List Mode

Send complete list of uploaded files instead of just prefix:

```bash
python scripts/trigger_endpoint.py --session-id 42 --list-files
```

### Override Endpoint URL

Override the endpoint URL via CLI:

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --endpoint-url https://custom-endpoint.com/api/process
```

### Override API Key

Override API key via CLI (not recommended for production):

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --api-key "your-temporary-key"
```

### Override Job Settings

Override any job configuration via CLI:

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --function-name register_videofiles \
  --module-name madxxx_workbench.video.register_video \
  --sqs-queue video_processing_queue \
  --sqs-region us-east-1
```

### Custom Job Name

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --job-name "my_custom_job_name"
```

### Custom Timeout

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --timeout 60
```

## Configuration Priority

The script uses this priority order for all settings:

1. **CLI flags** (highest priority)
2. **Environment variables** (.env file)
3. **Hardcoded defaults** (lowest priority)

### Examples

```bash
# API key priority:
# 1. --api-key flag
# 2. MADXXX_API_KEY env var
# (required - no default)

# Endpoint URL priority:
# 1. --endpoint-url flag
# 2. MADXXX_API_URL env var
# (required - no default)

# Function name priority:
# 1. --function-name flag
# 2. MADXXX_FUNCTION_NAME env var
# 3. Default: "register_audiofiles"

# Timeout priority:
# 1. --timeout flag
# 2. MADXXX_API_TIMEOUT env var
# 3. Default: 30
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MADXXX_API_KEY` | **Yes** | None | API key for authentication |
| `MADXXX_API_URL` | **Yes** | None | MadXXX API endpoint URL |
| `MADXXX_API_TIMEOUT` | No | 30 | Request timeout in seconds |
| `MADXXX_FUNCTION_NAME` | No | register_audiofiles | Backend function to call |
| `MADXXX_MODULE_NAME` | No | madxxx_workbench.audio.register_audio | Python module path |
| `MADXXX_SQS_QUEUE` | No | madXXX_tasks_data_registration | SQS queue name |
| `MADXXX_SQS_REGION` | No | eu-west-1 | AWS region for SQS |

## Request Payload

The script sends the correct MadXXX API payload format:

### Payload Structure (MadXXX Job Format)

```json
{
  "job": {
    "arguments": [
      [
        "s3://bucket-name/C1/file1.wav",
        "s3://bucket-name/C1/file2.wav",
        "s3://bucket-name/C1/file3.wav"
      ]
    ],
    "function_name": "register_audiofiles",
    "keywords": {},
    "module_name": "madxxx_workbench.audio.register_audio",
    "name": "session_42_register_audiofiles"
  },
  "sqs_queue": "madXXX_tasks_data_registration",
  "sqs_region": "eu-west-1"
}
```

### Key Points

- **`job.arguments`**: Must be a list of lists containing S3 paths in format `s3://bucket/key`
- **`job.function_name`**: Backend function to call (from MADXXX_FUNCTION_NAME env var or default)
- **`job.module_name`**: Python module path (from MADXXX_MODULE_NAME env var or default)
- **`job.keywords`**: Custom parameters (optional, currently empty)
- **`job.name`**: Unique job name (auto-generated or custom via --job-name)
- **`sqs_queue`**: SQS queue name for async processing
- **`sqs_region`**: AWS region for SQS

### Two Modes

**1. Prefix Mode (default):**
```bash
python scripts/trigger_endpoint.py --session-id 42
```

Sends only the S3 prefix - API will list all files:
```json
{
  "job": {
    "arguments": [["s3://bucket-name/C1"]],
    ...
  }
}
```

**2. File List Mode (--list-files):**
```bash
python scripts/trigger_endpoint.py --session-id 42 --list-files
```

Loads all uploaded files from database and sends complete list:
```json
{
  "job": {
    "arguments": [[
      "s3://bucket-name/C1/SENSOR_001/file1.wav",
      "s3://bucket-name/C1/SENSOR_001/file2.wav",
      ...
    ]],
    ...
  }
}
```

## Authentication Headers

The MadXXX API uses simple API key authentication:

```
accept: application/json
api_key: your-api-key-here
Content-Type: application/json
```

**Note:** The API does NOT use `Authorization: Bearer` format. It uses a direct `api_key` header.

## Response Handling

The script accepts these status codes as successful:
- 200 OK
- 201 Created
- 202 Accepted

Example output:

```
==========================================================================================
📡 TRIGGER MADXXX ENDPOINT
==========================================================================================
📋 Session ID: 42
📁 Bucket: my-bucket
📂 Prefix: C1
📊 Files uploaded: 1,234
🌐 Endpoint: https://your-api-endpoint.com/api/v1/madxxx_tasks/job
📤 Sending request to MadXXX API...
🔑 Using API key authentication
📦 Job name: session_42_register_audiofiles
📦 Function: register_audiofiles
📦 Files/paths: 1
✅ Endpoint triggered successfully!
📥 Status Code: 200
📥 Response: {
  "status": "success",
  "job_id": "abc-123",
  "message": "Job queued for processing"
}
🆔 Job ID: abc-123
```

## Error Handling

### Common Errors

**No endpoint URL provided:**
```
❌ No endpoint URL provided. Set MADXXX_API_URL in .env or use --endpoint-url
```
Solution: Set MADXXX_API_URL in .env or use --endpoint-url flag

**No API key provided:**
```
❌ No API key provided. Set MADXXX_API_KEY in .env or use --api-key
```
Solution: Set MADXXX_API_KEY in .env or use --api-key flag

**Session not found:**
```
❌ Session not found: 42
```
Solution: Verify session ID exists in database

**Request timeout:**
```
❌ Request timeout after 30s
```
Solution: Increase timeout with --timeout flag or check endpoint availability

**Authentication error:**
```
❌ Endpoint returned error: 401
📥 Response: Unauthorized
```
Solution: Verify API key is correct in .env file

## Integration with Master Pipeline

The master script can automatically trigger the endpoint after upload:

```bash
python scripts/master.py \
  --config config_files/my_config.json \
  --endpoint-url https://api.example.com/register
```

Or use environment variables:

```bash
# Set in .env
MADXXX_API_URL=https://api.example.com/register
MADXXX_API_KEY=your-key

# Run master pipeline
python scripts/master.py --config config_files/my_config.json
```

## Testing

### Test with webhook.site

Use webhook.site for testing without a real endpoint:

```bash
# Create a unique URL at https://webhook.site
# Then test:
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --endpoint-url https://webhook.site/your-unique-id \
  --auth-type none
```

### Test with dry-run

The upload script supports --dry-run which won't trigger the endpoint but will show what would be sent.

## Security Best Practices

1. ✅ **DO** store API keys and endpoint URLs in .env file
2. ✅ **DO** add .env to .gitignore
3. ✅ **DO** use environment variables in production
4. ✅ **DO** use HTTPS endpoints only
5. ✅ **DO** use .env.example with placeholder values for documentation
6. ❌ **DON'T** commit API keys to git
7. ❌ **DON'T** hardcode endpoint URLs in code
8. ❌ **DON'T** share .env files
9. ❌ **DON'T** use plain HTTP in production

## Troubleshooting

### Check environment variables

```bash
# Verify .env is loaded
cat .env | grep MADXXX

# Test environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('MADXXX_API_KEY'))"
```

### Verbose output

The script shows the full payload being sent. Check this to verify:
- Correct endpoint URL
- Authentication headers
- Session data
- Job configuration parameters

### Test endpoint connectivity

```bash
# Test if endpoint is reachable
curl -X POST https://your-endpoint.com/api/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"test": "data"}'
```
