#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ID="linear-semantic-agents"
REGION="us-central1"
CLUSTER_NAME="mapache-agents"

echo -e "${YELLOW}=== GCP Setup for Linear Semantic Agent ===${NC}"

# 1. Set project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable \
  aiplatform.googleapis.com \
  container.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  firestore.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  secretmanager.googleapis.com

# 3. Create GKE cluster (if doesn't exist)
echo -e "${YELLOW}Creating GKE cluster...${NC}"
if ! gcloud container clusters describe $CLUSTER_NAME --region=$REGION &>/dev/null; then
  gcloud container clusters create $CLUSTER_NAME \
    --region=$REGION \
    --num-nodes=1 \
    --machine-type=n1-standard-4 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=3 \
    --enable-stackdriver-kubernetes \
    --addons=HttpLoadBalancing,HorizontalPodAutoscaling
fi

# 4. Get cluster credentials
echo -e "${YELLOW}Getting cluster credentials...${NC}"
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# 5. Create namespace
echo -e "${YELLOW}Creating Kubernetes namespace...${NC}"
kubectl create namespace mapache --dry-run=client -o yaml | kubectl apply -f -

# 6. Create Firestore database (if doesn't exist)
echo -e "${YELLOW}Creating Firestore database...${NC}"
gcloud firestore databases create --region=$REGION || true

# 7. Create secrets
echo -e "${YELLOW}Creating Kubernetes secrets...${NC}"
echo "Enter your Linear API Key (from https://linear.app/settings/api):"
read LINEAR_API_KEY

echo "Enter your Composio API Key:"
read COMPOSIO_API_KEY

kubectl create secret generic agent-secrets \
  --from-literal=linear-api-key="$LINEAR_API_KEY" \
  --from-literal=composio-api-key="$COMPOSIO_API_KEY" \
  --namespace=mapache \
  --dry-run=client -o yaml | kubectl apply -f -

# 8. Create ConfigMap
echo -e "${YELLOW}Creating ConfigMap...${NC}"
kubectl create configmap agent-config \
  --from-literal=gcp-project-id=$PROJECT_ID \
  --from-literal=vertex-ai-location=$REGION \
  --namespace=mapache \
  --dry-run=client -o yaml | kubectl apply -f -

# 9. Grant service account permissions
echo -e "${YELLOW}Granting IAM permissions...${NC}"
SA_EMAIL="linear-semantic-agent@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create linear-semantic-agent \
  --display-name="Linear Semantic Agent" || true

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user"

echo -e "${GREEN}✓ GCP setup complete!${NC}"
echo -e "${GREEN}✓ Ready for deployment.${NC}"
