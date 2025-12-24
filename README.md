# Data Uploader

A Python CLI application for uploading field sensor data (audio recordings, camera trap images/videos) to AWS S3 buckets with PostgreSQL-backed tracking and resume capability.

## Features

- Upload large datasets (300k+ files) to AWS S3
- Resume support - track upload status and skip already uploaded files
- Configurable retry mechanism for failed uploads
- Progress tracking with in-place progress bar
- Support for both Linux/macOS (find command) and Windows (Python scanning)
- PostgreSQL database for tracking sync sessions and file status
- Configuration via JSON files with CLI override support

## Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- AWS credentials configured in `~/.aws/credentials`

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start PostgreSQL database:
   ```bash
   docker-compose up -d
   ```
5. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

### Configuration

Create a JSON configuration file in `config_files/` directory:

```json
{
    "local_directory": "path/to/data",
    "bucket_name": "your-bucket-name",
    "s3_prefix": "C1",
    "max_workers": 15,
    "aws_region": "eu-west-1",
    "times_to_retry": 3,
    "aws_profile": "aws-eos",
    "use_find": "yes"
}
```

### Usage

Upload files:
```bash
python scripts/upload.py --config config_files/your_config.json
```

Retry failed uploads:
```bash
python scripts/retry.py --session-id <session_id>
```

Run full pipeline:
```bash
python scripts/master.py --config config_files/your_config.json
```

## Documentation

- [Quick Start Guide](doc/QUICKSTART.md) - Detailed setup and usage instructions
- [Architecture Overview](doc/ARCHITECTURE.md) - System design and data flow
- [Database Schema](doc/DATABASE_SCHEMA.md) - Database structure and queries
- [Grafana Queries](doc/GRAFANA_QUERIES.md) - Monitoring dashboard queries
- [Project Structure](doc/PROJECT_STRUCTURE.md) - File organization

## Project Structure

```
data_uploader/
├── scripts/           # CLI scripts (upload, retry, trigger, master)
├── src/data_uploader/ # Core modules (config, database, s3, scanner)
├── config_files/      # JSON configuration files
├── doc/               # Documentation
├── sql/               # Database schema
└── logs/              # Application logs
```

## Key Scripts

- **upload.py**: Main upload script - scan and upload files to S3
- **retry.py**: Retry failed uploads with auto-retry support
- **trigger_endpoint.py**: Call external API after upload
- **master.py**: Run complete pipeline (upload → retry → trigger)
- **init_db.py**: Initialize database schema

## Supported File Types

- Audio: `.wav`
- Images: `.jpg`, `.jpeg`
- Video: `.mp4`, `.mov`, `.avi`

## Key Features

### Resume Capability
Automatically tracks uploaded files in PostgreSQL. Interrupted uploads can be resumed - previously uploaded files are skipped.

### Parallel Uploads
Uses ThreadPoolExecutor with configurable workers (default: 15) for fast parallel uploads.

### Smart File Discovery
- Native `find` command on Linux/macOS (fastest)
- Python `os.walk` fallback on Windows
- Progress updates every 10,000 files

### Retry Logic
- Automatic retry during upload (configurable attempts)
- Manual retry script for failed files
- Auto-retry with exponential backoff

### Monitoring
- Real-time progress bar with speed and ETA
- PostgreSQL tracking of all uploads
- Grafana dashboards for analytics

## Contributing

When adding new features:
1. Update relevant modules in `src/data_uploader/`
2. Update documentation in `doc/`
3. Update CLAUDE.md if architecture changes

## License

See [LICENSE](LICENSE) file.
