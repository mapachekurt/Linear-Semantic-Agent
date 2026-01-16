#!/bin/bash
set -e

PROJECT_ID="linear-semantic-agents"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/linear-semantic-agent"

echo "=== Deploying Linear Semantic Agent ==="

# 1. Build image
echo "Building Docker image..."
docker build \
  -t $IMAGE_NAME:latest \
  -f docker/Dockerfile \
  .

# 2. Push to Container Registry
echo "Pushing image to Container Registry..."
docker push $IMAGE_NAME:latest

# 3. Deploy to Kubernetes
echo "Deploying to GKE..."
kubectl apply -f kubernetes/

# 4. Wait for rollout
echo "Waiting for deployment..."
kubectl rollout status deployment/linear-semantic-agent \
  -n mapache \
  --timeout=5m

# 5. Get service endpoint
echo "Getting service endpoint..."
SERVICE_IP=$(kubectl get svc linear-semantic-agent \
  -n mapache \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "=== Deployment Complete ==="
echo "Service IP: $SERVICE_IP"
echo "API endpoint: http://$SERVICE_IP/docs (Swagger UI)"
