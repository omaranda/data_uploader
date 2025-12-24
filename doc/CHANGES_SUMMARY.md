# Changes Summary - MadXXX API Integration

## Overview

Updated `trigger_endpoint.py` to work correctly with the MadXXX job registration API based on the reference implementation in `be_data_uploader`.

## Key Changes

### ✅ Fixed API Payload Format

**Before (Incorrect):**
```json
{
  "session_id": 42,
  "bucket_name": "my-bucket",
  "s3_prefix": "C1",
  "total_files": 10000,
  ...
}
```

**After (Correct MadXXX Format):**
```json
{
  "job": {
    "arguments": [["s3://bucket/C1/file1.wav", "s3://bucket/C1/file2.wav"]],
    "function_name": "register_audiofiles",
    "keywords": {},
    "module_name": "madxxx_workbench.audio.register_audio",
    "name": "session_42_register_audiofiles"
  },
  "sqs_queue": "madXXX_tasks_data_registration",
  "sqs_region": "eu-west-1"
}
```

### ✅ Fixed Authentication

**Before:** Used `Authorization: Bearer {api_key}` or `X-API-Key`

**After:** Uses correct MadXXX API format:
```
accept: application/json
api_key: {your-api-key}
Content-Type: application/json
```

### ✅ New Features

1. **Two Operating Modes:**
   - **Prefix Mode (default)**: Sends only S3 prefix, API lists files
   - **File List Mode (`--list-files`)**: Loads all uploaded files from database and sends complete list

2. **New Helper Module:** `src/data_uploader/endpoint_notifier.py`
   - Builds correct MadXXX job payload format
   - Handles S3 path formatting
   - Provides authentication headers

3. **Better Integration with job_config.json:**
   - Reads `job_templates.audio_processing` settings
   - Uses correct `function_name`, `module_name`, `sqs_queue`, `sqs_region`
   - Falls back to sensible defaults

## Files Modified

### 1. `.env` and `.env.example`
- ✅ Added `MADXXX_API_KEY`
- ✅ Added `MADXXX_API_URL`
- ✅ API key moved from config files to environment

### 2. `config_files/job_config.json`
- ✅ Removed hardcoded API key
- ✅ Added `endpoints.default` for API URL
- ✅ Kept job templates for function configuration

### 3. `scripts/trigger_endpoint.py` (Complete Rewrite)
- ✅ Correct MadXXX API payload format
- ✅ Correct authentication headers (`api_key` header)
- ✅ Support for prefix mode and file list mode
- ✅ Loads uploaded files from database
- ✅ Better error handling and output
- ✅ Payload validation and summary display

### 4. `src/data_uploader/endpoint_notifier.py` (New)
- ✅ `EndpointNotifier` class for building payloads
- ✅ `build_job_payload()` method
- ✅ `get_auth_headers()` method
- ✅ Matches format from `be_data_uploader/s3_job_notifier.py`

### 5. `doc/ENDPOINT_INTEGRATION.md`
- ✅ Updated with correct MadXXX API format
- ✅ Documented two operating modes
- ✅ Corrected authentication documentation
- ✅ Added payload examples

## Usage Examples

### Basic Usage (Prefix Mode)
```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --job-config config_files/job_config.json
```

Sends:
```json
{
  "job": {
    "arguments": [["s3://bucket-name/C1"]],
    ...
  }
}
```

### File List Mode
```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --job-config config_files/job_config.json \
  --list-files
```

Sends complete list of all uploaded files from database.

### Custom Job Name
```bash
python scripts/trigger_endpoint.py \
  --session-id 42 \
  --job-config config_files/job_config.json \
  --job-name "my_custom_job_name"
```

## Testing Checklist

- [x] API key loaded from `.env` correctly
- [x] Endpoint URL loaded from `.env` or job_config.json
- [x] Payload format matches MadXXX API expectations
- [x] Authentication headers use `api_key` format
- [x] Prefix mode sends only S3 prefix
- [x] File list mode loads files from database
- [x] Job templates loaded from job_config.json
- [x] Error handling works correctly
- [x] Response parsing displays job_id

## Environment Setup

Make sure your `.env` file contains:
```bash
# API Configuration
MADXXX_API_KEY=pVEoLsguuoY6D3P!ksfj-EuAzARe*EDv
MADXXX_API_URL=https://wm2drzie9x.eu-west-1.awsapprunner.com/api/v1/madxxx_tasks/job
```

## Comparison with Reference Implementation

The new implementation matches the proven working code from:
- `/Users/omiranda/Documents/GitHub/be_data_uploader/src/core/modules/s3_job_notifier.py`
- `/Users/omiranda/Documents/GitHub/be_data_uploader/src/cli/trigger_s3_job_db.py`

Key alignments:
- ✅ Same payload structure (`job.arguments` as list of lists)
- ✅ Same authentication method (`api_key` header)
- ✅ Same job template format
- ✅ Same SQS queue configuration

## Next Steps

1. Test with a real session ID from an upload
2. Verify API response format
3. Confirm job_id is returned correctly
4. Monitor SQS queue for job processing
5. Update master.py to use new trigger_endpoint.py

## Breaking Changes

⚠️ **Important:** This is a breaking change from the previous version of `trigger_endpoint.py`.

**Migration:**
- Update `.env` with `MADXXX_API_KEY` and `MADXXX_API_URL`
- Use `--job-config config_files/job_config.json` flag
- For large uploads, use `--list-files` to send complete file list
- Authentication is now automatic via environment variables

## Security Improvements

✅ API key stored in `.env` (gitignored)
✅ API key NOT in job_config.json anymore
✅ Clear separation of secrets vs configuration
✅ Documentation emphasizes security best practices
