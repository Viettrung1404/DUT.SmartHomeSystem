# Docker Quick Start Guide

Quick reference for common Docker operations with the Vietnamese NLP Intent Classification Server.

## Quick Commands

### CPU Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```

### GPU Deployment

```bash
# Start with GPU support
docker-compose -f docker-compose.gpu.yml up -d

# View logs
docker-compose -f docker-compose.gpu.yml logs -f

# Stop services
docker-compose -f docker-compose.gpu.yml down

# Check GPU usage
nvidia-smi -l 1
```

## Health Checks

```bash
# Check service status
docker-compose ps

# Test API health
curl http://localhost:8001/health

# View metrics
curl http://localhost:8001/api/v1/metrics

# Test classification
curl -X POST http://localhost:8001/api/v1/intent/classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"text": "Bật đèn phòng khách", "user_id": "test_user"}'
```

## Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs for specific service
docker-compose logs -f nlp-server

# View last 100 lines
docker-compose logs --tail=100 nlp-server

# Access container shell
docker-compose exec nlp-server bash

# Run tests inside container
docker-compose exec nlp-server pytest tests/
```

## Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U nlp_user -d nlp_db

# Backup database
docker-compose exec postgres pg_dump -U nlp_user nlp_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U nlp_user nlp_db < backup.sql

# View database logs
docker-compose logs postgres
```

## Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Check Redis info
docker-compose exec redis redis-cli INFO

# Monitor Redis commands
docker-compose exec redis redis-cli MONITOR

# Flush cache
docker-compose exec redis redis-cli FLUSHALL
```

## Resource Monitoring

```bash
# Monitor all containers
docker stats

# Monitor specific container
docker stats vietnamese-nlp-server

# Check disk usage
docker system df

# View container details
docker inspect vietnamese-nlp-server
```

## Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes (WARNING: deletes data)
docker-compose down -v

# Remove unused images
docker image prune -a

# Clean everything (WARNING: removes all unused Docker resources)
docker system prune -a --volumes
```

## Troubleshooting

```bash
# Restart specific service
docker-compose restart nlp-server

# Rebuild specific service
docker-compose up -d --no-deps --build nlp-server

# View container logs with timestamps
docker-compose logs -f -t nlp-server

# Check container health
docker inspect --format='{{json .State.Health}}' vietnamese-nlp-server | jq

# Check environment variables
docker-compose exec nlp-server env
```

## Configuration Files

- **Dockerfile**: CPU-only build configuration
- **Dockerfile.gpu**: GPU-enabled build configuration
- **docker-compose.yml**: CPU deployment configuration
- **docker-compose.gpu.yml**: GPU deployment configuration
- **.dockerignore**: Files excluded from Docker build
- **.env**: Environment variables (create from .env.example)

## Port Mappings

| Service | Host Port | Container Port | Description |
|---------|-----------|----------------|-------------|
| NLP Server | 8001 | 8001 | API endpoint |
| PostgreSQL | 5433 | 5432 | Database |
| Redis | 6380 | 6379 | Cache |

## Volume Mappings

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| ./models | /app/models | ML models (read-only) |
| ./logs | /app/logs | Application logs |
| ./data | /app/data | Training/processed data |
| postgres-data | /var/lib/postgresql/data | Database persistence |
| redis-data | /data | Cache persistence |

## Environment Variables

Key variables in `.env`:

```bash
# API
API_HOST=0.0.0.0
API_PORT=8001

# Database
DATABASE_URL=postgresql://nlp_user:nlp_password@postgres:5432/nlp_db

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key

# Model
MODEL_PATH=/app/models/model.pt
USE_ONNX=true

# GPU (for GPU deployment)
USE_GPU=true
CUDA_VISIBLE_DEVICES=0
```

## Common Issues

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8002:8001"  # Use different host port
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Model Not Found
```bash
# Check model files exist
ls -la models/

# Verify MODEL_PATH in .env matches actual filename
```

### Out of Memory
```bash
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
```

## Production Checklist

- [ ] Change default database credentials
- [ ] Set strong JWT_SECRET_KEY
- [ ] Configure resource limits
- [ ] Enable health checks
- [ ] Set up log rotation
- [ ] Configure backup strategy
- [ ] Use HTTPS/TLS
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure rate limiting
- [ ] Test disaster recovery

## Next Steps

1. **Development**: Use `docker-compose.yml` for local development
2. **Testing**: Run tests inside container with `pytest`
3. **Production**: Review [DOCKER.md](DOCKER.md) for production deployment guide
4. **Monitoring**: Set up Prometheus metrics collection
5. **Scaling**: Use load balancer for multiple replicas

For detailed documentation, see [DOCKER.md](DOCKER.md).
