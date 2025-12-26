# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""
Configure CORS settings for S3 bucket to allow browser uploads.

This script sets up CORS rules on an S3 bucket to allow direct uploads
from the browser using presigned URLs.
"""

import sys
import boto3
from botocore.exceptions import ClientError


def configure_cors(bucket_name: str, allowed_origins: list[str] = None):
    """
    Configure CORS on an S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket
        allowed_origins: List of allowed origins (default: ['*'] for all)
    """
    if allowed_origins is None:
        allowed_origins = ['*']

    # CORS configuration
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                'AllowedOrigins': allowed_origins,
                'ExposeHeaders': ['ETag', 'x-amz-request-id'],
                'MaxAgeSeconds': 3600
            }
        ]
    }

    # Create S3 client
    s3_client = boto3.client('s3')

    try:
        # Apply CORS configuration
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )

        print(f"✅ CORS configuration applied successfully to bucket: {bucket_name}")
        print(f"   Allowed origins: {', '.join(allowed_origins)}")
        print(f"   Allowed methods: GET, PUT, POST, DELETE, HEAD")

        # Verify configuration
        response = s3_client.get_bucket_cors(Bucket=bucket_name)
        print(f"\n📋 Current CORS rules:")
        for i, rule in enumerate(response['CORSRules'], 1):
            print(f"\n   Rule {i}:")
            print(f"   - Origins: {rule['AllowedOrigins']}")
            print(f"   - Methods: {rule['AllowedMethods']}")
            print(f"   - Headers: {rule['AllowedHeaders']}")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']

        print(f"❌ Error configuring CORS: {error_code}")
        print(f"   {error_msg}")

        if error_code == 'NoSuchBucket':
            print(f"\n   Bucket '{bucket_name}' does not exist.")
        elif error_code == 'AccessDenied':
            print(f"\n   Access denied. Make sure you have permission to modify bucket CORS settings.")

        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python configure_s3_cors.py <bucket-name> [allowed-origin1] [allowed-origin2] ...")
        print("\nExamples:")
        print("  python configure_s3_cors.py demo-borrame-001")
        print("  python configure_s3_cors.py demo-borrame-001 http://localhost:3000")
        print("  python configure_s3_cors.py demo-borrame-001 http://localhost:3000 https://myapp.com")
        print("\nIf no origins are specified, all origins (*) will be allowed.")
        sys.exit(1)

    bucket_name = sys.argv[1]
    allowed_origins = sys.argv[2:] if len(sys.argv) > 2 else ['*']

    print(f"🔧 Configuring CORS for bucket: {bucket_name}")
    print(f"   Using AWS credentials from environment/config\n")

    success = configure_cors(bucket_name, allowed_origins)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
