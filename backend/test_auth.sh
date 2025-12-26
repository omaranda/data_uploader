#!/bin/bash
# Test authentication endpoints

echo "=== Testing Login ==="
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "Access token obtained: ${TOKEN:0:50}..."

echo ""
echo "=== Testing /me endpoint ==="
curl -s -X GET 'http://localhost:8000/api/auth/me' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== Testing invalid credentials ==="
curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"wrongpassword"}' | python3 -m json.tool
