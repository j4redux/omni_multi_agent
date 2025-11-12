# Deployment Guide

Complete guide for deploying the Omni Multi-Agent System to production environments.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [AWS Deployment](#aws-deployment)
3. [GCP Deployment](#gcp-deployment)
4. [Azure Deployment](#azure-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Secrets Management](#secrets-management)
8. [Monitoring & Observability](#monitoring--observability)
9. [Scaling Strategies](#scaling-strategies)
10. [Troubleshooting](#troubleshooting)

---

## Docker Deployment

### Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed
- API keys for Anthropic and OpenAI

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/omni_multi_agent.git
   cd omni_multi_agent
   ```

2. **Configure environment variables**
   
   Create `.env` file:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
   CONVERSATIONAL_AGENT_ID=  # Will be populated after initialization
   ```

3. **Build and start services**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   # Check service status
   docker-compose ps
   
   # Check Letta server health
   curl http://localhost:8283/v1/health
   
   # View logs
   docker-compose logs -f
   ```

### Production Configuration

For production deployments, modify `docker-compose.yml`:

```yaml
services:
  letta-server:
    # Use specific version instead of latest
    image: letta/letta:1.0.0
    
    # Add resource limits
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    
    # Enable logging driver
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Docker Commands Reference

```bash
# Build images
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Remove all data (CAUTION: deletes volumes)
docker-compose down -v

# Restart single service
docker-compose restart letta-server

# Execute command in running container
docker-compose exec letta-server bash

# View resource usage
docker stats
```

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | `sk-ant-xxx` | Yes |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | `sk-xxx` | Yes |
| `LETTA_SERVER_URL` | Letta server endpoint | `http://localhost:8283` | Yes |
| `CONVERSATIONAL_AGENT_ID` | Conversational agent ID | `agent-abc123` | Yes* |

*Required after agent initialization

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LETTA_SERVER_HOST` | Server bind address | `0.0.0.0` |
| `LETTA_SERVER_PORT` | Server port | `8283` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_RETRIES` | API retry attempts | `3` |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | `30` |

### Environment File Examples

**Development (.env.dev):**
```bash
ANTHROPIC_API_KEY=sk-ant-dev-key
OPENAI_API_KEY=sk-dev-key
LETTA_SERVER_URL=http://localhost:8283
LOG_LEVEL=DEBUG
```

**Production (.env.prod):**
```bash
ANTHROPIC_API_KEY=sk-ant-prod-key
OPENAI_API_KEY=sk-prod-key
LETTA_SERVER_URL=https://letta.yourdomain.com
LOG_LEVEL=INFO
MAX_RETRIES=5
REQUEST_TIMEOUT=60
```

---

*To be continued in subsequent tasks...*

## AWS Deployment

### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform 1.0+ installed
- Docker image pushed to Amazon ECR
- Anthropic and OpenAI API keys

### Deployment Options

#### Option 1: ECS Fargate (Recommended for Serverless)

**Advantages:**
- No server management
- Auto-scaling
- Pay-per-use pricing
- High availability

**Steps:**

1. **Create infrastructure with Terraform**
   
   ```bash
   cd infrastructure/aws/terraform
   
   # Initialize Terraform
   terraform init
   
   # Review plan
   terraform plan -var="environment=prod"
   
   # Apply configuration
   terraform apply -var="environment=prod"
   ```

2. **Store API keys in Secrets Manager**
   
   ```bash
   # Store Anthropic API key
   aws secretsmanager put-secret-value \
     --secret-id omni/anthropic-key-prod \
     --secret-string "sk-ant-xxxxxxxxxxxxxxxxxxxx"
   
   # Store OpenAI API key
   aws secretsmanager put-secret-value \
     --secret-id omni/openai-key-prod \
     --secret-string "sk-xxxxxxxxxxxxxxxxxxxx"
   ```

3. **Build and push Docker image to ECR**
   
   ```bash
   # Get AWS account ID
   AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   AWS_REGION="us-east-1"
   
   # Create ECR repository
   aws ecr create-repository \
     --repository-name omni-multi-agent \
     --region $AWS_REGION
   
   # Login to ECR
   aws ecr get-login-password --region $AWS_REGION | \
     docker login --username AWS --password-stdin \
     $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
   
   # Build and tag image
   docker build -t omni-multi-agent:latest .
   docker tag omni-multi-agent:latest \
     $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/omni-multi-agent:latest
   
   # Push to ECR
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/omni-multi-agent:latest
   ```

4. **Update ECS task definition with your account ID**
   
   ```bash
   # Update placeholders in ecs-task-definition.json
   sed -i "s/ACCOUNT_ID/$AWS_ACCOUNT_ID/g" infrastructure/aws/ecs-task-definition.json
   sed -i "s/REGION/$AWS_REGION/g" infrastructure/aws/ecs-task-definition.json
   
   # Get EFS ID from Terraform output
   EFS_ID=$(terraform output -raw efs_id)
   sed -i "s/fs-XXXXXXXXX/$EFS_ID/g" infrastructure/aws/ecs-task-definition.json
   ```

5. **Register task definition**
   
   ```bash
   aws ecs register-task-definition \
     --cli-input-json file://infrastructure/aws/ecs-task-definition.json
   ```

6. **Create ECS service**
   
   ```bash
   CLUSTER_NAME=$(terraform output -raw cluster_name)
   
   aws ecs create-service \
     --cluster $CLUSTER_NAME \
     --service-name omni-service \
     --task-definition omni-multi-agent \
     --desired-count 1 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=DISABLED}"
   ```

7. **Verify deployment**
   
   ```bash
   # Check service status
   aws ecs describe-services \
     --cluster $CLUSTER_NAME \
     --services omni-service
   
   # View logs
   aws logs tail /ecs/omni-multi-agent-prod --follow
   ```

#### Option 2: EKS (Elastic Kubernetes Service)

For Kubernetes-based deployment, see [Kubernetes Deployment](#kubernetes-deployment) section.

### Cost Estimation

**Monthly costs for production deployment (us-east-1):**

| Service | Configuration | Monthly Cost (USD) |
|---------|--------------|-------------------|
| ECS Fargate | 2 vCPU, 4GB RAM, 24/7 | ~$100 |
| EFS | 10GB storage | ~$3 |
| CloudWatch Logs | 5GB ingestion, 30 day retention | ~$3 |
| NAT Gateway | 2 AZs, 100GB data | ~$70 |
| Secrets Manager | 3 secrets | ~$1.20 |
| **Total** | | **~$177/month** |

**Cost optimization tips:**
- Use Fargate Spot for non-production (70% savings)
- Implement auto-scaling based on demand
- Use VPC endpoints to avoid NAT Gateway costs
- Set up log filtering to reduce CloudWatch costs

### Monitoring

AWS provides built-in monitoring through:

1. **CloudWatch Container Insights**
   - CPU/Memory utilization
   - Network metrics
   - Task count

2. **CloudWatch Logs**
   - Application logs
   - Error tracking
   - Search and filter

3. **AWS X-Ray** (optional)
   - Distributed tracing
   - Performance analysis

**View metrics:**
```bash
# CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=omni-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3+ (optional, for package management)
- Docker image pushed to container registry

### Deployment Steps

1. **Create namespace**
   
   ```bash
   kubectl apply -f kubernetes/namespace.yaml
   ```

2. **Create secrets**
   
   ```bash
   # Base64 encode your API keys
   ANTHROPIC_KEY_B64=$(echo -n "sk-ant-your-key" | base64)
   OPENAI_KEY_B64=$(echo -n "sk-your-key" | base64)
   
   # Copy template and replace placeholders
   cp kubernetes/secrets.yaml.template kubernetes/secrets.yaml
   sed -i "s/<BASE64_ENCODED_ANTHROPIC_KEY>/$ANTHROPIC_KEY_B64/g" kubernetes/secrets.yaml
   sed -i "s/<BASE64_ENCODED_OPENAI_KEY>/$OPENAI_KEY_B64/g" kubernetes/secrets.yaml
   
   # Apply secrets
   kubectl apply -f kubernetes/secrets.yaml
   ```

3. **Create ConfigMap**
   
   ```bash
   kubectl apply -f kubernetes/configmap.yaml
   ```

4. **Create persistent volume**
   
   ```bash
   kubectl apply -f kubernetes/persistent-volume.yaml
   ```

5. **Deploy Letta server**
   
   ```bash
   kubectl apply -f kubernetes/letta-deployment.yaml
   
   # Wait for Letta server to be ready
   kubectl wait --for=condition=ready pod \
     -l app=letta-server \
     -n omni-agents \
     --timeout=180s
   ```

6. **Create services**
   
   ```bash
   kubectl apply -f kubernetes/service.yaml
   ```

7. **Initialize agents**
   
   ```bash
   # Run initialization job
   kubectl run agent-init \
     --image=your-registry/omni-multi-agent:latest \
     --restart=Never \
     --namespace=omni-agents \
     --env="LETTA_SERVER_URL=http://letta-service:8283" \
     -- python scripts/initialize_agents.py
   
   # Check logs
   kubectl logs -f agent-init -n omni-agents
   
   # Get agent IDs and update secrets
   kubectl get pod agent-init -n omni-agents -o jsonpath='{.status.containerStatuses[0].state.terminated.message}'
   ```

8. **Deploy agent services**
   
   ```bash
   kubectl apply -f kubernetes/agent-deployment.yaml
   ```

9. **Set up ingress (optional)**
   
   ```bash
   # Install nginx ingress controller (if not already installed)
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm install nginx-ingress ingress-nginx/ingress-nginx \
     --namespace ingress-nginx \
     --create-namespace
   
   # Apply ingress
   kubectl apply -f kubernetes/ingress.yaml
   ```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n omni-agents

# Check pod status
kubectl get pods -n omni-agents

# View logs
kubectl logs -f deployment/letta-server -n omni-agents
kubectl logs -f deployment/conversational-agent -n omni-agents

# Check service endpoints
kubectl get endpoints -n omni-agents

# Port-forward for local testing
kubectl port-forward svc/letta-service 8283:8283 -n omni-agents
```

### Scaling

```bash
# Scale agent deployment (if stateless)
kubectl scale deployment conversational-agent \
  --replicas=3 \
  -n omni-agents

# Horizontal Pod Autoscaler
kubectl autoscale deployment conversational-agent \
  --cpu-percent=70 \
  --min=1 \
  --max=10 \
  -n omni-agents

# View HPA status
kubectl get hpa -n omni-agents
```

### Cloud-Specific Notes

#### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name omni-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4

# Use EBS for persistent volumes
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-ebs-csi-driver/master/deploy/kubernetes/base/ebs-csi-driver.yaml
```

#### GCP GKE

```bash
# Create GKE cluster
gcloud container clusters create omni-cluster \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 4

# Get credentials
gcloud container clusters get-credentials omni-cluster --zone us-central1-a
```

#### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group omni-rg \
  --name omni-cluster \
  --node-count 2 \
  --node-vm-size Standard_D2_v2 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group omni-rg --name omni-cluster
```

---
