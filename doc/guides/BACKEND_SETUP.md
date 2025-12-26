# FastAPI Backend Setup Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose (for running database services)

---

## Quick Start

### 1. Start Database Services

```bash
# From project root
docker-compose up -d

# Verify services are running
docker-compose ps
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

### 2. Set Up Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
./venv/bin/activate  # Alternative

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (default values work for local development)
```

### 4. Run the API

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Test Authentication

```bash
# Run the test script
./test_auth.sh
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings and configuration
│   ├── database.py             # SQLAlchemy database setup
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── cycle.py
│   │   ├── sync_session.py
│   │   └── file_upload.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── company.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── cycle.py
│   │   ├── sync_session.py
│   │   └── file_upload.py
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── middleware/             # Authentication middleware
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py         # Password hashing & JWT
│   │   └── company_scoped.py   # Company-scoped queries
│   ├── services/               # Business logic (future)
│   │   └── __init__.py
│   └── workers/                # Background workers (future)
│       └── __init__.py
├── venv/                       # Python virtual environment
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (local)
├── .env.example               # Example environment file
└── test_auth.sh               # Authentication test script
```

---

## Database Models

### Company
- Client organizations in the multi-tenant system
- One-to-many: users, projects

### User
- Employees of companies
- Roles: `admin`, `user`
- Authentication via username/password (bcrypt hashed)

### Project
- S3 upload projects
- Company-scoped (users only see their company's projects)
- One-to-many: cycles, sessions

### Cycle
- Structured data collection cycles (C1, C2, C3, etc.)
- Linked to projects
- Statuses: `pending`, `in_progress`, `completed`, `incomplete`

### SyncSession
- Individual upload sessions
- Tracks files uploaded, failed, skipped
- Linked to project, cycle, and user

### FileUpload
- Individual file upload records
- Tracks per-file status and metadata

---

## Configuration

### Environment Variables (.env)

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=data_uploader
DB_USER=uploader
DB_PASSWORD=uploader_pass

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT Authentication
JWT_SECRET=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (JSON array format)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Application
DEBUG=true
```

**Important Security Notes:**
- Change `JWT_SECRET` in production (use `openssl rand -hex 32`)
- Use strong passwords for database
- Enable HTTPS in production
- Configure CORS strictly

---

## Dependencies

### Core Framework
- `fastapi==0.109.0` - Web framework
- `uvicorn[standard]==0.27.0` - ASGI server
- `python-multipart==0.0.6` - Form data parsing

### Database
- `sqlalchemy==2.0.25` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL driver
- `alembic==1.13.1` - Database migrations

### Data Validation
- `pydantic==2.5.3` - Data validation
- `pydantic-settings==2.1.0` - Settings management
- `email-validator==2.1.0` - Email validation

### Authentication & Security
- `python-jose[cryptography]==3.3.0` - JWT tokens
- `passlib==1.7.4` - Password hashing
- `bcrypt==4.0.1` - Bcrypt implementation
- `python-dotenv==1.0.0` - Environment variables

### Job Queue
- `redis==5.0.1` - Redis client
- `rq==1.16.1` - Redis Queue

### HTTP Client
- `httpx==0.26.0` - HTTP client

### Development
- `pytest==7.4.4` - Testing framework
- `pytest-asyncio==0.23.3` - Async testing

---

## Testing

### Manual Testing with Curl

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get current user (replace TOKEN)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

### Using the Test Script

```bash
cd backend
./test_auth.sh
```

### Interactive Testing

Visit http://localhost:8000/docs for Swagger UI with:
- Interactive API documentation
- Try out endpoints directly
- View request/response schemas

---

## Common Issues

### 1. Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### 2. Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### 3. Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### 4. Bcrypt Errors

If you see bcrypt-related errors, ensure you have bcrypt 4.0.1:

```bash
pip install bcrypt==4.0.1
```

---

## Development Workflow

1. **Make changes** to code
2. **Server auto-reloads** (thanks to `--reload` flag)
3. **Test** using Swagger UI or curl
4. **Check logs** in terminal for errors

---

## Next Steps

After setup:
1. ✅ Authentication is working
2. Implement CRUD routers (Week 3)
3. Add job queue for uploads (Week 4)
4. Build Next.js frontend (Week 5-6)

---

## Troubleshooting

### Check Service Status

```bash
# Database
docker-compose exec postgres psql -U uploader -d data_uploader -c "SELECT 1;"

# Redis
docker-compose exec redis redis-cli ping
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs postgres
docker-compose logs redis

# Follow logs
docker-compose logs -f
```

### Reset Database

```bash
# WARNING: This deletes all data
docker-compose down -v
docker-compose up -d
```

---

Last Updated: December 25, 2025
