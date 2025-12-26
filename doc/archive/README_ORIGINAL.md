# Data Uploader - Multi-Tenant Web Application

Production-ready web application for managing S3 file uploads with real-time progress tracking, built with Next.js 15 and FastAPI.

---

## Features

### 🚀 Core Functionality
- **Multi-Tenant Architecture** - Complete company isolation with role-based access
- **Real-Time Upload Tracking** - Live progress updates with 2-second polling
- **Background Job Processing** - Asynchronous uploads via Redis Queue
- **Project & Cycle Management** - Organized upload workflows
- **Session History** - Complete audit trail of all uploads
- **User Management** - Admin controls for user creation and management

### 🛠️ Technical Stack

**Frontend:**
- Next.js 15 with App Router
- TypeScript 5.7
- TailwindCSS + shadcn/ui
- NextAuth.js v5
- TanStack Query

**Backend:**
- FastAPI 0.109
- PostgreSQL 16
- Redis 7
- SQLAlchemy 2.0
- RQ (Redis Queue)

**Deployment:**
- Docker & Docker Compose
- Multi-stage builds
- Health checks
- Auto-restart policies

---

## Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- 4GB RAM minimum
- 10GB free disk space

### 1. Clone Repository

```bash
git clone <repository-url>
cd data_uploader
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Generate secrets (Linux/macOS)
openssl rand -base64 32 | sed 's/^/JWT_SECRET=/' >> .env
openssl rand -base64 32 | sed 's/^/NEXTAUTH_SECRET=/' >> .env
```

### 3. Start Application

**Option A: Using stack.sh (recommended)**

```bash
# Start all services with one command
./stack.sh start

# View status
./stack.sh status

# View demo credentials
./stack.sh demo
```

**Option B: Using docker-compose directly**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

**Default Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change the default password after first login!**

---

## Documentation

- **[STACK_MANAGEMENT.md](STACK_MANAGEMENT.md)** - Stack management with stack.sh
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Docker build guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[DEMO_CREDENTIALS.md](DEMO_CREDENTIALS.md)** - Demo users and passwords
- **[backend/README.md](backend/README.md)** - Backend documentation
- **[frontend/README.md](frontend/README.md)** - Frontend documentation
- **[doc/API_DOCUMENTATION.md](doc/API_DOCUMENTATION.md)** - API reference
- **[doc/DATABASE_SCHEMA.md](doc/DATABASE_SCHEMA.md)** - Database schema

---

## Development

See individual README files for detailed development instructions:

- Backend: [backend/README.md](backend/README.md)
- Frontend: [frontend/README.md](frontend/README.md)

---

## Support

For issues or questions:
- **API Docs:** http://localhost:8000/docs
- **Documentation:** See `doc/` folder

---

**Version:** 1.0.0  
**Status:** Production Ready ✅
