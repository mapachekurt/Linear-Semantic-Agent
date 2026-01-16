"""Task data model for incoming tasks to be evaluated."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Represents a task/issue to be evaluated by the agent."""

    task_id: str = Field(..., description="Unique identifier from source system")
    task_description: str = Field(..., description="Task description/title")
    source: str = Field(..., description="Source system: linear, clickup, trello, google_tasks")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Creation timestamp")
    priority: Optional[str] = Field(None, description="Priority: high, medium, low")
    assigned_to: Optional[str] = Field(None, description="Assignee email")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "CLK-123",
                "task_description": "Build Slack MCP server integration",
                "source": "clickup",
                "metadata": {
                    "list_id": "abc123",
                    "status": "open"
                },
                "priority": "high"
            }
        }


class TaskRequest(BaseModel):
    """API request model for task evaluation."""

    task_description: str = Field(..., description="Task description")
    source: str = Field(..., description="Source: linear, clickup, trello, google_tasks")
    task_id: str = Field(..., description="Task ID from source system")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    def to_task(self) -> Task:
        """Convert request to Task model."""
        return Task(
            task_id=self.task_id,
            task_description=self.task_description,
            source=self.source,
            metadata=self.metadata,
            priority=self.metadata.get("priority"),
            assigned_to=self.metadata.get("assigned_to")
        )
