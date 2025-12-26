#!/bin/bash
# Test sessions endpoints

echo "=== Getting auth token (admin) ==="
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "Token: ${TOKEN:0:50}..."
echo ""

echo "=== Create a project first (needed for sessions) ==="
PROJECT_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/projects/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "project_name": "Session Test Project",
    "bucket_name": "session-test-bucket",
    "aws_region": "us-east-1"
  }')

PROJECT_ID=$(echo $PROJECT_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "Created project ID: $PROJECT_ID"
echo ""

echo "=== Create a cycle for the project ==="
CYCLE_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/cycles/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"cycle_name\": \"C1\",
    \"cycle_number\": 1,
    \"s3_prefix\": \"cycle1/\",
    \"status\": \"pending\"
  }")

CYCLE_ID=$(echo $CYCLE_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "Created cycle ID: $CYCLE_ID"
echo ""

echo "=== List all sessions (should be empty) ==="
curl -s -X GET 'http://localhost:8000/api/sessions/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Create a new session ==="
curl -s -X POST 'http://localhost:8000/api/sessions/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"cycle_id\": $CYCLE_ID,
    \"local_directory\": \"/tmp/test-data\",
    \"s3_prefix\": \"cycle1/batch1/\",
    \"aws_profile\": \"default\",
    \"max_workers\": 10,
    \"times_to_retry\": 3,
    \"use_find\": true
  }" | python3 -m json.tool
echo ""

echo "=== List sessions again (should show 1 session) ==="
curl -s -X GET 'http://localhost:8000/api/sessions/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Get session by ID (session 1) ==="
curl -s -X GET 'http://localhost:8000/api/sessions/1' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Update session status ==="
curl -s -X PUT 'http://localhost:8000/api/sessions/1' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "in_progress",
    "total_files": 100,
    "files_uploaded": 50
  }' | python3 -m json.tool
echo ""

echo "=== Get session stats ==="
curl -s -X GET 'http://localhost:8000/api/sessions/stats' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Filter sessions by project ==="
curl -s -X GET "http://localhost:8000/api/sessions/?project_id=$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Try to delete active session (should fail) ==="
curl -s -X DELETE 'http://localhost:8000/api/sessions/1' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Update session to completed ==="
curl -s -X PUT 'http://localhost:8000/api/sessions/1' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "completed",
    "files_uploaded": 100
  }' | python3 -m json.tool
echo ""

echo "=== Delete completed session (should succeed) ==="
curl -s -X DELETE 'http://localhost:8000/api/sessions/1' \
  -H "Authorization: Bearer $TOKEN" -w "\nHTTP Status: %{http_code}\n"
echo ""
