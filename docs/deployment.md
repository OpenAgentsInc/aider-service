# Deployment Guide

This guide covers deploying the Aider Repository Map Service to DigitalOcean App Platform.

## Overview

The service can be deployed to App Platform in two ways:
1. Container Registry deployment (Recommended for Production)
2. Source Code deployment (Suitable for Development/Testing)

## Why Container Registry Deployment?

We strongly recommend the container-based approach for production because:

1. **Dependency Control**:
   - Our service requires specific system packages (git, build tools)
   - Needs precise permission configurations for git operations
   - Custom cache directory setup and permissions

2. **Security**:
   - Our Dockerfile implements specific security measures
   - Runs as non-root user with exact permissions
   - Controlled system package installation

3. **Reliability**:
   - Identical environment across all deployments
   - Predictable git operations behavior
   - Consistent cache handling

4. **Performance**:
   - Optimized container size
   - Efficient layer caching
   - Pre-built dependencies

## Prerequisites

1. DigitalOcean account with App Platform access
2. GitHub repository access
3. DigitalOcean API token
4. Environment variables for configuration

## Environment Variables

Required environment variables:

```
AIDER_API_KEY=your-api-key
AIDER_GITHUB_TOKEN=your-github-token
AIDER_MAX_TOKENS=8192
AIDER_CACHE_DIR=/tmp/.aider.cache
```

## Production Deployment Steps

1. **Build Docker Image**:
   ```bash
   docker build -t aider-service -f docker/Dockerfile.api .
   ```

2. **Create DOCR Registry**:
   ```bash
   doctl registry create aider-service
   ```

3. **Push to DOCR**:
   ```bash
   # Tag the image
   docker tag aider-service registry.digitalocean.com/aider-service/api:latest
   
   # Push to registry
   docker push registry.digitalocean.com/aider-service/api:latest
   ```

4. **Deploy on App Platform**:
   - Go to App Platform dashboard
   - Click "Create App"
   - Choose "Deploy from Container Registry"
   - Select your pushed image
   - Configure Resources (see below)
   - Set Environment Variables
   - Deploy

## Resource Configuration

Recommended App Platform resources for production:

```yaml
services:
- name: aider-service
  instance_count: 2  # For high availability
  instance_size_slug: professional-xs  # 2 vCPU, 4GB RAM
  source_dir: /
  git:
    repo_clone_url: https://github.com/OpenAgentsInc/aider-service.git
    branch: main
  health_check:
    http_path: /health
    port: 8000
    initial_delay_seconds: 30
  image:
    registry: registry.digitalocean.com
    registry_type: DOCR
    repository: aider-service/api
    tag: latest
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
```

## Development Deployment (Alternative)

If you prefer to deploy directly from source (not recommended for production):

1. Connect your GitHub repository to App Platform
2. Create a new App
3. Select the repository and branch
4. Configure build settings:
   ```yaml
   build_command: pip install -r requirements.txt
   run_command: uvicorn aider.api.main:app --host 0.0.0.0 --port 8000
   ```
5. Set environment variables
6. Deploy

Note: This approach may require additional configuration to handle system dependencies and permissions.

## Monitoring

1. Enable App Platform Metrics:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

2. Configure Alerts:
   - High CPU usage (>80%)
   - High memory usage (>80%)
   - Error rate increase
   - Response time degradation

## Security Considerations

1. API Key Management:
   - Use App Platform's encrypted environment variables
   - Rotate keys regularly
   - Monitor key usage

2. Network Security:
   - Enable HTTPS (automatic with App Platform)
   - Configure CORS appropriately
   - Use App Platform's automatic SSL certificates

3. Rate Limiting:
   - Configure at application level
   - Use App Platform's DDoS protection

## Maintenance

1. Updates:
   - Push new versions to DOCR
   - App Platform handles rolling updates
   - Monitor deployment health

2. Monitoring:
   - Set up uptime monitoring
   - Configure error alerting
   - Monitor resource usage

## Troubleshooting

Common issues and solutions:

1. Git Operation Failures:
   - Check AIDER_GITHUB_TOKEN
   - Verify container permissions
   - Check git configuration

2. Performance Issues:
   - Monitor resource usage
   - Check cache directory
   - Analyze request patterns

3. Deployment Failures:
   - Check container build logs
   - Verify environment variables
   - Check resource limits

## Cost Optimization

1. Resource Allocation:
   - Start with Professional-xs plan
   - Monitor usage patterns
   - Scale based on demand

2. Caching:
   - Enable response caching
   - Configure cache TTL
   - Monitor cache hit rates

## Next Steps

After deployment:

1. Set up monitoring and alerting
2. Configure backup schedules
3. Document operational procedures
4. Plan scaling strategy
5. Implement logging analysis