"""
Similarity matching utilities using cosine similarity.
"""

import numpy as np
from typing import List, Tuple
from src.config.constants import (
    SIMILARITY_THRESHOLD_MATCH,
    SIMILARITY_THRESHOLD_DUPLICATE,
    SIMILARITY_THRESHOLD_EXACT
)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Similarity score between 0.0 and 1.0
    """
    if vec1 is None or vec2 is None:
        return 0.0

    if len(vec1) == 0 or len(vec2) == 0:
        return 0.0

    # Normalize vectors
    vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
    vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)

    # Compute cosine similarity
    similarity = np.dot(vec1_norm, vec2_norm)

    # Clip to [0, 1] range
    return float(np.clip(similarity, 0.0, 1.0))


def find_most_similar(
    query_embedding: np.ndarray,
    candidate_embeddings: List[np.ndarray],
    threshold: float = SIMILARITY_THRESHOLD_MATCH
) -> List[Tuple[int, float]]:
    """
    Find most similar embeddings above threshold.

    Args:
        query_embedding: Query vector
        candidate_embeddings: List of candidate vectors
        threshold: Minimum similarity threshold

    Returns:
        List of (index, similarity_score) tuples, sorted by score descending
    """
    if query_embedding is None or not candidate_embeddings:
        return []

    similarities = []
    for idx, candidate in enumerate(candidate_embeddings):
        if candidate is not None:
            score = cosine_similarity(query_embedding, candidate)
            if score >= threshold:
                similarities.append((idx, score))

    # Sort by score descending
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities


def is_duplicate(similarity_score: float) -> bool:
    """Check if similarity score indicates a duplicate."""
    return similarity_score >= SIMILARITY_THRESHOLD_DUPLICATE


def is_exact_duplicate(similarity_score: float) -> bool:
    """Check if similarity score indicates an exact duplicate."""
    return similarity_score >= SIMILARITY_THRESHOLD_EXACT


def is_related(similarity_score: float) -> bool:
    """Check if similarity score indicates related content."""
    return similarity_score >= SIMILARITY_THRESHOLD_MATCH


def get_match_confidence(similarity_score: float) -> float:
    """
    Convert similarity score to confidence level.

    Args:
        similarity_score: Cosine similarity (0.0-1.0)

    Returns:
        Confidence level (0.0-1.0)
    """
    if similarity_score >= SIMILARITY_THRESHOLD_EXACT:
        return 0.95
    elif similarity_score >= SIMILARITY_THRESHOLD_DUPLICATE:
        return 0.85
    elif similarity_score >= SIMILARITY_THRESHOLD_MATCH:
        return 0.75
    else:
        # Linear interpolation for lower scores
        return similarity_score * 0.75
