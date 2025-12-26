# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# AWS Deployment Guide

Complete step-by-step guide for deploying Data Uploader to AWS using Terraform.

## Prerequisites

1. **AWS Account** with administrator access
2. **AWS CLI** installed and configured
3. **Terraform** >= 1.5.0 installed
4. **Docker** installed for building images
5. **Git** for version control

## Initial Setup

### 1. Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your output format (json)
```

### 2. Set Your AWS Account ID

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=us-east-1
echo "AWS Account ID: $AWS_ACCOUNT_ID"
```

## Step 1: Create AWS Secrets

Create the required secrets in AWS Secrets Manager:

```bash
cd terraform
./scripts/create-secrets.sh prod us-east-1
```

This will create:
- `data-uploader/prod/jwt-secret` - JWT authentication secret
- `data-uploader/prod/nextauth-secret` - NextAuth secret

**Note**: Database password is automatically created by Terraform.

## Step 2: Build and Push Docker Images

Build your application images and push to ECR:

```bash
./scripts/build-and-push.sh $AWS_ACCOUNT_ID $AWS_REGION latest
```

This will:
1. Create ECR repositories if they don't exist
2. Build frontend and backend Docker images
3. Push images to ECR
4. Display the image URLs to use in terraform.tfvars

## Step 3: Configure Terraform Variables

Navigate to your environment directory:

```bash
cd environments/prod
```

Copy the example variables file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and update:

```hcl
# REQUIRED: Update with your ECR image URLs from Step 2
frontend_image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/data-uploader-frontend:latest"
backend_image  = "123456789012.dkr.ecr.us-east-1.amazonaws.com/data-uploader-backend:latest"
worker_image   = "123456789012.dkr.ecr.us-east-1.amazonaws.com/data-uploader-backend:latest"

# OPTIONAL: Configure HTTPS (requires ACM certificate)
# certificate_arn = "arn:aws:acm:us-east-1:xxx:certificate/xxx"
# domain_name = "uploads.yourdomain.com"

# OPTIONAL: Customize instance sizes
db_instance_class = "db.t3.small"  # or db.r6g.large for production
redis_node_type   = "cache.t3.micro"  # or cache.r6g.large for production

# Tags
tags = {
  Project     = "DataUploader"
  Environment = "Production"
  ManagedBy   = "Terraform"
  Owner       = "YourName"
}
```

## Step 4: Deploy Infrastructure

### Option A: Using the Deploy Script (Recommended)

```bash
cd ../..  # Back to terraform root
./deploy.sh prod
```

This script will:
1. Initialize Terraform
2. Validate configuration
3. Show the execution plan
4. Ask for confirmation
5. Apply changes
6. Display outputs

### Option B: Manual Deployment

```bash
cd environments/prod

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply changes
terraform apply
```

## Step 5: Post-Deployment Setup

### Get Deployment Outputs

```bash
cd environments/prod
terraform output
```

Important outputs:
- `application_url` - URL to access your application
- `alb_dns_name` - Load balancer DNS name
- `upload_bucket_name` - S3 bucket for uploads

### Run Database Migrations

Connect to the backend container and run migrations:

```bash
# Get the cluster name and task ID
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)

# List tasks to get task ID
aws ecs list-tasks --cluster $CLUSTER_NAME --service-name data-uploader-prod-backend

# Execute command in container (replace TASK_ID)
aws ecs execute-command \
  --cluster $CLUSTER_NAME \
  --task <TASK_ID> \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside the container:
cd /app
alembic upgrade head
exit
```

### Configure S3 CORS

Get the upload bucket name and configure CORS:

```bash
BUCKET_NAME=$(terraform output -raw upload_bucket_name)
ALB_DNS=$(terraform output -raw alb_dns_name)

# If using custom domain:
python scripts/configure_s3_cors.py $BUCKET_NAME https://your-domain.com

# If using ALB DNS:
python scripts/configure_s3_cors.py $BUCKET_NAME http://$ALB_DNS
```

### Create Admin User

Access the application and create the first admin user through the frontend, or use the backend API:

```bash
# Get the application URL
terraform output application_url

# Access the application in your browser
# Default credentials (if seeded): admin / admin123
# Change these immediately!
```

## Step 6: Configure DNS (Optional)

If using a custom domain:

1. Get the ALB DNS name:
```bash
terraform output alb_dns_name
```

2. Create a CNAME record in your DNS provider:
```
uploads.yourdomain.com  CNAME  data-uploader-prod-alb-xxxxxxxxx.us-east-1.elb.amazonaws.com
```

## Monitoring and Maintenance

### View Logs

```bash
# Frontend logs
aws logs tail /ecs/data-uploader-prod-frontend --follow

# Backend logs
aws logs tail /ecs/data-uploader-prod-backend --follow

# Worker logs (if enabled)
aws logs tail /ecs/data-uploader-prod-worker --follow
```

### Scale Services

Edit `terraform.tfvars` and update desired counts:

```hcl
frontend_desired_count = 4  # Scale to 4 instances
backend_desired_count = 6   # Scale to 6 instances
```

Then apply:

```bash
terraform apply
```

### Update Application

Build and push new images with a new tag:

```bash
./scripts/build-and-push.sh $AWS_ACCOUNT_ID $AWS_REGION v1.2.0
```

Update `terraform.tfvars` with new image tags, then:

```bash
terraform apply
```

## Cost Optimization

### Development Environment

Use the `dev` environment for lower costs:

```bash
cd environments/dev
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars
terraform init
terraform apply
```

Dev environment features:
- Single AZ (no multi-AZ costs)
- Smaller instance types
- Reduced backup retention
- Redis disabled by default

### Production Cost Savings

1. **Stop dev/staging when not in use**:
```bash
# Scale down to 0
terraform apply -var="frontend_desired_count=0" -var="backend_desired_count=0"
```

2. **Use S3 Intelligent-Tiering** for old uploads
3. **Enable RDS auto-scaling** for variable workloads
4. **Use Spot instances** for worker (not implemented in current config)

## Disaster Recovery

### Backup Strategy

- **RDS**: Automated backups enabled (7-day retention for prod)
- **S3**: Versioning enabled on upload bucket
- **Terraform State**: Store in S3 with versioning (see `backend.tf`)

### Restore from Backup

```bash
# List RDS snapshots
aws rds describe-db-snapshots --db-instance-identifier data-uploader-prod

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier data-uploader-prod-restored \
  --db-snapshot-identifier <snapshot-id>
```

## Troubleshooting

### ECS Tasks Not Starting

```bash
# Check service events
aws ecs describe-services \
  --cluster data-uploader-prod \
  --services data-uploader-prod-backend

# Check task logs
aws logs tail /ecs/data-uploader-prod-backend --follow
```

### Database Connection Issues

```bash
# Verify security groups allow traffic from ECS to RDS
# Check that RDS is in the same VPC as ECS tasks
terraform show | grep security_group
```

### S3 Upload Failures

```bash
# Verify CORS configuration
aws s3api get-bucket-cors --bucket <bucket-name>

# Check IAM task role permissions
aws iam get-role-policy \
  --role-name data-uploader-prod-backend-task-role \
  --policy-name s3-access
```

## Clean Up

To destroy all resources:

```bash
cd environments/prod
terraform destroy
```

**WARNING**: This will delete:
- All ECS tasks and services
- RDS database (unless deletion protection is enabled)
- S3 buckets (if empty)
- All networking resources

## Security Checklist

- [ ] Secrets stored in AWS Secrets Manager
- [ ] Database password auto-generated by Terraform
- [ ] RDS in private subnets (no public access)
- [ ] S3 bucket encryption enabled (AES256)
- [ ] HTTPS enabled with valid ACM certificate
- [ ] Security groups follow least-privilege principle
- [ ] CloudWatch logging enabled for all services
- [ ] Deletion protection enabled for prod RDS
- [ ] IAM roles use specific permissions (no wildcards)
- [ ] VPC endpoints configured for S3 (cost optimization)

## Next Steps

1. Set up CloudWatch alarms for monitoring
2. Configure auto-scaling policies for ECS
3. Enable AWS WAF for application protection
4. Set up CI/CD pipeline for automated deployments
5. Configure Route53 for DNS management
6. Enable AWS Config for compliance monitoring

## Support

For issues or questions:
- Check CloudWatch Logs
- Review Terraform state: `terraform show`
- Consult AWS documentation
- Contact AWS Support (if you have a support plan)
