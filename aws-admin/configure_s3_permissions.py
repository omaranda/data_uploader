#!/usr/bin/env python3
"""
Configure S3 permissions for browser uploads.

This script reads AWS profiles from ~/.aws/credentials, allows you to select one,
and applies the necessary S3 permissions policy for browser uploads.
"""

import os
import sys
import configparser
import json
import boto3
from botocore.exceptions import ClientError


def read_aws_profiles():
    """Read AWS profiles from ~/.aws/credentials."""
    credentials_path = os.path.expanduser("~/.aws/credentials")

    if not os.path.exists(credentials_path):
        print(f"❌ AWS credentials file not found at: {credentials_path}")
        print("   Please configure AWS credentials first.")
        return None

    config = configparser.ConfigParser()
    config.read(credentials_path)

    profiles = {}
    for section in config.sections():
        if config.has_option(section, 'aws_access_key_id'):
            profiles[section] = {
                'access_key_id': config.get(section, 'aws_access_key_id'),
                'secret_access_key': config.get(section, 'aws_secret_access_key'),
                'region': config.get(section, 'region') if config.has_option(section, 'region') else 'us-east-1'
            }

    return profiles


def select_profile(profiles):
    """Allow user to select an AWS profile."""
    if not profiles:
        return None

    print("\n📋 Available AWS Profiles:")
    print("-" * 60)

    profile_list = list(profiles.keys())
    for i, profile_name in enumerate(profile_list, 1):
        access_key = profiles[profile_name]['access_key_id']
        region = profiles[profile_name]['region']
        print(f"  {i}. {profile_name:20} (Key: {access_key[:10]}..., Region: {region})")

    print("-" * 60)

    while True:
        try:
            choice = input("\nSelect profile number (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                return None

            index = int(choice) - 1
            if 0 <= index < len(profile_list):
                return profile_list[index]
            else:
                print(f"❌ Invalid selection. Please enter a number between 1 and {len(profile_list)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")


def get_current_user_info(session):
    """Get information about the current IAM user."""
    try:
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()

        # Extract username from ARN
        # ARN format: arn:aws:iam::123456789012:user/username
        arn = identity['Arn']
        if ':user/' in arn:
            username = arn.split(':user/')[-1]
        else:
            username = None

        return {
            'arn': arn,
            'account': identity['Account'],
            'user_id': identity['UserId'],
            'username': username
        }
    except ClientError as e:
        print(f"❌ Error getting user info: {e}")
        return None


def create_s3_policy(bucket_name, include_all_buckets=False):
    """Create S3 permission policy."""
    if include_all_buckets:
        resource_bucket = "arn:aws:s3:::*"
        resource_objects = "arn:aws:s3:::*/*"
        policy_name = "S3FullAccessAllBuckets"
    else:
        resource_bucket = f"arn:aws:s3:::{bucket_name}"
        resource_objects = f"arn:aws:s3:::{bucket_name}/*"
        policy_name = f"S3Access_{bucket_name.replace('-', '_')}"

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ListBucketAccess",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "s3:GetBucketCors",
                    "s3:PutBucketCors"
                ],
                "Resource": resource_bucket
            },
            {
                "Sid": "ObjectAccess",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:DeleteObject"
                ],
                "Resource": resource_objects
            }
        ]
    }

    return policy_name, policy_document


def list_user_policies(iam_client, username):
    """List all policies attached to a user."""
    try:
        # Managed policies
        managed_response = iam_client.list_attached_user_policies(UserName=username)
        managed_policies = managed_response.get('AttachedPolicies', [])

        # Inline policies
        inline_response = iam_client.list_user_policies(UserName=username)
        inline_policies = inline_response.get('PolicyNames', [])

        return {
            'managed': managed_policies,
            'inline': inline_policies
        }
    except ClientError as e:
        print(f"❌ Error listing policies: {e}")
        return None


def apply_inline_policy(iam_client, username, policy_name, policy_document):
    """Apply an inline policy to the IAM user."""
    try:
        iam_client.put_user_policy(
            UserName=username,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document, indent=2)
        )
        return True
    except ClientError as e:
        print(f"❌ Error applying policy: {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("AWS S3 Permissions Configuration Tool")
    print("=" * 60)

    # Read AWS profiles
    profiles = read_aws_profiles()
    if not profiles:
        sys.exit(1)

    # Select profile
    profile_name = select_profile(profiles)
    if not profile_name:
        print("\n👋 Cancelled.")
        sys.exit(0)

    print(f"\n✅ Selected profile: {profile_name}")

    # Create boto3 session
    profile_creds = profiles[profile_name]
    session = boto3.Session(
        aws_access_key_id=profile_creds['access_key_id'],
        aws_secret_access_key=profile_creds['secret_access_key'],
        region_name=profile_creds['region']
    )

    # Get current user info
    print("\n🔍 Fetching IAM user information...")
    user_info = get_current_user_info(session)
    if not user_info:
        sys.exit(1)

    print(f"\n📋 IAM User Details:")
    print(f"   ARN:      {user_info['arn']}")
    print(f"   Account:  {user_info['account']}")
    print(f"   User ID:  {user_info['user_id']}")

    if not user_info['username']:
        print("\n❌ This appears to be a role or federated user, not an IAM user.")
        print("   This script only works with IAM users.")
        sys.exit(1)

    username = user_info['username']
    print(f"   Username: {username}")

    # List current policies
    iam_client = session.client('iam')
    print(f"\n📋 Current Policies for user '{username}':")
    policies = list_user_policies(iam_client, username)

    if policies:
        if policies['managed']:
            print("\n   Managed Policies:")
            for policy in policies['managed']:
                print(f"   - {policy['PolicyName']} ({policy['PolicyArn']})")
        else:
            print("\n   Managed Policies: None")

        if policies['inline']:
            print("\n   Inline Policies:")
            for policy_name in policies['inline']:
                print(f"   - {policy_name}")
        else:
            print("\n   Inline Policies: None")

    # Ask for bucket name
    print("\n" + "=" * 60)
    bucket_name = input("Enter S3 bucket name (or '*' for all buckets): ").strip()

    if not bucket_name:
        print("❌ Bucket name cannot be empty.")
        sys.exit(1)

    include_all_buckets = (bucket_name == '*')
    if include_all_buckets:
        print("\n⚠️  WARNING: This will grant access to ALL S3 buckets!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("👋 Cancelled.")
            sys.exit(0)

    # Create policy
    policy_name, policy_document = create_s3_policy(
        bucket_name if not include_all_buckets else '*',
        include_all_buckets
    )

    # Display policy
    print(f"\n📄 Policy to be applied:")
    print("=" * 60)
    print(f"Policy Name: {policy_name}")
    print("\nPolicy Document:")
    print(json.dumps(policy_document, indent=2))
    print("=" * 60)

    # Confirm
    print("\nThis policy will be applied as an inline policy to the user.")
    confirm = input("\nProceed? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("👋 Cancelled.")
        sys.exit(0)

    # Apply policy
    print(f"\n🔧 Applying policy '{policy_name}' to user '{username}'...")

    success = apply_inline_policy(iam_client, username, policy_name, policy_document)

    if success:
        print(f"\n✅ Policy applied successfully!")
        print(f"\n📋 Summary:")
        print(f"   User:        {username}")
        print(f"   Policy Name: {policy_name}")
        print(f"   Bucket:      {bucket_name if not include_all_buckets else 'All buckets (*)'}")
        print(f"\n✅ The user now has the following S3 permissions:")
        print(f"   - ListBucket, GetBucketLocation, GetBucketCors, PutBucketCors")
        print(f"   - GetObject, PutObject, PutObjectAcl, DeleteObject")
    else:
        print(f"\n❌ Failed to apply policy.")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
