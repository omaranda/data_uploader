# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

output "upload_bucket_name" {
  description = "Name of the upload bucket"
  value       = aws_s3_bucket.uploads.id
}

output "upload_bucket_arn" {
  description = "ARN of the upload bucket"
  value       = aws_s3_bucket.uploads.arn
}

output "upload_bucket_domain_name" {
  description = "Domain name of the upload bucket"
  value       = aws_s3_bucket.uploads.bucket_domain_name
}
