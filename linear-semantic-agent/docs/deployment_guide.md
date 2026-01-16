# Linear Semantic Agent - Deployment Guide

Complete step-by-step guide for deploying the Linear Semantic Agent to Google Cloud Platform.

## Prerequisites

### Required Accounts & Keys

1. **GCP Project**
   - Project ID: `linear-semantic-agents` (or your choice)
   - Billing enabled
   - Owner or Editor role

2. **Linear Account**
   - Linear API key from https://linear.app/settings/api
   - Workspace ID

3. **Composio Account**
   - Composio API key for OAuth orchestration

### Required Tools

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Install kubectl
gcloud components install kubectl

# Install Docker
# Follow: https://docs.docker.com/engine/install/

# Verify installations
gcloud --version
kubectl version --client
docker --version
```

## Step 1: GCP Project Setup

### 1.1 Create GCP Project

```bash
# Set project ID
export PROJECT_ID="linear-semantic-agents"

# Create project
gcloud projects create $PROJECT_ID --name="Linear Semantic Agents"

# Set as active project
gcloud config set project $PROJECT_ID

# Link billing account (replace with your billing account ID)
gcloud billing accounts list
gcloud billing projects link $PROJECT_ID --billing-account=<BILLING_ACCOUNT_ID>
```

### 1.2 Enable Required APIs

```bash
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
```

## Step 2: Infrastructure Setup

### 2.1 Create GKE Cluster

```bash
export REGION="us-central1"
export CLUSTER_NAME="mapache-agents"

gcloud container clusters create $CLUSTER_NAME \
  --region=$REGION \
  --num-nodes=1 \
  --machine-type=n1-standard-4 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=3 \
  --enable-stackdriver-kubernetes \
  --addons=HttpLoadBalancing,HorizontalPodAutoscaling
```

**Estimated time**: 5-10 minutes

### 2.2 Get Cluster Credentials

```bash
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION
```

### 2.3 Create Firestore Database

```bash
gcloud firestore databases create --region=$REGION
```

### 2.4 Create Kubernetes Namespace

```bash
kubectl create namespace mapache
```

## Step 3: Secrets & Configuration

### 3.1 Create Secrets

```bash
# Prompt for API keys
echo "Enter your Linear API Key:"
read -s LINEAR_API_KEY

echo "Enter your Composio API Key:"
read -s COMPOSIO_API_KEY

# Create Kubernetes secret
kubectl create secret generic agent-secrets \
  --from-literal=linear-api-key="$LINEAR_API_KEY" \
  --from-literal=composio-api-key="$COMPOSIO_API_KEY" \
  --namespace=mapache
```

### 3.2 Create ConfigMap

```bash
kubectl create configmap agent-config \
  --from-literal=gcp-project-id=$PROJECT_ID \
  --from-literal=vertex-ai-location=$REGION \
  --namespace=mapache
```

### 3.3 Create Service Account

```bash
# Create GCP service account
gcloud iam service-accounts create linear-semantic-agent \
  --display-name="Linear Semantic Agent"

# Grant permissions
SA_EMAIL="linear-semantic-agent@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user"
```

## Step 4: Build & Deploy

### 4.1 Build Docker Image

```bash
cd linear-semantic-agent

# Build image
docker build \
  -t gcr.io/$PROJECT_ID/linear-semantic-agent:latest \
  -f docker/Dockerfile \
  .
```

### 4.2 Push to Container Registry

```bash
# Configure Docker auth
gcloud auth configure-docker

# Push image
docker push gcr.io/$PROJECT_ID/linear-semantic-agent:latest
```

### 4.3 Deploy to Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Wait for deployment
kubectl rollout status deployment/linear-semantic-agent \
  -n mapache \
  --timeout=5m
```

## Step 5: Verification

### 5.1 Check Pod Status

```bash
kubectl get pods -n mapache

# Expected output:
# NAME                                     READY   STATUS    RESTARTS   AGE
# linear-semantic-agent-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

### 5.2 Check Logs

```bash
kubectl logs -f deployment/linear-semantic-agent -n mapache

# Look for:
# {"event": "Linear Semantic Agent initialized successfully", ...}
```

### 5.3 Test Health Endpoint

```bash
# Port forward
kubectl port-forward svc/linear-semantic-agent 8080:80 -n mapache

# In another terminal:
curl http://localhost:8080/health

# Expected response:
# {"status": "healthy", "agent": {...}, ...}
```

## Step 6: Test the Agent

### 6.1 Test Evaluation

```bash
# Create test request
cat > test_request.json <<EOF
{
  "task_description": "Build Slack MCP server integration",
  "source": "clickup",
  "task_id": "TEST-001"
}
EOF

# Send request
curl -X POST http://localhost:8080/evaluate-task \
  -H "Content-Type: application/json" \
  -d @test_request.json

# Expected: Decision with "add" or similar
```

### 6.2 View Swagger Docs

```bash
# Open browser to:
http://localhost:8080/docs
```

## Step 7: Production Setup

### 7.1 Setup Cloud Build (Optional)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

### 7.2 Setup Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-check-configs create http \
  linear-semantic-agent-health \
  --resource-type=uptime-url \
  --host=<SERVICE_IP> \
  --path=/health
```

### 7.3 Setup Alerts

Configure alerts in GCP Console:
- Navigate to Monitoring > Alerting
- Create alert for pod restarts
- Create alert for high error rates

## Troubleshooting

### Pod CrashLoopBackOff

```bash
# Check logs for errors
kubectl logs deployment/linear-semantic-agent -n mapache

# Common issues:
# - Missing API keys: Check secrets
# - API not enabled: Run gcloud services enable
# - Insufficient permissions: Check IAM roles
```

### Firestore Connection Issues

```bash
# Verify Firestore database
gcloud firestore databases list

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:linear-semantic-agent@*"
```

### Vertex AI Errors

```bash
# Check Vertex AI quotas
gcloud ai-platform quotas list --region=$REGION

# Test Vertex AI access
gcloud ai-platform models list --region=$REGION
```

## Cleanup

### Delete Resources

```bash
# Delete GKE cluster
gcloud container clusters delete $CLUSTER_NAME --region=$REGION

# Delete Firestore database (WARNING: Deletes all data)
gcloud firestore databases delete --database='(default)'

# Delete service account
gcloud iam service-accounts delete $SA_EMAIL

# Delete project (WARNING: Deletes everything)
gcloud projects delete $PROJECT_ID
```

## Next Steps

1. **Configure monitoring**: Setup dashboards in GCP Console
2. **Tune thresholds**: Adjust similarity thresholds based on usage
3. **Add integrations**: Connect to ClickUp, Trello, etc.
4. **Scale up**: Increase replicas for higher load
5. **Setup CI/CD**: Automate deployments with Cloud Build

## Support

For deployment issues:
- Check logs: `kubectl logs -f deployment/linear-semantic-agent -n mapache`
- Check events: `kubectl get events -n mapache`
- Check status: `kubectl describe pod -n mapache`

## References

- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [Linear API Documentation](https://developers.linear.app/docs)
