# Docker Build Guide

Complete guide for building Docker images for the Data Uploader application.

---

## Quick Reference

```bash
# Build all images
./stack.sh build

# Build without cache (clean build)
./stack.sh build --no-cache

# Build with latest base images
./stack.sh build --pull

# Build in parallel (faster)
./stack.sh build --parallel

# Build specific service
./stack.sh build backend
./stack.sh build frontend

# Combine options
./stack.sh build --no-cache --pull --parallel
```

---

## Build Commands

### Basic Build

```bash
# Build all services (backend, frontend, worker)
./stack.sh build
```

**What gets built:**
- **backend** - FastAPI application (Python 3.11)
- **frontend** - Next.js application (Node 20)
- **worker** - Background job worker (same as backend)

**Not built:**
- postgres - Uses official `postgres:16-alpine` image
- redis - Uses official `redis:7-alpine` image

### Build Options

#### --no-cache

Build without using Docker cache (clean build):

```bash
./stack.sh build --no-cache
```

**When to use:**
- After major dependency changes
- When build is behaving unexpectedly
- For production deployments
- To ensure reproducible builds

**Trade-off:** Slower build time, but guaranteed fresh build

#### --pull

Pull latest base images before building:

```bash
./stack.sh build --pull
```

**What it does:**
- Pulls `python:3.11-slim` (backend)
- Pulls `node:20-alpine` (frontend)
- Ensures you have latest security patches

**When to use:**
- Monthly maintenance
- Before production deployments
- After security advisories

#### --parallel

Build images in parallel:

```bash
./stack.sh build --parallel
```

**Benefits:**
- Faster build on multi-core systems
- Backend and frontend build simultaneously

**Requirements:**
- Docker Compose 1.25+
- Multi-core CPU

### Build Specific Service

```bash
# Build only backend
./stack.sh build backend

# Build only frontend
./stack.sh build frontend

# Build only worker (same as backend)
./stack.sh build worker
```

**Use cases:**
- Changed only frontend code
- Testing backend changes
- Faster iteration during development

---

## Build Strategies

### Development Build (Fast Iteration)

```bash
# Quick build with cache
./stack.sh build backend

# Rebuild and restart
./stack.sh rebuild backend
```

**Best for:**
- Active development
- Quick testing
- Iterating on changes

### Production Build (Clean & Verified)

```bash
# Complete clean build with latest base images
./stack.sh build --no-cache --pull

# Or
./stack.sh build --no-cache --pull --parallel
```

**Best for:**
- Production deployments
- Release builds
- Ensuring reproducibility

### Maintenance Build (Security Updates)

```bash
# Pull latest base images and rebuild
./stack.sh build --pull
```

**Best for:**
- Monthly maintenance
- Security patch updates
- Updating dependencies

---

## Build Output

After building, the script shows:

1. **Build progress** - Real-time build output
2. **Build status** - Success or error messages
3. **Image sizes** - Size of built images

Example output:

```
════════════════════════════════════════════════════════════════
  Building Docker Images
════════════════════════════════════════════════════════════════

ℹ Building all services...

ℹ Services to build:
  • backend (FastAPI)
  • frontend (Next.js)
  • worker (Background jobs)

[+] Building 45.2s (28/28) FINISHED
...

✓ Build complete!

ℹ Image sizes:
REPOSITORY                    TAG       SIZE
data_uploader-backend         latest    450MB
data_uploader-frontend        latest    180MB
data_uploader-worker          latest    450MB
```

---

## Image Details

### Backend Image

**Base:** `python:3.11-slim`
**Size:** ~450MB
**Layers:**
1. Base Python image
2. System dependencies (postgresql-client)
3. Python dependencies (pip install)
4. Application code

**Multi-stage:** No (single stage)

**Optimization tips:**
- Use `.dockerignore` to exclude unnecessary files
- Requirements cached separately from code
- Minimal system packages

### Frontend Image

**Base:** `node:20-alpine`
**Size:** ~180MB (production build)
**Layers:**
1. Dependencies stage (npm ci)
2. Build stage (npm run build)
3. Runtime stage (minimal production)

**Multi-stage:** Yes (3 stages)

**Optimization:**
- Only production dependencies in final image
- Static assets pre-built
- Standalone Next.js build

### Worker Image

**Base:** `python:3.11-slim`
**Size:** ~450MB
**Same as backend**

**Difference:** Uses different CMD (rq worker)

---

## Build Troubleshooting

### Build Fails

```bash
# Check Docker daemon
docker info

# Try clean build
./stack.sh build --no-cache

# Check disk space
df -h
docker system df
```

### Out of Disk Space

```bash
# Clean unused images and cache
./stack.sh clean

# More aggressive
docker system prune -a

# Remove old images
docker images | grep data_uploader
docker rmi <image_id>
```

### Network Errors During Build

```bash
# Retry build (usually transient)
./stack.sh build

# Check internet connection
ping google.com

# Try with pull to refresh base images
./stack.sh build --pull
```

### Cache Issues

```bash
# Force rebuild without cache
./stack.sh build --no-cache

# Specific service
./stack.sh build --no-cache backend
```

### Build is Slow

```bash
# Use parallel builds
./stack.sh build --parallel

# Check system resources
docker stats

# Increase Docker resources (Docker Desktop)
# Settings → Resources → CPU/Memory
```

---

## Build Best Practices

### For Development

1. **Use cache** - Don't use `--no-cache` unless needed
2. **Build specific services** - Only rebuild what changed
3. **Use rebuild** - Automatically restarts after build

```bash
# Edit backend code
./stack.sh rebuild backend

# Edit frontend code
./stack.sh rebuild frontend
```

### For Production

1. **Clean build** - Always use `--no-cache` for production
2. **Pull base images** - Get latest security patches
3. **Test locally first** - Build and test before deploying

```bash
# Production build checklist
./stack.sh build --no-cache --pull
./stack.sh start
./stack.sh health
./stack.sh db backup
```

### For CI/CD

```bash
# Automated build in CI pipeline
docker-compose build --no-cache --pull
docker-compose push  # If using registry
```

---

## Advanced Build Scenarios

### Build with Custom Dockerfile

```bash
# Edit Dockerfile
vim backend/Dockerfile

# Rebuild
./stack.sh build --no-cache backend
```

### Build Arguments

Docker Compose supports build args in `docker-compose.yml`:

```yaml
services:
  backend:
    build:
      context: ./backend
      args:
        PYTHON_VERSION: "3.11"
```

### Multi-Platform Builds

For ARM64 (M1/M2 Mac) and AMD64:

```bash
# Build for current platform
./stack.sh build

# Cross-platform (requires buildx)
docker buildx build --platform linux/amd64,linux/arm64 backend/
```

---

## Build Performance

### Typical Build Times

**From scratch (no cache):**
- Backend: ~2-3 minutes
- Frontend: ~3-5 minutes
- Total: ~5-8 minutes

**With cache (no changes):**
- Backend: ~10 seconds
- Frontend: ~15 seconds
- Total: ~25 seconds

**With code changes only:**
- Backend: ~30 seconds
- Frontend: ~1 minute
- Total: ~1.5 minutes

### Improving Build Speed

1. **Use parallel builds**
   ```bash
   ./stack.sh build --parallel
   ```

2. **Use build cache**
   - Don't delete images unnecessarily
   - Reuse cache between builds

3. **Optimize Dockerfiles**
   - Order layers from least to most frequently changed
   - Copy `requirements.txt` before code
   - Use `.dockerignore`

4. **Increase Docker resources**
   - More CPU → faster builds
   - More RAM → larger cache

---

## Build Verification

### After Building

```bash
# Check images were created
docker images | grep data_uploader

# Check image sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep data_uploader

# Test the build
./stack.sh start
./stack.sh status
./stack.sh health
```

### Verify Image Contents

```bash
# Inspect backend image
docker run --rm data_uploader-backend python --version
docker run --rm data_uploader-backend pip list

# Inspect frontend image
docker run --rm data_uploader-frontend node --version
```

---

## Examples

### Complete Development Workflow

```bash
# 1. Make code changes
vim backend/app/main.py

# 2. Rebuild backend
./stack.sh build backend

# 3. Restart backend
docker-compose restart backend

# 4. Check logs
./stack.sh logs backend

# 5. Test
curl http://localhost:8000/health
```

### Production Deployment Workflow

```bash
# 1. Pull latest code
git pull origin main

# 2. Clean build all services
./stack.sh build --no-cache --pull

# 3. Backup database
./stack.sh db backup

# 4. Deploy
./stack.sh down
./stack.sh start

# 5. Verify
./stack.sh health
./stack.sh status
```

### Emergency Rebuild

```bash
# Something is broken, start fresh
./stack.sh destroy
./stack.sh build --no-cache --pull
./stack.sh start
```

---

## Build Monitoring

### Watch Build Progress

```bash
# Build with live output
./stack.sh build

# Or with docker-compose directly
docker-compose build --progress=plain
```

### Build History

```bash
# See when images were built
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}" | grep data_uploader

# See image layers
docker history data_uploader-backend
```

---

## FAQ

**Q: Do I need to rebuild after changing code?**
A: Yes, Docker images are immutable. Changes require rebuild.

**Q: When should I use --no-cache?**
A: For production builds, after dependency changes, or when debugging build issues.

**Q: Can I build just one service?**
A: Yes: `./stack.sh build backend`

**Q: How do I speed up builds?**
A: Use `--parallel`, keep cache, optimize Dockerfiles, increase Docker resources.

**Q: Why is the first build slow?**
A: Downloading base images and dependencies. Subsequent builds use cache.

**Q: Do I need to stop services to rebuild?**
A: No, but you need to restart them: `./stack.sh rebuild backend`

**Q: How much disk space do images use?**
A: ~1.5GB total for all images plus base images

---

**Last Updated:** December 25, 2025
**Docker Version:** 20.10+
**Docker Compose Version:** 2.0+
