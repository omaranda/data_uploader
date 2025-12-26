# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# Development Environment Configuration

module "data_uploader" {
  source = "../.."

  environment = "dev"
  aws_region  = var.aws_region

  # VPC Configuration
  vpc_cidr             = var.vpc_cidr
  availability_zones   = ["us-east-1a"]  # Single AZ for cost savings
  public_subnet_cidrs  = ["10.1.1.0/24"]
  private_subnet_cidrs = ["10.1.10.0/24"]

  # ECS Configuration - smaller instances for dev
  frontend_image         = var.frontend_image
  frontend_cpu           = 256
  frontend_memory        = 512
  frontend_desired_count = 1

  backend_image         = var.backend_image
  backend_cpu           = 512
  backend_memory        = 1024
  backend_desired_count = 1

  worker_image         = var.worker_image
  worker_cpu           = 256
  worker_memory        = 512
  worker_desired_count = 1

  # Database Configuration - smaller instance for dev
  db_name                  = var.db_name
  db_username              = var.db_username
  db_instance_class        = "db.t3.micro"
  db_allocated_storage     = 20
  db_multi_az              = false  # Single AZ for cost savings
  db_backup_retention_days = 1

  # Redis Configuration
  enable_redis    = var.enable_redis
  redis_node_type = "cache.t3.micro"
  redis_num_nodes = 1

  # S3 Configuration
  upload_bucket_prefix = "data-uploader-uploads"

  # No HTTPS for dev (HTTP only)
  certificate_arn = ""
  domain_name     = ""

  # Tags
  tags = {
    Project     = "DataUploader"
    Environment = "Development"
    ManagedBy   = "Terraform"
  }
}
