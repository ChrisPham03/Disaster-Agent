# Disaster Rescue System - AWS EC2 Deployment

Production-ready deployment using **EC2 Auto Scaling + ALB + S3/CloudFront**.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CloudFront CDN                             │
│                    (HTTPS, Global Edge Caching)                      │
└─────────────────┬───────────────────────────────┬───────────────────┘
                  │                               │
                  ▼                               ▼
         ┌───────────────┐              ┌─────────────────┐
         │   S3 Bucket   │              │  Application    │
         │  (Frontend)   │              │  Load Balancer  │
         │   React App   │              │    (HTTP/S)     │
         └───────────────┘              └────────┬────────┘
                                                 │
                                    ┌────────────┴────────────┐
                                    ▼                         ▼
                            ┌─────────────┐           ┌─────────────┐
                            │    EC2      │           │    EC2      │
                            │ Instance 1  │           │ Instance 2  │
                            │   (API)     │           │   (API)     │
                            └─────────────┘           └─────────────┘
                                    │                         │
                                    └────────────┬────────────┘
                                                 │
                                    ┌────────────┴────────────┐
                                    │   Auto Scaling Group    │
                                    │   (2-10 instances)      │
                                    └─────────────────────────┘
```

## Cost Estimate

| Component | Monthly Cost |
|-----------|--------------|
| EC2 t3.medium x2 | ~$60 |
| ALB | ~$20 |
| NAT Gateway | ~$35 |
| CloudFront | ~$5-20 |
| S3 | ~$1 |
| **Total** | **~$120-140/month** |

> **Dev/Testing**: Use `t3.micro` with `min_instances=1` for ~$50/month

## Prerequisites

- AWS account with admin access
- AWS CLI installed and configured
- Terraform >= 1.5.0
- Docker installed
- Node.js >= 18

## Quick Start

### Step 1: Configure Terraform

```bash
cd terraform

# Copy example config
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Required settings in terraform.tfvars:**
```hcl
aws_region           = "us-east-1"
llm_service_endpoint = "https://api.openai.com/v1"
llm_service_api_key  = "sk-your-actual-key"
llm_model_name       = "gpt-4"

# For dev/testing (cheaper)
instance_type     = "t3.micro"
min_instances     = 1
desired_instances = 1
```

### Step 2: Create Infrastructure

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Create resources (type 'yes' when prompted)
terraform apply

# Save the outputs
terraform output
```

### Step 3: Build and Push API Image

```bash
# Get ECR URL from Terraform output
ECR_REPO=$(terraform output -raw ecr_repository_url)
REGION=$(terraform output -raw aws_region)

# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ECR_REPO

# Build image (run from project root)
cd ..
docker build -t $ECR_REPO:latest -f docker/Dockerfile.api .

# Push to ECR
docker push $ECR_REPO:latest
```

### Step 4: Refresh EC2 Instances

```bash
# Get ASG name
ASG_NAME=$(cd terraform && terraform output -raw asg_name)

# Trigger instance refresh (new instances will pull latest image)
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name $ASG_NAME \
  --region $REGION

# Check refresh status
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name $ASG_NAME \
  --region $REGION
```

### Step 5: Deploy Frontend

```bash
# Build React app
cd dashboard
npm install
npm run build

# Get S3 bucket name
BUCKET=$(cd ../terraform && terraform output -raw frontend_bucket)

# Upload to S3
aws s3 sync dist/ s3://$BUCKET/ --delete

# Invalidate CloudFront cache
CF_ID=$(cd ../terraform && terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $CF_ID --paths "/*"
```

### Step 6: Access Your App

```bash
# Get the URL
cd terraform && terraform output cloudfront_url
```

## GitHub Actions Setup

Add these secrets to your repository (Settings → Secrets → Actions):

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_REGION` | AWS region (e.g., `us-east-1`) |
| `ECR_REPOSITORY` | ECR repository URL |
| `ASG_NAME` | Auto Scaling Group name |
| `FRONTEND_BUCKET` | S3 bucket name |
| `CLOUDFRONT_DISTRIBUTION` | CloudFront distribution ID |
| `LLM_SERVICE_ENDPOINT` | LLM API endpoint |
| `LLM_SERVICE_API_KEY` | LLM API key |

Get values from Terraform:
```bash
cd terraform
terraform output github_secrets
```

## Auto Scaling Behavior

| Condition | Action |
|-----------|--------|
| CPU > 70% for 4 min | Add 2 instances |
| CPU < 30% for 4 min | Remove 1 instance |
| Minimum | 2 instances (HA) |
| Maximum | 10 instances |

## SSH Access (Optional)

1. Create a key pair in AWS Console (EC2 → Key Pairs)
2. Add to `terraform.tfvars`:
   ```hcl
   key_pair_name = "your-key-pair-name"
   ```
3. Run `terraform apply`
4. Connect via Session Manager (recommended) or SSH through a bastion

## Useful Commands

```bash
# View running instances
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=disaster-rescue-*" \
  --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name,IP:PrivateIpAddress}'

# View Auto Scaling activity
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name $(terraform output -raw asg_name) \
  --max-items 5

# View ALB target health
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --names disaster-rescue-prod-api-tg \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

# Force new deployment
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name $(terraform output -raw asg_name)

# View CloudWatch logs (if configured)
aws logs tail /aws/ec2/disaster-rescue --follow
```

## Troubleshooting

### Instances not passing health checks

```bash
# Check ALB target health
aws elbv2 describe-target-health --target-group-arn <tg-arn>

# Connect to instance via Session Manager
aws ssm start-session --target <instance-id>

# On the instance, check:
docker ps
docker logs disaster-rescue-api
curl localhost:5050/api/health
```

### Instance refresh stuck

```bash
# Cancel and retry
aws autoscaling cancel-instance-refresh \
  --auto-scaling-group-name $(terraform output -raw asg_name)

# Then start again
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name $(terraform output -raw asg_name)
```

### CloudFront showing old content

```bash
# Force cache invalidation
aws cloudfront create-invalidation \
  --distribution-id $(terraform output -raw cloudfront_distribution_id) \
  --paths "/*"
```

## Cleanup

```bash
cd terraform

# Destroy all resources
terraform destroy

# Type 'yes' when prompted
```

## EC2 vs App Runner Comparison

| Feature | EC2 + ALB | App Runner |
|---------|-----------|------------|
| Setup time | ~30 min | ~15 min |
| Control | Full control | Limited |
| Customization | High | Low |
| SSH access | Yes | No |
| Cost (baseline) | ~$120/month | ~$50/month |
| Cost (scale) | Better at scale | Better for low traffic |
| Auto-scaling speed | ~3-5 minutes | ~30 seconds |

**Choose EC2 when:**
- You need SSH/debugging access
- You want full control over instances
- You have consistent traffic
- You need custom networking

**Choose App Runner when:**
- You want simplest setup
- Traffic is variable/low
- You don't need instance access
