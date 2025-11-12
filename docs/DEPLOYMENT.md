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
