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
