#!/usr/bin/env python
"""Trigger endpoint to register files for downstream processing."""

import json
import os
import sys
from pathlib import Path

import click
import requests
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_uploader.config import Config
from data_uploader.database import Database
from data_uploader.endpoint_notifier import EndpointNotifier
from data_uploader.progress import print_status, print_header


# Load environment variables
load_dotenv()


def get_uploaded_s3_paths(db: Database, session_id: int) -> list:
    """Get list of successfully uploaded S3 paths for a session.

    Args:
        db: Database instance
        session_id: Session ID

    Returns:
        List of S3 paths
    """
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT s3_key
                FROM file_uploads
                WHERE session_id = %s AND status = 'uploaded'
                ORDER BY id
                """,
                (session_id,)
            )
            results = cur.fetchall()
            return [row['s3_key'] for row in results]
    except Exception as e:
        print_status("⚠️", f"Could not load file list from database: {e}")
        return []


@click.command()
@click.option('--session-id', '-s', required=True, type=int,
              help='Session ID to trigger processing for')
@click.option('--endpoint-url', '-e', type=str,
              help='Endpoint URL to call (overrides MADXXX_API_URL env var)')
@click.option('--api-key', '-k', type=str,
              help='API key for authentication (overrides MADXXX_API_KEY env var)')
@click.option('--timeout', '-t', type=int,
              help='Request timeout in seconds (overrides MADXXX_API_TIMEOUT env var)')
@click.option('--list-files', is_flag=True,
              help='Include specific file list in payload (otherwise sends prefix only)')
@click.option('--job-name', type=str,
              help='Custom job name')
@click.option('--function-name', type=str,
              help='Backend function name (overrides MADXXX_FUNCTION_NAME env var)')
@click.option('--module-name', type=str,
              help='Backend module path (overrides MADXXX_MODULE_NAME env var)')
@click.option('--sqs-queue', type=str,
              help='SQS queue name (overrides MADXXX_SQS_QUEUE env var)')
@click.option('--sqs-region', type=str,
              help='SQS region (overrides MADXXX_SQS_REGION env var)')
def main(session_id, endpoint_url, api_key, timeout, list_files, job_name,
         function_name, module_name, sqs_queue, sqs_region):
    """Trigger endpoint to register uploaded files for processing.

    This script sends a job registration request to the MadXXX API endpoint
    with the correct payload format expected by the backend.

    Configuration is read from environment variables (.env file) with optional
    CLI overrides. All required values must be set in .env or passed via CLI.
    """

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

        # Determine API key (priority: CLI > env)
        final_api_key = api_key or os.getenv('MADXXX_API_KEY')

        if not final_api_key:
            click.echo("❌ No API key provided. Set MADXXX_API_KEY in .env or use --api-key", err=True)
            sys.exit(1)

        # Determine endpoint URL (priority: CLI > env)
        final_endpoint_url = endpoint_url or os.getenv('MADXXX_API_URL')

        if not final_endpoint_url:
            click.echo("❌ No endpoint URL provided. Set MADXXX_API_URL in .env or use --endpoint-url", err=True)
            sys.exit(1)

        # Determine timeout (priority: CLI > env > default)
        final_timeout = timeout or int(os.getenv('MADXXX_API_TIMEOUT', '30'))

        # Determine job settings (priority: CLI > env > defaults)
        final_function_name = function_name or os.getenv('MADXXX_FUNCTION_NAME', 'register_audiofiles')
        final_module_name = module_name or os.getenv('MADXXX_MODULE_NAME', 'madxxx_workbench.audio.register_audio')
        final_sqs_queue = sqs_queue or os.getenv('MADXXX_SQS_QUEUE', 'madXXX_tasks_data_registration')
        final_sqs_region = sqs_region or os.getenv('MADXXX_SQS_REGION', 'eu-west-1')

        print_header("📡 TRIGGER MADXXX ENDPOINT")
        print_status("📋", f"Session ID: {session_id}")
        print_status("📁", f"Bucket: {session_info['bucket_name']}")
        print_status("📂", f"Prefix: {session_info['s3_prefix']}")
        print_status("📊", f"Files uploaded: {session_info['files_uploaded']:,}")
        print_status("🌐", f"Endpoint: {final_endpoint_url}")

        # Initialize notifier
        notifier = EndpointNotifier(api_key=final_api_key, api_endpoint=final_endpoint_url)

        # Build S3 paths
        if list_files:
            print_status("🔍", "Loading file list from database...")
            uploaded_files = get_uploaded_s3_paths(db, session_id)

            if not uploaded_files:
                click.echo("❌ No uploaded files found for this session", err=True)
                sys.exit(1)

            # Convert to full S3 paths
            s3_paths = []
            for s3_key in uploaded_files:
                # s3_key is already in format: prefix/path/to/file
                s3_path = f"s3://{session_info['bucket_name']}/{s3_key}"
                s3_paths.append(s3_path)

            print_status("✅", f"Loaded {len(s3_paths):,} file paths from database")

        else:
            # Send prefix only - API will list files
            s3_paths = [f"s3://{session_info['bucket_name']}/{session_info['s3_prefix']}"]
            print_status("ℹ️", "Sending prefix path (API will list files)")

        # Prepare custom job name
        final_job_name = job_name or f"session_{session_id}_{final_function_name}"

        # Build payload
        payload = notifier.build_job_payload(
            s3_paths=s3_paths,
            job_name=final_job_name,
            function_name=final_function_name,
            module_name=final_module_name,
            sqs_queue=final_sqs_queue,
            sqs_region=final_sqs_region,
            custom_keywords={}
        )

        # Prepare headers
        headers = notifier.get_auth_headers()

        print_status("📤", "Sending request to MadXXX API...")
        print_status("🔑", "Using API key authentication")
        print_status("📦", f"Job name: {final_job_name}")
        print_status("📦", f"Function: {final_function_name}")
        print_status("📦", f"Files/paths: {len(s3_paths):,}")

        # Show payload summary (not full file list for large batches)
        payload_summary = payload.copy()
        if len(s3_paths) > 5:
            payload_summary['job']['arguments'] = [
                s3_paths[:3] + [f"... and {len(s3_paths) - 3} more files"]
            ]

        print_status("📄", f"Payload structure:\n{json.dumps(payload_summary, indent=2)}")

        # Make request
        response = requests.post(
            final_endpoint_url,
            json=payload,
            timeout=final_timeout,
            headers=headers
        )

        # Check response
        if response.status_code in (200, 201, 202):
            print_status("✅", "Endpoint triggered successfully!")
            print_status("📥", f"Status Code: {response.status_code}")

            try:
                response_json = response.json()
                print_status("📥", f"Response:\n{json.dumps(response_json, indent=2)}")

                # Extract job_id if present
                job_id = response_json.get('job_id')
                if job_id:
                    print_status("🆔", f"Job ID: {job_id}")

            except json.JSONDecodeError:
                print_status("📥", f"Response: {response.text}")

        else:
            print_status("❌", f"Endpoint returned error: {response.status_code}")
            print_status("📥", f"Response: {response.text}")

            # Try to parse error response
            try:
                error_json = response.json()
                print_status("📥", f"Error details:\n{json.dumps(error_json, indent=2)}")
            except:
                pass

            sys.exit(1)

    except requests.exceptions.Timeout:
        click.echo(f"❌ Request timeout after {final_timeout}s", err=True)
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
