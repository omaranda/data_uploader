"""Database connection and models for data uploader."""

import json
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

from .config import Config


class Database:
    """Database connection manager."""

    def __init__(self, config: Config):
        """Initialize database connection.

        Args:
            config: Configuration object with database settings
        """
        self.config = config
        self._connection = None

    def connect(self) -> None:
        """Establish database connection."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                host=self.config.db_host,
                port=self.config.db_port,
                database=self.config.db_name,
                user=self.config.db_user,
                password=self.config.db_password
            )

    def close(self) -> None:
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()

    @contextmanager
    def cursor(self):
        """Context manager for database cursor.

        Yields:
            Database cursor
        """
        self.connect()
        cur = self._connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cur.close()

    def get_or_create_project(self, project_name: str, bucket_name: str, aws_region: str) -> int:
        """Get existing project or create new one.

        Args:
            project_name: Name of the project
            bucket_name: S3 bucket name
            aws_region: AWS region

        Returns:
            Project ID
        """
        with self.cursor() as cur:
            # Try to get existing project
            cur.execute(
                "SELECT id FROM projects WHERE bucket_name = %s",
                (bucket_name,)
            )
            result = cur.fetchone()

            if result:
                return result['id']

            # Create new project
            cur.execute(
                """
                INSERT INTO projects (project_name, bucket_name, aws_region)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (project_name, bucket_name, aws_region)
            )
            return cur.fetchone()['id']

    def create_sync_session(
        self,
        project_id: int,
        local_directory: str,
        s3_prefix: str,
        aws_profile: str,
        max_workers: int,
        times_to_retry: int,
        use_find: bool
    ) -> int:
        """Create a new sync session.

        Args:
            project_id: Project ID
            local_directory: Local directory path
            s3_prefix: S3 prefix (cycle)
            aws_profile: AWS profile name
            max_workers: Number of parallel workers
            times_to_retry: Number of retry attempts
            use_find: Whether find command was used

        Returns:
            Session ID
        """
        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sync_sessions (
                    project_id, local_directory, s3_prefix, aws_profile,
                    max_workers, times_to_retry, use_find
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (project_id, local_directory, s3_prefix, aws_profile,
                 max_workers, times_to_retry, use_find)
            )
            return cur.fetchone()['id']

    def save_config(self, session_id: int, config_dict: dict) -> None:
        """Save configuration to config_history.

        Args:
            session_id: Session ID
            config_dict: Configuration dictionary
        """
        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO config_history (session_id, config_json)
                VALUES (%s, %s)
                """,
                (session_id, json.dumps(config_dict))
            )

    def insert_files_batch(self, session_id: int, files: List[Dict[str, Any]]) -> None:
        """Insert multiple files in batch.

        Args:
            session_id: Session ID
            files: List of file dictionaries with keys: local_path, s3_key, file_size, file_type
        """
        if not files:
            return

        with self.cursor() as cur:
            values = [
                (session_id, f['local_path'], f['s3_key'], f['file_size'], f['file_type'])
                for f in files
            ]

            execute_values(
                cur,
                """
                INSERT INTO file_uploads (session_id, local_path, s3_key, file_size, file_type)
                VALUES %s
                """,
                values
            )

    def get_uploaded_files(self, bucket_name: str, s3_prefix: str) -> set:
        """Get set of S3 keys that were previously uploaded successfully.

        Args:
            bucket_name: S3 bucket name
            s3_prefix: S3 prefix

        Returns:
            Set of S3 keys
        """
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT fu.s3_key
                FROM file_uploads fu
                JOIN sync_sessions ss ON fu.session_id = ss.id
                JOIN projects p ON ss.project_id = p.id
                WHERE p.bucket_name = %s
                  AND ss.s3_prefix = %s
                  AND fu.status = 'uploaded'
                """,
                (bucket_name, s3_prefix)
            )
            return {row['s3_key'] for row in cur.fetchall()}

    def get_pending_files(self, session_id: int) -> List[Dict[str, Any]]:
        """Get files pending upload for a session.

        Args:
            session_id: Session ID

        Returns:
            List of file records
        """
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT id, local_path, s3_key, file_size, file_type, retry_count
                FROM file_uploads
                WHERE session_id = %s AND status = 'pending'
                ORDER BY id
                """,
                (session_id,)
            )
            return [dict(row) for row in cur.fetchall()]

    def get_failed_files(self, session_id: int) -> List[Dict[str, Any]]:
        """Get files that failed to upload.

        Args:
            session_id: Session ID

        Returns:
            List of failed file records
        """
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT id, local_path, s3_key, file_size, file_type, retry_count, error_message
                FROM file_uploads
                WHERE session_id = %s AND status = 'failed'
                ORDER BY id
                """,
                (session_id,)
            )
            return [dict(row) for row in cur.fetchall()]

    def mark_file_uploaded(self, file_id: int) -> None:
        """Mark a file as successfully uploaded.

        Args:
            file_id: File record ID
        """
        with self.cursor() as cur:
            cur.execute(
                """
                UPDATE file_uploads
                SET status = 'uploaded', uploaded_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (file_id,)
            )

    def mark_file_failed(self, file_id: int, error_message: str, retry_count: int) -> None:
        """Mark a file as failed.

        Args:
            file_id: File record ID
            error_message: Error message
            retry_count: Number of retry attempts
        """
        with self.cursor() as cur:
            cur.execute(
                """
                UPDATE file_uploads
                SET status = 'failed', error_message = %s, retry_count = %s
                WHERE id = %s
                """,
                (error_message, retry_count, file_id)
            )

    def update_session_stats(
        self,
        session_id: int,
        total_files: int,
        total_size: int,
        files_uploaded: int,
        files_failed: int,
        files_skipped: int
    ) -> None:
        """Update session statistics.

        Args:
            session_id: Session ID
            total_files: Total number of files
            total_size: Total size in bytes
            files_uploaded: Number of files uploaded
            files_failed: Number of files failed
            files_skipped: Number of files skipped
        """
        with self.cursor() as cur:
            cur.execute(
                """
                UPDATE sync_sessions
                SET total_files = %s,
                    total_size_bytes = %s,
                    files_uploaded = %s,
                    files_failed = %s,
                    files_skipped = %s
                WHERE id = %s
                """,
                (total_files, total_size, files_uploaded, files_failed, files_skipped, session_id)
            )

    def complete_session(self, session_id: int, status: str = 'completed') -> None:
        """Mark session as completed.

        Args:
            session_id: Session ID
            status: Final status (completed/failed)
        """
        with self.cursor() as cur:
            cur.execute(
                """
                UPDATE sync_sessions
                SET status = %s, completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (status, session_id)
            )

    def get_session_info(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get session information.

        Args:
            session_id: Session ID

        Returns:
            Session information or None
        """
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT ss.*, p.bucket_name, p.aws_region
                FROM sync_sessions ss
                JOIN projects p ON ss.project_id = p.id
                WHERE ss.id = %s
                """,
                (session_id,)
            )
            result = cur.fetchone()
            return dict(result) if result else None
