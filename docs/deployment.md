# Deployment Guide

This guide covers deploying the Aider Repository Map Service to DigitalOcean App Platform.

## Overview

The service is designed to run as a containerized FastAPI application. We provide two deployment options:
1. Direct deployment to App Platform using source code
2. Container-based deployment using our Docker image

## Prerequisites

1. DigitalOcean account with App Platform access
2. GitHub repository access
3. DigitalOcean API token
4. Environment variables for configuration

## Environment Variables

The service requires the following environment variables:

```
AIDER_API_KEY=your-api-key
AIDER_GITHUB_TOKEN=your-github-token
AIDER_MAX_TOKENS=8192
AIDER_CACHE_DIR=/tmp/.aider.cache
```

## Deployment Options

### 1. Direct Source Deployment

This is the simplest approach for development and testing:

1. Connect your GitHub repository to App Platform
2. Create a new App
3. Select the repository and branch
4. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `uvicorn aider.api.main:app --host 0.0.0.0 --port 8000`
5. Set environment variables
6. Deploy

### 2. Container-based Deployment

For production, we recommend using the container-based approach:

1. Build the Docker image:
   ```bash
   docker build -t aider-service -f docker/Dockerfile.api .
   ```

2. Push to DigitalOcean Container Registry:
   ```bash
   # Tag the image
   docker tag aider-service registry.digitalocean.com/your-registry/aider-service:latest
   
   # Push to registry
   docker push registry.digitalocean.com/your-registry/aider-service:latest
   ```

3. Create new App Platform app:
   - Choose "Deploy from Container Registry"
   - Select the pushed image
   - Configure environment variables
   - Deploy

## Resource Configuration

Recommended App Platform resources:

- Basic Plan:
  - CPU: 1 vCPU
  - Memory: 2 GB
  - Storage: 10 GB
  - Instances: 1

- Production Plan:
  - CPU: 2 vCPU
  - Memory: 4 GB
  - Storage: 20 GB
  - Instances: 2-3

## Scaling Configuration

App Platform automatic scaling settings:

```yaml
services:
- name: aider-service
  instance_count: 1
  instance_size_slug: basic-xxs
  auto_scaling:
    min_instance_count: 1
    max_instance_count: 3
    metrics:
    - type: cpu_utilization
      target_value: 70
```

## Health Checks

The service provides a health check endpoint at `/health`. Configure App Platform health check:

- HTTP Path: `/health`
- Port: 8000
- Initial Delay: 30s
- Period: 10s
- Timeout: 5s
- Success Threshold: 1
- Failure Threshold: 3

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

## Logging

App Platform automatically collects logs. Configure log management:

1. Enable log aggregation
2. Set log retention period
3. Configure log forwarding (optional)

## Security Considerations

1. API Key Management:
   - Use App Platform's encrypted environment variables
   - Rotate keys regularly
   - Monitor key usage

2. Network Security:
   - Enable HTTPS
   - Configure CORS appropriately
   - Use App Platform's automatic SSL certificates

3. Rate Limiting:
   - Configure at application level
   - Use App Platform's DDoS protection

## Backup and Recovery

1. Database Backups:
   - Configure automatic backups for cache storage
   - Set retention policy

2. Disaster Recovery:
   - Document recovery procedures
   - Test recovery process regularly

## Maintenance

1. Updates:
   - Configure automatic platform updates
   - Schedule maintenance windows
   - Use rolling updates

2. Monitoring:
   - Set up uptime monitoring
   - Configure error alerting
   - Monitor resource usage

## Cost Optimization

1. Resource Allocation:
   - Start with Basic plan
   - Monitor usage patterns
   - Scale based on demand

2. Caching:
   - Enable response caching
   - Configure cache TTL
   - Monitor cache hit rates

## Troubleshooting

Common issues and solutions:

1. Deployment Failures:
   - Check build logs
   - Verify environment variables
   - Check resource limits

2. Performance Issues:
   - Monitor resource usage
   - Check database connections
   - Analyze request patterns

3. Connection Issues:
   - Verify network settings
   - Check DNS configuration
   - Validate SSL certificates

## Next Steps

After deployment:

1. Set up monitoring and alerting
2. Configure backup schedules
3. Document operational procedures
4. Plan scaling strategy
5. Implement logging analysis