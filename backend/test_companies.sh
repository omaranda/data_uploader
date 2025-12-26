#!/bin/bash
# Test companies endpoints

echo "=== Getting auth token (admin) ==="
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo "Token: ${TOKEN:0:50}..."
echo ""

echo "=== List companies (admin should see their own company) ==="
curl -s -X GET 'http://localhost:8000/api/companies/' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Get company by ID (company 1) ==="
curl -s -X GET 'http://localhost:8000/api/companies/1' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Update company ==="
curl -s -X PUT 'http://localhost:8000/api/companies/1' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "contact_email": "updated@defaultcompany.com"
  }' | python3 -m json.tool
echo ""

echo "=== Try to get non-existent company (should fail) ==="
curl -s -X GET 'http://localhost:8000/api/companies/999' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
