# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Job queue service using Redis Queue (RQ)."""

from __future__ import annotations

import redis
from rq import Queue
from typing import Optional, Dict, Any

from app.config import settings


# Redis connection
redis_conn = redis.Redis(
    host=getattr(settings, 'REDIS_HOST', 'localhost'),
    port=getattr(settings, 'REDIS_PORT', 6379),
    db=getattr(settings, 'REDIS_DB', 0),
    decode_responses=False
)

# Job queues
upload_queue = Queue('uploads', connection=redis_conn, default_timeout='24h')


def enqueue_upload_job(
    session_id: int,
    config: Dict[str, Any],
    timeout: Optional[str] = '24h'
) -> str:
    """
    Enqueue an upload job to the background queue.

    Args:
        session_id: The sync session ID
        config: Upload configuration dictionary
        timeout: Job timeout (default: 24 hours)

    Returns:
        Job ID
    """
    from app.workers.upload_worker import run_upload

    job = upload_queue.enqueue(
        run_upload,
        session_id=session_id,
        config=config,
        job_timeout=timeout
    )

    return job.id


def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a job.

    Args:
        job_id: The job ID

    Returns:
        Dictionary with job status information
    """
    from rq.job import Job

    try:
        job = Job.fetch(job_id, connection=redis_conn)

        return {
            'job_id': job.id,
            'status': job.get_status(),
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'ended_at': job.ended_at.isoformat() if job.ended_at else None,
            'result': job.result,
            'exc_info': job.exc_info
        }
    except Exception as e:
        return {
            'job_id': job_id,
            'status': 'not_found',
            'error': str(e)
        }


def cancel_job(job_id: str) -> bool:
    """
    Cancel a job.

    Args:
        job_id: The job ID

    Returns:
        True if cancelled successfully
    """
    from rq.job import Job

    try:
        job = Job.fetch(job_id, connection=redis_conn)
        job.cancel()
        return True
    except Exception:
        return False
