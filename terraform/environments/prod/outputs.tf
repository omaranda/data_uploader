# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

output "application_url" {
  description = "Application URL"
  value       = module.data_uploader.application_url
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.data_uploader.alb_dns_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.data_uploader.ecs_cluster_name
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.data_uploader.rds_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.data_uploader.redis_endpoint
  sensitive   = true
}

output "upload_bucket_name" {
  description = "Upload S3 bucket name"
  value       = module.data_uploader.upload_bucket_name
}
