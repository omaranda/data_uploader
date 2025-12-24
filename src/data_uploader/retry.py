"""Retry mechanism for failed uploads."""

import time
from typing import List, Dict, Any, Callable, Optional

from .database import Database
from .s3_uploader import S3Uploader
from .progress import ProgressTracker, print_status


class RetryManager:
    """Manage retry logic for failed uploads."""

    def __init__(
        self,
        database: Database,
        s3_uploader: S3Uploader,
        max_attempts: int = 3,
        delay_seconds: int = 5
    ):
        """Initialize retry manager.

        Args:
            database: Database instance
            s3_uploader: S3Uploader instance
            max_attempts: Maximum retry attempts
            delay_seconds: Delay between retries in seconds
        """
        self.database = database
        self.s3_uploader = s3_uploader
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds

    def retry_failed_files(
        self,
        session_id: int,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Retry all failed files for a session.

        Args:
            session_id: Session ID
            progress_callback: Optional progress callback

        Returns:
            Dictionary with retry statistics
        """
        # Get failed files
        failed_files = self.database.get_failed_files(session_id)

        if not failed_files:
            print_status("✅", "No failed files to retry")
            return {
                'total': 0,
                'retried': 0,
                'successful': 0,
                'still_failed': 0
            }

        print_status("🔄", f"Found {len(failed_files):,} failed files to retry")

        stats = {
            'total': len(failed_files),
            'retried': 0,
            'successful': 0,
            'still_failed': 0
        }

        # Calculate total size
        total_size = sum(f['file_size'] for f in failed_files)

        # Create progress tracker
        tracker = ProgressTracker(len(failed_files), total_size)

        # Retry each file
        for file_info in failed_files:
            retry_count = file_info['retry_count']

            # Check if we've exceeded max attempts
            if retry_count >= self.max_attempts:
                print_status(
                    "⚠️",
                    f"Skipping {file_info['local_path']} - max retries exceeded"
                )
                stats['still_failed'] += 1
                continue

            # Wait before retry
            if retry_count > 0:
                time.sleep(self.delay_seconds)

            stats['retried'] += 1

            # Attempt upload
            result = self.s3_uploader.upload_file(
                file_info['local_path'],
                file_info['s3_key'],
                retry_count,
                self.max_attempts
            )

            # Update database
            if result['success']:
                self.database.mark_file_uploaded(file_info['id'])
                stats['successful'] += 1
                tracker.update(uploaded=1, file_size=file_info['file_size'])
            else:
                self.database.mark_file_failed(
                    file_info['id'],
                    result['error'],
                    result['retry_count']
                )
                stats['still_failed'] += 1
                tracker.update(failed=1)

            # Update progress
            tracker.display_progress_bar()

            # Call custom progress callback
            if progress_callback:
                progress_callback(stats)

        # Final progress
        tracker.display_progress_bar(force=True)
        tracker.display_final_summary()

        return stats

    def auto_retry_with_backoff(
        self,
        session_id: int,
        max_rounds: int = 3
    ) -> Dict[str, Any]:
        """Automatically retry failed files with exponential backoff.

        Args:
            session_id: Session ID
            max_rounds: Maximum retry rounds

        Returns:
            Dictionary with final statistics
        """
        print_status("🔄", f"Auto-retry enabled: {max_rounds} rounds with exponential backoff")

        all_stats = {
            'rounds': [],
            'total_failed': 0,
            'total_recovered': 0
        }

        for round_num in range(1, max_rounds + 1):
            print(f"\n--- Retry Round {round_num}/{max_rounds} ---")

            stats = self.retry_failed_files(session_id)

            all_stats['rounds'].append(stats)
            all_stats['total_recovered'] += stats['successful']

            # If no files left to retry, we're done
            if stats['still_failed'] == 0:
                print_status("✅", "All files successfully uploaded!")
                break

            # Exponential backoff delay between rounds
            if round_num < max_rounds:
                delay = self.delay_seconds * (2 ** (round_num - 1))
                print_status("⏳", f"Waiting {delay}s before next retry round...")
                time.sleep(delay)

        # Final failed count
        all_stats['total_failed'] = (
            all_stats['rounds'][-1]['still_failed'] if all_stats['rounds'] else 0
        )

        return all_stats
