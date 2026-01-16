"""
Semantic reasoning engine.
Core decision logic using mapache.app context and similarity matching.
"""

from typing import List, Tuple, Optional
import numpy as np

from src.models.task import Task
from src.models.project import LinearProject, Match
from src.models.decision import Decision, DecisionType
from src.models.mapache_context import MapacheContext
from src.config.constants import (
    SIMILARITY_THRESHOLD_MATCH,
    SIMILARITY_THRESHOLD_DUPLICATE,
    SCORE_WEIGHT_CONTEXT,
    SCORE_WEIGHT_SIMILARITY,
    SCORE_WEIGHT_CLARITY,
    SCORE_WEIGHT_RED_FLAGS,
    ALIGNMENT_SCORE_THRESHOLD,
    CONFIDENCE_FILTER,
    MIN_DESCRIPTION_LENGTH
)
from src.utils.similarity import cosine_similarity, find_most_similar
from src.utils.text_processing import (
    normalize_text,
    is_empty_or_vague,
    extract_keywords,
    extract_project_indicators
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReasoningEngine:
    """Semantic reasoning engine for task evaluation."""

    def __init__(self):
        """Initialize reasoning engine."""
        self.context = MapacheContext()
        logger.info("Reasoning engine initialized")

    async def evaluate(
        self,
        task: Task,
        task_embedding: np.ndarray,
        existing_projects: List[LinearProject]
    ) -> Decision:
        """
        Evaluate task and make decision.

        Args:
            task: Task to evaluate
            task_embedding: Task embedding vector
            existing_projects: List of existing Linear projects

        Returns:
            Decision object
        """
        logger.info("Evaluating task", task_id=task.task_id, source=task.source)

        # Step 1: Normalize task
        normalized_desc = normalize_text(task.task_description)

        # Step 2: Filter by context (is it mapache work?)
        filter_score = self.filter_score(task)
        logger.debug("Filter score", score=filter_score)

        if filter_score < CONFIDENCE_FILTER:
            return self._create_filter_decision(task, filter_score)

        # Step 3: Check clarity
        clarity_score = self.clarity_score(task)
        logger.debug("Clarity score", score=clarity_score)

        if clarity_score < 0.4:
            return self._create_clarify_decision(task, clarity_score)

        # Step 4: Similarity matching
        matches = self._find_similar_projects(task_embedding, existing_projects)
        logger.debug("Found matches", count=len(matches))

        # Step 5: Duplicate detection
        if matches:
            best_match = matches[0]
            duplicate_score = self.duplicate_score(task, best_match.project, best_match.similarity_score)
            logger.debug("Duplicate score", score=duplicate_score, best_similarity=best_match.similarity_score)

            if duplicate_score >= 0.75:
                return self._create_consolidate_decision(task, matches, duplicate_score)

        # Step 6: Alignment scoring
        alignment_score = self.alignment_score(
            filter_score,
            matches[0].similarity_score if matches else 0.0,
            clarity_score
        )
        logger.debug("Alignment score", score=alignment_score)

        # Step 7: Make decision
        if alignment_score >= ALIGNMENT_SCORE_THRESHOLD:
            return self._create_add_decision(task, matches, alignment_score, filter_score, clarity_score)
        else:
            return self._create_clarify_decision(task, clarity_score)

    def filter_score(self, task: Task) -> float:
        """
        Calculate filter score (0.0 = definitely not mapache, 1.0 = definitely mapache).

        Args:
            task: Task to evaluate

        Returns:
            Filter score (0.0-1.0)
        """
        description_lower = task.task_description.lower()

        # Check for filter-out categories
        filter_category = self.context.get_filter_category(description_lower)
        if filter_category:
            logger.debug("Filter category detected", category=filter_category)
            return 0.1  # Strong signal to filter out

        # Check for mapache keywords
        mapache_count = sum(1 for kw in self.context.MAPACHE_KEYWORDS if kw in description_lower)

        # Check for filter keywords
        filter_count = sum(1 for kw in self.context.FILTER_OUT_KEYWORDS if kw in description_lower)

        # Check for red flags
        red_flag_count = sum(1 for flag in self.context.RED_FLAGS if flag in description_lower)

        # Calculate score
        base_score = 0.5

        # Positive signals
        base_score += min(mapache_count * 0.1, 0.4)

        # Negative signals
        base_score -= filter_count * 0.2
        base_score -= red_flag_count * 0.15

        # Check for project indicators
        indicators = extract_project_indicators(description_lower)
        base_score += len(indicators) * 0.05

        return max(0.0, min(1.0, base_score))

    def duplicate_score(
        self,
        task: Task,
        existing_project: LinearProject,
        similarity: float
    ) -> float:
        """
        Calculate duplicate score (0.0 = completely different, 1.0 = exact duplicate).

        Args:
            task: Task to evaluate
            existing_project: Existing project to compare
            similarity: Cosine similarity score

        Returns:
            Duplicate score (0.0-1.0)
        """
        # Base on similarity
        base_score = similarity

        # Check title/name similarity
        task_keywords = set(extract_keywords(task.task_description))
        project_keywords = set(extract_keywords(existing_project.name))

        if existing_project.description:
            project_keywords.update(extract_keywords(existing_project.description))

        # Keyword overlap
        if task_keywords and project_keywords:
            overlap = len(task_keywords & project_keywords) / len(task_keywords | project_keywords)
            base_score = (base_score + overlap) / 2

        return base_score

    def clarity_score(self, task: Task) -> float:
        """
        Calculate clarity score (0.0 = empty/nonsensical, 1.0 = clear with criteria).

        Args:
            task: Task to evaluate

        Returns:
            Clarity score (0.0-1.0)
        """
        description = task.task_description.strip()

        # Empty or very short
        if len(description) < MIN_DESCRIPTION_LENGTH:
            return 0.2

        # Check if vague
        if is_empty_or_vague(description):
            return 0.3

        # Check for clarity indicators
        clarity_indicators = [
            'implement', 'build', 'create', 'deploy', 'setup', 'configure',
            'add', 'remove', 'update', 'fix', 'optimize', 'integrate'
        ]
        has_clarity = any(ind in description.lower() for ind in clarity_indicators)

        # Check for vague indicators
        vague_indicators = ['maybe', 'possibly', 'think about', 'consider', 'explore']
        has_vague = any(ind in description.lower() for ind in vague_indicators)

        # Check length
        length_score = min(len(description) / 200, 1.0)  # Normalize to 200 chars

        # Calculate final score
        base_score = length_score

        if has_clarity:
            base_score += 0.3
        if has_vague:
            base_score -= 0.2

        # Check for details (acceptance criteria, technical terms)
        technical_terms = ['api', 'database', 'service', 'endpoint', 'component', 'module']
        has_technical = any(term in description.lower() for term in technical_terms)
        if has_technical:
            base_score += 0.1

        return max(0.0, min(1.0, base_score))

    def alignment_score(
        self,
        filter_s: float,
        similarity_s: float,
        clarity_s: float
    ) -> float:
        """
        Calculate weighted alignment score.

        Args:
            filter_s: Filter score
            similarity_s: Best similarity score
            clarity_s: Clarity score

        Returns:
            Alignment score (0.0-1.0)
        """
        # Red flags component
        red_flags_s = 1.0  # Assume no red flags for now (already accounted in filter_s)

        # Weighted combination
        alignment = (
            SCORE_WEIGHT_CONTEXT * filter_s +
            SCORE_WEIGHT_SIMILARITY * similarity_s +
            SCORE_WEIGHT_CLARITY * clarity_s +
            SCORE_WEIGHT_RED_FLAGS * red_flags_s
        )

        return max(0.0, min(1.0, alignment))

    def _find_similar_projects(
        self,
        task_embedding: np.ndarray,
        projects: List[LinearProject]
    ) -> List[Match]:
        """Find similar projects using embeddings."""
        if not projects:
            return []

        # Get project embeddings
        project_embeddings = []
        valid_projects = []

        for project in projects:
            if project.embedding:
                project_embeddings.append(np.array(project.embedding))
                valid_projects.append(project)

        if not project_embeddings:
            return []

        # Find similar
        similar_indices = find_most_similar(
            task_embedding,
            project_embeddings,
            threshold=SIMILARITY_THRESHOLD_MATCH
        )

        # Create matches
        matches = []
        for idx, score in similar_indices[:5]:  # Top 5
            match = Match(
                project=valid_projects[idx],
                similarity_score=score,
                match_reason=f"Semantic similarity: {score:.2f}"
            )
            matches.append(match)

        return matches

    def _create_add_decision(
        self,
        task: Task,
        matches: List[Match],
        alignment_score: float,
        filter_score: float,
        clarity_score: float
    ) -> Decision:
        """Create ADD decision."""
        # Generate reasoning
        reasoning = f"This task aligns with mapache.app work (alignment: {alignment_score:.2f}). "

        if matches:
            reasoning += f"Found {len(matches)} related project(s), but no strong duplicate. "

        # Determine tags
        tags = self.context.get_tags(task.task_description)

        # Suggested action
        domain = self.context.get_domain(task.task_description)
        action = f"Create new Linear project/issue"
        if domain:
            action += f" in domain: {domain}"

        return Decision(
            decision=DecisionType.ADD,
            confidence=min(alignment_score + 0.1, 1.0),
            reasoning=reasoning,
            suggested_action=action,
            alignment_score=alignment_score,
            tags=tags,
            mapped_project=matches[0].project.id if matches else None
        )

    def _create_filter_decision(self, task: Task, filter_score: float) -> Decision:
        """Create FILTER decision."""
        filter_category = self.context.get_filter_category(task.task_description)

        reasoning = f"This task does not align with mapache.app work (score: {filter_score:.2f}). "
        if filter_category:
            reasoning += f"Detected category: {filter_category}. "

        reasoning += "Not suitable for Linear."

        return Decision(
            decision=DecisionType.FILTER,
            confidence=1.0 - filter_score,
            reasoning=reasoning,
            suggested_action="Archive this task. Store personal tasks in Google Tasks instead.",
            alignment_score=filter_score,
            tags=[filter_category] if filter_category else ["not_mapache"]
        )

    def _create_consolidate_decision(
        self,
        task: Task,
        matches: List[Match],
        duplicate_score: float
    ) -> Decision:
        """Create CONSOLIDATE decision."""
        best_match = matches[0]

        reasoning = (
            f"This task is {best_match.similarity_score:.0%} similar to existing project "
            f"'{best_match.project.name}' (ID: {best_match.project.id}). "
            f"Suggest consolidating instead of creating duplicate."
        )

        consolidate_with = [m.project.id for m in matches[:3]]

        return Decision(
            decision=DecisionType.CONSOLIDATE,
            confidence=duplicate_score,
            mapped_project=best_match.project.id,
            consolidate_with=consolidate_with,
            reasoning=reasoning,
            suggested_action=f"Link to existing project {best_match.project.id} instead of creating new",
            alignment_score=0.90,
            tags=self.context.get_tags(task.task_description)
        )

    def _create_clarify_decision(self, task: Task, clarity_score: float) -> Decision:
        """Create CLARIFY decision."""
        reasoning = f"Task description needs clarification (clarity: {clarity_score:.2f}). "

        questions = []

        if len(task.task_description) < 20:
            questions.append("Can you provide more details about what needs to be done?")

        if not extract_keywords(task.task_description):
            questions.append("What is the specific goal or expected outcome?")

        domain = self.context.get_domain(task.task_description)
        if not domain:
            questions.append(
                "Which mapache.app component does this relate to? "
                "(core platform, SaaS integration, intelligence features, or internal ops)"
            )

        if not questions:
            questions.append("Please provide more context about this task.")

        return Decision(
            decision=DecisionType.CLARIFY,
            confidence=0.3 + clarity_score * 0.3,
            reasoning=reasoning,
            suggested_action="Ask user for clarification",
            alignment_score=0.5,
            tags=["needs_clarification"],
            clarification_questions=questions
        )
