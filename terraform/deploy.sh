#!/bin/bash
# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is provided
if [ -z "$1" ]; then
    print_error "Usage: ./deploy.sh [dev|staging|prod]"
    exit 1
fi

ENV=$1

if [[ ! "$ENV" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment. Use: dev, staging, or prod"
    exit 1
fi

print_info "Starting deployment for environment: $ENV"

# Change to environment directory
cd "environments/$ENV" || exit 1

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    print_error "terraform.tfvars not found!"
    print_info "Copy terraform.tfvars.example to terraform.tfvars and fill in your values"
    exit 1
fi

# Initialize Terraform
print_info "Initializing Terraform..."
terraform init

# Validate configuration
print_info "Validating Terraform configuration..."
terraform validate

if [ $? -ne 0 ]; then
    print_error "Terraform validation failed"
    exit 1
fi

# Format check
print_info "Checking Terraform formatting..."
terraform fmt -check -recursive

# Show plan
print_info "Generating Terraform plan..."
terraform plan -out=tfplan

# Confirm deployment
if [ "$ENV" == "prod" ]; then
    print_warning "You are about to deploy to PRODUCTION!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_info "Deployment cancelled"
        exit 0
    fi
else
    read -p "Apply this plan? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_info "Deployment cancelled"
        exit 0
    fi
fi

# Apply changes
print_info "Applying Terraform changes..."
terraform apply tfplan

# Clean up plan file
rm -f tfplan

print_info "Deployment completed successfully!"

# Show outputs
print_info "Deployment outputs:"
terraform output
