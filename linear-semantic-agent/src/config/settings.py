"""
Environment configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # GCP Configuration
    gcp_project_id: str = "linear-semantic-agents"
    gcp_region: str = "us-central1"

    # Vertex AI Configuration
    vertex_ai_location: str = "us-central1"
    vertex_ai_model: str = "gemini-2.0-flash-exp"

    # Linear MCP Configuration
    linear_mcp_url: str = "https://mcp.linear.app/sse"
    linear_api_key: Optional[str] = None
    linear_workspace_id: Optional[str] = None

    # Composio Configuration
    composio_api_key: Optional[str] = None

    # Firestore Configuration
    firestore_database_id: Optional[str] = "(default)"
    firestore_collection_prefix: str = "mapache_"

    # Embeddings Configuration
    embeddings_model: str = "text-embedding-005"
    embeddings_dimension: int = 768

    # Agent Configuration
    agent_name: str = "linear-semantic-agent"
    agent_version: str = "1.0.0"
    similarity_threshold: float = 0.75
    confidence_min_threshold: float = 0.60

    # Logging Configuration
    log_level: str = "INFO"
    structured_logging: bool = True

    # Development/Testing
    environment: str = "production"
    debug: bool = False
    testing: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
