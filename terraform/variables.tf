# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# General Configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

# ECS Frontend Configuration
variable "frontend_image" {
  description = "Docker image for frontend service"
  type        = string
}

variable "frontend_cpu" {
  description = "CPU units for frontend task (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "frontend_memory" {
  description = "Memory for frontend task in MB"
  type        = number
  default     = 1024
}

variable "frontend_desired_count" {
  description = "Desired number of frontend tasks"
  type        = number
  default     = 2
}

# ECS Backend Configuration
variable "backend_image" {
  description = "Docker image for backend service"
  type        = string
}

variable "backend_cpu" {
  description = "CPU units for backend task (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "backend_memory" {
  description = "Memory for backend task in MB"
  type        = number
  default     = 2048
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

# ECS Worker Configuration
variable "worker_image" {
  description = "Docker image for worker service"
  type        = string
  default     = ""
}

variable "worker_cpu" {
  description = "CPU units for worker task (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "worker_memory" {
  description = "Memory for worker task in MB"
  type        = number
  default     = 1024
}

variable "worker_desired_count" {
  description = "Desired number of worker tasks"
  type        = number
  default     = 1
}

# Database Configuration
variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "uploader"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "uploader"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "db_multi_az" {
  description = "Enable multi-AZ deployment for RDS"
  type        = bool
  default     = false
}

variable "db_backup_retention_days" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

# Redis Configuration
variable "enable_redis" {
  description = "Enable Redis for CLI upload queue (optional)"
  type        = bool
  default     = true
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

# S3 Configuration
variable "upload_bucket_prefix" {
  description = "Prefix for S3 upload bucket name"
  type        = string
  default     = "data-uploader-uploads"
}

# Load Balancer Configuration
variable "certificate_arn" {
  description = "ARN of ACM certificate for HTTPS (optional)"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Custom domain name for application (optional)"
  type        = string
  default     = ""
}
