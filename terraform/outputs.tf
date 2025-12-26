# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = module.vpc.private_subnet_ids
}

# Load Balancer Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = module.alb.alb_zone_id
}

output "application_url" {
  description = "Application URL (HTTP or HTTPS if certificate provided)"
  value       = var.certificate_arn != "" ? "https://${var.domain_name != "" ? var.domain_name : module.alb.alb_dns_name}" : "http://${module.alb.alb_dns_name}"
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.ecs_cluster_name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs.ecs_cluster_arn
}

output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = module.ecs.frontend_service_name
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = module.ecs.backend_service_name
}

output "worker_service_name" {
  description = "Name of the worker ECS service"
  value       = var.enable_redis ? module.ecs.worker_service_name : "N/A - Worker disabled"
}

# Database Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_endpoint
  sensitive   = true
}

output "rds_address" {
  description = "RDS instance address"
  value       = module.rds.db_address
}

output "rds_port" {
  description = "RDS instance port"
  value       = module.rds.db_port
}

output "db_name" {
  description = "Database name"
  value       = var.db_name
}

# Redis Outputs
output "redis_endpoint" {
  description = "Redis primary endpoint"
  value       = var.enable_redis ? module.redis[0].redis_endpoint : "N/A - Redis disabled"
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = var.enable_redis ? module.redis[0].redis_port : "N/A - Redis disabled"
}

# S3 Outputs
output "upload_bucket_name" {
  description = "Name of the S3 upload bucket"
  value       = module.s3.upload_bucket_name
}

output "upload_bucket_arn" {
  description = "ARN of the S3 upload bucket"
  value       = module.s3.upload_bucket_arn
}

# IAM Outputs
output "backend_task_role_arn" {
  description = "ARN of the backend task IAM role"
  value       = module.iam.backend_task_role_arn
}

output "worker_task_role_arn" {
  description = "ARN of the worker task IAM role"
  value       = module.iam.worker_task_role_arn
}

# CloudWatch Outputs
output "cloudwatch_log_group_frontend" {
  description = "CloudWatch log group for frontend"
  value       = "/ecs/data-uploader-${var.environment}-frontend"
}

output "cloudwatch_log_group_backend" {
  description = "CloudWatch log group for backend"
  value       = "/ecs/data-uploader-${var.environment}-backend"
}

output "cloudwatch_log_group_worker" {
  description = "CloudWatch log group for worker"
  value       = var.enable_redis ? "/ecs/data-uploader-${var.environment}-worker" : "N/A - Worker disabled"
}

# Connection Commands
output "connect_to_database" {
  description = "Command to connect to the database"
  value       = "psql -h ${module.rds.db_address} -U ${var.db_username} -d ${var.db_name}"
  sensitive   = true
}

output "ecs_execute_command_backend" {
  description = "Command to execute into backend container"
  value       = "aws ecs execute-command --cluster ${module.ecs.ecs_cluster_name} --task <task-id> --container backend --interactive --command '/bin/bash'"
}
