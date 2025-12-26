#!/bin/bash
# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ -z "$1" ]; then
    print_error "Usage: ./create-secrets.sh [dev|staging|prod] [AWS_REGION]"
    print_info "Example: ./create-secrets.sh prod us-east-1"
    exit 1
fi

ENV=$1
AWS_REGION=${2:-us-east-1}

print_info "Creating secrets for environment: $ENV in region: $AWS_REGION"

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2

    print_info "Checking secret: $secret_name"

    if aws secretsmanager describe-secret --secret-id "$secret_name" --region "$AWS_REGION" &> /dev/null; then
        print_warning "Secret already exists: $secret_name"
        read -p "Do you want to update it? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            aws secretsmanager put-secret-value \
                --secret-id "$secret_name" \
                --secret-string "$secret_value" \
                --region "$AWS_REGION"
            print_info "Secret updated: $secret_name"
        else
            print_info "Skipping: $secret_name"
        fi
    else
        aws secretsmanager create-secret \
            --name "$secret_name" \
            --secret-string "$secret_value" \
            --region "$AWS_REGION"
        print_info "Secret created: $secret_name"
    fi
}

# Generate JWT secret
print_info "Generating JWT secret..."
JWT_SECRET=$(openssl rand -base64 32)
create_or_update_secret "data-uploader/$ENV/jwt-secret" "$JWT_SECRET"

# Generate NextAuth secret
print_info "Generating NextAuth secret..."
NEXTAUTH_SECRET=$(openssl rand -base64 32)
create_or_update_secret "data-uploader/$ENV/nextauth-secret" "$NEXTAUTH_SECRET"

print_info ""
print_info "All secrets created successfully!"
print_info ""
print_warning "Note: Database password is managed by Terraform (in RDS module)"
print_info "It will be automatically created during terraform apply"
