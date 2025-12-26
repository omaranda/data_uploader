# Data Uploader API - Backend

Multi-tenant FastAPI backend for the Data Uploader system with background job processing.

## Features

- 🔐 **JWT Authentication** - Secure login with access and refresh tokens
- 🏢 **Multi-Tenant Architecture** - Company-scoped data isolation
- 👥 **Role-Based Access Control** - Admin and user roles with different permissions
- 📁 **Full CRUD APIs** - Companies, Users, Projects, Cycles, Sessions
- 🔄 **Background Job Queue** - Redis + RQ for asynchronous upload processing
- 📊 **Real-Time Progress Tracking** - Database updates during upload execution
- 🔍 **Session Statistics** - Aggregate metrics for upload sessions

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose (for containerized setup)

### Development Setup

1. **Start PostgreSQL and Redis:**
   ```bash
   docker-compose up -d postgres redis
   ```

2. **Create virtual environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations:**
   - Migrations are automatically applied via docker-compose volumes

6. **Start the API server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start the RQ worker (in another terminal):**
   ```bash
   cd backend
   ./start_worker.sh
   ```

### Access the API

- **API Documentation (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### Default Credentials

- **Username:** `admin`
- **Password:** `admin123`
- **Company:** Default Company (ID: 1)

## API Endpoints

### Authentication

```
POST   /api/auth/login     - Login with username/password
POST   /api/auth/refresh   - Refresh access token
GET    /api/auth/me        - Get current user info
```

### Companies (Admin Only)

```
GET    /api/companies/              - List companies (own company only)
GET    /api/companies/{id}          - Get company details
PUT    /api/companies/{id}          - Update company
```

### Users

```
GET    /api/users/                  - List users (company-scoped)
GET    /api/users/{id}              - Get user details
POST   /api/users/                  - Create user (admin only)
PUT    /api/users/{id}              - Update user (admin only)
DELETE /api/users/{id}              - Delete user (admin only)
```

### Projects

```
GET    /api/projects/               - List projects (company-scoped)
GET    /api/projects/{id}           - Get project details
POST   /api/projects/               - Create project
PUT    /api/projects/{id}           - Update project
DELETE /api/projects/{id}           - Delete project
```

### Cycles

```
GET    /api/cycles/                 - List cycles (company-scoped)
GET    /api/cycles/{id}             - Get cycle details
POST   /api/cycles/                 - Create cycle
PUT    /api/cycles/{id}             - Update cycle
DELETE /api/cycles/{id}             - Delete cycle
```

### Sessions

```
GET    /api/sessions/               - List sessions (company-scoped)
GET    /api/sessions/{id}           - Get session details
GET    /api/sessions/stats          - Get session statistics
POST   /api/sessions/               - Create session
PUT    /api/sessions/{id}           - Update session
DELETE /api/sessions/{id}           - Delete session (not active)
```

### Uploads

```
POST   /api/uploads/start           - Start background upload job
GET    /api/uploads/status/{job_id} - Get job status
```

## Architecture

### Directory Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── project.py
│   │   ├── cycle.py
│   │   ├── sync_session.py
│   │   └── file_upload.py
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── project.py
│   │   ├── cycle.py
│   │   └── sync_session.py
│   ├── routers/                # API endpoint routers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── companies.py
│   │   ├── projects.py
│   │   ├── cycles.py
│   │   ├── sessions.py
│   │   └── uploads.py
│   ├── middleware/             # Custom middleware
│   │   └── auth.py            # JWT authentication
│   ├── services/               # Business logic services
│   │   └── queue.py           # Job queue management
│   ├── workers/                # Background workers
│   │   └── upload_worker.py   # Upload job processor
│   └── utils/                  # Utility functions
│       ├── security.py        # Password hashing, JWT
│       └── company_scoped.py  # Access control helpers
├── requirements.txt            # Python dependencies
├── start_worker.sh            # RQ worker startup script
└── .env.example               # Environment variables template
```

### Technology Stack

- **Framework:** FastAPI 0.109.0
- **Server:** Uvicorn (ASGI)
- **Database:** PostgreSQL 16 + SQLAlchemy 2.0
- **Cache/Queue:** Redis 7 + RQ (Redis Queue)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **Validation:** Pydantic v2
- **Migration:** Alembic

## Background Job System

The backend uses Redis Queue (RQ) for asynchronous upload processing:

1. **Job Enqueueing:**
   - User creates a session via `POST /api/sessions/`
   - User starts upload via `POST /api/uploads/start`
   - Job is queued to Redis with session configuration

2. **Worker Processing:**
   - RQ worker picks up the job
   - Updates session status to `in_progress`
   - Scans local directory for files
   - Updates progress in database after each file
   - Marks session as `completed` or `failed`

3. **Progress Monitoring:**
   - Poll job status: `GET /api/uploads/status/{job_id}`
   - Or query session directly: `GET /api/sessions/{session_id}`
   - Session object contains live statistics

### Starting the Worker

```bash
cd backend
./start_worker.sh
```

The worker script includes a macOS fork safety fix:
```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

## Multi-Tenant Security

### Company-Scoped Access

All data access is scoped to the user's company:

```python
# Example: List projects for current user's company
@router.get("/")
async def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Filter by company_id automatically
    projects = db.query(Project).filter(
        Project.company_id == current_user.company_id
    ).all()
    return projects
```

### Access Control Helpers

Located in `app/utils/company_scoped.py`:

- `verify_project_access()` - Check if user can access a project
- `verify_cycle_access()` - Check if user can access a cycle (via project)
- `verify_session_access()` - Check if user can access a session (via project)
- `get_project_company_id()` - Get company ID for a project

### Role-Based Permissions

**Admin Role:**
- Create/update/delete users
- Update company details
- Full access to company's data

**User Role:**
- Read-only access to users list
- Full access to projects, cycles, sessions
- Cannot modify other users or company settings

## Testing

### Run Integration Test

```bash
cd backend
./venv/bin/python3 test_upload_integration.py
```

This test verifies:
- ✅ Authentication
- ✅ Session creation
- ✅ Job enqueueing
- ✅ Worker processing
- ✅ Progress tracking
- ✅ Status updates

### Manual Testing with cURL

See test scripts:
- `test_auth.sh` - Authentication endpoints
- `test_projects.sh` - Projects CRUD
- `test_users.sh` - Users CRUD
- `test_companies.sh` - Companies endpoints
- `test_cycles.sh` - Cycles CRUD
- `test_sessions.sh` - Sessions CRUD

## Environment Variables

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
REDIS_DB=0

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

## Development

### Adding a New Endpoint

1. **Create Schema** in `app/schemas/`
2. **Add Route** to appropriate router in `app/routers/`
3. **Apply Company Scoping** using `current_user.company_id`
4. **Test** with curl or test script

### Database Changes

1. Update model in `app/models/`
2. Create migration in `sql/migrations/`
3. Apply migration (restart docker-compose)
4. Update schemas in `app/schemas/`

## Troubleshooting

### Worker Crashes on macOS

If you see `fork() was called` errors:

```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

This is already included in `start_worker.sh`.

### Database Connection Issues

Check if PostgreSQL is running:
```bash
docker ps | grep postgres
```

Test connection:
```bash
docker exec -it data_uploader_db psql -U uploader -d data_uploader
```

### Redis Connection Issues

Check if Redis is running:
```bash
docker exec data_uploader_redis redis-cli ping
```

Should return `PONG`.

## Production Deployment

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Security Considerations

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Use HTTPS only (configure reverse proxy)
- [ ] Set `DEBUG=False` in production
- [ ] Configure firewall rules
- [ ] Enable CORS only for trusted origins
- [ ] Use strong database passwords
- [ ] Implement rate limiting on auth endpoints

## API Documentation

Full API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Additional documentation in `doc/`:
- `API_DOCUMENTATION.md` - Detailed API reference
- `BACKEND_SETUP.md` - Setup guide
- `DATABASE_SCHEMA.md` - Database schema reference

## License

[Your License Here]
