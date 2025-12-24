#!/usr/bin/env python
"""Master script to run the full upload pipeline."""

import subprocess
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@click.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to JSON configuration file')
@click.option('--endpoint-url', '-e', type=str,
              help='Endpoint URL to trigger after upload')
@click.option('--skip-retry', is_flag=True,
              help='Skip automatic retry of failed files')
@click.option('--skip-endpoint', is_flag=True,
              help='Skip triggering endpoint')
@click.option('--dry-run', is_flag=True,
              help='Analyze files without uploading')
def main(config, endpoint_url, skip_retry, skip_endpoint, dry_run):
    """Run the complete upload pipeline: upload -> retry -> trigger endpoint."""

    scripts_dir = Path(__file__).parent
    python_exe = sys.executable

    print("=" * 88)
    print("🚀 DATA UPLOADER - MASTER PIPELINE")
    print("=" * 88)

    # Step 1: Upload files
    print("\n📤 STEP 1: UPLOADING FILES")
    print("-" * 88)

    upload_cmd = [python_exe, str(scripts_dir / 'upload.py'), '--config', config]
    if dry_run:
        upload_cmd.append('--dry-run')

    result = subprocess.run(upload_cmd)

    if result.returncode != 0:
        print("\n❌ Upload failed. Aborting pipeline.")
        sys.exit(1)

    # Extract session ID from upload output (we'll need to parse it)
    # For now, user will need to provide it manually or we read from DB
    # This is a simplified version

    if dry_run:
        print("\n✅ Dry run completed. Pipeline finished.")
        return

    # Step 2: Retry failed files (optional)
    if not skip_retry:
        print("\n🔄 STEP 2: RETRYING FAILED FILES")
        print("-" * 88)

        # Get latest session ID from database
        # For this to work, we need to add a helper function
        session_id = get_latest_session_id()

        if session_id:
            retry_cmd = [
                python_exe,
                str(scripts_dir / 'retry.py'),
                '--session-id', str(session_id),
                '--auto-retry',
                '--max-rounds', '3'
            ]

            result = subprocess.run(retry_cmd)

            if result.returncode != 0:
                print("\n⚠️ Retry had errors, but continuing pipeline...")
        else:
            print("\n⚠️ Could not determine session ID. Skipping retry.")
    else:
        print("\n⏭️ STEP 2: SKIPPING RETRY (--skip-retry flag)")

    # Step 3: Trigger endpoint (optional)
    if not skip_endpoint and endpoint_url:
        print("\n📡 STEP 3: TRIGGERING ENDPOINT")
        print("-" * 88)

        session_id = get_latest_session_id()

        if session_id:
            endpoint_cmd = [
                python_exe,
                str(scripts_dir / 'trigger_endpoint.py'),
                '--session-id', str(session_id),
                '--endpoint-url', endpoint_url
            ]

            result = subprocess.run(endpoint_cmd)

            if result.returncode != 0:
                print("\n⚠️ Endpoint trigger failed.")
                sys.exit(1)
        else:
            print("\n⚠️ Could not determine session ID. Skipping endpoint trigger.")
    else:
        print("\n⏭️ STEP 3: SKIPPING ENDPOINT (no URL provided or --skip-endpoint flag)")

    print("\n" + "=" * 88)
    print("✅ PIPELINE COMPLETED")
    print("=" * 88)


def get_latest_session_id():
    """Get the latest session ID from the database.

    Returns:
        Session ID or None
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
        from data_uploader.config import Config
        from data_uploader.database import Database

        cfg = Config.from_env()
        db = Database(cfg)

        with db.cursor() as cur:
            cur.execute(
                "SELECT id FROM sync_sessions ORDER BY created_at DESC LIMIT 1"
            )
            result = cur.fetchone()
            return result['id'] if result else None

    except Exception as e:
        print(f"Warning: Could not get session ID: {e}")
        return None


if __name__ == '__main__':
    main()
