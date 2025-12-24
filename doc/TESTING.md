# Testing Guide

This guide explains how to test the Data Uploader before using it with production data.

## Pre-Flight Checks

Before uploading large datasets, perform these validation steps:

### 1. Database Connection Test

```bash
# Start database
docker-compose up -d

# Wait for database to be ready (check logs)
docker-compose logs -f postgres

# Initialize database
python scripts/init_db.py

# Verify tables were created
docker-compose exec postgres psql -U uploader -d data_uploader -c "\dt"
```

Expected output should show tables: `projects`, `sync_sessions`, `file_uploads`, `config_history`

### 2. AWS Credentials Test

```bash
# Test AWS credentials
aws sts get-caller-identity --profile your-profile-name

# Test S3 access
aws s3 ls s3://your-bucket-name --profile your-profile-name
```

### 3. Dry Run Test

Create a test configuration and run in dry-run mode:

```bash
# Create test config
cat > config_files/test_config.json << EOF
{
    "local_directory": "/path/to/test/data",
    "bucket_name": "your-test-bucket",
    "s3_prefix": "TEST",
    "max_workers": 5,
    "aws_region": "eu-west-1",
    "times_to_retry": 3,
    "aws_profile": "your-profile",
    "use_find": "yes"
}
EOF

# Run dry run
python scripts/upload.py --config config_files/test_config.json --dry-run
```

This will:
- Verify directory exists
- Check AWS credentials
- Scan files
- Show what would be uploaded
- NOT actually upload anything

## Test Scenarios

### Scenario 1: Small Dataset Test

Test with a small dataset (10-100 files) before large uploads.

1. **Prepare test data**
   ```bash
   mkdir -p /tmp/test_upload/SENSOR_001
   # Add some test files (wav, jpg, mp4)
   ```

2. **Create test config**
   ```json
   {
       "local_directory": "/tmp/test_upload",
       "bucket_name": "your-test-bucket",
       "s3_prefix": "TEST_SMALL",
       "max_workers": 5,
       "aws_region": "eu-west-1",
       "times_to_retry": 3,
       "aws_profile": "your-profile",
       "use_find": "yes"
   }
   ```

3. **Run upload**
   ```bash
   python scripts/upload.py --config config_files/test_small.json
   ```

4. **Verify results**
   ```bash
   # Check S3
   aws s3 ls s3://your-test-bucket/TEST_SMALL/ --recursive --profile your-profile

   # Check database
   docker-compose exec postgres psql -U uploader -d data_uploader \
     -c "SELECT * FROM sync_sessions ORDER BY id DESC LIMIT 1;"
   ```

### Scenario 2: Resume Test

Test that resume capability works correctly.

1. **Start upload and interrupt it** (Ctrl+C during upload)
   ```bash
   python scripts/upload.py --config config_files/test_config.json
   # Press Ctrl+C after some files upload
   ```

2. **Re-run same upload**
   ```bash
   python scripts/upload.py --config config_files/test_config.json
   ```

3. **Verify**
   - Should skip already uploaded files
   - Should show "files already uploaded and excluded"
   - Should not re-upload successful files

### Scenario 3: Retry Test

Test retry mechanism for failed uploads.

1. **Simulate failures** (temporarily remove AWS credentials or use wrong bucket)
   ```bash
   # Use invalid profile to cause failures
   python scripts/upload.py --config config_files/test_config.json --aws-profile invalid-profile
   ```

2. **Fix credentials and retry**
   ```bash
   # Get session ID from output
   python scripts/retry.py --session-id <id> --auto-retry
   ```

3. **Verify**
   - Failed files should be retried
   - Database should update status to 'uploaded'

### Scenario 4: Performance Test

Test with medium dataset to estimate performance.

1. **Prepare 1000-10000 test files**
   ```bash
   # Create test files
   for i in {1..1000}; do
     echo "test" > /tmp/test_upload/SENSOR_001/file_$i.wav
   done
   ```

2. **Upload with timing**
   ```bash
   time python scripts/upload.py --config config_files/test_perf.json
   ```

3. **Analyze performance**
   - Files per second
   - Time to scan files
   - Time to upload
   - Use results to estimate production upload time

### Scenario 5: Pipeline Test

Test the complete master pipeline.

```bash
# Run full pipeline with test endpoint (optional)
python scripts/master.py \
  --config config_files/test_config.json \
  --endpoint-url https://webhook.site/your-unique-url
```

Verify:
- Upload completes
- Retry runs (if there were failures)
- Endpoint receives correct payload

## Database Queries for Testing

### Check session status
```sql
SELECT
    id,
    status,
    total_files,
    files_uploaded,
    files_failed,
    files_skipped
FROM sync_sessions
ORDER BY id DESC
LIMIT 5;
```

### Check file upload status
```sql
SELECT
    status,
    COUNT(*) as count,
    SUM(file_size) as total_size
FROM file_uploads
WHERE session_id = <session_id>
GROUP BY status;
```

### Check for duplicate uploads
```sql
SELECT
    s3_key,
    COUNT(*) as upload_count
FROM file_uploads
WHERE status = 'uploaded'
GROUP BY s3_key
HAVING COUNT(*) > 1;
```

Should return 0 rows (no duplicates).

## Common Issues and Solutions

### Issue: "Directory does not exist"
**Solution:** Check local_directory path in config file. Use absolute paths.

### Issue: "Access denied to bucket"
**Solution:**
- Verify AWS credentials: `aws sts get-caller-identity --profile your-profile`
- Check IAM permissions for S3 bucket
- Verify bucket name is correct

### Issue: "Database connection failed"
**Solution:**
- Check PostgreSQL is running: `docker-compose ps`
- Verify .env file has correct credentials
- Check database logs: `docker-compose logs postgres`

### Issue: "Permission denied" when scanning files
**Solution:**
- Check file permissions on local directory
- On Unix, you may need read access: `chmod -R +r /path/to/data`

### Issue: Upload is very slow
**Solution:**
- Increase max_workers (try 20-30)
- Check network connection to S3
- Use `use_find: "yes"` on Unix systems for faster scanning
- Check if files are on slow storage (network drives)

### Issue: Files uploaded but not in database
**Solution:**
- Check for errors in terminal output
- Verify database connection during upload
- Check database logs for errors

## Validation Checklist

Before production use, verify:

- [ ] Database connection works
- [ ] AWS credentials are valid
- [ ] S3 bucket is accessible
- [ ] Small test upload succeeds
- [ ] Resume capability works (skip already uploaded files)
- [ ] Retry mechanism works
- [ ] Progress bar displays correctly
- [ ] Database tracks all files
- [ ] No duplicate uploads occur
- [ ] Performance is acceptable
- [ ] Configuration is correct (bucket name, prefix, region)

## Clean Up Test Data

After testing:

```bash
# Delete test files from S3
aws s3 rm s3://your-test-bucket/TEST/ --recursive --profile your-profile

# Delete test sessions from database
docker-compose exec postgres psql -U uploader -d data_uploader << EOF
DELETE FROM sync_sessions WHERE s3_prefix LIKE 'TEST%';
EOF

# Remove local test files
rm -rf /tmp/test_upload
```

## Production Readiness

Once all tests pass:

1. Create production configuration file
2. Double-check bucket name and prefix
3. Verify local directory path is correct
4. Start with dry-run mode
5. Monitor first few uploads closely
6. Set up Grafana dashboards for monitoring
7. Document session IDs for your uploads

## Performance Benchmarks

Expected performance (varies by network, file size, etc.):

- **File scanning**: 100-200 files/second (with find command)
- **Upload speed**: 1-10 files/second (depends on file size and workers)
- **Resume check**: Loads 300k+ files from DB in ~2 seconds

For 300,000 files at 5 files/second = ~16 hours upload time
