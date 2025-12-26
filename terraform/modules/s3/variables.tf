# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "upload_bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
}

variable "frontend_domain" {
  description = "Frontend domain for CORS configuration"
  type        = string
  default     = ""
}
