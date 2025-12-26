# Deployment Guide

Complete guide for deploying the Data Uploader application using Docker.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Full Stack Deployment](#full-stack-deployment)
5. [Development Mode](#development-mode)
6. [Production Mode](#production-mode)
7. [Troubleshooting](#troubleshooting)
8. [Monitoring](#monitoring)
9. [Backup & Recovery](#backup--recovery)
10. [Security Checklist](#security-checklist)

---

## Prerequisites

### Required Software

- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **Git** (for cloning the repository)

### System Requirements

- **CPU:** 2+ cores recommended
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 10GB free space
- **OS:** Linux, macOS, or Windows with WSL2

---

## Quick Start

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

# Or manually edit .env and replace:
# JWT_SECRET=your-generated-secret-here
# NEXTAUTH_SECRET=your-generated-secret-here
```

### 3. Start All Services

```bash
docker-compose up -d
```

### 4. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

**Default Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANT:** Change the default password after first login!

---

## Configuration

### Environment Variables

Edit `.env` file to customize configuration:

```bash
# ===== REQUIRED SECRETS =====
JWT_SECRET=your-jwt-secret-min-32-chars
NEXTAUTH_SECRET=your-nextauth-secret-min-32-chars

# ===== DATABASE =====
DB_NAME=data_uploader
DB_USER=uploader
DB_PASSWORD=uploader_pass

# ===== VOLUME MOUNTS =====
# Customize if needed (for file system access)
HOME=/Users/yourusername
```

### Volume Mounts

The application needs access to local file systems for uploads:

**macOS:**
```yaml
volumes:
  - /Volumes:/Volumes:ro  # External drives
  - ${HOME}:/host_home:ro # User home directory
```

**Linux:**
```yaml
volumes:
  - /mnt:/mnt:ro          # Mounted drives
  - ${HOME}:/host_home:ro # User home directory
```

**Windows (WSL2):**
```yaml
volumes:
  - /mnt/c:/mnt/c:ro      # C: drive
  - ${HOME}:/host_home:ro # WSL home
```

---

## Full Stack Deployment

### Services Overview

The stack includes 5 services:

1. **postgres** - PostgreSQL 16 database
2. **redis** - Redis 7 cache and job queue
3. **backend** - FastAPI application (port 8000)
4. **worker** - RQ background worker
5. **frontend** - Next.js application (port 3000)

### Start All Services

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f worker
```

### Stop All Services

```bash
# Stop services (keep data)
docker-compose stop

# Stop and remove containers (keep data)
docker-compose down

# Stop, remove containers, and remove volumes (DELETE DATA)
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart worker
```

---

## Development Mode

For development, you can run services individually:

### Database Only

```bash
docker-compose up -d postgres redis
```

### Backend Development

```bash
# Start dependencies
docker-compose up -d postgres redis

# Run backend locally
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run worker locally (in another terminal)
cd backend
source venv/bin/activate
./start_worker.sh
```

### Frontend Development

```bash
# Start backend
docker-compose up -d backend

# Run frontend locally
cd frontend
npm install
npm run dev
```

---

## Production Mode

### 1. Security Configuration

**Update `.env`:**
```bash
# Strong secrets (32+ characters)
JWT_SECRET=$(openssl rand -base64 32)
NEXTAUTH_SECRET=$(openssl rand -base64 32)

# Strong database password
DB_PASSWORD=$(openssl rand -base64 16)
```

**Change default admin password:**
1. Log in as admin
2. Navigate to Profile
3. Update password (or create new admin and delete default)

### 2. Build Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### 3. Deploy

```bash
# Start services
docker-compose up -d

# Verify all services are healthy
docker-compose ps
```

### 4. Configure S3 CORS for Browser Uploads

For browser-based uploads to work, configure CORS on your S3 bucket:

```bash
# For production deployment
python scripts/configure_s3_cors.py your-bucket-name https://yourdomain.com

# For development and production
python scripts/configure_s3_cors.py your-bucket-name http://localhost:3000 https://yourdomain.com
```

**Important:** Add all domains where your frontend will be hosted to the CORS configuration. Without this, browser uploads will fail with CORS errors.

### 5. Enable HTTPS

For production, use a reverse proxy (nginx or Caddy):

**nginx example:**
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6. Set up Auto-restart

Services are configured with `restart: unless-stopped` in docker-compose.yml.

For system boot:
```bash
# Enable Docker service
sudo systemctl enable docker

# Or use systemd service for docker-compose
# See: https://docs.docker.com/compose/production/
```

---

## Troubleshooting

### Check Service Health

```bash
# View all services
docker-compose ps

# Check service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs worker

# Check health status
docker inspect data_uploader_backend | grep -A 10 Health
```

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000
# Or port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### 2. Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### 3. Worker Not Processing Jobs

```bash
# Check worker logs
docker-compose logs worker

# Verify Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart worker
docker-compose restart worker
```

#### 4. Frontend Build Errors

```bash
# Rebuild frontend
docker-compose build --no-cache frontend

# Check logs
docker-compose logs frontend
```

#### 5. Permission Errors (Volume Mounts)

```bash
# Check volume permissions
docker-compose exec backend ls -la /Volumes
docker-compose exec backend ls -la /host_home

# Verify HOME environment variable
echo $HOME
```

### Reset Everything

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

---

## Monitoring

### Health Checks

All services have health checks configured:

```bash
# View health status
docker-compose ps

# Manually check endpoints
curl http://localhost:8000/health  # Backend
curl http://localhost:3000/        # Frontend
```

### Resource Usage

```bash
# View resource usage
docker stats

# Specific container
docker stats data_uploader_backend
```

### Logs

```bash
# Follow logs for all services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service with timestamps
docker-compose logs -f --timestamps backend
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U uploader data_uploader > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251225.sql | docker-compose exec -T postgres psql -U uploader -d data_uploader
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v data_uploader_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volumes
docker run --rm -v data_uploader_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

### Configuration Backup

```bash
# Backup configuration
tar czf config_backup.tar.gz .env docker-compose.yml backend/app frontend/app
```

---

## Security Checklist

### Before Production Deployment

- [ ] Change `JWT_SECRET` to strong random value (32+ chars)
- [ ] Change `NEXTAUTH_SECRET` to strong random value (32+ chars)
- [ ] Change default admin password (`admin`/`admin123`)
- [ ] Update `DB_PASSWORD` to strong value
- [ ] Enable HTTPS (use reverse proxy)
- [ ] Configure firewall rules
- [ ] Set `CORS_ORIGINS` to production domains only
- [ ] Disable debug mode
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Enable rate limiting on auth endpoints
- [ ] Review volume mount permissions (use `:ro` for read-only)
- [ ] Set up monitoring and alerts
- [ ] Document disaster recovery procedures

### Network Security

```bash
# Expose only necessary ports
# In docker-compose.yml, remove port mappings for internal services:
# postgres: don't expose 5432
# redis: don't expose 6379

# Access backend API through frontend proxy only
```

### Regular Maintenance

- [ ] Update Docker images monthly
- [ ] Review and rotate secrets quarterly
- [ ] Audit user accounts monthly
- [ ] Review logs for suspicious activity
- [ ] Test backups monthly

---

## Scaling

### Horizontal Scaling

To scale workers:

```bash
# Scale workers to 3 instances
docker-compose up -d --scale worker=3

# Verify
docker-compose ps worker
```

### Performance Tuning

**Backend:**
```yaml
# In docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

**Database:**
```yaml
postgres:
  command:
    - postgres
    - -c
    - max_connections=200
    - -c
    - shared_buffers=256MB
```

---

## Update Procedure

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Restart services (zero downtime)
docker-compose up -d --no-deps --build backend frontend worker
```

### Update Dependencies

```bash
# Backend
cd backend
pip-compile requirements.in
# Update requirements.txt

# Frontend
cd frontend
npm update
# Review and commit package-lock.json

# Rebuild
docker-compose build
```

---

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section
3. Check health endpoints
4. Consult documentation in `doc/` folder

---

**Last Updated:** December 25, 2025
