# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""Test S3 upload permissions."""

import boto3
import sys
from botocore.exceptions import ClientError

def test_upload(bucket_name, key):
    """Test uploading to S3."""
    print(f"Testing upload to s3://{bucket_name}/{key}")

    # Create S3 client
    s3 = boto3.client('s3')

    try:
        # Try to put an object
        print("\nAttempting to upload test object...")
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=b'Test content from Python script'
        )
        print("✅ Upload successful!")

        # Try to read it back
        print("\nAttempting to read object...")
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read()
        print(f"✅ Read successful! Content: {content.decode('utf-8')}")

        # Clean up
        print("\nCleaning up test object...")
        s3.delete_object(Bucket=bucket_name, Key=key)
        print("✅ Cleanup successful!")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"\n❌ Error: {error_code}")
        print(f"   Message: {error_msg}")

        if error_code == 'AccessDenied':
            print("\n   This is a permissions issue. Possible causes:")
            print("   1. IAM user policy doesn't allow s3:PutObject")
            print("   2. Bucket policy explicitly denies access")
            print("   3. Account doesn't own the bucket")
            print("   4. Bucket has server-side encryption requiring specific headers")

        return False

def check_bucket_policy(bucket_name):
    """Check if bucket has a policy that might block uploads."""
    print(f"\nChecking bucket policy for: {bucket_name}")
    s3 = boto3.client('s3')

    try:
        response = s3.get_bucket_policy(Bucket=bucket_name)
        policy = response['Policy']
        print("Bucket policy exists:")
        print(policy)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            print("✅ No bucket policy (this is fine)")
        else:
            print(f"❌ Error getting bucket policy: {e}")

def check_bucket_encryption(bucket_name):
    """Check bucket encryption settings."""
    print(f"\nChecking bucket encryption for: {bucket_name}")
    s3 = boto3.client('s3')

    try:
        response = s3.get_bucket_encryption(Bucket=bucket_name)
        print("Bucket encryption enabled:")
        import json
        print(json.dumps(response['ServerSideEncryptionConfiguration'], indent=2))
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            print("✅ No encryption requirement")
        else:
            print(f"Error: {e}")

def main():
    bucket_name = "demo-borrame-001"
    test_key = "cycle2/test_upload_script.txt"

    print("=" * 60)
    print("S3 Upload Permissions Test")
    print("=" * 60)

    # Get current identity
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print(f"\nCurrent IAM identity:")
    print(f"  ARN: {identity['Arn']}")
    print(f"  Account: {identity['Account']}")

    # Check bucket policy
    check_bucket_policy(bucket_name)

    # Check encryption
    check_bucket_encryption(bucket_name)

    # Test upload
    print("\n" + "=" * 60)
    success = test_upload(bucket_name, test_key)
    print("=" * 60)

    if success:
        print("\n✅ All tests passed! S3 upload permissions are working.")
    else:
        print("\n❌ Upload failed. Check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
