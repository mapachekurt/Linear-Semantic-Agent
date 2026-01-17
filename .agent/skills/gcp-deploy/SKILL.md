---
name: gcp-deploy
description: Skill for deploying and managing agents on Google Cloud Platform, specifically Vertex AI Reasoning Engine.
---

# GCP Deployment Skill

This skill provides a standardized way to deploy and manage AI agents on Google Cloud Platform. It handles environment validation, IAM permissions management, and deployment orchestration.

## Features

- **Environment Validation**: Checks for required CLIs (`gcloud`), project settings, and authentication.
- **IAM Management**: Automatically audits and grants necessary permissions to deployment service accounts.
- **Vertex AI Reasoning Engine Support**: Specialized support for deploying Python agents as Vertex AI Reasoning Engines.
- **Automated Staging**: Handles the creation and configuration of GCS staging buckets.

## Usage

When tasked with deploying to GCP, follow these steps:

1. **Initialize Environment**:
   ```bash
   pwsh .agent/skills/gcp-deploy/scripts/validate_env.ps1
   ```

2. **Fix Permissions**:
   ```bash
   pwsh .agent/skills/gcp-deploy/scripts/fix_iam.ps1
   ```

3. **Deploy Agent**:
   ```bash
   pwsh .agent/skills/gcp-deploy/scripts/deploy.ps1
   ```

## Configuration

The skill uses environment variables from the project's `.env` file:
- `GCP_PROJECT_ID`: The GCP Project ID.
- `GCP_REGION`: The region for deployment (e.g., `us-central1`).
- `GCP_STAGING_BUCKET`: (Optional) The bucket used for staging artifacts.

## Resources

- [Vertex AI Reasoning Engine Documentation](https://cloud.google.com/vertex-ai/docs/reasoning-engine/overview)
- [GCP IAM Roles for Vertex AI](https://cloud.google.com/vertex-ai/docs/general/access-control)
