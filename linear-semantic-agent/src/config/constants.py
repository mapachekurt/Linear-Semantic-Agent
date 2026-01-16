"""
Magic numbers, thresholds, and configuration constants.
"""

# Similarity Thresholds
SIMILARITY_THRESHOLD_MATCH = 0.75          # Consider as related project
SIMILARITY_THRESHOLD_DUPLICATE = 0.80      # Suggest consolidation
SIMILARITY_THRESHOLD_EXACT = 0.90          # Definitely a duplicate

# Confidence Thresholds
CONFIDENCE_MIN = 0.60                      # Minimum to make any decision
CONFIDENCE_FILTER = 0.40                   # Below this → filter out
CONFIDENCE_CONSOLIDATE = 0.75              # Above this → suggest consolidate

# Scoring Weights (must sum to 1.0)
SCORE_WEIGHT_CONTEXT = 0.40                # Does it fit mapache domain?
SCORE_WEIGHT_SIMILARITY = 0.30             # How similar to existing projects?
SCORE_WEIGHT_CLARITY = 0.20                # How clear is the description?
SCORE_WEIGHT_RED_FLAGS = 0.10              # Any red flags present?

# Alignment Scoring
ALIGNMENT_SCORE_MIN = 0.0                  # Not mapache work
ALIGNMENT_SCORE_MAX = 1.0                  # Definitely mapache work
ALIGNMENT_SCORE_THRESHOLD = 0.75           # Recommend "add" if >= this

# Caching
CACHE_TTL_PROJECTS = 3600                  # 1 hour
CACHE_TTL_EMBEDDINGS = 2592000             # 30 days
CACHE_TTL_DECISIONS = 604800               # 7 days

# API Limits
VERTEX_AI_BATCH_SIZE = 100                 # Max texts per embedding batch
VERTEX_AI_QPM = 1000                       # Queries per minute limit

# Linear MCP
LINEAR_MAX_RETRIES = 3
LINEAR_TIMEOUT_SECONDS = 30
LINEAR_BATCH_SIZE = 50                     # Projects per API call

# Text Processing
MIN_DESCRIPTION_LENGTH = 10                # Characters
MAX_DESCRIPTION_LENGTH = 5000              # Characters
MIN_TITLE_LENGTH = 3                       # Characters

# Decision Rules
DECISION_ENUM = ["add", "filter", "consolidate", "clarify"]
