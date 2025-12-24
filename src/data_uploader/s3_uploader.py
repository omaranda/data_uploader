"""S3 upload functionality with progress tracking."""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, Callable

import boto3
from botocore.exceptions import ClientError, BotoCoreError


class S3Uploader:
    """Handle S3 uploads with progress tracking."""

    def __init__(
        self,
        bucket_name: str,
        aws_region: str,
        aws_profile: str,
        max_workers: int = 15
    ):
        """Initialize S3 uploader.

        Args:
            bucket_name: S3 bucket name
            aws_region: AWS region
            aws_profile: AWS profile name
            max_workers: Number of parallel upload workers
        """
        self.bucket_name = bucket_name
        self.aws_region = aws_region
        self.aws_profile = aws_profile
        self.max_workers = max_workers

        # Initialize boto3 session
        self.session = boto3.Session(
            profile_name=aws_profile,
            region_name=aws_region
        )
        self.s3_client = self.session.client('s3')

    def verify_access(self) -> Dict[str, Any]:
        """Verify AWS credentials and bucket access.

        Returns:
            Dictionary with verification results

        Raises:
            ClientError: If access verification fails
        """
        try:
            # Get AWS identity
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()

            # Check bucket access
            self.s3_client.head_bucket(Bucket=self.bucket_name)

            # Test list permission
            self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )

            return {
                'identity': identity['Arn'],
                'bucket_accessible': True,
                'list_permission': True
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '403':
                raise PermissionError(f"Access denied to bucket: {self.bucket_name}")
            elif error_code == '404':
                raise ValueError(f"Bucket not found: {self.bucket_name}")
            else:
                raise

    def verify_prefix_structure(self, prefix: str) -> bool:
        """Verify if prefix structure exists in S3.

        Args:
            prefix: S3 prefix to check

        Returns:
            True if prefix exists (has objects), False otherwise
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=1
            )
            return 'Contents' in response

        except ClientError:
            return False

    def list_s3_files(self, prefix: str) -> set:
        """List all files in S3 bucket with given prefix.

        Args:
            prefix: S3 prefix

        Returns:
            Set of S3 keys
        """
        s3_keys = set()
        paginator = self.s3_client.get_paginator('list_objects_v2')

        try:
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_keys.add(obj['Key'])

        except ClientError as e:
            print(f"Warning: Error listing S3 objects: {e}")

        return s3_keys

    def upload_file(
        self,
        local_path: str,
        s3_key: str,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Upload a single file to S3.

        Args:
            local_path: Local file path
            s3_key: S3 key (destination path)
            retry_count: Current retry attempt
            max_retries: Maximum retry attempts

        Returns:
            Dictionary with upload result
        """
        result = {
            'success': False,
            'local_path': local_path,
            's3_key': s3_key,
            'retry_count': retry_count,
            'error': None
        }

        try:
            # Upload file
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key
            )

            result['success'] = True
            return result

        except FileNotFoundError:
            result['error'] = f"File not found: {local_path}"
            return result

        except (ClientError, BotoCoreError) as e:
            error_msg = str(e)
            result['error'] = error_msg

            # Retry on transient errors
            if retry_count < max_retries:
                time.sleep(5)  # Wait before retry
                return self.upload_file(
                    local_path,
                    s3_key,
                    retry_count + 1,
                    max_retries
                )

            return result

        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            return result

    def upload_files_batch(
        self,
        files: list,
        progress_callback: Optional[Callable] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Upload multiple files in parallel.

        Args:
            files: List of file dictionaries with 'local_path' and 's3_key'
            progress_callback: Optional callback for progress updates
            max_retries: Maximum retry attempts per file

        Returns:
            Dictionary with upload statistics
        """
        stats = {
            'total': len(files),
            'uploaded': 0,
            'failed': 0,
            'results': []
        }

        if not files:
            return stats

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all upload tasks
            future_to_file = {
                executor.submit(
                    self.upload_file,
                    f['local_path'],
                    f['s3_key'],
                    0,
                    max_retries
                ): f
                for f in files
            }

            # Process completed uploads
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]

                try:
                    result = future.result()
                    result['file_id'] = file_info.get('id')  # Database ID
                    stats['results'].append(result)

                    if result['success']:
                        stats['uploaded'] += 1
                    else:
                        stats['failed'] += 1

                    # Call progress callback
                    if progress_callback:
                        progress_callback(stats)

                except Exception as e:
                    stats['failed'] += 1
                    stats['results'].append({
                        'success': False,
                        'local_path': file_info['local_path'],
                        's3_key': file_info['s3_key'],
                        'file_id': file_info.get('id'),
                        'error': str(e),
                        'retry_count': 0
                    })

                    if progress_callback:
                        progress_callback(stats)

        return stats

    def get_file_size(self, s3_key: str) -> Optional[int]:
        """Get size of file in S3.

        Args:
            s3_key: S3 key

        Returns:
            File size in bytes or None if not found
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response['ContentLength']

        except ClientError:
            return None
