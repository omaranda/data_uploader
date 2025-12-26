# Stack Management Guide

Comprehensive guide for using `stack.sh` to manage the Data Uploader Docker stack.

---

## Quick Reference

```bash
./stack.sh help          # Show all commands
./stack.sh start         # Start the stack
./stack.sh stop          # Stop the stack
./stack.sh status        # Check status
./stack.sh logs backend  # View backend logs
./stack.sh db stats      # Database statistics
```

---

## Installation

The `stack.sh` script is already executable. If needed:

```bash
chmod +x stack.sh
```

---

## Core Commands

### Start / Stop

```bash
# Start all services
./stack.sh start

# Stop all services (keeps containers)
./stack.sh stop

# Restart all services
./stack.sh restart

# Stop and remove containers (keeps data)
./stack.sh down

# DESTROY everything including data ⚠️
./stack.sh destroy
```

### Status & Monitoring

```bash
# Show service status and health
./stack.sh status

# Alternative syntax
./stack.sh ps

# Check all endpoints
./stack.sh health

# Show access URLs
./stack.sh urls
```

---

## Logs & Debugging

### View Logs

```bash
# Follow all logs (Ctrl+C to exit)
./stack.sh logs

# Follow specific service
./stack.sh logs backend
./stack.sh logs frontend
./stack.sh logs worker

# Show last 50 lines
./stack.sh logs-tail
./stack.sh logs-tail backend
```

### Examples

```bash
# Debug backend issues
./stack.sh logs backend

# Monitor worker jobs
./stack.sh logs worker

# View all recent activity
./stack.sh logs-tail
```

---

## Database Management

### Database Shell

```bash
# Open PostgreSQL shell
./stack.sh db shell

# Same as above
./stack.sh db psql
```

### Backup & Restore

```bash
# Create backup
./stack.sh db backup
# Creates: backup_YYYYMMDD_HHMMSS.sql

# Restore from backup
./stack.sh db restore backup_20251225_163000.sql
```

### Database Stats

```bash
# Show row counts
./stack.sh db stats

# Output:
# Companies  | 13
# Users      | 29
# Projects   | 16
# Cycles     | 49
# Sessions   | 0
```

### Reset Database

```bash
# WARNING: Deletes all data!
./stack.sh db reset
```

---

## Redis Management

### Redis CLI

```bash
# Open Redis CLI
./stack.sh redis cli

# Ping Redis
./stack.sh redis ping

# Show Redis info
./stack.sh redis info
```

### Flush Redis

```bash
# WARNING: Deletes all cached data!
./stack.sh redis flush
```

---

## Build & Deploy

### Build Images

```bash
# Build all services
./stack.sh build

# Build specific service
./stack.sh build backend
./stack.sh build frontend
```

### Rebuild & Restart

```bash
# Rebuild and restart all
./stack.sh rebuild

# Rebuild and restart specific service
./stack.sh rebuild backend
```

### Update Stack

```bash
# Pull latest code, rebuild, restart
./stack.sh update
```

### Pull Base Images

```bash
# Pull latest postgres, redis, node images
./stack.sh pull
```

---

## Scaling Workers

### Scale Worker Instances

```bash
# Scale to 3 workers
./stack.sh scale 3

# Scale to 5 workers
./stack.sh scale 5

# Scale back to 1 worker
./stack.sh scale 1
```

**When to scale:**
- During high upload volume
- Processing large batches
- Multiple simultaneous uploads

**Resource note:** Each worker uses ~80MB RAM

---

## Execute Commands

### Open Shell

```bash
# Open shell in backend
./stack.sh exec backend

# Open shell in worker
./stack.sh exec worker

# Open shell in frontend
./stack.sh exec frontend
```

### Run Specific Commands

```bash
# Run Python in backend
./stack.sh exec backend python --version

# Check backend environment
./stack.sh exec backend env | grep DB

# Run npm command in frontend
./stack.sh exec frontend npm --version
```

---

## Utility Commands

### Demo Credentials

```bash
# Show quick demo credentials
./stack.sh demo

# Output shows:
# - Default admin
# - One user per region
# - Link to full credentials table
```

### Clean Docker

```bash
# Remove unused Docker resources
./stack.sh clean

# Removes:
# - Stopped containers
# - Unused images
# - Unused networks
```

---

## Common Workflows

### Fresh Start

```bash
# Complete fresh start with demo data
./stack.sh destroy    # ⚠️ Deletes everything!
./stack.sh start      # Rebuilds with fresh demo data
./stack.sh status     # Verify all healthy
```

### Development Workflow

```bash
# Make code changes
# ... edit backend/app/main.py ...

# Rebuild and restart backend only
./stack.sh rebuild backend

# Check logs
./stack.sh logs backend
```

### Production Deployment

```bash
# Pull latest code
git pull origin main

# Update and restart
./stack.sh update

# Verify health
./stack.sh health
./stack.sh status
```

### Debugging Issues

```bash
# Check overall status
./stack.sh status

# Check specific service logs
./stack.sh logs backend

# Check endpoints
./stack.sh health

# Check database
./stack.sh db stats
```

### Backup Before Changes

```bash
# Create backup
./stack.sh db backup

# Make changes
./stack.sh rebuild

# If something goes wrong
./stack.sh db restore backup_YYYYMMDD_HHMMSS.sql
```

---

## Service Details

### Service Names

| Service | Container Name | Port |
|---------|---------------|------|
| postgres | data_uploader_db | 5432 |
| redis | data_uploader_redis | 6379 |
| backend | data_uploader_backend | 8000 |
| worker | data_uploader_worker | - |
| frontend | data_uploader_frontend | 3000 |

### Health Checks

- **postgres**: `pg_isready` check
- **redis**: `redis-cli ping`
- **backend**: HTTP `/health` endpoint
- **frontend**: HTTP root endpoint
- **worker**: No health check (always shows "RUNNING")

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker daemon
docker info

# Check logs
./stack.sh logs

# Rebuild
./stack.sh build
./stack.sh start
```

### Port Already in Use

```bash
# Check what's using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

### Database Connection Failed

```bash
# Check postgres is running
./stack.sh status

# Check postgres logs
./stack.sh logs postgres

# Restart postgres
docker compose restart postgres
```

### Worker Not Processing

```bash
# Check worker logs
./stack.sh logs worker

# Check Redis connection
./stack.sh redis ping

# Restart worker
docker compose restart worker

# Scale workers
./stack.sh scale 2
```

### Out of Disk Space

```bash
# Clean Docker resources
./stack.sh clean

# More aggressive cleanup
docker system prune -a

# Check disk usage
docker system df
```

### Reset Everything

```bash
# Nuclear option - start completely fresh
./stack.sh destroy
./stack.sh start
```

---

## Environment Variables

The stack uses environment variables from `.env` file:

```bash
# View current environment
./stack.sh exec backend env | grep DB

# Edit environment
vim .env

# Restart to apply changes
./stack.sh restart
```

**Important variables:**
- `JWT_SECRET` - Backend authentication
- `NEXTAUTH_SECRET` - Frontend authentication
- `DB_PASSWORD` - Database password

---

## Performance Tips

### Monitor Resources

```bash
# Check resource usage
docker stats

# Check specific container
docker stats data_uploader_backend
```

### Optimize Workers

```bash
# Start with 1 worker
./stack.sh scale 1

# Monitor queue with Redis
./stack.sh redis cli
> LLEN rq:queue:uploads

# Scale up if queue grows
./stack.sh scale 3
```

### Database Performance

```bash
# Check database size
./stack.sh db shell
SELECT pg_size_pretty(pg_database_size('data_uploader'));

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Security Checklist

Before production:

```bash
# 1. Check current passwords
./stack.sh demo

# 2. Create database backup
./stack.sh db backup

# 3. Change all passwords (see DEMO_CREDENTIALS.md)

# 4. Update .env with strong secrets
vim .env

# 5. Restart with new environment
./stack.sh restart

# 6. Verify health
./stack.sh health
```

---

## Command Reference

### Stack Management
- `start` - Start all services
- `stop` - Stop all services
- `restart` - Restart all services
- `down` - Stop and remove containers
- `destroy` - Remove everything including data
- `status` / `ps` - Show service status

### Logs & Monitoring
- `logs [service]` - Follow logs
- `logs-tail [service]` - Last 50 lines
- `health` - Check endpoints
- `urls` - Show access URLs

### Build & Deploy
- `build [service]` - Build images
- `rebuild [service]` - Rebuild and restart
- `pull` - Pull base images
- `update` - Full update

### Database
- `db shell` - PostgreSQL shell
- `db backup` - Create backup
- `db restore <file>` - Restore backup
- `db reset` - Reset database
- `db stats` - Show statistics

### Redis
- `redis cli` - Redis CLI
- `redis ping` - Ping Redis
- `redis info` - Redis info
- `redis flush` - Flush data

### Utilities
- `exec <service> [cmd]` - Execute command
- `scale <number>` - Scale workers
- `clean` - Clean Docker resources
- `demo` - Show demo credentials

---

## Examples

```bash
# Complete workflow
./stack.sh start
./stack.sh status
./stack.sh db stats
./stack.sh demo
./stack.sh urls

# Development cycle
./stack.sh logs backend
# ... make changes ...
./stack.sh rebuild backend
./stack.sh logs backend

# Scaling for production
./stack.sh scale 5
./stack.sh status

# Backup before changes
./stack.sh db backup
./stack.sh rebuild
./stack.sh db restore backup_20251225_163000.sql

# Debugging
./stack.sh health
./stack.sh logs backend
./stack.sh exec backend env
```

---

**Last Updated:** December 25, 2025
**Script Version:** 1.0.0
