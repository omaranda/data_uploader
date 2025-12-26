# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# Terraform Infrastructure Setup - Complete

## Overview

Complete Terraform infrastructure as code (IaC) setup for deploying the Data Uploader application to AWS using a containerized Docker approach with ECS Fargate.

## What Was Created

### 📁 Directory Structure

```
terraform/
├── README.md                          # Comprehensive Terraform documentation
├── DEPLOYMENT_GUIDE.md                # Step-by-step deployment guide
├── main.tf                            # Root module orchestration
├── variables.tf                       # Root module variables
├── outputs.tf                         # Root module outputs
├── backend.tf                         # Terraform state backend config
├── .gitignore                         # Terraform-specific gitignore
├── deploy.sh                          # Deployment automation script
│
├── scripts/
│   ├── build-and-push.sh             # Build Docker images and push to ECR
│   └── create-secrets.sh             # Create AWS Secrets Manager secrets
│
├── modules/
│   ├── vpc/                          # VPC and networking module
│   │   ├── main.tf                   # VPC, subnets, NAT gateways, IGW
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── iam/                          # IAM roles and policies module
│   │   ├── main.tf                   # ECS task roles, execution roles, S3 permissions
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── s3/                           # S3 buckets module
│   │   ├── main.tf                   # Upload bucket, CORS, encryption, lifecycle
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── rds/                          # RDS PostgreSQL module
│   │   ├── main.tf                   # Database instance, security groups, secrets
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── redis/                        # ElastiCache Redis module
│   │   ├── main.tf                   # Redis cluster, security groups
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── alb/                          # Application Load Balancer module
│   │   ├── main.tf                   # ALB, target groups, listeners, HTTPS
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── ecs/                          # ECS cluster and services module
│       ├── main.tf                   # Cluster, task definitions, services
│       ├── variables.tf
│       └── outputs.tf
│
└── environments/
    ├── dev/                          # Development environment
    │   ├── main.tf                   # Dev configuration (single AZ, small instances)
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── terraform.tfvars.example  # Example variables for dev
    │
    └── prod/                         # Production environment
        ├── main.tf                   # Prod configuration (multi-AZ, scalable)
        ├── variables.tf
        ├── outputs.tf
        └── terraform.tfvars.example  # Example variables for prod
```

## Infrastructure Components

### ✅ Networking (VPC Module)
- Custom VPC with configurable CIDR
- Public subnets (for ALB) across multiple AZs
- Private subnets (for ECS, RDS, Redis) across multiple AZs
- Internet Gateway for public internet access
- NAT Gateways for private subnet internet access
- VPC endpoints for S3 (cost optimization)
- Route tables and associations

### ✅ Compute (ECS Module)
- **ECS Fargate Cluster** - Serverless container orchestration
- **Frontend Service** - Next.js application
  - Configurable CPU/memory
  - Auto-scaling ready
  - CloudWatch logging
- **Backend Service** - FastAPI application
  - Configurable CPU/memory
  - Health checks
  - ECS Exec enabled for debugging
  - Environment variables for database, Redis, S3
- **Worker Service** - RQ worker (optional for CLI uploads)
  - Redis queue processing
  - Same backend image with different command
- Security groups with least-privilege access

### ✅ Database (RDS Module)
- **PostgreSQL 16** managed database
- Configurable instance class
- Auto-scaling storage (up to 5x initial size)
- Automated backups (configurable retention)
- Multi-AZ support for high availability
- Encryption at rest
- CloudWatch logs export
- Secrets Manager integration for password
- Deletion protection for production

### ✅ Cache/Queue (Redis Module)
- **ElastiCache Redis 7.1** cluster
- Optional (can be disabled for browser-only uploads)
- Configurable node type
- Snapshots for production
- Private subnet deployment
- Security group restrictions

### ✅ Storage (S3 Module)
- Upload bucket with encryption (AES256)
- Versioning enabled
- CORS configuration for browser uploads
- Lifecycle policies:
  - Transition old versions to IA/Glacier
  - Delete incomplete multipart uploads
- Public access blocked
- Bucket policy for presigned URLs

### ✅ Load Balancing (ALB Module)
- Application Load Balancer (internet-facing)
- HTTP listener (redirect to HTTPS if cert provided)
- HTTPS listener (optional with ACM certificate)
- Target groups for frontend and backend
- Path-based routing:
  - `/` → Frontend
  - `/api/*`, `/docs` → Backend
- Health checks

### ✅ Security (IAM Module)
- **ECS Task Execution Role** - Pull images, write logs, read secrets
- **Backend Task Role** - S3 access for presigned URLs
- **Worker Task Role** - S3 upload access
- Secrets Manager access for JWT/NextAuth secrets
- ECS Exec permissions for debugging

## Key Features

### 🔒 Security
- All secrets in AWS Secrets Manager (auto-generated)
- Database password auto-rotation support
- Private subnets for all application components
- Security groups with minimal required access
- Encryption at rest for RDS and S3
- HTTPS support with ACM certificates

### 💰 Cost Optimization
- **Dev Environment**: Single AZ, small instances, Redis optional
- **Prod Environment**: Multi-AZ, auto-scaling, proper sizing
- VPC endpoints reduce NAT gateway costs
- S3 lifecycle policies for old data
- Configurable backup retention

### 📊 Observability
- CloudWatch Logs for all services
- Container Insights enabled
- Health checks for all services
- ECS Exec for debugging
- CloudWatch metrics

### 🚀 Scalability
- Auto-scaling storage for RDS
- Configurable task counts for all services
- Multi-AZ deployment for high availability
- Load balancer distributes traffic
- Fargate auto-scales infrastructure

## Quick Start Commands

### 1. Create Secrets
```bash
cd terraform
./scripts/create-secrets.sh prod us-east-1
```

### 2. Build and Push Images
```bash
./scripts/build-and-push.sh <AWS_ACCOUNT_ID> us-east-1 latest
```

### 3. Configure Variables
```bash
cd environments/prod
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 4. Deploy
```bash
cd ../..
./deploy.sh prod
```

## Environment Differences

### Development Environment
- **Cost**: ~$50-100/month
- Single availability zone
- Smaller instance types (t3.micro, t3.small)
- Redis disabled by default
- Single-AZ RDS
- 1-day backup retention
- No deletion protection

### Production Environment
- **Cost**: ~$200-500/month (depending on usage)
- Multiple availability zones
- Production instance types (configurable)
- Redis enabled
- Multi-AZ RDS
- 7-day backup retention
- Deletion protection enabled

## Estimated AWS Costs

### Development (~$50-100/month)
- ECS Fargate: ~$20-30
- RDS t3.micro: ~$15
- NAT Gateway: ~$30
- S3 + misc: ~$5-10

### Production (~$200-500/month)
- ECS Fargate: ~$100-150
- RDS t3.small multi-AZ: ~$60
- Redis: ~$15
- NAT Gateways (2): ~$60
- ALB: ~$20
- S3 + misc: ~$20

*Note: Actual costs vary based on usage, data transfer, and instance sizes*

## Important Files to Customize

1. **`environments/{env}/terraform.tfvars`** - Your configuration
   - Docker image URLs (from ECR)
   - Instance sizes
   - Domain/certificate (for HTTPS)

2. **`backend.tf`** - Terraform state backend
   - Uncomment and configure for team collaboration
   - Stores state in S3 with DynamoDB locking

3. **`modules/*/main.tf`** - Infrastructure definitions
   - Modify if you need custom configurations

## Outputs After Deployment

After running `terraform apply`, you'll get:

- `application_url` - URL to access your application
- `alb_dns_name` - Load balancer DNS (for DNS CNAME)
- `ecs_cluster_name` - ECS cluster name
- `rds_endpoint` - Database connection endpoint
- `redis_endpoint` - Redis connection endpoint
- `upload_bucket_name` - S3 bucket for uploads

## Next Steps After Infrastructure Deployment

1. **Run database migrations** - Connect to backend task via ECS Exec
2. **Configure S3 CORS** - Use provided scripts
3. **Create admin user** - Access frontend and register
4. **Set up DNS** - Create CNAME record for custom domain
5. **Configure monitoring** - CloudWatch alarms, dashboards
6. **Test uploads** - Browser and CLI uploads

## Documentation

- **[README.md](README.md)** - Comprehensive Terraform documentation
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step deployment
- **[../doc/setup/DEPLOYMENT.md](../doc/setup/DEPLOYMENT.md)** - Application deployment guide

## Maintenance

### Update Application
```bash
./scripts/build-and-push.sh $AWS_ACCOUNT_ID $AWS_REGION v1.2.0
# Update terraform.tfvars with new image tags
terraform apply
```

### Scale Services
```bash
# Edit terraform.tfvars
frontend_desired_count = 4
backend_desired_count = 6
# Apply changes
terraform apply
```

### View Logs
```bash
aws logs tail /ecs/data-uploader-prod-backend --follow
```

## Troubleshooting

All Terraform files include:
- ✅ Copyright headers (Omar Miranda)
- ✅ SPDX license identifiers (Apache-2.0)
- ✅ Proper variable descriptions
- ✅ Resource tags
- ✅ Security best practices

## Support

For issues:
1. Check CloudWatch Logs
2. Review Terraform outputs: `terraform output`
3. Inspect resources: `terraform show`
4. Consult [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**Infrastructure Status**: ✅ Complete and Ready for Deployment

**Created by**: Omar Miranda
**License**: Apache-2.0
**Date**: 2025-12-26
