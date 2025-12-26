# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "frontend_service_name" {
  description = "Name of frontend service"
  value       = aws_ecs_service.frontend.name
}

output "backend_service_name" {
  description = "Name of backend service"
  value       = aws_ecs_service.backend.name
}

output "worker_service_name" {
  description = "Name of worker service"
  value       = var.enable_worker ? aws_ecs_service.worker[0].name : "N/A"
}

output "frontend_security_group_id" {
  description = "Security group ID for frontend"
  value       = aws_security_group.frontend.id
}

output "backend_security_group_id" {
  description = "Security group ID for backend"
  value       = aws_security_group.backend.id
}

output "worker_security_group_id" {
  description = "Security group ID for worker"
  value       = var.enable_worker ? aws_security_group.worker[0].id : "N/A"
}
