# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Upload worker - executes upload jobs as background tasks."""

from __future__ import annotations

import time
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from app.database import SessionLocal
from app.models import SyncSession


def run_upload(session_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute upload job for a given session.

    This function runs as a background RQ job.

    NOTE: This is a simplified implementation for demonstration.
    In production, this would integrate with the existing upload.py script
    or implement the full S3 upload logic directly.

    Args:
        session_id: The sync session ID
        config: Upload configuration with keys:
            - local_directory: str
            - bucket_name: str (from project)
            - s3_prefix: str
            - aws_region: str (from project)
            - aws_profile: str
            - max_workers: int
            - times_to_retry: int
            - use_find: bool

    Returns:
        Dictionary with execution results
    """
    db = SessionLocal()

    try:
        # Get session from database
        session = db.query(SyncSession).filter(SyncSession.id == session_id).first()

        if not session:
            return {
                'success': False,
                'error': f'Session {session_id} not found'
            }

        # Update session status to in_progress
        session.status = 'in_progress'
        session.started_at = datetime.utcnow()
        db.commit()

        # Verify local directory exists
        local_dir = Path(config['local_directory'])
        if not local_dir.exists():
            session.status = 'failed'
            session.completed_at = datetime.utcnow()
            db.commit()

            return {
                'success': False,
                'session_id': session_id,
                'error': f"Local directory not found: {config['local_directory']}"
            }

        # Simulate file scanning and upload
        # In production, this would call the actual S3 upload logic
        print(f"[Worker] Processing upload job for session {session_id}")
        print(f"[Worker] Local directory: {config['local_directory']}")
        print(f"[Worker] S3 bucket: {config['bucket_name']}")
        print(f"[Worker] S3 prefix: {config['s3_prefix']}")

        # Count files (simple implementation)
        try:
            files = list(local_dir.rglob('*'))
            file_list = [f for f in files if f.is_file()]
            total_files = len(file_list)

            print(f"[Worker] Found {total_files} files to process")

            # Simulate processing with progress updates
            for i, file_path in enumerate(file_list, 1):
                # Simulate upload time
                time.sleep(0.1)

                # Update progress
                session.total_files = total_files
                session.files_uploaded = i
                session.total_size_bytes = sum(f.stat().st_size for f in file_list[:i])
                db.commit()

                print(f"[Worker] Processed {i}/{total_files}: {file_path.name}")

            # Mark as completed
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
            db.commit()

            print(f"[Worker] Upload job {session_id} completed successfully")

            return {
                'success': True,
                'session_id': session_id,
                'total_files': total_files,
                'files_uploaded': total_files,
                'files_failed': 0,
                'message': f'Successfully processed {total_files} files'
            }

        except Exception as e:
            session.status = 'failed'
            session.completed_at = datetime.utcnow()
            db.commit()

            return {
                'success': False,
                'session_id': session_id,
                'error': f'Error processing files: {str(e)}'
            }

    except Exception as e:
        session.status = 'failed'
        session.completed_at = datetime.utcnow()
        db.commit()

        return {
            'success': False,
            'session_id': session_id,
            'error': str(e)
        }

    finally:
        db.close()
