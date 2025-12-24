# Endpoint Integration Guide

This guide explains how to use the `trigger_endpoint.py` script to integrate with external APIs for downstream processing.

## Overview

After uploading files to S3, you can trigger an external endpoint to register the files for processing. The script supports:

- Bearer token authentication
- API key authentication
- Job configuration files
- Environment variable configuration
- CLI overrides

## Security: API Key Management

**IMPORTANT:** API keys should NEVER be stored in config files or committed to git. Always use environment variables.

### Setup

1. **Add API key to .env file** (this file is gitignored):
   ```bash
   # Edit .env
   MADXXX_API_KEY=your-api-key-here
   MADXXX_API_URL=https://your-api-endpoint.com/api/register
   ```

2. **Job configuration** should NOT contain the API key:
   ```json
   {
     "api_keys": {
       "auth_type": "bearer"
     },
     "endpoints": {
       "default": "https://your-api-endpoint.com/api/register"
     }
   }
   ```

## Usage

### Basic Usage

Trigger endpoint using environment variables:

```bash
python scripts/trigger_endpoint.py --session-id 42
```

This will:
- Read API key from `MADXXX_API_KEY` env variable
- Read endpoint URL from `MADXXX_API_URL` env variable
- Use Bearer token authentication (default)
- Send session information to the endpoint

### Using Job Configuration

Use a job configuration file for additional parameters:

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --job-config config_files/job_config.json
```

The job config can include:
- Endpoint URL
- Authentication type
- Job templates (function names, SQS queues, etc.)
- Default settings (batch size, file extensions, etc.)

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

### Different Authentication Types

Use API Key header authentication instead of Bearer token:

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --auth-type apikey
```

No authentication:

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --auth-type none
```

### Override Batch Size

```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --job-config config_files/job_config.json \
  --batch-size 1000
```

## Configuration Priority

The script uses this priority order for configuration:

1. **CLI flags** (highest priority)
2. **Environment variables**
3. **Job config file**
4. **Defaults** (lowest priority)

### Example

```bash
# API key priority:
# 1. --api-key flag
# 2. MADXXX_API_KEY env var
# 3. job_config.json api_keys.madxxx_api_key (NOT RECOMMENDED)

# Endpoint URL priority:
# 1. --endpoint-url flag
# 2. MADXXX_API_URL env var
# 3. job_config.json endpoints.default
```

## Job Configuration File

### Structure

```json
{
  "api_keys": {
    "auth_type": "bearer",
    "aws_profiles": {
      "default": "aws-eos",
      "production": "aws-production"
    }
  },
  "endpoints": {
    "default": "https://api.example.com/register"
  },
  "default_settings": {
    "batch_size": 500,
    "batch_delay": 2,
    "max_files": null,
    "file_extensions": [".wav", ".mp3", ".flac"],
    "aws_region": "eu-west-1",
    "recursive": true
  },
  "job_templates": {
    "audio_processing": {
      "function_name": "register_audiofiles",
      "module_name": "madxxx_workbench.audio.register_audio",
      "sqs_queue": "madXXX_tasks_data_registration",
      "sqs_region": "eu-west-1"
    }
  },
  "logging": {
    "database_enabled": true,
    "log_level": "INFO",
    "save_payload_samples": true
  }
}
```

### Parameters

- **api_keys.auth_type**: Authentication method (bearer, apikey, none)
- **endpoints.default**: Default endpoint URL
- **default_settings**: Settings to include in request payload
  - **batch_size**: Number of files to process per batch
  - **batch_delay**: Delay between batches in seconds
  - **file_extensions**: Supported file types
- **job_templates**: Predefined job configurations
  - **function_name**: Function to call on backend
  - **module_name**: Module path
  - **sqs_queue**: SQS queue name for async processing
  - **sqs_region**: AWS region for SQS

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
- **`job.function_name`**: Backend function to call (from job_config.json)
- **`job.module_name`**: Python module path (from job_config.json)
- **`job.keywords`**: Custom parameters (optional)
- **`job.name`**: Unique job name (auto-generated or custom)
- **`sqs_queue`**: SQS queue name for async processing
- **`sqs_region`**: AWS region for SQS

### Two Modes

**1. Prefix Mode (default):**
```bash
python scripts/trigger_endpoint.py --session-id 42 --job-config config_files/job_config.json
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
python scripts/trigger_endpoint.py --session-id 42 --list-files --job-config config_files/job_config.json
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
📡 TRIGGER ENDPOINT
==========================================================================================
📋 Session ID: 42
📁 Bucket: my-bucket
📂 Prefix: C1
🌐 Endpoint: https://api.example.com/register
🔐 Auth Type: bearer
🔑 Using Bearer token authentication
📋 Loaded job config: config_files/job_config.json
📤 Sending request...
📦 Payload: {
  "session_id": 42,
  "bucket_name": "my-bucket",
  ...
}
✅ Endpoint triggered successfully
📥 Status Code: 200
📥 Response: {
  "status": "success",
  "job_id": "abc-123",
  "message": "Files queued for processing"
}
```

## Error Handling

### Common Errors

**No endpoint URL provided:**
```
❌ No endpoint URL provided. Use --endpoint-url, MADXXX_API_URL env var, or job config
```
Solution: Set MADXXX_API_URL in .env or use --endpoint-url flag

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

1. ✅ **DO** store API keys in .env file
2. ✅ **DO** add .env to .gitignore
3. ✅ **DO** use environment variables in production
4. ✅ **DO** use HTTPS endpoints only
5. ❌ **DON'T** commit API keys to git
6. ❌ **DON'T** store API keys in job_config.json
7. ❌ **DON'T** share .env files
8. ❌ **DON'T** use plain HTTP in production

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
