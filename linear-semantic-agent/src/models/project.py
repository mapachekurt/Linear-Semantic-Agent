"""Project data model for Linear projects."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import numpy as np


class LinearProject(BaseModel):
    """Represents a Linear project with semantic information."""

    id: str = Field(..., description="Linear project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    team: Optional[str] = Field(None, description="Team name")
    status: Optional[str] = Field(None, description="Project status")
    lead: Optional[Dict[str, Any]] = Field(None, description="Project lead info")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    cached_at: Optional[datetime] = Field(None, description="Cache timestamp")

    # Semantic fields
    embedding: Optional[List[float]] = Field(None, description="Text embedding vector")
    alignment_score: Optional[float] = Field(None, description="Mapache alignment score")
    domain: Optional[str] = Field(None, description="Domain: core_platform, saaS_integrations, etc")

    # Raw data
    raw_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Full Linear API response")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "proj_123abc",
                "name": "Linear Semantic Agent",
                "description": "Build semantic agent for Linear task validation",
                "team": "Mapache Solutions",
                "status": "active",
                "domain": "core_platform",
                "alignment_score": 0.95
            }
        }
        arbitrary_types_allowed = True


class LinearIssue(BaseModel):
    """Represents a Linear issue."""

    id: str = Field(..., description="Linear issue ID (e.g., MAPAI-123)")
    title: str = Field(..., description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    status: Optional[str] = Field(None, description="Issue status")
    project_id: Optional[str] = Field(None, description="Parent project ID")
    priority: Optional[int] = Field(None, description="Priority 1-4")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    raw_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Full Linear API response")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "MAPAI-123",
                "title": "Implement semantic search",
                "description": "Add semantic search across projects",
                "status": "Backlog",
                "priority": 2
            }
        }


class Match(BaseModel):
    """Represents a similarity match between task and project."""

    project: LinearProject = Field(..., description="Matched project")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0-1.0)")
    match_reason: Optional[str] = Field(None, description="Explanation of match")

    class Config:
        json_schema_extra = {
            "example": {
                "project": {"id": "proj_123", "name": "Semantic Search"},
                "similarity_score": 0.82,
                "match_reason": "Both involve semantic search functionality"
            }
        }
