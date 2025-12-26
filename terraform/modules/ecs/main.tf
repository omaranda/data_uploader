# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "data-uploader-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "data-uploader-${var.environment}-cluster"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/data-uploader-${var.environment}-frontend"
  retention_in_days = 7

  tags = {
    Name = "data-uploader-${var.environment}-frontend-logs"
  }
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/data-uploader-${var.environment}-backend"
  retention_in_days = 7

  tags = {
    Name = "data-uploader-${var.environment}-backend-logs"
  }
}

resource "aws_cloudwatch_log_group" "worker" {
  count = var.enable_worker ? 1 : 0

  name              = "/ecs/data-uploader-${var.environment}-worker"
  retention_in_days = 7

  tags = {
    Name = "data-uploader-${var.environment}-worker-logs"
  }
}

# Security Group for Frontend
resource "aws_security_group" "frontend" {
  name        = "data-uploader-${var.environment}-frontend-sg"
  description = "Security group for frontend ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "data-uploader-${var.environment}-frontend-sg"
  }
}

# Security Group for Backend
resource "aws_security_group" "backend" {
  name        = "data-uploader-${var.environment}-backend-sg"
  description = "Security group for backend ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  ingress {
    description     = "HTTP from Frontend"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "data-uploader-${var.environment}-backend-sg"
  }
}

# Security Group for Worker
resource "aws_security_group" "worker" {
  count = var.enable_worker ? 1 : 0

  name        = "data-uploader-${var.environment}-worker-sg"
  description = "Security group for worker ECS tasks"
  vpc_id      = var.vpc_id

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "data-uploader-${var.environment}-worker-sg"
  }
}

# Secrets for database password
data "aws_secretsmanager_secret" "db_password" {
  name = "data-uploader/${var.environment}/db-password"
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = data.aws_secretsmanager_secret.db_password.id
}

# Frontend Task Definition
resource "aws_ecs_task_definition" "frontend" {
  family                   = "data-uploader-${var.environment}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.frontend_cpu
  memory                   = var.frontend_memory
  execution_role_arn       = var.task_execution_role_arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = var.frontend_image

      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NEXT_PUBLIC_API_URL"
          value = "http://localhost:8000"
        },
        {
          name  = "NODE_ENV"
          value = var.environment == "prod" ? "production" : "development"
        }
      ]

      secrets = [
        {
          name      = "NEXTAUTH_SECRET"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:data-uploader/${var.environment}/nextauth-secret"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.frontend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name = "data-uploader-${var.environment}-frontend-task"
  }
}

# Backend Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "data-uploader-${var.environment}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn            = var.backend_task_role_arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = var.backend_image

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)}@${var.db_endpoint}/${var.db_name}"
        },
        {
          name  = "REDIS_URL"
          value = var.redis_endpoint != "" ? "redis://${var.redis_endpoint}:6379/0" : ""
        },
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        },
        {
          name  = "UPLOAD_BUCKET_NAME"
          value = var.upload_bucket_name
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        }
      ]

      secrets = [
        {
          name      = "JWT_SECRET"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:data-uploader/${var.environment}/jwt-secret"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }

      essential = true

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "data-uploader-${var.environment}-backend-task"
  }
}

# Worker Task Definition
resource "aws_ecs_task_definition" "worker" {
  count = var.enable_worker ? 1 : 0

  family                   = "data-uploader-${var.environment}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn            = var.worker_task_role_arn

  container_definitions = jsonencode([
    {
      name    = "worker"
      image   = var.worker_image
      command = ["rq", "worker", "--url", "redis://${var.redis_endpoint}:6379/0"]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)}@${var.db_endpoint}/${var.db_name}"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${var.redis_endpoint}:6379/0"
        },
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        },
        {
          name  = "UPLOAD_BUCKET_NAME"
          value = var.upload_bucket_name
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.worker[0].name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name = "data-uploader-${var.environment}-worker-task"
  }
}

# Frontend ECS Service
resource "aws_ecs_service" "frontend" {
  name            = "data-uploader-${var.environment}-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = var.frontend_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.frontend.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.frontend_target_group_arn
    container_name   = "frontend"
    container_port   = 3000
  }

  depends_on = [var.frontend_target_group_arn]

  tags = {
    Name = "data-uploader-${var.environment}-frontend-service"
  }
}

# Backend ECS Service
resource "aws_ecs_service" "backend" {
  name            = "data-uploader-${var.environment}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_desired_count
  launch_type     = "FARGATE"

  enable_execute_command = true

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.backend.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.backend_target_group_arn
    container_name   = "backend"
    container_port   = 8000
  }

  depends_on = [var.backend_target_group_arn]

  tags = {
    Name = "data-uploader-${var.environment}-backend-service"
  }
}

# Worker ECS Service
resource "aws_ecs_service" "worker" {
  count = var.enable_worker ? 1 : 0

  name            = "data-uploader-${var.environment}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker[0].arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.worker[0].id]
    assign_public_ip = false
  }

  tags = {
    Name = "data-uploader-${var.environment}-worker-service"
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
