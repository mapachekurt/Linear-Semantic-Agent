"""
Text normalization and processing utilities.
"""

import re
from typing import List, Set


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison and embedding.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.

    Args:
        text: Input text
        min_length: Minimum keyword length

    Returns:
        List of keywords
    """
    if not text:
        return []

    # Normalize
    text = normalize_text(text)

    # Remove common stop words
    stop_words = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
        'in', 'with', 'to', 'for', 'of', 'as', 'by', 'this', 'that',
        'from', 'be', 'are', 'was', 'were', 'been', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should'
    }

    # Split into words
    words = re.findall(r'\b\w+\b', text)

    # Filter keywords
    keywords = [
        word for word in words
        if len(word) >= min_length and word not in stop_words
    ]

    return keywords


def is_empty_or_vague(text: str) -> bool:
    """
    Check if text is empty or too vague.

    Args:
        text: Input text

    Returns:
        True if empty or vague
    """
    if not text or len(text.strip()) < 10:
        return True

    vague_patterns = [
        r'^(thing|stuff|fix|improve|update)s?\s*$',
        r'^(untitled|tbd|todo)$',
        r'^\s*$'
    ]

    normalized = normalize_text(text)

    for pattern in vague_patterns:
        if re.match(pattern, normalized, re.IGNORECASE):
            return True

    return False


def clean_description(text: str) -> str:
    """
    Clean and format description text.

    Args:
        text: Input description

    Returns:
        Cleaned description
    """
    if not text:
        return ""

    # Remove markdown
    text = re.sub(r'[#*`_~]', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip
    text = text.strip()

    return text


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length-3] + "..."


def extract_project_indicators(text: str) -> Set[str]:
    """
    Extract indicators that suggest this is a project (vs personal task).

    Args:
        text: Input text

    Returns:
        Set of project indicators found
    """
    indicators = {
        'technical': ['api', 'server', 'database', 'deployment', 'integration', 'sdk', 'framework'],
        'business': ['customer', 'user', 'revenue', 'product', 'feature', 'requirement'],
        'development': ['implement', 'build', 'create', 'develop', 'deploy', 'setup', 'configure'],
        'architecture': ['system', 'architecture', 'design', 'component', 'service', 'infrastructure']
    }

    text_lower = text.lower()
    found_indicators = set()

    for category, terms in indicators.items():
        for term in terms:
            if term in text_lower:
                found_indicators.add(category)
                break

    return found_indicators
