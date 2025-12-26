# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# Production Environment Configuration

module "data_uploader" {
  source = "../.."

  environment = "prod"
  aws_region  = var.aws_region

  # VPC Configuration
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs

  # ECS Configuration
  frontend_image         = var.frontend_image
  frontend_cpu           = var.frontend_cpu
  frontend_memory        = var.frontend_memory
  frontend_desired_count = var.frontend_desired_count

  backend_image         = var.backend_image
  backend_cpu           = var.backend_cpu
  backend_memory        = var.backend_memory
  backend_desired_count = var.backend_desired_count

  worker_image         = var.worker_image
  worker_cpu           = var.worker_cpu
  worker_memory        = var.worker_memory
  worker_desired_count = var.worker_desired_count

  # Database Configuration
  db_name                 = var.db_name
  db_username             = var.db_username
  db_instance_class       = var.db_instance_class
  db_allocated_storage    = var.db_allocated_storage
  db_multi_az             = var.db_multi_az
  db_backup_retention_days = var.db_backup_retention_days

  # Redis Configuration
  enable_redis      = var.enable_redis
  redis_node_type   = var.redis_node_type
  redis_num_nodes   = var.redis_num_nodes

  # S3 Configuration
  upload_bucket_prefix = var.upload_bucket_prefix

  # Load Balancer Configuration
  certificate_arn = var.certificate_arn
  domain_name     = var.domain_name

  # Tags
  tags = var.tags
}
