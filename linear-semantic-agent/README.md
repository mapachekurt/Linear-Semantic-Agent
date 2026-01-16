# Linear Semantic Agent

AI agent for validating and categorizing Linear tasks for mapache.app, an AI Operating System that orchestrates SaaS ecosystems through conversation.

## Overview

The Linear Semantic Agent uses Google Vertex AI and semantic embeddings to:

- **Validate tasks** against mapache.app's business model
- **Detect duplicates** using similarity matching (0.75 threshold)
- **Filter out** personal, learning, and off-topic tasks
- **Categorize** tasks into proper domains (core platform, SaaS integrations, etc.)
- **Make decisions**: "add", "filter", "consolidate", or "clarify"

## Features

- **Semantic Understanding**: Uses Vertex AI embeddings (text-embedding-005) to understand task context
- **Context-Aware**: Embedded mapache.app business knowledge guides all decisions
- **Duplicate Detection**: Identifies similar tasks with 75%+ confidence
- **Smart Caching**: Firestore-based caching for projects and embeddings
- **A2A Protocol**: Standard agent-to-agent communication
- **Production-Ready**: Deployed on GKE with health checks and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         LINEAR SEMANTIC AGENT (FastAPI)             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Reasoning Engine                            │  │
│  │  - Task evaluation                           │  │
│  │  - Similarity matching                       │  │
│  │  - Decision making                           │  │
│  └──────────────────────────────────────────────┘  │
│           │              │              │           │
│           ▼              ▼              ▼           │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────┐ │
│  │ Linear MCP   │ │ Vertex AI  │ │ Firestore    │ │
│  │ (via         │ │ Embeddings │ │ (Caching)    │ │
│  │  Composio)   │ │            │ │              │ │
│  └──────────────┘ └────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- GCP Project with billing enabled
- Linear API key
- Composio API key
- Docker and kubectl installed
- gcloud CLI configured

### 1. Setup GCP Infrastructure

```bash
cd linear-semantic-agent
./gcp_setup.sh
```

This will:
- Enable required GCP APIs
- Create GKE cluster
- Setup Firestore database
- Create Kubernetes secrets and config maps
- Grant IAM permissions

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Deploy to GKE

```bash
./deploy.sh
```

This will:
- Build Docker image
- Push to Google Container Registry
- Deploy to Kubernetes
- Wait for rollout to complete

### 4. Verify Deployment

```bash
# Check pod status
kubectl get pods -n mapache

# Check logs
kubectl logs -f deployment/linear-semantic-agent -n mapache

# Test health endpoint
kubectl port-forward svc/linear-semantic-agent 8080:80 -n mapache
curl http://localhost:8080/health
```

## Usage

### API Endpoints

#### Evaluate Task

```bash
POST /evaluate-task
```

**Request:**
```json
{
  "task_description": "Build Slack MCP server integration",
  "source": "clickup",
  "task_id": "CLK-123",
  "metadata": {
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "decision": "add",
  "confidence": 0.95,
  "reasoning": "Slack MCP is a planned SaaS integration. Valid mapache.app work.",
  "suggested_action": "Create MAPAI project: 'Slack MCP Server Implementation'",
  "alignment_score": 0.95,
  "tags": ["saaS_integrations", "mcp"],
  "processing_time_ms": 234.5
}
```

#### Health Check

```bash
GET /health
```

Returns agent health status and configuration.

#### API Documentation

Visit `/docs` for interactive Swagger UI documentation.

## Decision Types

### "add"
Task is valid mapache.app work. Create new Linear project/issue.

### "filter"
Task does not align with mapache.app (personal, learning, etc.). Archive it.

### "consolidate"
Task is similar to existing project (≥80% similarity). Link instead of creating duplicate.

### "clarify"
Task description is too vague. Ask user for more information.

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `SIMILARITY_THRESHOLD`: Minimum similarity for matching (default: 0.75)
- `CONFIDENCE_MIN_THRESHOLD`: Minimum confidence for decisions (default: 0.60)
- `CACHE_TTL_PROJECTS`: Project cache TTL in seconds (default: 3600)

### Similarity Thresholds

- **0.75**: Consider as related project
- **0.80**: Suggest consolidation
- **0.90**: Definitely a duplicate

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run locally (requires GCP credentials)
python -m src.main
```

### Project Structure

```
linear-semantic-agent/
├── src/
│   ├── main.py                  # FastAPI application
│   ├── agent.py                 # Core agent logic
│   ├── tools/
│   │   └── reasoning.py         # Reasoning engine
│   ├── models/
│   │   ├── task.py              # Task models
│   │   ├── project.py           # Project models
│   │   ├── decision.py          # Decision models
│   │   └── mapache_context.py   # Business context
│   ├── integrations/
│   │   ├── linear_mcp.py        # Linear MCP client
│   │   ├── vertex_ai.py         # Vertex AI client
│   │   └── firestore_client.py  # Firestore client
│   └── utils/
│       ├── similarity.py        # Similarity matching
│       ├── text_processing.py   # Text utilities
│       └── logger.py            # Logging
├── tests/                       # Unit tests
├── docker/                      # Docker configuration
├── kubernetes/                  # K8s manifests
└── docs/                        # Documentation
```

## Monitoring

### Health Checks

- **Liveness**: `/live` - Is the agent running?
- **Readiness**: `/ready` - Is the agent ready to serve?
- **Health**: `/health` - Detailed health status

### Metrics

Prometheus metrics available at `/metrics`:
- `agent_projects_total`: Total cached projects
- `agent_cache_valid`: Cache validity status
- `agent_version`: Agent version

### Logs

Structured JSON logs with Google Cloud Logging:

```bash
# View logs in GCP Console
gcloud logging read "resource.type=k8s_container AND resource.labels.container_name=agent"

# Follow logs locally
kubectl logs -f deployment/linear-semantic-agent -n mapache
```

## Troubleshooting

### Agent fails to initialize

Check that all required APIs are enabled:
```bash
gcloud services list --enabled
```

### Embedding generation fails

Verify Vertex AI API access and quotas:
```bash
gcloud ai-platform models list --region=us-central1
```

### Firestore connection issues

Check Firestore database exists:
```bash
gcloud firestore databases list
```

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run `pytest` to verify
4. Format with `black src/`
5. Submit pull request

## License

Proprietary - mapache.app

## Support

For issues or questions:
- GitHub Issues: https://github.com/mapachekurt/Linear-Semantic-Agent
- Documentation: See `docs/` directory
