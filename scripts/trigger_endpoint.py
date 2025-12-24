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


def load_job_config(config_path: str) -> dict:
    """Load job configuration from JSON file.

    Args:
        config_path: Path to job config JSON file

    Returns:
        Job configuration dictionary
    """
    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r') as f:
        return json.load(f)


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
              help='Endpoint URL to call (overrides env and job config)')
@click.option('--job-config', '-j', type=click.Path(exists=True),
              help='Path to job configuration JSON file')
@click.option('--api-key', '-k', type=str,
              help='API key for authentication (overrides env and job config)')
@click.option('--timeout', '-t', type=int, default=30,
              help='Request timeout in seconds')
@click.option('--batch-size', type=int,
              help='Override batch size from job config')
@click.option('--list-files', is_flag=True,
              help='Include specific file list in payload (otherwise sends prefix only)')
@click.option('--job-name', type=str,
              help='Custom job name')
def main(session_id, endpoint_url, job_config, api_key, timeout, batch_size, list_files, job_name):
    """Trigger endpoint to register uploaded files for processing.

    This script sends a job registration request to the MadXXX API endpoint
    with the correct payload format expected by the backend.
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

        # Load job configuration if provided
        job_cfg = {}
        if job_config:
            job_cfg = load_job_config(job_config)
            print_status("📋", f"Loaded job config: {job_config}")

        # Determine API key (priority: CLI > env > job_config)
        final_api_key = (
            api_key or
            os.getenv('MADXXX_API_KEY') or
            job_cfg.get('api_keys', {}).get('madxxx_api_key')
        )

        if not final_api_key:
            click.echo("❌ No API key provided. Use --api-key, MADXXX_API_KEY env var, or job config", err=True)
            sys.exit(1)

        # Determine endpoint URL (priority: CLI > env > job_config)
        # No hardcoded default for security - must be in .env or config
        final_endpoint_url = (
            endpoint_url or
            os.getenv('MADXXX_API_URL') or
            job_cfg.get('endpoints', {}).get('default')
        )

        if not final_endpoint_url:
            click.echo("❌ No endpoint URL provided. Set MADXXX_API_URL in .env, use --endpoint-url, or configure in job_config.json", err=True)
            sys.exit(1)

        print_header("📡 TRIGGER MADXXX ENDPOINT")
        print_status("📋", f"Session ID: {session_id}")
        print_status("📁", f"Bucket: {session_info['bucket_name']}")
        print_status("📂", f"Prefix: {session_info['s3_prefix']}")
        print_status("📊", f"Files uploaded: {session_info['files_uploaded']:,}")
        print_status("🌐", f"Endpoint: {final_endpoint_url}")

        # Initialize notifier
        notifier = EndpointNotifier(api_key=final_api_key, api_endpoint=final_endpoint_url)

        # Get job template settings from config
        template = {}
        if job_cfg and 'job_templates' in job_cfg:
            template = job_cfg['job_templates'].get('audio_processing', {})

        function_name = template.get('function_name', 'register_audiofiles')
        module_name = template.get('module_name', 'madxxx_workbench.audio.register_audio')
        sqs_queue = template.get('sqs_queue', 'madXXX_tasks_data_registration')
        sqs_region = template.get('sqs_region', 'eu-west-1')

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
        final_job_name = job_name or f"session_{session_id}_{function_name}"

        # Build payload
        payload = notifier.build_job_payload(
            s3_paths=s3_paths,
            job_name=final_job_name,
            function_name=function_name,
            module_name=module_name,
            sqs_queue=sqs_queue,
            sqs_region=sqs_region,
            custom_keywords={}
        )

        # Prepare headers
        headers = notifier.get_auth_headers()

        print_status("📤", "Sending request to MadXXX API...")
        print_status("🔑", "Using API key authentication")
        print_status("📦", f"Job name: {final_job_name}")
        print_status("📦", f"Function: {function_name}")
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
            timeout=timeout,
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
