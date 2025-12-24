#!/usr/bin/env python
"""Retry script for failed uploads."""

import sys
from pathlib import Path

import click
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_uploader.config import Config
from data_uploader.database import Database
from data_uploader.s3_uploader import S3Uploader
from data_uploader.retry import RetryManager
from data_uploader.progress import print_status, print_header


# Load environment variables
load_dotenv()


@click.command()
@click.option('--session-id', '-s', required=True, type=int,
              help='Session ID to retry failed files for')
@click.option('--max-attempts', '-m', type=int, default=3,
              help='Maximum retry attempts per file')
@click.option('--delay', '-d', type=int, default=5,
              help='Delay between retries in seconds')
@click.option('--auto-retry', '-a', is_flag=True,
              help='Enable automatic retry with exponential backoff')
@click.option('--max-rounds', '-r', type=int, default=3,
              help='Maximum retry rounds for auto-retry mode')
def main(session_id, max_attempts, delay, auto_retry, max_rounds):
    """Retry failed uploads for a specific session."""

    # Load config for database connection
    cfg = Config.from_env()

    # Initialize database
    db = Database(cfg)

    try:
        # Get session info
        session_info = db.get_session_info(session_id)

        if not session_info:
            click.echo(f"❌ Session not found: {session_id}", err=True)
            sys.exit(1)

        print_header("🔄 RETRY FAILED UPLOADS")
        print_status("📋", f"Session ID: {session_id}")
        print_status("📁", f"Bucket: {session_info['bucket_name']}")
        print_status("📂", f"Prefix: {session_info['s3_prefix']}")
        print_status("⚙️", f"Max attempts: {max_attempts}")
        print_status("⏱️", f"Delay: {delay}s")

        # Initialize S3 uploader
        uploader = S3Uploader(
            bucket_name=session_info['bucket_name'],
            aws_region=session_info['aws_region'],
            aws_profile=session_info['aws_profile'],
            max_workers=session_info['max_workers']
        )

        # Initialize retry manager
        retry_manager = RetryManager(
            database=db,
            s3_uploader=uploader,
            max_attempts=max_attempts,
            delay_seconds=delay
        )

        # Retry files
        if auto_retry:
            stats = retry_manager.auto_retry_with_backoff(
                session_id=session_id,
                max_rounds=max_rounds
            )

            print_header("AUTO-RETRY SUMMARY")
            print(f"Total rounds: {len(stats['rounds'])}")
            print(f"Files recovered: {stats['total_recovered']:,}")
            print(f"Files still failed: {stats['total_failed']:,}")

        else:
            stats = retry_manager.retry_failed_files(session_id)

            print_header("RETRY SUMMARY")
            print(f"Total failed files: {stats['total']:,}")
            print(f"Files retried: {stats['retried']:,}")
            print(f"Successful: {stats['successful']:,}")
            print(f"Still failed: {stats['still_failed']:,}")

        # Update session stats
        if stats.get('successful', 0) > 0 or stats.get('total_recovered', 0) > 0:
            session_info = db.get_session_info(session_id)
            print_status("✅", "Session statistics updated")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
