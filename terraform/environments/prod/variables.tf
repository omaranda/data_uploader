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
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "frontend_image" {
  description = "Frontend Docker image"
  type        = string
}

variable "frontend_cpu" {
  description = "Frontend CPU units"
  type        = number
  default     = 512
}

variable "frontend_memory" {
  description = "Frontend memory in MB"
  type        = number
  default     = 1024
}

variable "frontend_desired_count" {
  description = "Frontend desired task count"
  type        = number
  default     = 2
}

variable "backend_image" {
  description = "Backend Docker image"
  type        = string
}

variable "backend_cpu" {
  description = "Backend CPU units"
  type        = number
  default     = 1024
}

variable "backend_memory" {
  description = "Backend memory in MB"
  type        = number
  default     = 2048
}

variable "backend_desired_count" {
  description = "Backend desired task count"
  type        = number
  default     = 2
}

variable "worker_image" {
  description = "Worker Docker image"
  type        = string
  default     = ""
}

variable "worker_cpu" {
  description = "Worker CPU units"
  type        = number
  default     = 512
}

variable "worker_memory" {
  description = "Worker memory in MB"
  type        = number
  default     = 1024
}

variable "worker_desired_count" {
  description = "Worker desired task count"
  type        = number
  default     = 1
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

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_multi_az" {
  description = "Enable multi-AZ for RDS"
  type        = bool
  default     = true
}

variable "db_backup_retention_days" {
  description = "RDS backup retention days"
  type        = number
  default     = 7
}

variable "enable_redis" {
  description = "Enable Redis for CLI uploads"
  type        = bool
  default     = true
}

variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_nodes" {
  description = "Number of Redis nodes"
  type        = number
  default     = 1
}

variable "upload_bucket_prefix" {
  description = "S3 upload bucket prefix"
  type        = string
  default     = "data-uploader-uploads"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Custom domain name"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default = {
    Project     = "DataUploader"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}
