# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python
"""Main upload script for uploading files to S3."""

import os
import sys
import time
from pathlib import Path

import click
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_uploader.config import Config
from data_uploader.database import Database
from data_uploader.file_scanner import FileScanner
from data_uploader.s3_uploader import S3Uploader
from data_uploader.progress import ProgressTracker, print_status, print_header


# Load environment variables
load_dotenv()


@click.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to JSON configuration file')
@click.option('--local-directory', '-d', type=str,
              help='Override local directory from config')
@click.option('--bucket-name', '-b', type=str,
              help='Override bucket name from config')
@click.option('--s3-prefix', '-p', type=str,
              help='Override S3 prefix from config')
@click.option('--max-workers', '-w', type=int,
              help='Override max workers from config')
@click.option('--aws-profile', type=str,
              help='Override AWS profile from config')
@click.option('--dry-run', is_flag=True,
              help='Analyze files without uploading')
def main(config, local_directory, bucket_name, s3_prefix, max_workers, aws_profile, dry_run):
    """Upload files to S3 with database tracking and resume support."""

    # Load configuration
    cfg = Config.from_json_file(config)
    cfg.merge_with_env()

    # Apply CLI overrides
    if local_directory:
        cfg.local_directory = local_directory
    if bucket_name:
        cfg.bucket_name = bucket_name
    if s3_prefix:
        cfg.s3_prefix = s3_prefix
    if max_workers:
        cfg.max_workers = max_workers
    if aws_profile:
        cfg.aws_profile = aws_profile

    # Validate configuration
    try:
        cfg.validate()
    except ValueError as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)

    # Initialize database
    db = Database(cfg)

    try:
        # Create or get project
        project_id = db.get_or_create_project(
            project_name=cfg.bucket_name,
            bucket_name=cfg.bucket_name,
            aws_region=cfg.aws_region
        )

        # Create sync session
        session_id = db.create_sync_session(
            project_id=project_id,
            local_directory=cfg.local_directory,
            s3_prefix=cfg.s3_prefix,
            aws_profile=cfg.aws_profile,
            max_workers=cfg.max_workers,
            times_to_retry=cfg.times_to_retry,
            use_find=cfg.use_find
        )

        # Save configuration
        db.save_config(session_id, cfg.to_dict())

        print_header("🚀 SMART S3 SYNC UPLOADER")
        print_status("📋", f"Sync Session ID: {session_id}")
        print_status("🔄", f"Auto-retry enabled: {cfg.times_to_retry} attempts with 5s delay")
        print_status("✅", f"Verified directory: {cfg.local_directory}")
        print_status("✅", f"Using AWS profile: {cfg.aws_profile}")

        # Initialize S3 uploader
        uploader = S3Uploader(
            bucket_name=cfg.bucket_name,
            aws_region=cfg.aws_region,
            aws_profile=cfg.aws_profile,
            max_workers=cfg.max_workers
        )

        # Verify AWS access
        print_status("🔍", f"Verifying access to bucket: {cfg.bucket_name}")
        try:
            access_info = uploader.verify_access()
            print_status("✅", f"AWS Identity: {access_info['identity']}")
            print_status("✅", f"Bucket access verified: {cfg.bucket_name}")
            print_status("✅", "Bucket listing permissions verified")
        except Exception as e:
            click.echo(f"❌ AWS access error: {e}", err=True)
            db.complete_session(session_id, status='failed')
            sys.exit(1)

        # Check prefix structure
        prefix_exists = uploader.verify_prefix_structure(cfg.s3_prefix)
        if prefix_exists:
            print_status("✅", f"Prefix structure already exists: {cfg.s3_prefix}")
        else:
            print_status("ℹ️", f"Prefix structure will be created: {cfg.s3_prefix}")

        # Scan files
        print_status("🔍", "Analyzing files for sync...")
        scan_method = "native find command" if cfg.use_find else "Python os.walk"
        print_status("⚡", f"Using {scan_method} for maximum speed...")

        start_scan = time.time()

        def scan_progress(count):
            print_status("⚡", f"find: Found {count:,} files so far...")

        scanner = FileScanner(use_find=cfg.use_find, progress_callback=scan_progress)
        local_files = scanner.scan(cfg.local_directory)

        scan_time = time.time() - start_scan
        print_status("✅", f"Found {len(local_files):,} files in {scan_time:.1f}s")

        # Load S3 file list
        print_status("🔍", "Loading S3 bucket file list...")
        s3_files = uploader.list_s3_files(cfg.s3_prefix)
        print_status("✅", f"Loaded {len(s3_files):,} files from S3")

        # Load previously uploaded files from database
        print_status("📋", "Loading previously uploaded files from database...")
        db_uploaded = db.get_uploaded_files(cfg.bucket_name, cfg.s3_prefix)
        print_status("✅", f"Loaded {len(db_uploaded):,} previously uploaded files")

        # Determine files to upload
        files_to_upload = []
        skipped_count = 0
        total_size = 0

        for local_path in local_files:
            relative_path = scanner.get_relative_path(local_path, cfg.local_directory)
            s3_key = f"{cfg.s3_prefix}/{relative_path}"

            # Skip if already in S3 or database
            if s3_key in s3_files or s3_key in db_uploaded:
                skipped_count += 1
                continue

            file_size = os.path.getsize(local_path)
            file_type = scanner.get_file_type(local_path)

            files_to_upload.append({
                'local_path': local_path,
                's3_key': s3_key,
                'file_size': file_size,
                'file_type': file_type
            })
            total_size += file_size

        # Save files to database
        print_status("💾", "Saving file analysis to database...")
        db.insert_files_batch(session_id, files_to_upload)
        print_status("✅", f"Saved {len(files_to_upload):,} file records")

        if skipped_count > 0:
            print_status("📝", f"Note: {skipped_count:,} files already uploaded and excluded")

        # Display summary
        print_header("UPLOAD SUMMARY")
        print(f"📁 Total local files: {len(local_files):,}")
        print(f"💾 Total local size: {total_size / (1024**3):.2f} GB")
        print(f"✅ Files already in S3: {skipped_count:,}")
        print(f"🔄 Files to upload: {len(files_to_upload):,}")
        print(f"📦 S3 Destination: s3://{cfg.bucket_name}/{cfg.s3_prefix}")
        print(f"📊 Database Session ID: {session_id}")
        print("=" * 88)

        if len(files_to_upload) == 0:
            print_status("🎉", "All files are already synced with S3!")
            db.complete_session(session_id, status='completed')
            return

        if dry_run:
            print_status("ℹ️", "Dry run mode - no files will be uploaded")
            db.complete_session(session_id, status='completed')
            return

        # Upload files
        print_status("🚀", "Starting upload...")
        tracker = ProgressTracker(len(files_to_upload), total_size)

        def progress_callback(stats):
            """Update progress bar during upload."""
            # Get last result
            if stats['results']:
                last_result = stats['results'][-1]

                # Find corresponding file info
                file_info = next(
                    (f for f in files_to_upload if f['s3_key'] == last_result['s3_key']),
                    None
                )

                if file_info:
                    if last_result['success']:
                        tracker.update(uploaded=1, file_size=file_info['file_size'])
                        db.mark_file_uploaded(last_result['file_id'])
                    else:
                        tracker.update(failed=1)
                        db.mark_file_failed(
                            last_result['file_id'],
                            last_result['error'],
                            last_result['retry_count']
                        )

            tracker.display_progress_bar()

        # Perform upload
        upload_stats = uploader.upload_files_batch(
            files_to_upload,
            progress_callback=progress_callback,
            max_retries=cfg.times_to_retry
        )

        # Final progress
        tracker.display_progress_bar(force=True)
        tracker.display_final_summary()

        # Update session stats
        db.update_session_stats(
            session_id=session_id,
            total_files=len(local_files),
            total_size=total_size,
            files_uploaded=upload_stats['uploaded'],
            files_failed=upload_stats['failed'],
            files_skipped=skipped_count
        )

        # Complete session
        status = 'completed' if upload_stats['failed'] == 0 else 'completed_with_errors'
        db.complete_session(session_id, status=status)

        if upload_stats['failed'] > 0:
            print_status("⚠️", f"{upload_stats['failed']} files failed to upload")
            print_status("ℹ️", f"Run retry script with session ID {session_id} to retry failed files")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
