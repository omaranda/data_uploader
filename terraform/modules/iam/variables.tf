# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "upload_bucket_arn" {
  description = "ARN of the S3 upload bucket"
  type        = string
}
