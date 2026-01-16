"""
Firestore client for caching and state management.
Stores projects, embeddings, decisions, and agent state.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import hashlib
import numpy as np
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from src.config.settings import settings
from src.config.constants import (
    CACHE_TTL_PROJECTS,
    CACHE_TTL_EMBEDDINGS,
    CACHE_TTL_DECISIONS
)
from src.models.project import LinearProject, LinearIssue
from src.models.decision import Decision
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FirestoreClient:
    """Client for Firestore operations."""

    def __init__(self):
        """Initialize Firestore client."""
        self.db = firestore.Client(
            project=settings.gcp_project_id,
            database=settings.firestore_database_id
        )
        self.prefix = settings.firestore_collection_prefix

        # Collection references
        self.projects_col = self.db.collection(f"{self.prefix}projects")
        self.embeddings_col = self.db.collection(f"{self.prefix}embeddings")
        self.decisions_col = self.db.collection(f"{self.prefix}decisions")
        self.agent_state_col = self.db.collection(f"{self.prefix}agent_state")

        logger.info("Firestore client initialized", project=settings.gcp_project_id)

    # --- Projects Cache ---

    async def cache_projects(self, projects: List[LinearProject]) -> None:
        """
        Cache Linear projects in Firestore.

        Args:
            projects: List of Linear projects to cache
        """
        batch = self.db.batch()
        cached_at = datetime.now()

        for project in projects:
            doc_ref = self.projects_col.document(project.id)

            data = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "team": project.team,
                "status": project.status,
                "alignment_score": project.alignment_score,
                "domain": project.domain,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "cached_at": cached_at,
                "embedding": project.embedding,
                "raw_data": project.raw_data
            }

            batch.set(doc_ref, data)

        batch.commit()
        logger.info("Cached projects", count=len(projects))

    async def get_cached_projects(self, max_age_seconds: int = CACHE_TTL_PROJECTS) -> List[LinearProject]:
        """
        Get cached projects if not expired.

        Args:
            max_age_seconds: Maximum age in seconds

        Returns:
            List of cached projects, empty if expired
        """
        cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)

        query = self.projects_col.where(
            filter=FieldFilter("cached_at", ">=", cutoff_time)
        )

        docs = query.stream()
        projects = []

        for doc in docs:
            data = doc.to_dict()
            project = LinearProject(
                id=data["id"],
                name=data["name"],
                description=data.get("description"),
                team=data.get("team"),
                status=data.get("status"),
                lead=data.get("lead"),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                cached_at=data.get("cached_at"),
                embedding=data.get("embedding"),
                alignment_score=data.get("alignment_score"),
                domain=data.get("domain"),
                raw_data=data.get("raw_data", {})
            )
            projects.append(project)

        logger.info("Retrieved cached projects", count=len(projects))
        return projects

    async def get_project_by_id(self, project_id: str) -> Optional[LinearProject]:
        """
        Get project by ID from cache.

        Args:
            project_id: Linear project ID

        Returns:
            Project if found, None otherwise
        """
        doc = self.projects_col.document(project_id).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        return LinearProject(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            team=data.get("team"),
            status=data.get("status"),
            embedding=data.get("embedding"),
            alignment_score=data.get("alignment_score"),
            domain=data.get("domain"),
            raw_data=data.get("raw_data", {})
        )

    # --- Embeddings Cache ---

    def _hash_text(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.sha256(text.encode()).hexdigest()

    async def store_embedding(self, text: str, embedding: np.ndarray) -> None:
        """
        Store text embedding in cache.

        Args:
            text: Original text
            embedding: Embedding vector
        """
        text_hash = self._hash_text(text)
        doc_ref = self.embeddings_col.document(text_hash)

        data = {
            "text": text,
            "embedding": embedding.tolist(),
            "dimension": len(embedding),
            "model": settings.embeddings_model,
            "created_at": datetime.now(),
            "ttl_seconds": CACHE_TTL_EMBEDDINGS
        }

        doc_ref.set(data)
        logger.debug("Stored embedding", text_hash=text_hash)

    async def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get cached embedding for text.

        Args:
            text: Original text

        Returns:
            Embedding vector if found, None otherwise
        """
        text_hash = self._hash_text(text)
        doc = self.embeddings_col.document(text_hash).get()

        if not doc.exists:
            return None

        data = doc.to_dict()

        # Check TTL
        created_at = data.get("created_at")
        ttl_seconds = data.get("ttl_seconds", CACHE_TTL_EMBEDDINGS)

        if created_at:
            age = (datetime.now() - created_at).total_seconds()
            if age > ttl_seconds:
                # Expired
                return None

        embedding_list = data.get("embedding")
        if embedding_list:
            return np.array(embedding_list)

        return None

    # --- Decisions Storage ---

    async def store_decision(self, decision: Decision, task_id: str, task_description: str, source: str) -> None:
        """
        Store agent decision for audit.

        Args:
            decision: Decision object
            task_id: Task ID from source
            task_description: Task description
            source: Source system
        """
        doc_ref = self.decisions_col.document()

        data = {
            "task_id": task_id,
            "task_description": task_description,
            "source": source,
            "decision": decision.decision.value,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "mapped_project_id": decision.mapped_project,
            "consolidate_with": decision.consolidate_with,
            "alignment_score": decision.alignment_score,
            "tags": decision.tags,
            "created_at": datetime.now()
        }

        doc_ref.set(data)
        logger.info("Stored decision", task_id=task_id, decision=decision.decision.value)

    # --- Agent State ---

    async def update_agent_state(self, state: Dict[str, Any]) -> None:
        """
        Update agent state document.

        Args:
            state: State dictionary
        """
        doc_ref = self.agent_state_col.document("current")

        state["last_updated"] = datetime.now()
        doc_ref.set(state, merge=True)

        logger.debug("Updated agent state", keys=list(state.keys()))

    async def get_agent_state(self) -> Dict[str, Any]:
        """
        Get current agent state.

        Returns:
            State dictionary
        """
        doc = self.agent_state_col.document("current").get()

        if doc.exists:
            return doc.to_dict()

        return {}

    # --- Search ---

    async def search_projects(self, query: str, limit: int = 10) -> List[LinearProject]:
        """
        Search projects by query string (basic text match).

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching projects
        """
        # Note: This is a basic implementation
        # For production, use Vertex AI Search or full-text search
        query_lower = query.lower()

        all_docs = self.projects_col.limit(100).stream()
        matches = []

        for doc in all_docs:
            data = doc.to_dict()
            name = data.get("name", "").lower()
            description = data.get("description", "").lower()

            if query_lower in name or query_lower in description:
                project = LinearProject(
                    id=data["id"],
                    name=data["name"],
                    description=data.get("description"),
                    team=data.get("team"),
                    status=data.get("status"),
                    embedding=data.get("embedding"),
                    alignment_score=data.get("alignment_score"),
                    domain=data.get("domain"),
                    raw_data=data.get("raw_data", {})
                )
                matches.append(project)

                if len(matches) >= limit:
                    break

        logger.info("Search results", query=query, count=len(matches))
        return matches
