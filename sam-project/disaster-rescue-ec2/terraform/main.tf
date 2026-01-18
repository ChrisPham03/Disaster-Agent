# =============================================================================
# Disaster Rescue System - EC2 Deployment
# =============================================================================
# Uses EC2 Auto Scaling Group + ALB + S3/CloudFront
# More control than App Runner, cost-effective at scale
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for production - store state in S3
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "disaster-rescue/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "disaster-rescue"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# For CloudFront ACM certificate (must be us-east-1)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

# =============================================================================
# Data Sources
# =============================================================================

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# Latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# =============================================================================
# Local Variables
# =============================================================================

locals {
  name_prefix = "disaster-rescue-${var.environment}"
  account_id  = data.aws_caller_identity.current.account_id
  region      = data.aws_region.current.name
  azs         = slice(data.aws_availability_zones.available.names, 0, 2)
}
