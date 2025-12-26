#!/bin/bash
# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    print_error "Usage: ./build-and-push.sh [AWS_ACCOUNT_ID] [AWS_REGION] [TAG]"
    print_info "Example: ./build-and-push.sh 123456789012 us-east-1 latest"
    exit 1
fi

AWS_ACCOUNT_ID=$1
AWS_REGION=$2
TAG=${3:-latest}

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

print_info "Building and pushing Docker images to ECR"
print_info "Registry: $ECR_REGISTRY"
print_info "Tag: $TAG"

# Login to ECR
print_info "Logging in to ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Function to create ECR repository if it doesn't exist
create_ecr_repo() {
    local repo_name=$1
    print_info "Checking if ECR repository exists: $repo_name"

    if ! aws ecr describe-repositories --repository-names "$repo_name" --region "$AWS_REGION" &> /dev/null; then
        print_info "Creating ECR repository: $repo_name"
        aws ecr create-repository \
            --repository-name "$repo_name" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
    else
        print_info "ECR repository already exists: $repo_name"
    fi
}

# Create repositories
create_ecr_repo "data-uploader-frontend"
create_ecr_repo "data-uploader-backend"

# Build and push frontend
print_info "Building frontend image..."
cd ../../frontend
docker build -t data-uploader-frontend:$TAG .
docker tag data-uploader-frontend:$TAG $ECR_REGISTRY/data-uploader-frontend:$TAG

print_info "Pushing frontend image..."
docker push $ECR_REGISTRY/data-uploader-frontend:$TAG

# Build and push backend
print_info "Building backend image..."
cd ../backend
docker build -t data-uploader-backend:$TAG .
docker tag data-uploader-backend:$TAG $ECR_REGISTRY/data-uploader-backend:$TAG

print_info "Pushing backend image..."
docker push $ECR_REGISTRY/data-uploader-backend:$TAG

print_info "All images pushed successfully!"
print_info ""
print_info "Update your terraform.tfvars with:"
print_info "frontend_image = \"$ECR_REGISTRY/data-uploader-frontend:$TAG\""
print_info "backend_image  = \"$ECR_REGISTRY/data-uploader-backend:$TAG\""
print_info "worker_image   = \"$ECR_REGISTRY/data-uploader-backend:$TAG\""
