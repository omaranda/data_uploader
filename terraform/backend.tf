# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# Terraform State Backend Configuration
# Uncomment and configure after creating S3 bucket and DynamoDB table

# terraform {
#   backend "s3" {
#     bucket         = "data-uploader-terraform-state"
#     key            = "prod/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     dynamodb_table = "data-uploader-terraform-locks"
#   }
# }

# To create the S3 bucket and DynamoDB table for state management:
#
# 1. Create S3 bucket:
#    aws s3api create-bucket \
#      --bucket data-uploader-terraform-state \
#      --region us-east-1
#
#    aws s3api put-bucket-versioning \
#      --bucket data-uploader-terraform-state \
#      --versioning-configuration Status=Enabled
#
#    aws s3api put-bucket-encryption \
#      --bucket data-uploader-terraform-state \
#      --server-side-encryption-configuration '{
#        "Rules": [{
#          "ApplyServerSideEncryptionByDefault": {
#            "SSEAlgorithm": "AES256"
#          }
#        }]
#      }'
#
# 2. Create DynamoDB table:
#    aws dynamodb create-table \
#      --table-name data-uploader-terraform-locks \
#      --attribute-definitions AttributeName=LockID,AttributeType=S \
#      --key-schema AttributeName=LockID,KeyType=HASH \
#      --billing-mode PAY_PER_REQUEST \
#      --region us-east-1
#
# 3. Uncomment the backend configuration above
# 4. Run: terraform init -migrate-state
