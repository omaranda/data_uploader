#!/bin/bash
# Test users endpoints

echo "=== Getting auth token (admin) ==="
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "Token: ${TOKEN:0:50}..."
echo ""

echo "=== List all users (should show admin user) ==="
curl -s -X GET 'http://localhost:8000/api/users/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Create a new user ==="
curl -s -X POST 'http://localhost:8000/api/users/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "company_id": 1,
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpass123",
    "full_name": "Test User",
    "role": "user",
    "is_active": true
  }' | python3 -m json.tool
echo ""

echo "=== List users again (should show 2 users) ==="
curl -s -X GET 'http://localhost:8000/api/users/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Get user by ID (user 2) ==="
curl -s -X GET 'http://localhost:8000/api/users/2' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Update user ==="
curl -s -X PUT 'http://localhost:8000/api/users/2' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "full_name": "Test User Updated",
    "email": "updated@example.com"
  }' | python3 -m json.tool
echo ""

echo "=== Try to create duplicate username (should fail) ==="
curl -s -X POST 'http://localhost:8000/api/users/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "company_id": 1,
    "username": "testuser",
    "email": "another@example.com",
    "password": "pass123",
    "full_name": "Another User",
    "role": "user"
  }' | python3 -m json.tool
echo ""

echo "=== Try to delete yourself (should fail) ==="
curl -s -X DELETE 'http://localhost:8000/api/users/1' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Delete user 2 (should succeed) ==="
curl -s -X DELETE 'http://localhost:8000/api/users/2' \
  -H "Authorization: Bearer $TOKEN" -w "\nHTTP Status: %{http_code}\n"
echo ""
