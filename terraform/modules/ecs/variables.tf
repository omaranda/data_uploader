# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

# Frontend Configuration
variable "frontend_image" {
  description = "Docker image for frontend"
  type        = string
}

variable "frontend_cpu" {
  description = "CPU units for frontend task"
  type        = number
}

variable "frontend_memory" {
  description = "Memory for frontend task in MB"
  type        = number
}

variable "frontend_desired_count" {
  description = "Desired number of frontend tasks"
  type        = number
}

variable "frontend_target_group_arn" {
  description = "ARN of frontend target group"
  type        = string
}

# Backend Configuration
variable "backend_image" {
  description = "Docker image for backend"
  type        = string
}

variable "backend_cpu" {
  description = "CPU units for backend task"
  type        = number
}

variable "backend_memory" {
  description = "Memory for backend task in MB"
  type        = number
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
}

variable "backend_target_group_arn" {
  description = "ARN of backend target group"
  type        = string
}

# Worker Configuration
variable "enable_worker" {
  description = "Enable worker service"
  type        = bool
}

variable "worker_image" {
  description = "Docker image for worker"
  type        = string
  default     = ""
}

variable "worker_cpu" {
  description = "CPU units for worker task"
  type        = number
}

variable "worker_memory" {
  description = "Memory for worker task in MB"
  type        = number
}

variable "worker_desired_count" {
  description = "Desired number of worker tasks"
  type        = number
}

# IAM Roles
variable "task_execution_role_arn" {
  description = "ARN of ECS task execution role"
  type        = string
}

variable "backend_task_role_arn" {
  description = "ARN of backend task role"
  type        = string
}

variable "worker_task_role_arn" {
  description = "ARN of worker task role"
  type        = string
}

# Database Configuration
variable "db_endpoint" {
  description = "RDS endpoint"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

# Redis Configuration
variable "redis_endpoint" {
  description = "Redis endpoint"
  type        = string
}

# S3 Configuration
variable "upload_bucket_name" {
  description = "Name of upload S3 bucket"
  type        = string
}

# ALB Security Group
variable "alb_security_group_id" {
  description = "Security group ID of ALB"
  type        = string
}

# AWS Region
variable "aws_region" {
  description = "AWS region"
  type        = string
}
