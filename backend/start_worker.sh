#!/bin/bash
# Start RQ worker for processing upload jobs

cd "$(dirname "$0")"

# Fix macOS fork() issue
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

echo "Starting RQ worker for upload queue..."
./venv/bin/rq worker uploads --url redis://localhost:6379
