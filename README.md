# Data Uploader

A full-stack web application for uploading field sensor data (audio recordings, camera trap images/videos) to AWS S3 buckets. Features browser-based uploads with progress tracking, PostgreSQL-backed session management, and support for large-scale file operations (100k+ files).

## Quick Start

```bash
# 1. Clone and configure
git clone <repository-url>
cd data_uploader
cp .env.example .env

# 2. Generate secrets
openssl rand -base64 32 | sed 's/^/JWT_SECRET=/' >> .env
openssl rand -base64 32 | sed 's/^/NEXTAUTH_SECRET=/' >> .env

# 3. Add your AWS credentials to .env
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# AWS_DEFAULT_REGION=your-region

# 4. Start all services
docker compose up -d

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Default login: admin / admin123
```

**📚 [Complete Setup Guide](doc/guides/QUICKSTART.md)**

## Features

### Browser-Based Uploads
- 📁 **Folder Selection** - Upload entire directory structures
- 📊 **Real-time Progress** - Track upload status per file
- ⚡ **Direct to S3** - Files upload directly from browser to S3 (no server processing)
- 🔄 **Resume Support** - Track and skip already uploaded files
- 🔐 **Secure** - Uses presigned URLs with AWS Signature V4

### Data Management
- 🏢 **Multi-tenant** - Company-based access control
- 📦 **Project Organization** - Map projects to S3 buckets
- 🔁 **Cycle Tracking** - Organize data by collection cycles (C1, C2, C3...)
- 📈 **Session Tracking** - Full history of all upload sessions
- 📊 **Analytics Ready** - PostgreSQL backend for Grafana dashboards

### Technical Stack
- **Frontend:** Next.js 15, React, TypeScript, TailwindCSS
- **Backend:** FastAPI, Python 3.11, PostgreSQL 16
- **Storage:** AWS S3 with presigned URL uploads
- **Auth:** JWT-based authentication with NextAuth
- **Queue:** Redis + RQ (for CLI uploads, optional for browser uploads)
- **Deployment:** Docker Compose

## Documentation

### 🚀 Setup & Deployment
- [Quick Start Guide](doc/guides/QUICKSTART.md) - Get up and running in 5 minutes
- [Deployment Guide](doc/setup/DEPLOYMENT.md) - Production deployment with Docker
- [Build Guide](doc/setup/BUILD_GUIDE.md) - Building from source
- [Stack Management](doc/setup/STACK_MANAGEMENT.md) - Managing Docker services

### 📖 User Guides
- [Backend Setup](doc/guides/BACKEND_SETUP.md) - Backend configuration and CLI usage

### 📚 Reference
- [API Documentation](doc/reference/API_DOCUMENTATION.md) - REST API endpoints
- [Database Schema](doc/reference/DATABASE_SCHEMA.md) - Data model and relationships
- [Grafana Queries](doc/reference/GRAFANA_QUERIES.md) - Analytics and reporting

### 🔧 Development
- [Architecture](doc/development/ARCHITECTURE.md) - System architecture overview
- [Project Structure](doc/development/PROJECT_STRUCTURE.md) - Code organization
- [Testing](doc/development/TESTING.md) - Running tests
- [Endpoint Integration](doc/development/ENDPOINT_INTEGRATION.md) - API integration guide
- [Claude Code Instructions](doc/development/CLAUDE.md) - AI assistant guidance

## Data Model

```
Company (Client)
  └── Project (maps to S3 bucket)
      └── Cycle (C1, C2, C3... - used as S3 prefix)
          └── Sensor Serial Number (folder)
              └── Files (.wav, .jpg, .mp4)
```

**Example S3 Structure:**
```
s3://project-bucket/
  └── C2/                    # Cycle 2
      ├── 950349/           # Sensor serial number
      │   ├── 20250909_092000.WAV
      │   └── 20250909_093000.WAV
      └── 950350/
          └── 20250909_092000.WAV
```

## AWS Configuration

### S3 CORS Setup

For browser uploads to work, configure CORS on your S3 bucket:

```bash
# Development
python scripts/configure_s3_cors.py your-bucket-name http://localhost:3000

# Production
python scripts/configure_s3_cors.py your-bucket-name https://yourdomain.com
```

### IAM Permissions Setup

Grant S3 upload permissions to your IAM user:

```bash
# Interactive script to apply permissions
python aws-admin/configure_s3_permissions.py
```

**📚 [AWS Admin Tools Documentation](aws-admin/README.md)**

## Usage

### Two Upload Methods

The application supports two upload approaches depending on your needs:

#### 1. Browser Upload (Recommended for End Users)
✅ Upload from local computer via web interface
✅ Direct browser-to-S3 (no server processing)
✅ Real-time progress tracking
✅ No Redis/RQ required

#### 2. CLI Upload (Server-Side Batch Processing)
✅ Upload from server filesystem
✅ Automated batch processing
✅ Background job queue
✅ Requires Redis + RQ worker

---

### Web Interface (Browser Upload)

1. **Login** at http://localhost:3000
   - Default credentials: `admin` / `admin123`
   - ⚠️ Change password after first login!

2. **Create a Project**
   - Navigate to Projects → New Project
   - Enter project name and S3 bucket details

3. **Create a Cycle**
   - Select project → Cycles → New Cycle
   - Specify cycle name (e.g., "C1", "C2") and S3 prefix

4. **Upload Files**
   - Navigate to Upload
   - Select project and cycle
   - Choose folder containing sensor data
   - Click Upload

### CLI Upload (Server-Side)

For server-side uploads from mounted drives or server filesystems:

```bash
# 1. Start services with CLI support (includes Redis + Worker)
docker compose --profile cli up -d

# 2. Create JSON config file
cat > config_files/my-upload.json << EOF
{
    "local_directory": "/path/to/sensor/data",
    "bucket_name": "your-bucket-name",
    "s3_prefix": "C2",
    "max_workers": 15,
    "aws_region": "eu-west-1",
    "times_to_retry": 3,
    "aws_profile": "default",
    "use_find": "yes"
}
EOF

# 3. Run upload script
python scripts/upload.py --config config_files/my-upload.json

# 4. Monitor progress
# Check logs and progress updates in real-time
```

**CLI Features:**
- 🔍 Fast file discovery using native `find` command
- 📊 Progress updates every 10,000 files
- 🔄 Auto-retry failed uploads with configurable attempts
- 💾 Resume capability (skips already uploaded files)
- ⚡ Concurrent uploads with configurable worker count

**📚 [Complete CLI Documentation](doc/guides/BACKEND_SETUP.md)**

### API Usage

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# List projects
curl http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <token>"

# Create upload session
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "cycle_id": 1,
    "local_directory": "browser-upload",
    "s3_prefix": "C1"
  }'
```

**📚 [Full API Documentation](doc/reference/API_DOCUMENTATION.md)**

## Architecture

### Upload Flows

The application supports two distinct upload architectures:

#### Browser Upload Flow (Direct to S3)

```
Browser → Backend API (get presigned URL)
   ↓
Browser → S3 (direct upload with presigned URL)
   ↓
Browser → Backend API (update session status)
```

**Key Benefits:**
- No file data passes through backend server
- Scalable to large files and many concurrent uploads
- Lower bandwidth costs on application server
- Redis/RQ not required

**Services Used:** Frontend, Backend, PostgreSQL

#### CLI Upload Flow (Server-Side with Queue)

```
CLI Script → Backend API (start upload job)
   ↓
Backend → Redis (enqueue job)
   ↓
RQ Worker → Read local files → Upload to S3
   ↓
Worker → PostgreSQL (update session status)
```

**Key Benefits:**
- Server filesystem access (mounted drives, network storage)
- Background processing with job queue
- Automated batch operations
- Resume capability for large datasets

**Services Used:** Backend, PostgreSQL, Redis, RQ Worker

### Services

- **frontend** (port 3000) - Next.js web application
- **backend** (port 8000) - FastAPI REST API
- **worker** - RQ background worker (optional, for CLI uploads only)
- **postgres** (port 5432) - PostgreSQL database
- **redis** (port 6379) - Job queue and cache (optional, for CLI uploads only)

## Performance

- ✅ Handles 300k+ files efficiently
- ✅ Direct browser-to-S3 uploads (no server bottleneck)
- ✅ Resume capability for interrupted uploads
- ✅ Progress tracking every 10k files during scan
- ✅ Real-time upload speed and ETA

## Security

- 🔐 JWT-based authentication
- 🏢 Company-scoped data access
- 🔑 AWS presigned URLs with 1-hour expiration
- 🔒 Signature Version 4 for secure S3 access
- 👥 Role-based access control (admin, user, viewer)

**📚 [Security Checklist](doc/setup/DEPLOYMENT.md#security-checklist)**

## Monitoring & Analytics

Monitor upload progress and track statistics with Grafana dashboards:

### Real-Time Monitoring (for CLI uploads)
- 📊 Active upload sessions with live progress
- ⚡ Current upload speed (files/second)
- 📈 Progress gauges and completion percentages
- 🔔 Automatic alerts for failures or stalled uploads

### Historical Analytics
- 📦 Total files per project/bucket
- 🔄 Upload status per session
- 📊 Cycle-by-cycle comparisons (bar charts)
- 📉 Success rate trends over time
- 🥧 File type distribution (pie charts)

**📊 [Ready-to-Use Grafana Setup](grafana/)** - SQL queries, dashboard JSON, and configuration guide

**📚 [Complete Grafana Documentation](doc/reference/GRAFANA_QUERIES.md)**

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
lsof -i :3000  # Find process
kill -9 <PID>  # Kill process
```

**CORS errors during upload:**
```bash
# Configure S3 CORS
python scripts/configure_s3_cors.py your-bucket http://localhost:3000
```

**403 Forbidden on S3 upload:**
```bash
# Check and apply IAM permissions
python aws-admin/configure_s3_permissions.py
```

**Database connection failed:**
```bash
docker compose restart postgres
docker compose logs postgres
```

**📚 [Full Troubleshooting Guide](doc/setup/DEPLOYMENT.md#troubleshooting)**

## Development

```bash
# Start database only
docker compose up -d postgres redis

# Run backend locally
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Run frontend locally (separate terminal)
cd frontend
npm install
npm run dev
```

**📚 [Development Guide](doc/development/PROJECT_STRUCTURE.md)**

## Contributing

1. Follow the existing code structure
2. Write tests for new features
3. Update documentation
4. Use conventional commits

## License

[Your License Here]

## Support

- 📖 [Documentation](doc/)
- 🐛 [Issue Tracker](https://github.com/your-org/data_uploader/issues)
- 📧 [Contact](mailto:your-email@example.com)

---

**Built with ❤️ for field data management**
