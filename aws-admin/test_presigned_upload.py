#!/usr/bin/env python3
"""Test presigned URL generation and upload."""

import boto3
import requests
from botocore.exceptions import ClientError

def test_presigned_upload():
    """Test generating and using a presigned URL."""
    bucket_name = "demo-borrame-001"
    key = "cycle2/test_presigned_upload.txt"

    print("=" * 60)
    print("Testing Presigned URL Upload with Encryption")
    print("=" * 60)

    s3_client = boto3.client('s3')

    # Generate presigned URL WITH encryption header
    print("\n1. Generating presigned URL WITH ServerSideEncryption...")
    try:
        presigned_url_with_encryption = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ServerSideEncryption': 'AES256'
            },
            ExpiresIn=3600
        )
        print(f"✅ Generated URL (with encryption)")
        print(f"   URL contains: {presigned_url_with_encryption[:100]}...")

        # Test upload WITH encryption header
        print("\n2. Testing upload WITH encryption header...")
        test_data = b"Test content with encryption header"
        response = requests.put(
            presigned_url_with_encryption,
            data=test_data,
            headers={
                'x-amz-server-side-encryption': 'AES256'
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Upload successful with encryption header!")
        else:
            print(f"   ❌ Upload failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Generate presigned URL WITHOUT encryption header
    print("\n3. Generating presigned URL WITHOUT ServerSideEncryption...")
    try:
        presigned_url_no_encryption = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key + '_no_enc'
            },
            ExpiresIn=3600
        )
        print(f"✅ Generated URL (no encryption param)")

        # Test upload WITHOUT encryption header
        print("\n4. Testing upload WITHOUT encryption header...")
        test_data = b"Test content without encryption header"
        response = requests.put(
            presigned_url_no_encryption,
            data=test_data
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Upload successful without encryption header!")
        else:
            print(f"   ❌ Upload failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Cleanup
    print("\n5. Cleaning up test objects...")
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        s3_client.delete_object(Bucket=bucket_name, Key=key + '_no_enc')
        print("✅ Cleanup complete")
    except:
        pass

if __name__ == '__main__':
    test_presigned_upload()
