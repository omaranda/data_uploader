#!/usr/bin/env python
"""Trigger endpoint to register files for downstream processing."""

import sys
from pathlib import Path

import click
import requests
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_uploader.config import Config
from data_uploader.database import Database
from data_uploader.progress import print_status, print_header


# Load environment variables
load_dotenv()


@click.command()
@click.option('--session-id', '-s', required=True, type=int,
              help='Session ID to trigger processing for')
@click.option('--endpoint-url', '-e', required=True, type=str,
              help='Endpoint URL to call')
@click.option('--timeout', '-t', type=int, default=30,
              help='Request timeout in seconds')
def main(session_id, endpoint_url, timeout):
    """Trigger endpoint to register uploaded files for processing."""

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

        print_header("📡 TRIGGER ENDPOINT")
        print_status("📋", f"Session ID: {session_id}")
        print_status("📁", f"Bucket: {session_info['bucket_name']}")
        print_status("📂", f"Prefix: {session_info['s3_prefix']}")
        print_status("🌐", f"Endpoint: {endpoint_url}")

        # Prepare payload
        payload = {
            "session_id": session_id,
            "bucket_name": session_info['bucket_name'],
            "s3_prefix": session_info['s3_prefix'],
            "total_files": session_info['total_files'],
            "files_uploaded": session_info['files_uploaded'],
            "total_size_bytes": session_info['total_size_bytes'],
            "local_directory": session_info['local_directory']
        }

        print_status("📤", "Sending request...")

        # Make request
        response = requests.post(
            endpoint_url,
            json=payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )

        # Check response
        if response.status_code == 200:
            print_status("✅", "Endpoint triggered successfully")
            print_status("📥", f"Response: {response.text}")
        else:
            print_status("❌", f"Endpoint returned error: {response.status_code}")
            print_status("📥", f"Response: {response.text}")
            sys.exit(1)

    except requests.exceptions.Timeout:
        click.echo(f"❌ Request timeout after {timeout}s", err=True)
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Request error: {e}", err=True)
        sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
