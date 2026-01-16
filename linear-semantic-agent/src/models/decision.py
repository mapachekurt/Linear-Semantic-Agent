"""Decision data model for agent output."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DecisionType(str, Enum):
    """Decision types for task evaluation."""
    ADD = "add"                      # Create new Linear project/issue
    FILTER = "filter"                # Archive/discard (not mapache work)
    CONSOLIDATE = "consolidate"      # Merge with existing project
    CLARIFY = "clarify"              # Ask for more information


class Decision(BaseModel):
    """Agent decision output model."""

    decision: DecisionType = Field(..., description="Decision type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")

    # Mapping information
    mapped_project: Optional[str] = Field(None, description="Mapped project ID if applicable")
    mapped_issue: Optional[str] = Field(None, description="Mapped issue ID if applicable")
    consolidate_with: List[str] = Field(default_factory=list, description="Project IDs to consolidate with")

    # Explanation
    reasoning: str = Field(..., description="Clear explanation of decision")
    suggested_action: str = Field(..., description="What the user should do")

    # Scoring
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Alignment with mapache.app (0.0-1.0)")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Domain tags")
    blocking_issues: List[str] = Field(default_factory=list, description="Blocking issue IDs")
    clarification_questions: List[str] = Field(default_factory=list, description="Questions to ask user")

    # Audit
    created_at: datetime = Field(default_factory=datetime.now, description="Decision timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "add",
                "confidence": 0.95,
                "reasoning": "Slack MCP is a planned SaaS integration. Valid mapache.app work.",
                "suggested_action": "Create MAPAI project: 'Slack MCP Server Implementation'",
                "alignment_score": 0.95,
                "tags": ["saaS_integrations", "mcp"]
            }
        }


class AgentResponse(BaseModel):
    """Complete agent response including decision and metadata."""

    decision: DecisionType
    confidence: float
    mapped_project: Optional[str] = None
    mapped_issue: Optional[str] = None
    consolidate_with: List[str] = Field(default_factory=list)
    reasoning: str
    suggested_action: str
    alignment_score: float
    tags: List[str] = Field(default_factory=list)
    blocking_issues: List[str] = Field(default_factory=list)
    clarification_questions: List[str] = Field(default_factory=list)

    # Processing metadata
    processing_time_ms: Optional[float] = None
    agent_version: str = "1.0.0"

    @classmethod
    def from_decision(cls, decision: Decision, processing_time_ms: float = None):
        """Create response from decision."""
        return cls(
            decision=decision.decision,
            confidence=decision.confidence,
            mapped_project=decision.mapped_project,
            mapped_issue=decision.mapped_issue,
            consolidate_with=decision.consolidate_with,
            reasoning=decision.reasoning,
            suggested_action=decision.suggested_action,
            alignment_score=decision.alignment_score,
            tags=decision.tags,
            blocking_issues=decision.blocking_issues,
            clarification_questions=decision.clarification_questions,
            processing_time_ms=processing_time_ms
        )
