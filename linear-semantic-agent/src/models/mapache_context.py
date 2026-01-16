"""
Embedded mapache.app context for semantic understanding.
This is the business domain knowledge that guides all decisions.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class MapacheContext:
    """Embedded mapache.app context for decision-making."""

    # What mapache.app IS
    MAPACHE_DEFINITION = {
        "name": "mapache.app",
        "description": "AI Operating System for SaaS orchestration via conversation",
        "core_value": "Unified interface for all connected tools + System of Intelligence",
        "current_stage": "MVP",
        "founder": "solo",
        "tech_stack": ["Google ADK", "Vertex AI", "Composio", "A2UI", "A2A protocol"]
    }

    # Project domains (✅ ADD TO LINEAR)
    VALID_DOMAINS = {
        "core_platform": [
            "Agent Runtime", "Linear Integration", "GitHub Integration",
            "A2UI", "Composio", "A2A protocol", "Vertex AI"
        ],
        "saaS_integrations": [
            "Slack MCP", "HubSpot MCP", "Stripe MCP", "Google Cloud MCP",
            "Linear MCP", "GitHub MCP", "MCP server"
        ],
        "intelligence_features": [
            "Semantic Search", "Gap Detection", "Duplication Detection",
            "Insights", "Embeddings", "RAG", "System of Intelligence"
        ],
        "internal_ops": [
            "Infrastructure", "Development Setup", "Async Coding",
            "Dependency Management", "GCP", "Deployment", "Docker", "Kubernetes"
        ]
    }

    # Filter rules (❌ FILTER OUT)
    FILTER_OUT_RULES = {
        "personal_household": [
            "shopping", "furniture", "renovation", "home maintenance",
            "curtain", "door", "awning", "landscaping", "household"
        ],
        "learning_experiments": [
            "try out", "explore", "experiment", "learning", "study",
            "evaluate (for personal use)", "proof-of-concept (non-mapache)"
        ],
        "deprecated_platforms": [
            "mapache.solutions", "renovate bot (completed)",
            "old n8n", "asana", "monday.com", "clickup (migrated)"
        ],
        "generic_vague": [
            "untitled", "thing", "fix stuff", "[empty description]",
            "improve stuff", "tbd"
        ],
        "outside_scope": [
            "general productivity", "meditation", "well-being",
            "digital detox", "phone addiction", "personal finance",
            "subscriptions (personal)"
        ]
    }

    # Keywords that indicate valid mapache work
    MAPACHE_KEYWORDS = [
        "agent", "mcp", "a2ui", "a2a", "integration", "composio", "vertex ai",
        "linear semantic", "github mcp", "system of intelligence", "sub-agent",
        "deployment", "gcp", "firestore", "embeddings", "rag", "conversational",
        "oauth", "saaS", "orchestration", "chief agent", "runtime", "gemini",
        "semantic", "duplicate detection", "gap detection", "slack", "hubspot"
    ]

    # Keywords that indicate filter-out work
    FILTER_OUT_KEYWORDS = [
        "personal", "learning", "experiment (non-mapache)", "try",
        "shopping", "household", "meditation", "well-being", "todo (non-work)",
        "n8n (old)", "asana", "monday.com", "jira (not planned)",
        "furniture", "renovation", "home", "family", "hobby"
    ]

    # Red flags that reduce score
    RED_FLAGS = [
        "is this valid?",
        "[empty description]",
        "figure out",
        "not sure",
        "maybe",
        "digital well-being",
        "personal task",
        "home improvement",
        "shopping list"
    ]

    @staticmethod
    def is_valid_mapache_work(task_description: str) -> bool:
        """Check if task aligns with mapache.app"""
        description_lower = task_description.lower()

        # Check for mapache keywords
        mapache_score = sum(1 for kw in MapacheContext.MAPACHE_KEYWORDS if kw in description_lower)

        # Check for filter keywords
        filter_score = sum(1 for kw in MapacheContext.FILTER_OUT_KEYWORDS if kw in description_lower)

        # Check for red flags
        has_red_flags = any(flag in description_lower for flag in MapacheContext.RED_FLAGS)

        # Decision logic
        if has_red_flags or filter_score > 0:
            return False
        if mapache_score > 0:
            return True

        return False

    @staticmethod
    def get_domain(task_description: str) -> Optional[str]:
        """Identify domain: core_platform, saaS_integrations, intelligence_features, internal_ops, invalid"""
        description_lower = task_description.lower()

        # Check each domain
        for domain, keywords in MapacheContext.VALID_DOMAINS.items():
            if any(kw.lower() in description_lower for kw in keywords):
                return domain

        return None

    @staticmethod
    def get_filter_category(task_description: str) -> Optional[str]:
        """Return filter category if applies (personal, learning, deprecated, etc.)"""
        description_lower = task_description.lower()

        for category, keywords in MapacheContext.FILTER_OUT_RULES.items():
            if any(kw.lower() in description_lower for kw in keywords):
                return category

        return None

    @staticmethod
    def get_tags(task_description: str) -> List[str]:
        """Extract relevant tags from task description."""
        tags = []
        description_lower = task_description.lower()

        # Domain tags
        domain = MapacheContext.get_domain(description_lower)
        if domain:
            tags.append(domain)

        # Technology tags
        tech_tags = {
            "mcp": ["mcp", "model context protocol"],
            "agent": ["agent", "sub-agent"],
            "a2ui": ["a2ui", "user interface"],
            "integration": ["integration", "oauth"],
            "embeddings": ["embeddings", "semantic", "rag"],
            "deployment": ["deployment", "docker", "kubernetes"],
            "gcp": ["gcp", "google cloud", "vertex ai"]
        }

        for tag, keywords in tech_tags.items():
            if any(kw in description_lower for kw in keywords):
                tags.append(tag)

        return list(set(tags))

    @staticmethod
    def get_confidence_modifier(task_description: str) -> float:
        """Get confidence modifier based on description quality and red flags."""
        description = task_description.strip()

        # Empty or very short descriptions
        if len(description) < 10:
            return 0.3

        # Check for red flags
        has_red_flags = any(flag in description.lower() for flag in MapacheContext.RED_FLAGS)
        if has_red_flags:
            return 0.5

        # Check for clarity indicators
        clarity_indicators = ["implement", "build", "create", "deploy", "setup", "configure"]
        has_clarity = any(ind in description.lower() for ind in clarity_indicators)

        # Check for vague indicators
        vague_indicators = ["maybe", "possibly", "think about", "consider", "explore"]
        has_vague = any(ind in description.lower() for ind in vague_indicators)

        if has_clarity and not has_vague:
            return 1.0
        elif has_vague:
            return 0.6
        else:
            return 0.8
