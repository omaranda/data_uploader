# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

output "ecs_task_execution_role_arn" {
  description = "ARN of ECS task execution role"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "backend_task_role_arn" {
  description = "ARN of backend task role"
  value       = aws_iam_role.backend_task_role.arn
}

output "worker_task_role_arn" {
  description = "ARN of worker task role"
  value       = aws_iam_role.worker_task_role.arn
}
