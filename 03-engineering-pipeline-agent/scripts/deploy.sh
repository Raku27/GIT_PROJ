#!/bin/bash

# Deployment script for engineering pipeline
# This script handles deployment operations

set -e  # Exit on error

# Configuration
ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}
APP_NAME=${APP_NAME:-myapp}
REGISTRY=${REGISTRY:-docker.io}

echo "=========================================="
echo "Deployment Script"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "Image Tag: $IMAGE_TAG"
echo "App Name: $APP_NAME"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo "Error: Invalid environment. Use: dev, staging, or production"
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
docker build -t ${APP_NAME}:${IMAGE_TAG} .

# Tag image
echo "Tagging image..."
docker tag ${APP_NAME}:${IMAGE_TAG} ${REGISTRY}/${APP_NAME}:${IMAGE_TAG}

# Push to registry
echo "Pushing to registry..."
docker push ${REGISTRY}/${APP_NAME}:${IMAGE_TAG}

# Deploy to Kubernetes
if command -v kubectl &> /dev/null; then
    echo "Deploying to Kubernetes..."
    kubectl set image deployment/${APP_NAME} ${APP_NAME}=${REGISTRY}/${APP_NAME}:${IMAGE_TAG} -n ${ENVIRONMENT}
    kubectl rollout status deployment/${APP_NAME} -n ${ENVIRONMENT}
    echo "Deployment completed successfully!"
else
    echo "kubectl not found. Skipping Kubernetes deployment."
fi

# Health check
echo "Running health check..."
sleep 5
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "Health check passed!"
else
    echo "Warning: Health check failed"
fi

echo "=========================================="
echo "Deployment completed"
echo "=========================================="
