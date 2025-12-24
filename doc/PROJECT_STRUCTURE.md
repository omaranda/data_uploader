# Project Structure

```
data_uploader/
│
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── CLAUDE.md                     # Claude Code guidance
├── LICENSE                       # Project license
├── README.md                     # Project overview
├── SOW.md                        # Statement of Work
├── docker-compose.yml            # Docker services configuration
├── requirements.txt              # Python dependencies
│
├── config_files/                 # Configuration files directory
│   └── example_config.json       # Example configuration template
│
├── doc/                          # Documentation
│   ├── ARCHITECTURE.md           # System architecture overview
│   ├── DATABASE_SCHEMA.md        # Database schema documentation
│   ├── GRAFANA_QUERIES.md        # Grafana dashboard queries
│   ├── PROJECT_STRUCTURE.md      # This file
│   └── QUICKSTART.md             # Quick start guide
│
├── logs/                         # Application logs (created at runtime)
│
├── scripts/                      # CLI scripts
│   ├── init_db.py                # Database initialization script
│   ├── master.py                 # Master pipeline orchestrator
│   ├── retry.py                  # Retry failed uploads script
│   ├── trigger_endpoint.py       # Endpoint trigger script
│   └── upload.py                 # Main upload script
│
├── sql/                          # SQL scripts
│   └── init.sql                  # Database schema initialization
│
└── src/                          # Source code
    └── data_uploader/            # Main package
        ├── __init__.py           # Package initialization
        ├── config.py             # Configuration management
        ├── database.py           # Database operations
        ├── file_scanner.py       # File discovery module
        ├── progress.py           # Progress tracking utilities
        ├── retry.py              # Retry logic manager
        └── s3_uploader.py        # S3 upload functionality
```

## File Descriptions

### Root Level

- **`.env`**: Environment variables for database connection (not in git)
- **`.env.example`**: Template for environment variables
- **`.gitignore`**: Specifies files to ignore in git
- **`CLAUDE.md`**: Instructions for Claude Code when working in this repo
- **`LICENSE`**: Project license file
- **`README.md`**: Main project documentation and getting started guide
- **`SOW.md`**: Original statement of work and requirements
- **`docker-compose.yml`**: Docker configuration for PostgreSQL database
- **`requirements.txt`**: Python package dependencies

### config_files/

Configuration JSON files for upload sessions. Each file contains:
- Local directory path
- S3 bucket and prefix
- AWS credentials
- Upload settings

**Note:** User configuration files are gitignored for security. Only `example_config.json` is tracked.

### doc/

Complete project documentation:

- **`ARCHITECTURE.md`**: System design, data flow, and component interactions
- **`DATABASE_SCHEMA.md`**: Database tables, columns, and relationships
- **`GRAFANA_QUERIES.md`**: SQL queries for monitoring dashboards
- **`PROJECT_STRUCTURE.md`**: This file - project organization
- **`QUICKSTART.md`**: Step-by-step setup and usage guide

### logs/

Runtime directory for application logs (created automatically).

### scripts/

Executable Python scripts for CLI operations:

- **`init_db.py`**: Initialize database schema
- **`upload.py`**: Main upload script - scan files and upload to S3
- **`retry.py`**: Retry failed uploads for a session
- **`trigger_endpoint.py`**: Call external API to register uploaded files
- **`master.py`**: Run complete pipeline (upload → retry → trigger)

All scripts support `--help` flag for usage information.

### sql/

SQL scripts for database management:

- **`init.sql`**: Creates all tables, indexes, and triggers

### src/data_uploader/

Core Python modules:

- **`config.py`**: Configuration loader and validator
  - Load from JSON files
  - Merge with environment variables
  - CLI override support

- **`database.py`**: PostgreSQL operations
  - Connection management
  - CRUD operations for all tables
  - Batch inserts for performance

- **`file_scanner.py`**: File discovery
  - Native `find` command (Unix)
  - Python `os.walk` fallback (Windows)
  - Filter by supported extensions
  - Progress callbacks

- **`s3_uploader.py`**: S3 upload functionality
  - AWS credential verification
  - Parallel uploads with ThreadPoolExecutor
  - Automatic retry logic
  - S3 file listing

- **`retry.py`**: Retry manager
  - Manual retry mode
  - Auto-retry with exponential backoff
  - Tracks retry counts
  - Updates database

- **`progress.py`**: Progress tracking
  - Real-time progress bar
  - Speed calculation
  - ETA estimation
  - Human-readable formatting

## Development Workflow

1. **Setup**
   ```bash
   docker-compose up -d          # Start database
   python -m venv venv           # Create virtual environment
   source venv/bin/activate      # Activate (Windows: venv\Scripts\activate)
   pip install -r requirements.txt
   python scripts/init_db.py     # Initialize database
   ```

2. **Create Configuration**
   ```bash
   cp config_files/example_config.json config_files/my_project.json
   # Edit my_project.json with your settings
   ```

3. **Upload Files**
   ```bash
   python scripts/upload.py --config config_files/my_project.json
   ```

4. **Retry Failed (if needed)**
   ```bash
   python scripts/retry.py --session-id <id> --auto-retry
   ```

5. **Monitor**
   - Check terminal output
   - Query database for statistics
   - Use Grafana dashboards

## Adding New Features

### Adding a New Script

1. Create script in `scripts/` directory
2. Add to README.md usage section
3. Update QUICKSTART.md if user-facing

### Adding a New Module

1. Create module in `src/data_uploader/`
2. Import in `__init__.py` if needed
3. Add unit tests (if test framework added)
4. Document in ARCHITECTURE.md

### Adding a Database Table

1. Update `sql/init.sql` with new table
2. Add methods to `database.py`
3. Update DATABASE_SCHEMA.md
4. Add Grafana queries if relevant

### Adding a Configuration Option

1. Update Config class in `config.py`
2. Update `config_files/example_config.json`
3. Document in QUICKSTART.md
4. Add CLI flag if needed

## Configuration Files Not in Git

For security, these are gitignored:
- `config_files/*.json` (except example)
- `.env`
- `logs/*.log`
- Python cache files
- Virtual environment directories
