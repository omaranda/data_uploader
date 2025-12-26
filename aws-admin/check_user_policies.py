# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""Check IAM user policies."""

import boto3
import json
import sys

def main():
    # Use the access key from .env
    access_key = "AKIAVYKSXCWJWTAZVIHV"

    print(f"Checking policies for access key: {access_key}")

    # Create session
    session = boto3.Session()

    # Get user info
    sts = session.client('sts')
    try:
        identity = sts.get_caller_identity()
        print(f"\nCurrent identity: {identity['Arn']}")
    except Exception as e:
        print(f"Error getting identity: {e}")
        return

    # Extract username
    arn = identity['Arn']
    if ':user/' in arn:
        username = arn.split(':user/')[-1]
    else:
        print("Not an IAM user")
        return

    print(f"Username: {username}")

    # Get policies
    iam = session.client('iam')

    # Inline policies
    print("\n=== Inline Policies ===")
    try:
        response = iam.list_user_policies(UserName=username)
        inline_policies = response.get('PolicyNames', [])

        if not inline_policies:
            print("No inline policies found")
        else:
            for policy_name in inline_policies:
                print(f"\nPolicy: {policy_name}")
                policy_doc = iam.get_user_policy(UserName=username, PolicyName=policy_name)
                print(json.dumps(policy_doc['PolicyDocument'], indent=2))
    except Exception as e:
        print(f"Error: {e}")

    # Managed policies
    print("\n=== Managed Policies ===")
    try:
        response = iam.list_attached_user_policies(UserName=username)
        managed_policies = response.get('AttachedPolicies', [])

        if not managed_policies:
            print("No managed policies found")
        else:
            for policy in managed_policies:
                print(f"\n- {policy['PolicyName']}")
                print(f"  ARN: {policy['PolicyArn']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
