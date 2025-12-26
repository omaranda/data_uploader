# AWS Administration Scripts

This folder contains utility scripts for managing AWS resources used by the Data Uploader application.

## Scripts

### configure_s3_permissions.py

Configure S3 permissions for IAM users to enable browser-based uploads.

**Features:**
- Reads AWS profiles from `~/.aws/credentials`
- Interactive profile selection
- Displays current IAM user information
- Shows existing policies
- Applies S3 access policy (inline) to the selected user

**Usage:**

```bash
# Basic usage
python aws-admin/configure_s3_permissions.py

# The script will:
# 1. List all AWS profiles from ~/.aws/credentials
# 2. Let you select which profile to use
# 3. Show current IAM user details
# 4. Ask for the S3 bucket name
# 5. Display the policy to be applied
# 6. Apply the policy after confirmation
```

**Example Session:**

```bash
$ python aws-admin/configure_s3_permissions.py

============================================================
AWS S3 Permissions Configuration Tool
============================================================

📋 Available AWS Profiles:
------------------------------------------------------------
  1. default              (Key: AKIAVYKSX..., Region: us-east-1)
  2. aws-eos              (Key: AKIAVYKSX..., Region: eu-west-1)
------------------------------------------------------------

Select profile number (or 'q' to quit): 2

✅ Selected profile: aws-eos

🔍 Fetching IAM user information...

📋 IAM User Details:
   ARN:      arn:aws:iam::123456789012:user/uploader-service
   Account:  123456789012
   User ID:  AIDAI3RMEXAMPLE
   Username: uploader-service

📋 Current Policies for user 'uploader-service':

   Managed Policies:
   - ReadOnlyAccess (arn:aws:iam::aws:policy/ReadOnlyAccess)

   Inline Policies: None

============================================================
Enter S3 bucket name (or '*' for all buckets): demo-borrame-001

📄 Policy to be applied:
============================================================
Policy Name: S3Access_demo_borrame_001

Policy Document:
{
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
      "Resource": "arn:aws:s3:::demo-borrame-001"
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
      "Resource": "arn:aws:s3:::demo-borrame-001/*"
    }
  ]
}
============================================================

Proceed? (yes/no): yes

🔧 Applying policy 'S3Access_demo_borrame_001' to user 'uploader-service'...

✅ Policy applied successfully!

📋 Summary:
   User:        uploader-service
   Policy Name: S3Access_demo_borrame_001
   Bucket:      demo-borrame-001

✅ The user now has the following S3 permissions:
   - ListBucket, GetBucketLocation, GetBucketCors, PutBucketCors
   - GetObject, PutObject, PutObjectAcl, DeleteObject
```

**Permissions Applied:**

The script applies an inline policy that grants:

**Bucket-level permissions:**
- `s3:ListBucket` - List objects in the bucket
- `s3:GetBucketLocation` - Get bucket region
- `s3:GetBucketCors` - Read CORS configuration
- `s3:PutBucketCors` - Update CORS configuration

**Object-level permissions:**
- `s3:GetObject` - Download files
- `s3:PutObject` - Upload files
- `s3:PutObjectAcl` - Set object permissions
- `s3:DeleteObject` - Delete files

**All Buckets Option:**

If you enter `*` for the bucket name, the policy will grant access to all S3 buckets in the account. This is useful for development but not recommended for production.

```bash
Enter S3 bucket name (or '*' for all buckets): *

⚠️  WARNING: This will grant access to ALL S3 buckets!
Are you sure? (yes/no): yes
```

## Requirements

- Python 3.9+
- boto3 (`pip install boto3`)
- AWS credentials configured in `~/.aws/credentials`
- IAM permissions to modify user policies (for the profile you select)

## Security Notes

1. **Principle of Least Privilege:** Only grant permissions to specific buckets needed for the application
2. **Inline Policies:** The script uses inline policies attached directly to the user. You can also create managed policies in the IAM console
3. **Audit Regularly:** Review IAM user permissions periodically
4. **Rotate Keys:** Rotate AWS access keys regularly
5. **Production:** In production, consider using IAM roles instead of long-lived access keys

## Troubleshooting

### Access Denied when applying policy

You need IAM permissions to modify user policies. The AWS profile you select must have:
- `iam:PutUserPolicy` permission
- Or administrative access

### This appears to be a role or federated user

The script only works with IAM users (not roles or federated identities). Make sure your AWS credentials are for an IAM user.

### Policy already exists

If a policy with the same name already exists, it will be overwritten. Review existing policies before proceeding.

## Related Scripts

- `../scripts/configure_s3_cors.py` - Configure CORS on S3 buckets for browser uploads
