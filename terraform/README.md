# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# Terraform AWS Deployment

This directory contains Terraform configurations for deploying the Data Uploader application to AWS using a containerized approach with ECS Fargate.

## 📚 Documentation

- **[Setup Complete Summary](doc/TERRAFORM_SETUP_COMPLETE.md)** - Overview of what was created and quick reference
- **[Deployment Guide](doc/DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions with troubleshooting

## Architecture Overview

```
CloudFront (CDN)
    ↓
Application Load Balancer
    ↓
ECS Fargate Cluster
    ├── Frontend Service (Next.js)
    ├── Backend Service (FastAPI)
    └── Worker Service (RQ Worker - optional)
    ↓
RDS PostgreSQL (Database)
ElastiCache Redis (Queue - optional)
S3 Buckets (File Storage)
```

## Infrastructure Components

- **VPC**: Custom VPC with public and private subnets across 2 availability zones
- **ECS Fargate**: Serverless container orchestration
  - Frontend service (Next.js on port 3000)
  - Backend service (FastAPI on port 8000)
  - Worker service (RQ worker for CLI uploads)
- **RDS PostgreSQL**: Managed database (version 16)
- **ElastiCache Redis**: Managed Redis for job queue
- **S3**: File upload storage buckets
- **ALB**: Application Load Balancer with HTTPS
- **CloudFront**: CDN for frontend static assets (optional)
- **ECR**: Container registry for Docker images
- **IAM**: Service roles and policies
- **Secrets Manager**: Secure credential storage

## Directory Structure

```
terraform/
├── README.md                 # This file
├── main.tf                   # Root module
├── variables.tf              # Input variables
├── outputs.tf                # Output values
├── backend.tf                # Terraform state backend
├── deploy.sh                 # Deployment automation script
├── doc/                      # Documentation
│   ├── TERRAFORM_SETUP_COMPLETE.md  # Setup summary
│   └── DEPLOYMENT_GUIDE.md          # Deployment guide
├── scripts/
│   ├── build-and-push.sh     # Build and push Docker images
│   └── create-secrets.sh     # Create AWS secrets
├── modules/
│   ├── vpc/                  # VPC and networking
│   ├── ecs/                  # ECS cluster and services
│   ├── rds/                  # PostgreSQL database
│   ├── redis/                # ElastiCache Redis
│   ├── s3/                   # S3 buckets
│   ├── alb/                  # Application Load Balancer
│   └── iam/                  # IAM roles and policies
└── environments/
    ├── dev/                  # Development environment
    └── prod/                 # Production environment
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Terraform** >= 1.5.0
4. **Docker** images pushed to ECR
5. **Domain name** (optional, for custom domain)
6. **SSL certificate** in ACM (optional, for HTTPS)

## Quick Start

### 1. Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t data-uploader-backend .
docker tag data-uploader-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/data-uploader-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/data-uploader-backend:latest

# Build and push frontend
cd ../frontend
docker build -t data-uploader-frontend .
docker tag data-uploader-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/data-uploader-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/data-uploader-frontend:latest
```

### 2. Initialize Terraform

```bash
cd terraform/environments/prod
terraform init
```

### 3. Create Secrets in AWS Secrets Manager

```bash
# Create JWT secret
aws secretsmanager create-secret \
  --name data-uploader/prod/jwt-secret \
  --secret-string "$(openssl rand -base64 32)"

# Create NextAuth secret
aws secretsmanager create-secret \
  --name data-uploader/prod/nextauth-secret \
  --secret-string "$(openssl rand -base64 32)"

# Create database password
aws secretsmanager create-secret \
  --name data-uploader/prod/db-password \
  --secret-string "$(openssl rand -base64 32)"
```

### 4. Configure Variables

Create `terraform.tfvars`:

```hcl
environment = "prod"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"

# ECS Configuration
frontend_image = "<account-id>.dkr.ecr.us-east-1.amazonaws.com/data-uploader-frontend:latest"
backend_image  = "<account-id>.dkr.ecr.us-east-1.amazonaws.com/data-uploader-backend:latest"
worker_image   = "<account-id>.dkr.ecr.us-east-1.amazonaws.com/data-uploader-backend:latest"

frontend_cpu    = 512
frontend_memory = 1024
backend_cpu     = 1024
backend_memory  = 2048

# Database Configuration
db_instance_class = "db.t3.small"
db_allocated_storage = 20

# Redis Configuration (optional for CLI mode)
enable_redis = true
redis_node_type = "cache.t3.micro"

# S3 Configuration
upload_bucket_prefix = "data-uploader-uploads"

# Domain Configuration (optional)
domain_name = "uploads.yourdomain.com"
certificate_arn = "arn:aws:acm:us-east-1:xxx:certificate/xxx"

# Tags
tags = {
  Project     = "DataUploader"
  Environment = "Production"
  ManagedBy   = "Terraform"
}
```

### 5. Deploy Infrastructure

```bash
# Preview changes
terraform plan

# Apply configuration
terraform apply

# Get outputs (ALB URL, ECR repositories, etc.)
terraform output
```

### 6. Configure DNS (if using custom domain)

```bash
# Get ALB DNS name
terraform output alb_dns_name

# Create CNAME record pointing your domain to ALB DNS name
```

### 7. Run Database Migrations

```bash
# Get RDS endpoint
terraform output rds_endpoint

# Connect to ECS backend task and run migrations
aws ecs execute-command \
  --cluster data-uploader-prod \
  --task <task-id> \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside container:
cd /app
alembic upgrade head
```

## Environment-Specific Deployments

### Development

```bash
cd terraform/environments/dev
terraform init
terraform apply -var-file="dev.tfvars"
```

### Staging

```bash
cd terraform/environments/staging
terraform init
terraform apply -var-file="staging.tfvars"
```

### Production

```bash
cd terraform/environments/prod
terraform init
terraform apply -var-file="prod.tfvars"
```

## Cost Optimization

### Development/Staging
- Use smaller instance types (t3.micro, t3.small)
- Single AZ deployment
- Disable Redis if only using browser uploads
- Use S3 Intelligent-Tiering

### Production
- Multi-AZ for high availability
- Auto-scaling for ECS services
- RDS read replicas for analytics
- CloudFront CDN for global distribution

## Security Considerations

1. **Secrets Management**
   - All secrets stored in AWS Secrets Manager
   - No hardcoded credentials in Terraform or containers
   - Automatic secret rotation enabled

2. **Network Security**
   - Private subnets for ECS tasks and RDS
   - Security groups with least-privilege access
   - VPC endpoints for AWS services

3. **IAM Permissions**
   - Task-specific IAM roles
   - S3 bucket policies restricting access
   - CloudTrail logging enabled

4. **Encryption**
   - RDS encryption at rest
   - S3 encryption (AES256)
   - ALB HTTPS with TLS 1.2+

## Monitoring & Logging

- **CloudWatch Logs**: Container logs from ECS
- **CloudWatch Metrics**: ECS, RDS, ALB metrics
- **CloudWatch Alarms**: Auto-scaling triggers, error alerts
- **X-Ray**: Distributed tracing (optional)

## Backup & Disaster Recovery

- **RDS Automated Backups**: 7-day retention
- **RDS Snapshots**: Manual snapshots before major changes
- **S3 Versioning**: Enabled on upload buckets
- **Multi-Region**: Deploy to second region for DR (optional)

## Scaling Configuration

### ECS Auto-Scaling

```hcl
# Frontend: Scale based on CPU
Target CPU: 70%
Min tasks: 2
Max tasks: 10

# Backend: Scale based on CPU and ALB request count
Target CPU: 70%
Target request count: 1000/task
Min tasks: 2
Max tasks: 20
```

### Database Scaling

```hcl
# RDS
Instance class: db.t3.small → db.r6g.large (production)
Storage: Auto-scaling enabled (20GB → 100GB)
Read replicas: 1-2 for production
```

## Troubleshooting

### ECS Tasks Not Starting

```bash
# Check task logs
aws logs tail /ecs/data-uploader-backend --follow

# Check task definition
aws ecs describe-task-definition --task-definition data-uploader-backend

# Check service events
aws ecs describe-services --cluster data-uploader-prod --services backend
```

### Database Connection Issues

```bash
# Verify security group rules
# Ensure ECS task security group can reach RDS on port 5432

# Test connection from ECS task
aws ecs execute-command \
  --cluster data-uploader-prod \
  --task <task-id> \
  --container backend \
  --interactive \
  --command "psql -h <rds-endpoint> -U uploader -d uploader"
```

### S3 Upload Failures

```bash
# Check IAM task role permissions
# Verify CORS configuration on bucket
# Check CloudWatch logs for presigned URL errors
```

## Clean Up

```bash
# Destroy all resources
cd terraform/environments/prod
terraform destroy

# Warning: This will delete:
# - All ECS tasks and services
# - RDS database (unless backup protection enabled)
# - S3 buckets (if empty)
# - All networking resources
```

## Support

For issues or questions:
- Check CloudWatch Logs: `/ecs/data-uploader-*`
- Review Terraform state: `terraform show`
- AWS Support (if you have a support plan)

## License

Copyright 2025 Omar Miranda
Licensed under the Apache License, Version 2.0
