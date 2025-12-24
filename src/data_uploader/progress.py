"""Progress tracking and display utilities."""

import sys
import time
from datetime import datetime, timedelta
from typing import Optional


class ProgressTracker:
    """Track and display upload progress."""

    def __init__(self, total_files: int, total_size: int):
        """Initialize progress tracker.

        Args:
            total_files: Total number of files to upload
            total_size: Total size in bytes
        """
        self.total_files = total_files
        self.total_size = total_size
        self.uploaded = 0
        self.failed = 0
        self.skipped = 0
        self.successful = 0
        self.uploaded_size = 0
        self.start_time = time.time()
        self.last_update = 0

    def update(self, uploaded: int = 0, failed: int = 0, skipped: int = 0, file_size: int = 0):
        """Update progress counts.

        Args:
            uploaded: Number of files uploaded
            failed: Number of files failed
            skipped: Number of files skipped
            file_size: Size of file in bytes
        """
        self.uploaded += uploaded
        self.failed += failed
        self.skipped += skipped

        if uploaded:
            self.successful += uploaded
            self.uploaded_size += file_size

    def get_progress_percentage(self) -> float:
        """Get progress percentage.

        Returns:
            Progress percentage (0-100)
        """
        total_processed = self.uploaded + self.failed + self.skipped
        if self.total_files == 0:
            return 100.0
        return (total_processed / self.total_files) * 100

    def get_upload_speed(self) -> float:
        """Get upload speed in files per second.

        Returns:
            Upload speed (files/sec)
        """
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        return self.uploaded / elapsed

    def get_eta(self) -> Optional[str]:
        """Get estimated time of arrival.

        Returns:
            ETA string (HH:MM:SS) or None
        """
        remaining = self.total_files - (self.uploaded + self.failed + self.skipped)
        if remaining <= 0:
            return "00:00:00"

        speed = self.get_upload_speed()
        if speed == 0:
            return None

        eta_seconds = remaining / speed
        eta_delta = timedelta(seconds=int(eta_seconds))

        hours, remainder = divmod(eta_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def display_progress_bar(self, force: bool = False):
        """Display progress bar in terminal.

        Args:
            force: Force display even if update interval hasn't elapsed
        """
        current_time = time.time()

        # Update every 0.5 seconds unless forced
        if not force and (current_time - self.last_update) < 0.5:
            return

        self.last_update = current_time

        percentage = self.get_progress_percentage()
        speed = self.get_upload_speed()
        eta = self.get_eta()
        size = self.format_size(self.uploaded_size)

        total_processed = self.uploaded + self.failed + self.skipped

        # Build progress bar
        progress_bar = (
            f"\r| {percentage:.1f}% | "
            f"Uploaded: {total_processed:,}/{self.total_files:,} | "
            f"Skipped: {self.skipped:,} | "
            f"Size: {size} | "
            f"Successful: {self.successful:,} | "
            f"Failed: {self.failed:,} | "
            f"Speed: {speed:.1f} files/s"
        )

        if eta:
            progress_bar += f" | ETA: {eta}"

        # Write progress bar (overwrite previous line)
        sys.stdout.write(progress_bar)
        sys.stdout.flush()

    def display_final_summary(self):
        """Display final summary after completion."""
        # Move to new line after progress bar
        print()

        elapsed = time.time() - self.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        print("\n" + "=" * 88)
        print("UPLOAD SUMMARY")
        print("=" * 88)
        print(f"Total files processed: {self.uploaded + self.failed + self.skipped:,}")
        print(f"Successfully uploaded: {self.successful:,}")
        print(f"Failed: {self.failed:,}")
        print(f"Skipped (already in S3): {self.skipped:,}")
        print(f"Total size uploaded: {self.format_size(self.uploaded_size)}")
        print(f"Total time: {elapsed_str}")
        print(f"Average speed: {self.get_upload_speed():.1f} files/sec")
        print("=" * 88)


def print_status(emoji: str, message: str):
    """Print status message with emoji.

    Args:
        emoji: Emoji character
        message: Status message
    """
    print(f"{emoji} {message}")


def print_header(title: str):
    """Print section header.

    Args:
        title: Header title
    """
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)
