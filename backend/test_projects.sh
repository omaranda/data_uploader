#!/bin/bash
# Test projects endpoints

echo "=== Getting auth token ==="
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "Token: ${TOKEN:0:50}..."
echo ""

echo "=== List all projects (should be empty) ==="
curl -s -X GET 'http://localhost:8000/api/projects/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Create a new project ==="
curl -s -X POST 'http://localhost:8000/api/projects/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "project_name": "Test Project 1",
    "bucket_name": "test-bucket-001",
    "aws_region": "eu-west-1",
    "description": "First test project",
    "is_active": true
  }' | python3 -m json.tool
echo ""

echo "=== List projects again (should show 1 project) ==="
curl -s -X GET 'http://localhost:8000/api/projects/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Get project by ID (project 1) ==="
curl -s -X GET 'http://localhost:8000/api/projects/1' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Update project ==="
curl -s -X PUT 'http://localhost:8000/api/projects/1' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "description": "Updated description"
  }' | python3 -m json.tool
echo ""

echo "=== Try to create duplicate project (should fail) ==="
curl -s -X POST 'http://localhost:8000/api/projects/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "project_name": "Test Project 1",
    "bucket_name": "another-bucket",
    "aws_region": "us-east-1"
  }' | python3 -m json.tool
echo ""
