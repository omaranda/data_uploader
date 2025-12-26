# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.1.0.0/16"
}

variable "frontend_image" {
  description = "Frontend Docker image"
  type        = string
}

variable "backend_image" {
  description = "Backend Docker image"
  type        = string
}

variable "worker_image" {
  description = "Worker Docker image"
  type        = string
  default     = ""
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "uploader"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "uploader"
}

variable "enable_redis" {
  description = "Enable Redis for CLI uploads"
  type        = bool
  default     = false  # Disable by default for dev to save costs
}
