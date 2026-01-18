#!/bin/bash
set -e

# =============================================================================
# EC2 User Data Script - Installs Docker and runs the API container
# =============================================================================

exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting user data script at $(date)"

# Variables (injected by Terraform)
AWS_REGION="${aws_region}"
ECR_REPO="${ecr_repo}"
SECRET_ARN="${secret_arn}"
ENVIRONMENT="${environment}"

# =============================================================================
# Install Docker
# =============================================================================

echo "Installing Docker..."
yum update -y
yum install -y docker aws-cli jq

# Start Docker
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
usermod -a -G docker ec2-user

# =============================================================================
# Login to ECR
# =============================================================================

echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

# =============================================================================
# Get Secrets
# =============================================================================

echo "Fetching secrets from Secrets Manager..."
SECRETS=$(aws secretsmanager get-secret-value --secret-id $SECRET_ARN --region $AWS_REGION --query SecretString --output text)

LLM_ENDPOINT=$(echo $SECRETS | jq -r '.LLM_SERVICE_ENDPOINT')
LLM_API_KEY=$(echo $SECRETS | jq -r '.LLM_SERVICE_API_KEY')
LLM_MODEL=$(echo $SECRETS | jq -r '.LLM_MODEL_NAME')

# =============================================================================
# Pull and Run Container
# =============================================================================

echo "Pulling latest image..."
docker pull $ECR_REPO:latest

echo "Starting container..."
docker run -d \
  --name disaster-rescue-api \
  --restart unless-stopped \
  -p 5050:5050 \
  -e ENVIRONMENT=$ENVIRONMENT \
  -e NAMESPACE=disaster-rescue \
  -e FASTAPI_HOST=0.0.0.0 \
  -e FASTAPI_PORT=5050 \
  -e LLM_SERVICE_ENDPOINT="$LLM_ENDPOINT" \
  -e LLM_SERVICE_API_KEY="$LLM_API_KEY" \
  -e LLM_SERVICE_GENERAL_MODEL_NAME="$LLM_MODEL" \
  -e LLM_SERVICE_PLANNING_MODEL_NAME="$LLM_MODEL" \
  $ECR_REPO:latest

# =============================================================================
# Health Check
# =============================================================================

echo "Waiting for application to start..."
sleep 30

for i in {1..10}; do
  if curl -s http://localhost:5050/api/health > /dev/null 2>&1; then
    echo "Application is healthy!"
    break
  fi
  echo "Waiting for health check... attempt $i"
  sleep 10
done

echo "User data script completed at $(date)"

# =============================================================================
# Setup auto-update script (optional - runs on schedule)
# =============================================================================

cat > /usr/local/bin/update-container.sh << 'EOF'
#!/bin/bash
AWS_REGION="${aws_region}"
ECR_REPO="${ecr_repo}"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Pull latest
docker pull $ECR_REPO:latest

# Check if new image
NEW_IMAGE=$(docker images --no-trunc --quiet $ECR_REPO:latest)
CURRENT_IMAGE=$(docker inspect --format='{{.Image}}' disaster-rescue-api 2>/dev/null || echo "none")

if [ "$NEW_IMAGE" != "$CURRENT_IMAGE" ]; then
  echo "New image detected, restarting container..."
  docker stop disaster-rescue-api
  docker rm disaster-rescue-api
  
  # Re-run with same config
  SECRETS=$(aws secretsmanager get-secret-value --secret-id ${secret_arn} --region $AWS_REGION --query SecretString --output text)
  LLM_ENDPOINT=$(echo $SECRETS | jq -r '.LLM_SERVICE_ENDPOINT')
  LLM_API_KEY=$(echo $SECRETS | jq -r '.LLM_SERVICE_API_KEY')
  LLM_MODEL=$(echo $SECRETS | jq -r '.LLM_MODEL_NAME')
  
  docker run -d \
    --name disaster-rescue-api \
    --restart unless-stopped \
    -p 5050:5050 \
    -e ENVIRONMENT=${environment} \
    -e NAMESPACE=disaster-rescue \
    -e FASTAPI_HOST=0.0.0.0 \
    -e FASTAPI_PORT=5050 \
    -e LLM_SERVICE_ENDPOINT="$LLM_ENDPOINT" \
    -e LLM_SERVICE_API_KEY="$LLM_API_KEY" \
    -e LLM_SERVICE_GENERAL_MODEL_NAME="$LLM_MODEL" \
    -e LLM_SERVICE_PLANNING_MODEL_NAME="$LLM_MODEL" \
    $ECR_REPO:latest
fi
EOF

chmod +x /usr/local/bin/update-container.sh
