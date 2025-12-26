#!/bin/bash
#
# Data Uploader Stack Management Script
# Description: Manage the entire Docker stack (postgres, redis, backend, worker, frontend)
# Usage: ./stack.sh [command]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="data_uploader"

# Helper functions
print_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
}

check_compose() {
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
}

# Command functions

cmd_start() {
    print_header "Starting Data Uploader Stack"

    check_docker
    check_compose

    print_info "Starting all services..."
    docker compose up -d

    echo ""
    print_info "Waiting for services to be healthy..."
    sleep 5

    cmd_status

    echo ""
    print_success "Stack started successfully!"
    echo ""
    print_info "Access points:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
    print_info "Default login: admin / admin123"
    echo ""
}

cmd_stop() {
    print_header "Stopping Data Uploader Stack"

    check_docker
    check_compose

    print_info "Stopping all services..."
    docker compose stop

    print_success "Stack stopped successfully!"
}

cmd_restart() {
    print_header "Restarting Data Uploader Stack"

    check_docker
    check_compose

    print_info "Restarting all services..."
    docker compose restart

    echo ""
    cmd_status

    print_success "Stack restarted successfully!"
}

cmd_down() {
    print_header "Shutting Down Stack (removes containers)"

    print_warning "This will stop and remove all containers"
    print_warning "Database data will be preserved in volumes"
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cancelled"
        exit 0
    fi

    check_docker
    check_compose

    print_info "Stopping and removing containers..."
    docker compose down

    print_success "Stack shut down successfully!"
}

cmd_destroy() {
    print_header "⚠️  DESTROY STACK (removes everything including data) ⚠️"

    print_error "WARNING: This will DELETE ALL DATA!"
    print_warning "This action cannot be undone!"
    echo ""
    echo "This will remove:"
    echo "  • All containers"
    echo "  • All volumes (database data will be LOST)"
    echo "  • Network configuration"
    echo ""
    read -p "Type 'YES' to confirm: " -r
    echo

    if [[ ! $REPLY == "YES" ]]; then
        print_info "Cancelled"
        exit 0
    fi

    check_docker
    check_compose

    print_info "Destroying stack and volumes..."
    docker compose down -v

    print_success "Stack destroyed! All data removed."
}

cmd_status() {
    print_header "Stack Status"

    check_docker
    check_compose

    docker compose ps

    echo ""
    print_info "Service Health:"

    # Function to get container name for service
    get_container_name() {
        case "$1" in
            postgres) echo "data_uploader_db" ;;
            redis) echo "data_uploader_redis" ;;
            backend) echo "data_uploader_backend" ;;
            frontend) echo "data_uploader_frontend" ;;
            worker) echo "data_uploader_worker" ;;
            *) echo "data_uploader_$1" ;;
        esac
    }

    # Check each service
    for service in postgres redis backend frontend worker; do
        container_name=$(get_container_name "$service")

        if docker ps --filter "name=${container_name}" --format "{{.Names}}" | grep -q "${container_name}"; then
            health=$(docker inspect --format='{{.State.Health.Status}}' "${container_name}" 2>/dev/null || echo "no-health-check")

            if [[ "$health" == "healthy" ]]; then
                print_success "$service: HEALTHY"
            elif [[ "$health" == "no-health-check" ]]; then
                status=$(docker inspect --format='{{.State.Status}}' "${container_name}")
                if [[ "$status" == "running" ]]; then
                    print_success "$service: RUNNING (no health check)"
                else
                    print_warning "$service: $status"
                fi
            else
                print_warning "$service: $health"
            fi
        else
            print_error "$service: NOT RUNNING"
        fi
    done
}

cmd_logs() {
    print_header "Service Logs"

    check_docker
    check_compose

    if [ -z "$1" ]; then
        print_info "Showing logs for all services (Ctrl+C to exit)..."
        docker compose logs -f
    else
        print_info "Showing logs for $1 (Ctrl+C to exit)..."
        docker compose logs -f "$1"
    fi
}

cmd_logs_tail() {
    print_header "Recent Logs (last 50 lines)"

    check_docker
    check_compose

    if [ -z "$1" ]; then
        docker compose logs --tail=50
    else
        docker compose logs --tail=50 "$1"
    fi
}

cmd_ps() {
    check_docker
    docker compose ps
}

cmd_build() {
    print_header "Building Docker Images"

    check_docker
    check_compose

    # Parse options
    NO_CACHE=""
    PULL=""
    PARALLEL=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --no-cache)
                NO_CACHE="--no-cache"
                print_info "Building without cache..."
                shift
                ;;
            --pull)
                PULL="--pull"
                print_info "Pulling latest base images..."
                shift
                ;;
            --parallel)
                PARALLEL="--parallel"
                print_info "Building in parallel..."
                shift
                ;;
            -*)
                print_error "Unknown option: $1"
                echo "Usage: $0 build [--no-cache] [--pull] [--parallel] [service]"
                exit 1
                ;;
            *)
                # Service name
                SERVICE="$1"
                shift
                ;;
        esac
    done

    if [ -z "$SERVICE" ]; then
        print_info "Building all services..."
        echo ""
        print_info "Services to build:"
        echo "  • backend (FastAPI)"
        echo "  • frontend (Next.js)"
        echo "  • worker (Background jobs)"
        echo ""
        docker compose build $NO_CACHE $PULL $PARALLEL
    else
        print_info "Building $SERVICE..."
        docker compose build $NO_CACHE $PULL "$SERVICE"
    fi

    echo ""
    print_success "Build complete!"

    # Show image sizes
    echo ""
    print_info "Image sizes:"
    docker images | grep -E "data_uploader|IMAGE" | head -6
}

cmd_rebuild() {
    print_header "Rebuilding and Restarting Services"

    check_docker
    check_compose

    if [ -z "$1" ]; then
        print_info "Rebuilding all services..."
        docker compose build
        print_info "Restarting services..."
        docker compose up -d
    else
        print_info "Rebuilding $1..."
        docker compose build "$1"
        print_info "Restarting $1..."
        docker compose up -d "$1"
    fi

    print_success "Rebuild complete!"
}

cmd_pull() {
    print_header "Pulling Latest Images"

    check_docker
    check_compose

    print_info "Pulling latest images..."
    docker compose pull

    print_success "Pull complete!"
}

cmd_exec() {
    check_docker

    if [ -z "$1" ]; then
        print_error "Usage: $0 exec <service> [command]"
        exit 1
    fi

    service=$1
    shift

    container_name="${PROJECT_NAME}_${service}"

    if [ -z "$1" ]; then
        # No command specified, open shell
        print_info "Opening shell in $service..."
        docker exec -it "$container_name" /bin/sh
    else
        # Execute specific command
        docker exec -it "$container_name" "$@"
    fi
}

cmd_db() {
    print_header "Database Management"

    check_docker

    case "${1:-shell}" in
        shell|psql)
            print_info "Opening PostgreSQL shell..."
            docker exec -it "${PROJECT_NAME}_db" psql -U uploader -d data_uploader
            ;;

        backup)
            backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
            print_info "Creating database backup: $backup_file"
            docker exec "${PROJECT_NAME}_db" pg_dump -U uploader data_uploader > "$backup_file"
            print_success "Backup saved to $backup_file"
            ;;

        restore)
            if [ -z "$2" ]; then
                print_error "Usage: $0 db restore <backup_file>"
                exit 1
            fi
            print_warning "Restoring database from $2..."
            cat "$2" | docker exec -i "${PROJECT_NAME}_db" psql -U uploader -d data_uploader
            print_success "Database restored!"
            ;;

        reset)
            print_warning "⚠️  This will DELETE all database data!"
            read -p "Continue? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_info "Resetting database..."
                docker compose down postgres
                docker volume rm "${PROJECT_NAME}_postgres_data" 2>/dev/null || true
                docker compose up -d postgres
                print_success "Database reset complete!"
            fi
            ;;

        stats)
            print_info "Database Statistics:"
            docker exec "${PROJECT_NAME}_db" psql -U uploader -d data_uploader -c "
                SELECT 'Companies' as table_name, COUNT(*) as count FROM companies
                UNION ALL SELECT 'Users', COUNT(*) FROM users
                UNION ALL SELECT 'Projects', COUNT(*) FROM projects
                UNION ALL SELECT 'Cycles', COUNT(*) FROM cycles
                UNION ALL SELECT 'Sessions', COUNT(*) FROM sync_sessions
                ORDER BY table_name;
            "
            ;;

        *)
            print_error "Unknown database command: $1"
            echo "Available commands: shell, backup, restore, reset, stats"
            exit 1
            ;;
    esac
}

cmd_redis() {
    print_header "Redis Management"

    check_docker

    case "${1:-cli}" in
        cli|shell)
            print_info "Opening Redis CLI..."
            docker exec -it "${PROJECT_NAME}_redis" redis-cli
            ;;

        ping)
            print_info "Pinging Redis..."
            docker exec "${PROJECT_NAME}_redis" redis-cli ping
            ;;

        info)
            print_info "Redis Info:"
            docker exec "${PROJECT_NAME}_redis" redis-cli info | head -20
            ;;

        flush)
            print_warning "⚠️  This will DELETE all Redis data!"
            read -p "Continue? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker exec "${PROJECT_NAME}_redis" redis-cli FLUSHALL
                print_success "Redis flushed!"
            fi
            ;;

        *)
            print_error "Unknown redis command: $1"
            echo "Available commands: cli, ping, info, flush"
            exit 1
            ;;
    esac
}

cmd_scale() {
    print_header "Scaling Workers"

    check_docker
    check_compose

    if [ -z "$1" ]; then
        print_error "Usage: $0 scale <number>"
        print_info "Example: $0 scale 3 (run 3 worker instances)"
        exit 1
    fi

    print_info "Scaling workers to $1 instances..."
    docker compose up -d --scale worker="$1"

    print_success "Workers scaled to $1 instances!"
    cmd_status
}

cmd_clean() {
    print_header "Cleaning Docker Resources"

    check_docker

    print_info "Removing stopped containers..."
    docker container prune -f

    print_info "Removing unused images..."
    docker image prune -f

    print_info "Removing unused networks..."
    docker network prune -f

    print_success "Cleanup complete!"
}

cmd_health() {
    print_header "Health Check"

    check_docker

    echo ""
    print_info "Checking service endpoints..."

    # Check backend
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend (port 8000): HEALTHY"
    else
        print_error "Backend (port 8000): UNREACHABLE"
    fi

    # Check frontend
    if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend (port 3000): HEALTHY"
    else
        print_error "Frontend (port 3000): UNREACHABLE"
    fi

    # Check database
    if docker exec "${PROJECT_NAME}_db" pg_isready -U uploader > /dev/null 2>&1; then
        print_success "PostgreSQL: HEALTHY"
    else
        print_error "PostgreSQL: UNAVAILABLE"
    fi

    # Check redis
    if docker exec "${PROJECT_NAME}_redis" redis-cli ping > /dev/null 2>&1; then
        print_success "Redis: HEALTHY"
    else
        print_error "Redis: UNAVAILABLE"
    fi
}

cmd_urls() {
    print_header "Access URLs"

    echo ""
    echo -e "${CYAN}Frontend:${NC}"
    echo "  http://localhost:3000"
    echo ""
    echo -e "${CYAN}Backend API:${NC}"
    echo "  http://localhost:8000"
    echo "  http://localhost:8000/docs (Swagger UI)"
    echo "  http://localhost:8000/redoc (ReDoc)"
    echo ""
    echo -e "${CYAN}Database:${NC}"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: data_uploader"
    echo "  User: uploader"
    echo ""
    echo -e "${CYAN}Redis:${NC}"
    echo "  Host: localhost"
    echo "  Port: 6379"
    echo ""
    echo -e "${CYAN}Default Login:${NC}"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    print_warning "Change the default password after first login!"
    echo ""
}

cmd_demo() {
    print_header "Demo Credentials"

    echo ""
    echo "See DEMO_CREDENTIALS.md for complete list of all demo users"
    echo ""
    echo -e "${CYAN}Quick Access:${NC}"
    echo ""
    echo "Default Admin:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    echo "Kenya (Africa):"
    echo "  Username: jkamau"
    echo "  Password: admin123"
    echo ""
    echo "Brazil (Latin America):"
    echo "  Username: msilva"
    echo "  Password: admin123"
    echo ""
    echo "Thailand (Asia):"
    echo "  Username: sprasertsuk"
    echo "  Password: admin123"
    echo ""
    echo "Germany (Europe):"
    echo "  Username: hmüller"
    echo "  Password: admin123"
    echo ""
    print_info "All 29 demo users use password: admin123"
    echo ""
}

cmd_update() {
    print_header "Updating Stack"

    check_docker
    check_compose

    print_info "Pulling latest code (if using git)..."
    if [ -d ".git" ]; then
        git pull origin main || print_warning "Could not pull from git (manual update needed)"
    fi

    print_info "Pulling latest images..."
    docker compose pull

    print_info "Rebuilding services..."
    docker compose build

    print_info "Restarting with new images..."
    docker compose up -d

    print_success "Update complete!"
    cmd_status
}

cmd_help() {
    cat << EOF

${CYAN}Data Uploader Stack Management${NC}

${YELLOW}Usage:${NC}
  ./stack.sh <command> [options]

${YELLOW}Stack Management:${NC}
  start                 Start all services
  stop                  Stop all services (keep containers)
  restart               Restart all services
  down                  Stop and remove containers (keep data)
  destroy               Remove everything including data (⚠️  DANGEROUS)
  status                Show status of all services
  ps                    List containers (alias for status)

${YELLOW}Logs & Monitoring:${NC}
  logs [service]        Follow logs (all services or specific one)
  logs-tail [service]   Show last 50 log lines
  health                Check health of all endpoints
  urls                  Show all access URLs

${YELLOW}Build & Deploy:${NC}
  build [options] [service]  Build Docker images
    --no-cache          Build without using cache
    --pull              Pull latest base images before building
    --parallel          Build images in parallel
  rebuild [service]     Rebuild and restart services
  pull                  Pull latest base images
  update                Pull code, rebuild, and restart

${YELLOW}Database:${NC}
  db shell              Open PostgreSQL shell
  db backup             Create database backup
  db restore <file>     Restore from backup file
  db reset              Reset database (deletes all data)
  db stats              Show database statistics

${YELLOW}Redis:${NC}
  redis cli             Open Redis CLI
  redis ping            Ping Redis
  redis info            Show Redis info
  redis flush           Flush all Redis data

${YELLOW}Utilities:${NC}
  exec <service> [cmd]  Execute command in service container
  scale <number>        Scale worker instances
  clean                 Clean unused Docker resources
  demo                  Show demo user credentials

${YELLOW}Services:${NC}
  postgres              PostgreSQL database
  redis                 Redis cache/queue
  backend               FastAPI backend
  worker                Background job worker
  frontend              Next.js frontend

${YELLOW}Examples:${NC}
  ./stack.sh start
  ./stack.sh build
  ./stack.sh build --no-cache backend
  ./stack.sh build --pull --parallel
  ./stack.sh logs backend
  ./stack.sh exec backend bash
  ./stack.sh db backup
  ./stack.sh scale 3
  ./stack.sh health

${YELLOW}Documentation:${NC}
  README.md             Project overview
  DEPLOYMENT.md         Deployment guide
  DEMO_CREDENTIALS.md   All demo user logins

EOF
}

# Main command dispatcher
case "${1:-help}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    down)
        cmd_down
        ;;
    destroy)
        cmd_destroy
        ;;
    status|ps)
        cmd_status
        ;;
    logs)
        shift
        cmd_logs "$@"
        ;;
    logs-tail|tail)
        shift
        cmd_logs_tail "$@"
        ;;
    build)
        shift
        cmd_build "$@"
        ;;
    rebuild)
        shift
        cmd_rebuild "$@"
        ;;
    pull)
        cmd_pull
        ;;
    exec)
        shift
        cmd_exec "$@"
        ;;
    db)
        shift
        cmd_db "$@"
        ;;
    redis)
        shift
        cmd_redis "$@"
        ;;
    scale)
        shift
        cmd_scale "$@"
        ;;
    clean)
        cmd_clean
        ;;
    health)
        cmd_health
        ;;
    urls)
        cmd_urls
        ;;
    demo)
        cmd_demo
        ;;
    update)
        cmd_update
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac
