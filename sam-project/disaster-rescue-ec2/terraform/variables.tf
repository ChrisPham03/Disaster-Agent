# =============================================================================
# Variables - EC2 Deployment
# =============================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "disaster-rescue"
}

# =============================================================================
# VPC Configuration
# =============================================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# =============================================================================
# EC2 Configuration
# =============================================================================

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"  # 2 vCPU, 4GB RAM - good for most workloads
}

variable "min_instances" {
  description = "Minimum number of EC2 instances"
  type        = number
  default     = 2  # For high availability
}

variable "max_instances" {
  description = "Maximum number of EC2 instances"
  type        = number
  default     = 10
}

variable "desired_instances" {
  description = "Desired number of EC2 instances"
  type        = number
  default     = 2
}

variable "key_pair_name" {
  description = "EC2 Key Pair name for SSH access (optional)"
  type        = string
  default     = ""
}

# =============================================================================
# Auto Scaling Configuration
# =============================================================================

variable "scale_up_cpu_threshold" {
  description = "CPU percentage to trigger scale up"
  type        = number
  default     = 70
}

variable "scale_down_cpu_threshold" {
  description = "CPU percentage to trigger scale down"
  type        = number
  default     = 30
}

# =============================================================================
# LLM Service Configuration
# =============================================================================

variable "llm_service_endpoint" {
  description = "LLM service endpoint URL"
  type        = string
  sensitive   = true
}

variable "llm_service_api_key" {
  description = "LLM service API key"
  type        = string
  sensitive   = true
}

variable "llm_model_name" {
  description = "LLM model name"
  type        = string
  default     = "gpt-4"
}

# =============================================================================
# Optional: Custom Domain
# =============================================================================

variable "domain_name" {
  description = "Custom domain name (optional)"
  type        = string
  default     = ""
}

variable "create_dns_records" {
  description = "Create Route53 DNS records"
  type        = bool
  default     = false
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
  default     = ""
}
