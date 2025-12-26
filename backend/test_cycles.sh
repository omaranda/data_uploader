#!/bin/bash
# Test cycles endpoints

echo "=== Getting auth token (admin) ==="
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "Token: ${TOKEN:0:50}..."
echo ""

echo "=== Create a project first (needed for cycles) ==="
PROJECT_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/projects/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "project_name": "Cycle Test Project",
    "bucket_name": "cycle-test-bucket",
    "aws_region": "us-east-1",
    "description": "Project for testing cycles"
  }')

PROJECT_ID=$(echo $PROJECT_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "Created project ID: $PROJECT_ID"
echo ""

echo "=== List all cycles (should be empty) ==="
curl -s -X GET 'http://localhost:8000/api/cycles/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Create cycle C1 ==="
curl -s -X POST 'http://localhost:8000/api/cycles/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"cycle_name\": \"C1\",
    \"cycle_number\": 1,
    \"s3_prefix\": \"cycle1/\",
    \"status\": \"pending\",
    \"description\": \"First cycle\"
  }" | python3 -m json.tool
echo ""

echo "=== Create cycle C2 ==="
curl -s -X POST 'http://localhost:8000/api/cycles/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"cycle_name\": \"C2\",
    \"cycle_number\": 2,
    \"s3_prefix\": \"cycle2/\",
    \"status\": \"pending\",
    \"description\": \"Second cycle\"
  }" | python3 -m json.tool
echo ""

echo "=== List cycles for project ==="
curl -s -X GET "http://localhost:8000/api/cycles/?project_id=$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Get cycle by ID (cycle 1) ==="
curl -s -X GET 'http://localhost:8000/api/cycles/1' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Update cycle status ==="
curl -s -X PUT 'http://localhost:8000/api/cycles/1' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "in_progress",
    "description": "First cycle - in progress"
  }' | python3 -m json.tool
echo ""

echo "=== Try to create duplicate cycle name (should fail) ==="
curl -s -X POST 'http://localhost:8000/api/cycles/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"cycle_name\": \"C1\",
    \"cycle_number\": 99,
    \"s3_prefix\": \"duplicate/\"
  }" | python3 -m json.tool
echo ""

echo "=== Filter cycles by status ==="
curl -s -X GET 'http://localhost:8000/api/cycles/?status=pending' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Delete cycle 2 ==="
curl -s -X DELETE 'http://localhost:8000/api/cycles/2' \
  -H "Authorization: Bearer $TOKEN" -w "\nHTTP Status: %{http_code}\n"
echo ""
