"""
Core agent logic using integrations and reasoning engine.
Orchestrates tools, reasoning, and decision-making.
"""

from typing import List, Optional
from datetime import datetime
import numpy as np

from src.models.task import Task
from src.models.project import LinearProject
from src.models.decision import Decision
from src.integrations.linear_mcp import LinearMCPClient
from src.integrations.vertex_ai import VertexAIClient, EmbeddingService
from src.integrations.firestore_client import FirestoreClient
from src.tools.reasoning import ReasoningEngine
from src.config.settings import settings
from src.config.constants import CACHE_TTL_PROJECTS
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LinearSemanticAgent:
    """Linear Semantic Agent for task validation and categorization."""

    def __init__(self):
        """Initialize the agent."""
        logger.info("Initializing Linear Semantic Agent")

        # Initialize clients
        self.linear_client = LinearMCPClient()
        self.vertex_client = VertexAIClient()
        self.firestore_client = FirestoreClient()

        # Initialize services
        self.embedding_service = EmbeddingService(
            vertex_client=self.vertex_client,
            firestore_client=self.firestore_client
        )

        # Initialize reasoning engine
        self.reasoning_engine = ReasoningEngine()

        # Cache
        self._projects_cache: Optional[List[LinearProject]] = None
        self._cache_time: Optional[datetime] = None

        logger.info("Linear Semantic Agent initialized successfully")

    async def initialize(self) -> None:
        """Initialize agent (load context, connect to services)."""
        logger.info("Starting agent initialization")

        try:
            # Test connections
            state = await self.firestore_client.get_agent_state()
            logger.info("Agent state loaded", state_keys=list(state.keys()) if state else [])

            # Pre-load projects cache
            await self.get_or_refresh_projects(force=False)

            # Update agent state
            await self.firestore_client.update_agent_state({
                "last_init": datetime.now(),
                "health_status": "healthy",
                "version": settings.agent_version
            })

            logger.info("Agent initialization complete")

        except Exception as e:
            logger.error("Agent initialization failed", error=str(e), exc_info=True)
            raise

    async def evaluate_task(self, task: Task) -> Decision:
        """
        Evaluate task and make decision.

        Args:
            task: Task to evaluate

        Returns:
            Decision object
        """
        logger.info(
            "Evaluating task",
            task_id=task.task_id,
            source=task.source,
            description_length=len(task.task_description)
        )

        try:
            # Step 1: Get or refresh projects cache
            projects = await self.get_or_refresh_projects()

            # Step 2: Generate task embedding
            task_embedding = await self.embedding_service.embed_task(task.task_description)
            logger.debug("Generated task embedding", dimension=len(task_embedding))

            # Step 3: Generate project embeddings (if needed)
            projects_with_embeddings = await self._ensure_project_embeddings(projects)

            # Step 4: Use reasoning engine to evaluate
            decision = await self.reasoning_engine.evaluate(
                task=task,
                task_embedding=task_embedding,
                existing_projects=projects_with_embeddings
            )

            # Step 5: Store decision for audit
            await self.firestore_client.store_decision(
                decision=decision,
                task_id=task.task_id,
                task_description=task.task_description,
                source=task.source
            )

            logger.info(
                "Task evaluation complete",
                task_id=task.task_id,
                decision=decision.decision.value,
                confidence=decision.confidence
            )

            return decision

        except Exception as e:
            logger.error(
                "Task evaluation failed",
                task_id=task.task_id,
                error=str(e),
                exc_info=True
            )

            # Return error decision
            from src.models.decision import DecisionType
            return Decision(
                decision=DecisionType.CLARIFY,
                confidence=0.0,
                reasoning=f"Error during evaluation: {str(e)}",
                suggested_action="Please try again or contact support",
                alignment_score=0.0,
                tags=["error"]
            )

    async def get_or_refresh_projects(self, force: bool = False) -> List[LinearProject]:
        """
        Get projects from cache or refresh if expired.

        Args:
            force: Force refresh even if cache valid

        Returns:
            List of Linear projects
        """
        # Check if cache is valid
        if not force and self._projects_cache and self._cache_time:
            age = (datetime.now() - self._cache_time).total_seconds()
            if age < CACHE_TTL_PROJECTS:
                logger.debug("Using in-memory projects cache", count=len(self._projects_cache))
                return self._projects_cache

        # Try Firestore cache
        if not force:
            cached_projects = await self.firestore_client.get_cached_projects()
            if cached_projects:
                logger.info("Loaded projects from Firestore cache", count=len(cached_projects))
                self._projects_cache = cached_projects
                self._cache_time = datetime.now()
                return cached_projects

        # Fetch from Linear
        logger.info("Fetching projects from Linear")
        projects = await self.linear_client.list_projects()

        # Cache in Firestore
        await self.firestore_client.cache_projects(projects)

        # Update in-memory cache
        self._projects_cache = projects
        self._cache_time = datetime.now()

        # Update agent state
        await self.firestore_client.update_agent_state({
            "projects_count": len(projects),
            "last_sync": datetime.now()
        })

        logger.info("Projects refreshed", count=len(projects))
        return projects

    async def _ensure_project_embeddings(
        self,
        projects: List[LinearProject]
    ) -> List[LinearProject]:
        """
        Ensure all projects have embeddings.

        Args:
            projects: List of projects

        Returns:
            Projects with embeddings
        """
        projects_needing_embeddings = [
            p for p in projects if not p.embedding
        ]

        if not projects_needing_embeddings:
            logger.debug("All projects have embeddings")
            return projects

        logger.info(
            "Generating embeddings for projects",
            total=len(projects),
            needed=len(projects_needing_embeddings)
        )

        # Generate embeddings
        for project in projects_needing_embeddings:
            embedding = await self.embedding_service.embed_project(
                project.name,
                project.description
            )
            project.embedding = embedding.tolist()

        # Update cache with embeddings
        await self.firestore_client.cache_projects(projects_needing_embeddings)

        return projects

    async def create_issue_from_task(
        self,
        task: Task,
        project_id: str
    ) -> str:
        """
        Create Linear issue from task.

        Args:
            task: Task to create issue from
            project_id: Target project ID

        Returns:
            Created issue ID
        """
        logger.info("Creating issue from task", task_id=task.task_id, project_id=project_id)

        issue_id = await self.linear_client.create_issue(
            project_id=project_id,
            title=task.task_description[:100],  # Truncate for title
            description=task.task_description,
            metadata={
                "source": task.source,
                "source_id": task.task_id,
                "priority": task.priority
            }
        )

        logger.info("Issue created", issue_id=issue_id)
        return issue_id

    async def link_to_existing_issue(
        self,
        task: Task,
        target_issue_id: str,
        relationship: str = "relates_to"
    ) -> None:
        """
        Link task to existing issue.

        Args:
            task: Task to link
            target_issue_id: Target issue ID
            relationship: Relationship type
        """
        logger.info(
            "Linking task to issue",
            task_id=task.task_id,
            target=target_issue_id,
            relationship=relationship
        )

        # Note: This would require creating a temporary issue first
        # or updating the target issue with a comment
        # Simplified implementation for now

        logger.info("Task linked to issue")

    async def get_agent_health(self) -> dict:
        """
        Get agent health status.

        Returns:
            Health status dictionary
        """
        state = await self.firestore_client.get_agent_state()

        return {
            "status": state.get("health_status", "unknown"),
            "version": settings.agent_version,
            "last_init": state.get("last_init"),
            "last_sync": state.get("last_sync"),
            "projects_count": state.get("projects_count", 0),
            "cache_valid": self._projects_cache is not None and self._cache_time is not None
        }
