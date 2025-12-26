# Data Uploader API Documentation

## Overview

Multi-tenant FastAPI backend for the data uploader system with JWT authentication and company-scoped data access.

**Base URL:** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs` (Swagger UI)
**ReDoc:** `http://localhost:8000/redoc`

---

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with two token types:
- **Access Token**: Short-lived (30 minutes) - used for API requests
- **Refresh Token**: Long-lived (7 days) - used to obtain new access tokens

### Token Format

Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### POST /api/auth/login

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: User account disabled

---

### POST /api/auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- `401 Unauthorized`: Invalid or expired refresh token

---

### GET /api/auth/me

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "System Administrator",
  "role": "admin",
  "company_id": 1,
  "is_active": true
}
```

**Errors:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: User account disabled

---

## Health Check

### GET /health

Check API health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "data-uploader-api",
  "version": "1.0.0"
}
```

---

## Data Models

### User Roles

- `admin`: Full access to all resources within their company
- `user`: Standard user access within their company

### Company Scoping

All data is scoped by company. Users can only access data belonging to their company:
- Projects
- Users (within same company)
- Cycles (via projects)
- Sessions (via projects)

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Testing Authentication

Use the provided test script:

```bash
cd backend
./test_auth.sh
```

Or test manually with curl:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get user info (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Development

### Running the API

```bash
cd backend
source venv/bin/activate  # or ./venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

See `.env.example` for required configuration:
- Database connection (PostgreSQL)
- Redis connection
- JWT secrets
- CORS origins

---

## Next Steps (Week 3)

The following endpoints will be implemented:

- **Companies**: CRUD operations (admin only)
- **Users**: CRUD operations (company-scoped)
- **Projects**: CRUD operations (company-scoped)
- **Cycles**: CRUD operations
- **Sessions**: CRUD operations and statistics

---

Last Updated: December 25, 2025
