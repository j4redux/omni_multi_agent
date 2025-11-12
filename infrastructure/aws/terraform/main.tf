# Terraform configuration for AWS deployment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "omni-terraform-state"
    key    = "omni-multi-agent/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "omni-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name        = "omni-private-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name        = "omni-public-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "omni-igw"
    Environment = var.environment
  }
}

# NAT Gateway
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"
  
  tags = {
    Name        = "omni-nat-eip-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "main" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = {
    Name        = "omni-nat-${count.index + 1}"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "omni-cluster-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Environment = var.environment
  }
}

# EFS for persistent storage
resource "aws_efs_file_system" "letta_data" {
  creation_token = "omni-letta-data-${var.environment}"
  encrypted      = true
  
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }
  
  tags = {
    Name        = "omni-letta-data"
    Environment = var.environment
  }
}

resource "aws_efs_mount_target" "letta_data" {
  count           = 2
  file_system_id  = aws_efs_file_system.letta_data.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.efs.id]
}

# Security Groups
resource "aws_security_group" "ecs_tasks" {
  name        = "omni-ecs-tasks-${var.environment}"
  description = "Allow inbound traffic for ECS tasks"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    protocol    = "tcp"
    from_port   = 8283
    to_port     = 8283
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "omni-ecs-tasks-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "efs" {
  name        = "omni-efs-${var.environment}"
  description = "Allow NFS traffic from ECS tasks"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    protocol        = "tcp"
    from_port       = 2049
    to_port         = 2049
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  tags = {
    Name        = "omni-efs-sg"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/omni-multi-agent-${var.environment}"
  retention_in_days = 30
  
  tags = {
    Environment = var.environment
  }
}

# Secrets Manager
resource "aws_secretsmanager_secret" "anthropic_key" {
  name        = "omni/anthropic-key-${var.environment}"
  description = "Anthropic API key for Omni Multi-Agent System"
}

resource "aws_secretsmanager_secret" "openai_key" {
  name        = "omni/openai-key-${var.environment}"
  description = "OpenAI API key for Omni Multi-Agent System"
}

resource "aws_secretsmanager_secret" "agent_ids" {
  name        = "omni/agent-ids-${var.environment}"
  description = "Agent IDs for Omni Multi-Agent System"
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}
