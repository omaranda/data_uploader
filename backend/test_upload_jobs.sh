#!/bin/bash
# Test upload job queue system

echo "=== Getting auth token (admin) ==="
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "Token: ${TOKEN:0:50}..."
echo ""

echo "=== Create a project for upload testing ==="
PROJECT_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/projects/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "project_name": "Upload Test Project",
    "bucket_name": "test-upload-bucket",
    "aws_region": "us-east-1",
    "description": "Project for testing upload jobs"
  }')

PROJECT_ID=$(echo $PROJECT_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "Created project ID: $PROJECT_ID"
echo ""

echo "=== Create a cycle ==="
CYCLE_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/cycles/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"cycle_name\": \"C1\",
    \"cycle_number\": 1,
    \"s3_prefix\": \"test/cycle1/\",
    \"status\": \"pending\"
  }")

CYCLE_ID=$(echo $CYCLE_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "Created cycle ID: $CYCLE_ID"
echo ""

echo "=== Create a test directory with sample files ==="
TEST_DIR="/tmp/upload_test_data_$(date +%s)"
mkdir -p "$TEST_DIR"
echo "test file 1" > "$TEST_DIR/file1.txt"
echo "test file 2" > "$TEST_DIR/file2.txt"
mkdir -p "$TEST_DIR/subdir"
echo "test file 3" > "$TEST_DIR/subdir/file3.txt"
echo "Created test directory: $TEST_DIR"
echo ""

echo "=== Create a sync session ==="
SESSION_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/sessions/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"cycle_id\": $CYCLE_ID,
    \"local_directory\": \"$TEST_DIR\",
    \"s3_prefix\": \"test/cycle1/batch1/\",
    \"aws_profile\": \"default\",
    \"max_workers\": 5,
    \"times_to_retry\": 2,
    \"use_find\": true
  }")

SESSION_ID=$(echo $SESSION_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "Created session ID: $SESSION_ID"
echo ""

echo "=== Verify session is in pending status ==="
curl -s -X GET "http://localhost:8000/api/sessions/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c 'import sys,json; data=json.load(sys.stdin); print(f"Session status: {data[\"status\"]}")'
echo ""

echo "=== Start upload job ==="
JOB_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/uploads/start' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"session_id\": $SESSION_ID
  }")

echo "$JOB_RESPONSE" | python3 -m json.tool

JOB_ID=$(echo $JOB_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')
echo ""
echo "Job ID: $JOB_ID"
echo ""

echo "=== Check job status ==="
curl -s -X GET "http://localhost:8000/api/uploads/status/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Wait a few seconds for job to process ==="
sleep 5
echo ""

echo "=== Check job status again ==="
curl -s -X GET "http://localhost:8000/api/uploads/status/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Check session status ==="
curl -s -X GET "http://localhost:8000/api/sessions/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c 'import sys,json; data=json.load(sys.stdin); print(f"Session status: {data[\"status\"]}")'
echo ""

echo "=== Get session statistics ==="
curl -s -X GET "http://localhost:8000/api/sessions/stats?project_id=$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Try to start the same session again (should fail - not pending) ==="
curl -s -X POST 'http://localhost:8000/api/uploads/start' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"session_id\": $SESSION_ID
  }" | python3 -m json.tool
echo ""

echo "=== Cleanup test directory ==="
rm -rf "$TEST_DIR"
echo "Removed test directory: $TEST_DIR"
echo ""

echo "=== Test complete! ==="
