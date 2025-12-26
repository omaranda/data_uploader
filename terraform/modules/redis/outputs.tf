# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

output "redis_endpoint" {
  description = "Redis primary endpoint address"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "redis_port" {
  description = "Redis port"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].port
}

output "security_group_id" {
  description = "Security group ID for Redis"
  value       = aws_security_group.redis.id
}
