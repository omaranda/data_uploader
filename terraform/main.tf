# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"

  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

# IAM Roles and Policies
module "iam" {
  source = "./modules/iam"

  environment = var.environment
  upload_bucket_arn = module.s3.upload_bucket_arn
}

# S3 Buckets
module "s3" {
  source = "./modules/s3"

  environment = var.environment
  upload_bucket_prefix = var.upload_bucket_prefix
  frontend_domain = var.domain_name
}

# RDS PostgreSQL Database
module "rds" {
  source = "./modules/rds"

  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  db_name               = var.db_name
  db_username           = var.db_username
  db_instance_class     = var.db_instance_class
  db_allocated_storage  = var.db_allocated_storage
  multi_az              = var.db_multi_az
  backup_retention_days = var.db_backup_retention_days
  allowed_security_group_ids = [module.ecs.backend_security_group_id]
}

# ElastiCache Redis (optional - for CLI uploads)
module "redis" {
  source = "./modules/redis"

  count = var.enable_redis ? 1 : 0

  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_type        = var.redis_node_type
  num_cache_nodes  = var.redis_num_nodes
  allowed_security_group_ids = [module.ecs.backend_security_group_id, module.ecs.worker_security_group_id]
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"

  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  certificate_arn    = var.certificate_arn
  enable_https       = var.certificate_arn != ""
}

# ECS Cluster and Services
module "ecs" {
  source = "./modules/ecs"

  environment = var.environment
  vpc_id      = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # Frontend configuration
  frontend_image       = var.frontend_image
  frontend_cpu         = var.frontend_cpu
  frontend_memory      = var.frontend_memory
  frontend_desired_count = var.frontend_desired_count
  frontend_target_group_arn = module.alb.frontend_target_group_arn

  # Backend configuration
  backend_image       = var.backend_image
  backend_cpu         = var.backend_cpu
  backend_memory      = var.backend_memory
  backend_desired_count = var.backend_desired_count
  backend_target_group_arn = module.alb.backend_target_group_arn

  # Worker configuration (optional)
  enable_worker       = var.enable_redis
  worker_image        = var.worker_image
  worker_cpu          = var.worker_cpu
  worker_memory       = var.worker_memory
  worker_desired_count = var.worker_desired_count

  # IAM roles
  task_execution_role_arn = module.iam.ecs_task_execution_role_arn
  backend_task_role_arn   = module.iam.backend_task_role_arn
  worker_task_role_arn    = module.iam.worker_task_role_arn

  # Database configuration
  db_endpoint = module.rds.db_endpoint
  db_name     = var.db_name
  db_username = var.db_username

  # Redis configuration
  redis_endpoint = var.enable_redis ? module.redis[0].redis_endpoint : ""

  # S3 configuration
  upload_bucket_name = module.s3.upload_bucket_name

  # ALB security group
  alb_security_group_id = module.alb.alb_security_group_id

  # AWS region
  aws_region = var.aws_region
}
