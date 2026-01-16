"""
Tests for similarity matching.
"""

import pytest
import numpy as np
from src.utils.similarity import (
    cosine_similarity,
    find_most_similar,
    is_duplicate,
    is_exact_duplicate,
    is_related
)


class TestCosineSimilarity:
    """Tests for cosine similarity calculation."""

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical vectors."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.0, 2.0, 3.0])

        similarity = cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])

        similarity = cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0, abs=0.01)

    def test_cosine_similarity_similar(self):
        """Test cosine similarity of similar vectors."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.1, 2.1, 2.9])

        similarity = cosine_similarity(vec1, vec2)
        assert 0.9 < similarity < 1.0


class TestFindMostSimilar:
    """Tests for finding most similar vectors."""

    def test_find_most_similar_above_threshold(self):
        """Test finding vectors above threshold."""
        query = np.array([1.0, 2.0, 3.0])
        candidates = [
            np.array([1.0, 2.0, 3.0]),  # Very similar
            np.array([0.0, 0.0, 1.0]),  # Different
            np.array([1.1, 2.1, 2.9])   # Similar
        ]

        matches = find_most_similar(query, candidates, threshold=0.75)

        assert len(matches) >= 1, "Should find at least one match"
        assert matches[0][1] > 0.95, "First match should be highest similarity"


class TestThresholdFunctions:
    """Tests for threshold-based functions."""

    def test_is_duplicate(self):
        """Test duplicate detection."""
        assert is_duplicate(0.85) is True
        assert is_duplicate(0.75) is False

    def test_is_exact_duplicate(self):
        """Test exact duplicate detection."""
        assert is_exact_duplicate(0.95) is True
        assert is_exact_duplicate(0.85) is False

    def test_is_related(self):
        """Test related content detection."""
        assert is_related(0.80) is True
        assert is_related(0.70) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
