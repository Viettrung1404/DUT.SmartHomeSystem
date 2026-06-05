# Docker Deployment Guide

This guide covers deploying the Vietnamese NLP Intent Classification Server using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [CPU Deployment](#cpu-deployment)
- [GPU Deployment](#gpu-deployment)
- [Configuration](#configuration)
- [Volume Management](#volume-management)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

### For GPU Deployment (Optional)

- **NVIDIA GPU**: CUDA-compatible GPU (Compute Capability 3.5+)
- **NVIDIA Driver**: Version 450.80.02 or higher
- **NVIDIA Container Toolkit**: For Docker GPU support

#### Installing NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify installation
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Quick Start

### 1. Clone and Setup

```bash
cd ai/
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Services (CPU)

```bash
docker-compose up -d
```

### 3. Verify Deployment

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f nlp-server

# Test health endpoint
curl http://localhost:8001/health
```

### 4. Stop Services

```bash
docker-compose down
```

## CPU Deployment

### Standard Deployment

The default `docker-compose.yml` uses CPU-only configuration, suitable for development and moderate production workloads.

**Start services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f nlp-server
```

**Scale services (if needed):**
```bash
docker-compose up -d --scale nlp-server=3
```

### Build Configuration

The CPU Dockerfile (`Dockerfile`) uses:
- **Base Image**: `python:3.9-slim`
- **Multi-stage Build**: Reduces final image size
- **Non-root User**: Runs as `nlpuser` for security
- **Health Checks**: Automatic health monitoring

**Manual build:**
```bash
docker build -t vietnamese-nlp-server:cpu -f Dockerfile .
```

## GPU Deployment

### Prerequisites Check

Verify GPU is available:
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### GPU Deployment Steps

**1. Use GPU docker-compose file:**
```bash
docker-compose -f docker-compose.gpu.yml up -d
```

**2. Verify GPU usage:**
```bash
# Check if GPU is detected
docker-compose -f docker-compose.gpu.yml exec nlp-server-gpu python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Monitor GPU usage
nvidia-smi -l 1
```

**3. View logs:**
```bash
docker-compose -f docker-compose.gpu.yml logs -f nlp-server-gpu
```

### GPU Configuration

The GPU Dockerfile (`Dockerfile.gpu`) uses:
- **Base Image**: `nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04`
- **CUDA Support**: CUDA 11.8 with cuDNN 8
- **ONNX Runtime GPU**: For optimized GPU inference
- **Resource Limits**: 4 CPUs, 8GB RAM, 1 GPU

**Manual build:**
```bash
docker build -t vietnamese-nlp-server:gpu -f Dockerfile.gpu .
```

## Configuration

### Environment Variables

Create `.env` file from template:
```bash
cp .env.example .env
```

**Key variables:**

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
LOG_LEVEL=INFO
WORKERS=1

# Database Configuration
DATABASE_URL=postgresql://nlp_user:nlp_password@postgres:5432/nlp_db

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Model Configuration
MODEL_PATH=/app/models/phobert_intent_v1.0.0.pt
ONNX_MODEL_PATH=/app/models/phobert_intent_v1.0.0.onnx
USE_ONNX=true

# GPU Configuration (for GPU deployment)
USE_GPU=true
CUDA_VISIBLE_DEVICES=0

# Performance Configuration
MAX_BATCH_SIZE=32
CACHE_TTL_SECONDS=300
RATE_LIMIT_PER_MINUTE=60
```

### PostgreSQL Configuration

**Default credentials:**
- User: `nlp_user`
- Password: `nlp_password`
- Database: `nlp_db`
- Port: `5433` (host) → `5432` (container)

**Change credentials:**
Edit `docker-compose.yml`:
```yaml
postgres:
  environment:
    - POSTGRES_USER=your_user
    - POSTGRES_PASSWORD=your_password
    - POSTGRES_DB=your_db
```

### Redis Configuration

**Default configuration:**
- Port: `6380` (host) → `6379` (container)
- Persistence: AOF (Append-Only File)
- Max Memory: 512MB
- Eviction Policy: allkeys-lru

**Customize Redis:**
Edit `docker-compose.yml`:
```yaml
redis:
  command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
```

## Volume Management

### Volume Types

1. **Models Volume** (`./models:/app/models:ro`)
   - Stores trained ML models
   - Mounted as read-only for security
   - Place your `.pt` or `.onnx` files here

2. **Logs Volume** (`./logs:/app/logs`)
   - Application logs
   - Rotated daily, kept for 30 days

3. **Data Volume** (`./data:/app/data`)
   - Training data, processed data
   - Subdirectories: `raw/`, `processed/`, `augmented/`

4. **PostgreSQL Volume** (`postgres-data`)
   - Database persistence
   - Named volume managed by Docker

5. **Redis Volume** (`redis-data`)
   - Cache persistence
   - Named volume managed by Docker

### Volume Commands

**List volumes:**
```bash
docker volume ls
```

**Inspect volume:**
```bash
docker volume inspect ai_postgres-data
```

**Backup PostgreSQL:**
```bash
docker-compose exec postgres pg_dump -U nlp_user nlp_db > backup.sql
```

**Restore PostgreSQL:**
```bash
docker-compose exec -T postgres psql -U nlp_user nlp_db < backup.sql
```

**Clean volumes (WARNING: deletes data):**
```bash
docker-compose down -v
```

## Monitoring and Health Checks

### Health Check Endpoints

**Application health:**
```bash
curl http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1.0.0",
  "uptime_seconds": 3600,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Prometheus metrics:**
```bash
curl http://localhost:8001/api/v1/metrics
```

### Container Health Status

**Check health status:**
```bash
docker-compose ps
```

**View health check logs:**
```bash
docker inspect --format='{{json .State.Health}}' vietnamese-nlp-server | jq
```

### Resource Monitoring

**Monitor resource usage:**
```bash
docker stats
```

**Monitor specific container:**
```bash
docker stats vietnamese-nlp-server
```

**GPU monitoring (GPU deployment):**
```bash
nvidia-smi -l 1
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

**Check logs:**
```bash
docker-compose logs nlp-server
```

**Common causes:**
- Missing `.env` file → Copy from `.env.example`
- Port already in use → Change port in `docker-compose.yml`
- Insufficient memory → Increase Docker memory limit

#### 2. Database Connection Failed

**Check PostgreSQL status:**
```bash
docker-compose ps postgres
docker-compose logs postgres
```

**Test connection:**
```bash
docker-compose exec postgres psql -U nlp_user -d nlp_db -c "SELECT 1;"
```

**Reset database:**
```bash
docker-compose down
docker volume rm ai_postgres-data
docker-compose up -d
```

#### 3. Model Not Found

**Check model files:**
```bash
ls -la models/
```

**Mount models correctly:**
- Place model files in `./models/` directory
- Ensure filenames match `MODEL_PATH` in `.env`
- Check file permissions

#### 4. GPU Not Detected (GPU Deployment)

**Verify NVIDIA runtime:**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Check Docker daemon configuration:**
```bash
cat /etc/docker/daemon.json
```

**Should contain:**
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

**Restart Docker:**
```bash
sudo systemctl restart docker
```

#### 5. High Memory Usage

**Check memory stats:**
```bash
docker stats vietnamese-nlp-server
```

**Reduce memory usage:**
- Use ONNX model instead of PyTorch
- Enable INT8 quantization
- Reduce batch size
- Adjust resource limits in `docker-compose.yml`

### Debug Mode

**Run with debug logging:**
```bash
docker-compose down
docker-compose up
```

**Access container shell:**
```bash
docker-compose exec nlp-server bash
```

**Run tests inside container:**
```bash
docker-compose exec nlp-server pytest tests/
```

## Production Deployment

### Security Hardening

**1. Change default credentials:**
```yaml
# docker-compose.yml
postgres:
  environment:
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}  # Use env var
```

**2. Use secrets management:**
```bash
# Use Docker secrets or external secret manager
docker secret create jwt_secret jwt_secret.txt
```

**3. Enable TLS/SSL:**
- Use reverse proxy (Nginx, Traefik)
- Configure SSL certificates
- Enforce HTTPS

**4. Network isolation:**
```yaml
# docker-compose.yml
networks:
  nlp-network:
    internal: true  # No external access
  web:
    # Only expose through reverse proxy
```

### Performance Optimization

**1. Use ONNX Runtime:**
```bash
# .env
USE_ONNX=true
ONNX_MODEL_PATH=/app/models/model.onnx
```

**2. Enable caching:**
```bash
# .env
CACHE_TTL_SECONDS=300
```

**3. Adjust worker count:**
```bash
# .env
WORKERS=4  # CPU cores
```

**4. Resource limits:**
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
```

### High Availability

**1. Multiple replicas:**
```bash
docker-compose up -d --scale nlp-server=3
```

**2. Load balancer:**
```yaml
# docker-compose.yml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  ports:
    - "80:80"
  depends_on:
    - nlp-server
```

**3. Health checks:**
- Configure load balancer health checks
- Set appropriate timeouts
- Monitor health endpoint

### Monitoring Setup

**1. Prometheus + Grafana:**
```yaml
# docker-compose.monitoring.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

**2. Log aggregation:**
- Use ELK stack or Loki
- Configure log shipping
- Set up alerts

### Backup Strategy

**1. Automated backups:**
```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U nlp_user nlp_db > backup_$DATE.sql
```

**2. Schedule with cron:**
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

### Update Strategy

**1. Blue-green deployment:**
```bash
# Start new version
docker-compose -f docker-compose.new.yml up -d

# Test new version
curl http://localhost:8002/health

# Switch traffic (update load balancer)
# Stop old version
docker-compose down
```

**2. Rolling update:**
```bash
# Update one instance at a time
docker-compose up -d --no-deps --scale nlp-server=3 nlp-server
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review health status: `curl http://localhost:8001/health`
- Inspect containers: `docker-compose ps`
- Check resource usage: `docker stats`
