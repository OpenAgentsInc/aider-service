# Deployment Guide

This guide covers deploying the Aider Repository Map Service to DigitalOcean App Platform using containers.

## Overview

The service runs as a containerized FastAPI application, using a multi-stage build process for optimal security and performance. We use the same container configuration in both development and production to maintain environment parity.

## Prerequisites

1. DigitalOcean account with App Platform access
2. Docker installed locally
3. DigitalOcean CLI (doctl) configured
4. Environment variables for configuration

## Environment Variables

Required environment variables:

```
AIDER_API_KEY=your-api-key
AIDER_GITHUB_TOKEN=your-github-token
AIDER_MAX_TOKENS=8192
AIDER_CACHE_DIR=/tmp/.aider.cache
```

## Local Development

1. **Build the Container**:
   ```bash
   docker build -t aider-service -f docker/Dockerfile.api .
   ```

2. **Run Locally**:
   ```bash
   docker run -p 8000:8000 \
     -e AIDER_API_KEY=your-api-key \
     -e AIDER_GITHUB_TOKEN=your-github-token \
     aider-service
   ```

3. **Development with Hot Reload**:
   ```bash
   docker run -p 8000:8000 \
     -v $(pwd):/app \
     -e AIDER_API_KEY=your-api-key \
     -e AIDER_GITHUB_TOKEN=your-github-token \
     aider-service \
     uvicorn aider.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Production Deployment

1. **Create DOCR Registry**:
   ```bash
   doctl registry create aider-service
   ```

2. **Build and Push**:
   ```bash
   # Build production image
   docker build -t registry.digitalocean.com/aider-service/api:latest -f docker/Dockerfile.api .
   
   # Push to DOCR
   docker push registry.digitalocean.com/aider-service/api:latest
   ```

3. **Deploy on App Platform**:
   ```bash
   # Create app spec
   cat > app.yaml << EOL
   services:
   - name: aider-service
     instance_count: 2  # For high availability
     instance_size_slug: professional-xs  # 2 vCPU, 4GB RAM
     image:
       registry: registry.digitalocean.com
       registry_type: DOCR
       repository: aider-service/api
       tag: latest
     health_check:
       http_path: /health
       port: 8000
       initial_delay_seconds: 30
     envs:
     - key: AIDER_API_KEY
       scope: RUN_TIME
       type: SECRET
     - key: AIDER_GITHUB_TOKEN
       scope: RUN_TIME
       type: SECRET
     - key: AIDER_MAX_TOKENS
       scope: RUN_TIME
       value: "8192"
     - key: AIDER_CACHE_DIR
       scope: RUN_TIME
       value: "/tmp/.aider.cache"
   EOL

   # Create the app
   doctl apps create --spec app.yaml
   ```

## Container Details

Our Dockerfile implements:

1. **Multi-stage Build**:
   - Builder stage for compilation and dependencies
   - Slim production image with only runtime requirements

2. **Security**:
   - Non-root user (appuser)
   - Minimal system dependencies
   - Proper file permissions
   - Secure git configuration

3. **Performance**:
   - Layer caching optimization
   - Multi-worker uvicorn configuration
   - Health checks
   - Production-ready settings

4. **Development Features**:
   - Volume mounting for hot reload
   - Environment variable handling
   - Debug capabilities

## Monitoring

1. **Container Health**:
   - Built-in Docker health checks
   - App Platform metrics
   - FastAPI endpoint monitoring

2. **Alerts**:
   - Container health status
   - Resource usage
   - Error rates
   - Response times

## Security

1. **Container Security**:
   - Non-root user
   - Minimal base image
   - Multi-stage build
   - Proper permissions

2. **Runtime Security**:
   - Environment variable encryption
   - Network isolation
   - Resource limits
   - Health monitoring

## Maintenance

1. **Updates**:
   ```bash
   # Build new version
   docker build -t registry.digitalocean.com/aider-service/api:v1.0.1 -f docker/Dockerfile.api .
   
   # Push new version
   docker push registry.digitalocean.com/aider-service/api:v1.0.1
   
   # Update app spec with new version
   doctl apps update your-app-id --spec app.yaml
   ```

2. **Monitoring**:
   ```bash
   # View app health
   doctl apps list
   
   # View logs
   doctl apps logs your-app-id
   
   # View metrics
   doctl apps metrics your-app-id
   ```

## Troubleshooting

1. **Container Issues**:
   ```bash
   # Check container logs
   docker logs container-id
   
   # Inspect container
   docker inspect container-id
   
   # Check health
   docker ps --format "table {{.ID}}\t{{.Status}}\t{{.Health}}"
   ```

2. **App Platform Issues**:
   ```bash
   # Check app status
   doctl apps list
   
   # View deployment logs
   doctl apps logs your-app-id --follow
   ```

## Next Steps

1. Set up CI/CD pipeline
2. Configure automated testing
3. Implement monitoring alerts
4. Set up log aggregation
5. Document operational procedures