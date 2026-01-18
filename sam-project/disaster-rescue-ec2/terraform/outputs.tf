# =============================================================================
# Outputs
# =============================================================================

output "cloudfront_url" {
  description = "CloudFront URL (main entry point)"
  value       = "https://${aws_cloudfront_distribution.main.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.main.id
}

output "alb_dns_name" {
  description = "ALB DNS name (direct API access)"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.api.repository_url
}

output "frontend_bucket" {
  description = "S3 bucket for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "asg_name" {
  description = "Auto Scaling Group name"
  value       = aws_autoscaling_group.api.name
}

output "aws_region" {
  description = "AWS Region"
  value       = local.region
}

# =============================================================================
# GitHub Actions Secrets
# =============================================================================

output "github_secrets" {
  description = "Values for GitHub Actions secrets"
  sensitive   = true
  value = {
    AWS_REGION              = local.region
    ECR_REPOSITORY          = aws_ecr_repository.api.repository_url
    FRONTEND_BUCKET         = aws_s3_bucket.frontend.id
    CLOUDFRONT_DISTRIBUTION = aws_cloudfront_distribution.main.id
    ASG_NAME                = aws_autoscaling_group.api.name
  }
}

# =============================================================================
# Quick Start Commands
# =============================================================================

output "quick_start" {
  description = "Quick start commands"
  value       = <<-EOT

    ============================================================
    DEPLOYMENT COMPLETE! Here's how to deploy your app:
    ============================================================

    1. Login to ECR:
       aws ecr get-login-password --region ${local.region} | \
         docker login --username AWS --password-stdin ${aws_ecr_repository.api.repository_url}

    2. Build and push API image:
       docker build -t ${aws_ecr_repository.api.repository_url}:latest -f docker/Dockerfile.api .
       docker push ${aws_ecr_repository.api.repository_url}:latest

    3. Refresh EC2 instances (to pull new image):
       aws autoscaling start-instance-refresh \
         --auto-scaling-group-name ${aws_autoscaling_group.api.name} \
         --region ${local.region}

    4. Deploy frontend:
       cd dashboard && npm run build
       aws s3 sync dist/ s3://${aws_s3_bucket.frontend.id}/ --delete

    5. Invalidate CloudFront cache:
       aws cloudfront create-invalidation \
         --distribution-id ${aws_cloudfront_distribution.main.id} \
         --paths "/*"

    6. Access your app:
       ${aws_cloudfront_distribution.main.domain_name}

    ============================================================
  EOT
}
