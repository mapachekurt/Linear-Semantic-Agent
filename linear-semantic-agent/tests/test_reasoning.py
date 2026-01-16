"""
Tests for semantic reasoning engine.
"""

import pytest
from src.tools.reasoning import ReasoningEngine
from src.models.task import Task
from src.models.decision import DecisionType


@pytest.fixture
def reasoning_engine():
    """Create reasoning engine instance."""
    return ReasoningEngine()


class TestFilterScore:
    """Tests for filter scoring."""

    def test_filter_score_valid_mapache(self, reasoning_engine):
        """Test filter score for valid mapache work."""
        task = Task(
            task_id="TEST-001",
            task_description="Build Slack MCP server integration for mapache.app",
            source="clickup"
        )

        score = reasoning_engine.filter_score(task)
        assert score > 0.7, "Valid mapache work should have high filter score"

    def test_filter_score_personal_household(self, reasoning_engine):
        """Test filter score for personal household task."""
        task = Task(
            task_id="TEST-100",
            task_description="Buy curtain rods and door covers",
            source="google_tasks"
        )

        score = reasoning_engine.filter_score(task)
        assert score < 0.3, "Personal tasks should have low filter score"

    def test_filter_score_learning_experiment(self, reasoning_engine):
        """Test filter score for learning experiment."""
        task = Task(
            task_id="TEST-101",
            task_description="Learn Temporal.io workflow orchestration",
            source="clickup"
        )

        score = reasoning_engine.filter_score(task)
        assert score < 0.4, "Learning experiments should have low filter score"


class TestClarityScore:
    """Tests for clarity scoring."""

    def test_clarity_empty_description(self, reasoning_engine):
        """Test clarity score for empty description."""
        task = Task(
            task_id="TEST-200",
            task_description="",
            source="linear"
        )

        score = reasoning_engine.clarity_score(task)
        assert score < 0.3, "Empty description should have low clarity score"

    def test_clarity_vague_description(self, reasoning_engine):
        """Test clarity score for vague description."""
        task = Task(
            task_id="TEST-201",
            task_description="Fix stuff",
            source="clickup"
        )

        score = reasoning_engine.clarity_score(task)
        assert score < 0.5, "Vague description should have low clarity score"

    def test_clarity_detailed_description(self, reasoning_engine):
        """Test clarity score for detailed description."""
        task = Task(
            task_id="TEST-002",
            task_description="Implement semantic gap detection in Linear agent using "
                           "Vertex AI embeddings and Firestore caching with 0.75 threshold",
            source="linear"
        )

        score = reasoning_engine.clarity_score(task)
        assert score > 0.6, "Detailed description should have high clarity score"


class TestAlignmentScore:
    """Tests for alignment scoring."""

    def test_alignment_weighted_combination(self, reasoning_engine):
        """Test alignment score calculation."""
        filter_s = 0.8
        similarity_s = 0.7
        clarity_s = 0.9

        alignment = reasoning_engine.alignment_score(filter_s, similarity_s, clarity_s)

        # Should be weighted average
        assert 0.0 <= alignment <= 1.0
        assert alignment > 0.7, "High component scores should yield high alignment"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
