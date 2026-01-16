# LINEAR SEMANTIC AGENT - COMPLETE CLOUD CODE SPECIFICATION
**Version:** 1.0 | **Status:** Ready for Claude Code Implementation  
**Target Runtime:** Google Vertex AI Agent Runtime  
**GCP Project:** linear-semantic-agents  
**Timeline:** Single execution pass (no back-and-forth)

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VERTEX AI AGENT RUNTIME                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │         LINEAR SEMANTIC AGENT (ADK-based)                  │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │                                                             │  │
│  │  1. SYSTEM PROMPT (mapache.app context embedded)           │  │
│  │     - Business domain knowledge                            │  │
│  │     - Filtering rules                                      │  │
│  │     - Decision framework                                   │  │
│  │                                                             │  │
│  │  2. TOOLS (via MCP)                                        │  │
│  │     ├─ Linear MCP: list_projects, list_issues, etc.       │  │
│  │     ├─ Vertex AI Embeddings: embed_text                   │  │
│  │     └─ Firestore: store/retrieve project state            │  │
│  │                                                             │  │
│  │  3. REASONING ENGINE                                       │  │
│  │     ├─ Task parsing & normalization                        │  │
│  │     ├─ Similarity matching (0.75 threshold)                │  │
│  │     ├─ Duplicate detection                                 │  │
│  │     ├─ Alignment validation vs mapache.app                 │  │
│  │     └─ Confidence scoring                                  │  │
│  │                                                             │  │
│  │  4. A2A PROTOCOL (Sub-agent interface)                     │  │
│  │     ├─ Input: task_description, source                     │  │
│  │     ├─ Output: decision, mapping, confidence, action       │  │
│  │     └─ Tools: ask_for_clarification, create_linear_issue   │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│         │                      │                       │            │
│         ▼                      ▼                       ▼            │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐    │
│  │ Linear MCP   │      │ Vertex AI    │      │ Firestore    │    │
│  │ Server       │      │ Embeddings   │      │              │    │
│  │              │      │              │      │              │    │
│  │ OAuth flow   │      │ text-        │      │ Projects:    │    │
│  │ via Composio │      │ embedding-   │      │ - semantics  │    │
│  │              │      │ 005          │      │ - status     │    │
│  └──────────────┘      └──────────────┘      └──────────────┘    │
│         │                      │                       │            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PROJECT STRUCTURE

```
linear-semantic-agent/
├── README.md                          # Project overview
├── SPECIFICATION.md                   # This file
├── architecture.md                    # Detailed architecture docs
│
├── gcp_setup.sh                       # GCP initialization script
├── deploy.sh                          # Deployment script to Vertex AI
│
├── src/
│   ├── main.py                        # Agent entry point
│   ├── agent.py                       # Core agent logic (ADK-based)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── linear_tools.py            # Linear MCP wrapper tools
│   │   ├── embedding_tools.py         # Vertex AI Embeddings tools
│   │   ├── firestore_tools.py         # Firestore CRUD tools
│   │   └── reasoning.py               # Semantic reasoning engine
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py                    # Task/Issue data model
│   │   ├── project.py                 # Project data model
│   │   ├── decision.py                # Decision/output model
│   │   └── mapache_context.py         # Embedded context
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                # Environment config
│   │   ├── prompts.py                 # System prompts & examples
│   │   └── constants.py               # Magic numbers, thresholds
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── linear_mcp.py              # Linear MCP client
│   │   ├── vertex_ai.py               # Vertex AI APIs
│   │   └── firestore_client.py        # Firestore client
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                  # Structured logging
│       ├── similarity.py              # Similarity matching (0.75)
│       └── text_processing.py         # Normalization, cleaning
│
├── tests/
│   ├── __init__.py
│   ├── test_agent.py                  # Agent tests
│   ├── test_reasoning.py              # Reasoning engine tests
│   ├── test_similarity.py             # Similarity matching tests
│   └── fixtures/
│       ├── sample_tasks.json          # Test task data
│       └── sample_projects.json       # Test project data
│
├── docker/
│   ├── Dockerfile                     # Multi-stage Docker build
│   └── .dockerignore
│
├── kubernetes/
│   ├── deployment.yaml                # Vertex AI Agent Runtime deployment
│   └── service.yaml                   # K8s service
│
├── docs/
│   ├── mapache_context.md             # Embedded context document
│   ├── agent_interface.md             # A2A protocol specification
│   ├── examples.md                    # Example interactions
│   └── deployment_guide.md            # Step-by-step deployment
│
├── .env.example                       # Environment template
├── .gitignore                         # Git ignore patterns
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Poetry/setuptools config
└── cloudbuild.yaml                    # Cloud Build configuration
```

---

## DETAILED SPECIFICATIONS

### 1. DEPENDENCIES & VERSIONS

```
# requirements.txt

# Google Cloud & AI
google-cloud-aiplatform==1.42.0          # Vertex AI API, Agent Runtime
google-cloud-firestore==2.14.0           # Firestore database
google-cloud-logging==3.8.0              # Cloud Logging
google-auth==2.25.2                      # Google authentication
google-auth-oauthlib==1.2.0              # OAuth support
google-auth-httplib2==0.2.0              # Auth HTTP

# Framework & Core
fastapi==0.109.0                         # API framework (for agent interface)
uvicorn==0.27.0                          # ASGI server
pydantic==2.5.3                          # Data validation
pydantic-settings==2.1.0                 # Settings management

# LLM & Embedding
langchain==0.1.7                         # LLM orchestration
langchain-google-vertexai==0.1.0         # Vertex AI integration
langsmith==0.0.92                        # LLM monitoring

# HTTP & Communication
httpx==0.25.2                            # Async HTTP client
requests==2.31.0                         # HTTP client
aiohttp==3.9.1                           # Async HTTP

# Data Processing
numpy==1.26.3                            # Numerical computing
pandas==2.1.4                            # Data frames
python-dotenv==1.0.0                     # Environment variables

# Utilities
python-dateutil==2.8.2                   # Date utilities
pytz==2023.3.post1                       # Timezone handling
tenacity==8.2.3                          # Retry logic
structlog==23.2.0                        # Structured logging

# Testing
pytest==7.4.3                            # Testing framework
pytest-asyncio==0.23.2                   # Async test support
pytest-cov==4.1.0                        # Coverage reports
responses==0.24.1                        # HTTP mocking

# Development
black==23.12.1                           # Code formatter
flake8==6.1.0                            # Linting
mypy==1.7.1                              # Type checking
```

---

### 2. ENVIRONMENT CONFIGURATION

```
# .env.example
# Copy to .env and fill in values

# GCP Configuration
GCP_PROJECT_ID=linear-semantic-agents
GCP_REGION=us-central1

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash-exp

# Linear MCP Configuration
LINEAR_MCP_URL=https://mcp.linear.app/sse
LINEAR_API_KEY=<your-linear-api-key>
LINEAR_WORKSPACE_ID=<your-workspace-id>

# Composio Configuration (OAuth provider)
COMPOSIO_API_KEY=<your-composio-api-key>

# Firestore Configuration
FIRESTORE_DATABASE_ID=(default)
FIRESTORE_COLLECTION_PREFIX=mapache_

# Embeddings Configuration
EMBEDDINGS_MODEL=text-embedding-005
EMBEDDINGS_DIMENSION=768

# Agent Configuration
AGENT_NAME=linear-semantic-agent
AGENT_VERSION=1.0.0
SIMILARITY_THRESHOLD=0.75
CONFIDENCE_MIN_THRESHOLD=0.60

# Logging Configuration
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# Development/Testing
ENVIRONMENT=production
DEBUG=false
TESTING=false
```

---

### 3. CORE FILES: DETAILED SPECIFICATIONS

#### 3.1 src/main.py

```python
"""
Agent entry point and FastAPI application.
Handles requests, routes to agent, returns A2A protocol responses.
"""

IMPLEMENTATION REQUIREMENTS:
- Use FastAPI framework
- Accept POST /evaluate-task with JSON body:
  {
    "task_description": str,
    "source": str,  # "linear", "clickup", "trello", "google_tasks"
    "task_id": str,
    "metadata": dict (optional)
  }
- Return A2A protocol response:
  {
    "decision": "add" | "filter" | "consolidate" | "clarify",
    "confidence": float (0.0-1.0),
    "mapped_project": str (optional),
    "mapped_issue": str (optional),
    "reasoning": str,
    "suggested_action": str,
    "consolidate_with": list[str] (if duplicates found),
    "alignment_score": float,
    "tags": list[str],
    "blocking_issues": list[str]
  }

KEY FUNCTIONS:
- async def setup_agent() -> Agent
- async def evaluate_task(request: TaskRequest) -> AgentResponse
- Health check endpoint: GET /health
- Liveness probe: GET /live
- Readiness probe: GET /ready
```

#### 3.2 src/agent.py

```python
"""
Core agent logic using Google ADK (Agent Development Kit).
Orchestrates tools, reasoning, and decision-making.
"""

IMPLEMENTATION REQUIREMENTS:

CLASS: LinearSemanticAgent
- __init__(config: AgentConfig, tools: ToolRegistry)
- async def initialize()
  - Load mapache context
  - Connect to Linear MCP via Composio
  - Initialize Firestore
  - Initialize embeddings model
  
- async def evaluate_task(task: Task) -> Decision
  STEPS:
  1. Parse & normalize task description
  2. Fetch existing Linear projects (cached from Firestore)
  3. Generate embeddings for task + projects
  4. Similarity matching (threshold: 0.75)
  5. Rule-based filtering (is it mapache work?)
  6. Duplicate detection (if similarity > 0.80)
  7. Generate confidence score
  8. Format A2A response
  
- async def get_or_refresh_projects(force: bool = False) -> List[Project]
  - Check Firestore cache (TTL: 1 hour)
  - If cache miss: fetch from Linear MCP
  - Embed project semantics
  - Store in Firestore
  
- async def similarity_match(task_embedding, project_embeddings) -> List[Match]
  - Use cosine similarity
  - Return ranked matches (score > 0.75)
  
- def filter_by_mapache_context(task: Task, context: MapacheContext) -> bool
  - Apply filtering rules from mapache_context.md
  - Check against: platform, domain, keywords, patterns
  - Return: bool (valid for mapache or not)
  
- async def detect_duplicates(task: Task, existing_projects: List[Project]) -> List[Duplicate]
  - Find similar projects/issues
  - Return consolidated suggestions

TOOLS REGISTRY:
- linear_tools: Linear MCP operations
- embedding_tools: Vertex AI Embeddings API
- firestore_tools: Firestore CRUD
- reasoning_tools: Semantic reasoning
```

#### 3.3 src/tools/linear_tools.py

```python
"""
Wrapper around Linear MCP Server (via Composio).
Provides typed interfaces for Linear operations.
"""

IMPLEMENTATION REQUIREMENTS:

TOOLS TO IMPLEMENT:
1. list_projects() -> List[LinearProject]
   - Call Linear MCP: list_projects
   - Return: [{"id": str, "name": str, "description": str, "team": str, ...}]
   - Cache in Firestore

2. get_project(project_id: str) -> LinearProject
   - Fetch single project details
   - Include: issues, lead, team, status, created_at, updated_at

3. list_issues(project_id: str = None) -> List[LinearIssue]
   - List all issues (or filter by project)
   - Return: [{"id": str, "title": str, "description": str, "status": str, ...}]

4. search_issues(query: str) -> List[LinearIssue]
   - Full-text search across issues
   - Return ranked results

5. get_issue_details(issue_id: str) -> LinearIssue
   - Full issue details including comments, attachments

6. create_issue(project_id: str, title: str, description: str, metadata: dict) -> str
   - Create new Linear issue
   - Return: issue_id

7. link_issues(source_id: str, target_id: str, relationship: str)
   - Create relationship (duplicate_of, relates_to, blocks, etc.)

ERROR HANDLING:
- Retry on transient failures (exponential backoff)
- Log all API calls with structured logging
- Cache HTTP responses (TTL: 5 mins for list ops)
```

#### 3.4 src/tools/embedding_tools.py

```python
"""
Vertex AI Embeddings API wrapper.
Generates embeddings for task descriptions and projects.
"""

IMPLEMENTATION REQUIREMENTS:

CLASS: EmbeddingService

METHODS:
1. async def embed_text(text: str, task_type: str = "SEMANTIC_SIMILARITY") -> np.ndarray
   - Input: text, task_type
   - Model: text-embedding-005
   - Output dimension: 768
   - Task types:
     * SEMANTIC_SIMILARITY: general purpose
     * RETRIEVAL_DOCUMENT: for indexing project descriptions
     * RETRIEVAL_QUERY: for matching task descriptions
     * QUESTION_ANSWERING: for understanding intent
   
2. async def embed_texts(texts: List[str]) -> List[np.ndarray]
   - Batch embed multiple texts (more efficient)
   - Max batch size: 100
   
3. def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float
   - Return: similarity score 0.0-1.0
   - Used for threshold matching (0.75)

CACHING:
- Cache embeddings in Firestore (collection: "embeddings")
- Key: hash(text)
- TTL: 30 days
- Check cache before calling API

BATCHING:
- Batch requests when possible
- Rate limit: 1000 requests/min (Vertex AI quota)
- Implement queue with max batch size
```

#### 3.5 src/tools/firestore_tools.py

```python
"""
Firestore client for caching and state management.
Stores projects, embeddings, decisions, and agent state.
"""

IMPLEMENTATION REQUIREMENTS:

COLLECTIONS:
1. mapache_projects
   - Document: {project_id}
   - Fields:
     * id: str
     * name: str
     * description: str
     * team: str
     * status: str
     * alignment_score: float (mapache validation)
     * domain: str (core_platform, saaS_integrations, etc.)
     * created_at: timestamp
     * updated_at: timestamp
     * cached_at: timestamp (for TTL logic)
     * embedding: list[float] (STORE THIS)
     * raw_data: dict (full Linear project JSON)

2. mapache_embeddings
   - Document: {hash(text)}
   - Fields:
     * text: str
     * embedding: list[float]
     * dimension: int
     * model: str
     * created_at: timestamp
     * ttl_seconds: int (2592000 = 30 days)

3. mapache_decisions
   - Document: {auto-generated UUID}
   - Fields:
     * task_id: str (source)
     * task_description: str
     * source: str (linear, clickup, trello, google_tasks)
     * decision: str (add, filter, consolidate, clarify)
     * confidence: float
     * reasoning: str
     * mapped_project_id: str (if applicable)
     * consolidate_with: list[str]
     * created_at: timestamp
     * user_feedback: str (optional, for learning)

4. mapache_agent_state
   - Document: "current"
   - Fields:
     * last_sync: timestamp
     * projects_count: int
     * issues_count: int
     * last_error: str
     * health_status: str

METHODS:
1. async def cache_projects(projects: List[LinearProject])
2. async def get_cached_projects(max_age_seconds: int = 3600) -> List[LinearProject]
3. async def store_embedding(text: str, embedding: np.ndarray)
4. async def get_embedding(text: str) -> np.ndarray | None
5. async def store_decision(decision: Decision)
6. async def get_project_by_id(project_id: str) -> LinearProject
7. async def search_projects(query: str, limit: int = 10) -> List[LinearProject]
8. async def update_agent_state(state: dict)

TRANSACTIONALITY:
- Use Firestore transactions for multi-doc updates
- Implement retry logic for conflicts
```

#### 3.6 src/tools/reasoning.py

```python
"""
Semantic reasoning engine.
Core decision logic using mapache.app context and similarity matching.
"""

IMPLEMENTATION REQUIREMENTS:

CLASS: ReasoningEngine

MAIN FLOW:
async def evaluate(task: Task, context: MapacheContext) -> Decision:
  
  STEP 1: Parse Task
  - Normalize text (lowercase, whitespace handling)
  - Extract keywords, entities
  - Identify source (linear, clickup, trello, google_tasks)
  
  STEP 2: Filter by Context (is it mapache work?)
  - Check against FILTER_OUT rules from mapache_context.md
  - Apply keyword matching
  - Check domain (personal, learning, deprecated, generic, duplicates)
  - Score: 0.0 (definitely not) to 1.0 (definitely mapache)
  - If score < 0.40: DECISION = "filter"
  
  STEP 3: Fetch Existing Projects
  - Get from cache (Firestore)
  - If cache miss: fetch from Linear + cache
  
  STEP 4: Generate Embeddings
  - Task embedding (task_type=RETRIEVAL_QUERY)
  - Project embeddings (task_type=RETRIEVAL_DOCUMENT)
  - Use batch API if multiple projects
  
  STEP 5: Similarity Matching
  - For each project: compute cosine_similarity
  - Filter: similarity >= 0.75
  - Sort by score (descending)
  - Return top 3 matches
  
  STEP 6: Duplicate Detection
  - If best match similarity >= 0.80: likely duplicate
  - Check for multiple similar projects (consolidation opportunity)
  
  STEP 7: Alignment Scoring
  - Combine:
    * Mapache context filter score (0-1)
    * Similarity to existing projects (0-1)
    * Clarity of description (0-1)
    * Absence of red flags (0-1)
  - Weighted average (context: 40%, similarity: 30%, clarity: 20%, red_flags: 10%)
  
  STEP 8: Make Decision
  - IF filter_score < 0.40: "filter"
  - ELIF similarity >= 0.80 AND duplicate_confidence >= 0.75: "consolidate"
  - ELIF description is too vague: "clarify"
  - ELIF alignment_score >= 0.75: "add"
  - ELSE: "clarify"
  
  STEP 9: Generate Reasoning
  - Explain decision in natural language
  - Reference specific projects if mapping
  - Suggest consolidation if duplicate
  - Ask clarifying questions if uncertain

SCORING FUNCTIONS:

def filter_score(task: Task, context: MapacheContext) -> float:
  """
  0.0 = definitely not mapache (personal, off-topic)
  1.0 = definitely mapache (core platform, integrations)
  """
  - Check FILTER_OUT categories
  - Deduct points for red flags (personal, deprecated, learning)
  - Award points for mapache domains (core platform, integrations)

def duplicate_score(task: Task, existing: LinearProject) -> float:
  """
  0.0 = completely different
  1.0 = exact duplicate
  """
  - Consider: title similarity, description similarity, domain match
  - Threshold for consolidation: 0.75 (user might consolidate)

def clarity_score(task: Task) -> float:
  """
  0.0 = empty or nonsensical
  1.0 = clear, with acceptance criteria
  """
  - Check description length, detail level, specificity

def alignment_score(task: Task, filter_s: float, dup_s: float, clarity_s: float) -> float:
  """
  Weighted combination of above scores
  """
```

#### 3.7 src/models/mapache_context.py

```python
"""
Embedded mapache.app context for semantic understanding.
This is the business domain knowledge that guides all decisions.
"""

IMPLEMENTATION REQUIREMENTS:

CLASS: MapacheContext

ATTRIBUTES:

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
  "core_platform": ["Agent Runtime", "Linear Integration", "GitHub Integration", "A2UI", "Composio"],
  "saaS_integrations": ["Slack MCP", "HubSpot MCP", "Stripe MCP", "Google Cloud MCP"],
  "intelligence_features": ["Semantic Search", "Gap Detection", "Duplication Detection", "Insights"],
  "internal_ops": ["Infrastructure", "Development Setup", "Async Coding", "Dependency Mgmt"]
}

# Filter rules (❌ FILTER OUT)
FILTER_OUT_RULES = {
  "personal_household": ["shopping", "furniture", "renovation", "home maintenance"],
  "learning_experiments": ["try out", "explore", "experiment", "learning"],
  "deprecated_platforms": ["mapache.solutions", "renovate bot [completed]", "old n8n"],
  "generic_vague": ["untitled", "thing", "fix", "[empty description]"],
  "outside_scope": ["general productivity", "other SaaS evaluation for own use"]
}

# Keywords that indicate valid mapache work
MAPACHE_KEYWORDS = [
  "agent", "mcp", "a2ui", "a2a", "integration", "composio", "vertex ai",
  "linear semantic", "github mcp", "system of intelligence", "sub-agent",
  "deployment", "gcp", "firestore", "embeddings", "rag", "conversational"
]

# Keywords that indicate filter-out work
FILTER_OUT_KEYWORDS = [
  "personal", "learning", "experiment", "try", "evaluate (other tools)",
  "shopping", "household", "meditation", "well-being", "todo (non-work)",
  "n8n (old)", "asana", "monday.com", "jira (not planned integration)"
]

# Red flags that reduce score
RED_FLAGS = [
  "is this valid?",
  "[empty description]",
  "figure out",
  "not sure",
  "maybe",
  "digital well-being",
  "personal task"
]

METHODS:

def is_valid_mapache_work(task: Task) -> bool:
  """Check if task aligns with mapache.app"""
  - Check domain
  - Check keywords
  - Check red flags
  
def get_domain(task: Task) -> str:
  """Identify domain: core_platform, saaS_integrations, intelligence_features, internal_ops, invalid"""

def get_filter_category(task: Task) -> str | None:
  """Return filter category if applies (personal, learning, deprecated, etc.)"""

def should_consolidate_with(task: Task, projects: List[Project]) -> List[str]:
  """Identify which existing projects this should consolidate with"""

def get_suggested_project(task: Task) -> str | None:
  """Suggest which existing project this belongs in"""
```

#### 3.8 src/config/prompts.py

```python
"""
System prompts and example interactions for the agent.
"""

IMPLEMENTATION REQUIREMENTS:

SYSTEM_PROMPT = """
You are the Linear Semantic Agent for mapache.app, an AI Operating System that provides
a unified conversational interface to orchestrate a user's entire SaaS ecosystem.

## Your Role
You validate, categorize, and organize tasks/projects for mapache.app based on:
1. Alignment with mapache.app's business model
2. Similarity to existing Linear projects
3. Quality and clarity of task descriptions
4. Duplicate detection and consolidation

## mapache.app Context
[EMBEDDED: src/models/mapache_context.py - full context document]

## Your Decision Framework
When evaluating a task:

1. Is this mapache.app work? (not personal, learning, or off-topic)
   - Check against FILTER_OUT_RULES
   - Score: 0.0 (no) to 1.0 (yes)

2. Is this a duplicate of existing work?
   - Use semantic similarity matching (threshold: 0.75)
   - If similarity >= 0.80: suggest consolidation

3. Is the description clear enough?
   - Score: 0.0 (empty) to 1.0 (detailed with criteria)

4. What should happen?
   - "add": Create new Linear project/issue
   - "filter": Archive/discard (not mapache work)
   - "consolidate": Merge with existing project
   - "clarify": Ask for more information

## Output Format
Always respond with valid JSON:
{
  "decision": "add" | "filter" | "consolidate" | "clarify",
  "confidence": 0.75,
  "mapped_project": "MAPAI-123" (if applicable),
  "consolidate_with": ["MAPAI-120", "MAPAI-115"] (if duplicates),
  "reasoning": "Clear explanation of decision",
  "suggested_action": "What the user should do",
  "alignment_score": 0.85,
  "tags": ["core_platform", "agent_runtime"],
  "blocking_issues": ["MAPAI-100"] (if applicable)
}

## Examples

EXAMPLE 1: Valid mapache.app work
Input: "Build Slack MCP server so Slack becomes an agent in mapache"
Output:
{
  "decision": "add",
  "confidence": 0.95,
  "mapped_project": null,
  "reasoning": "Slack MCP is planned SaaS integration. Valid mapache.app work.",
  "suggested_action": "Create MAPAI project: 'Slack MCP Server Implementation'",
  "alignment_score": 0.95,
  "tags": ["saaS_integrations", "mcp"]
}

EXAMPLE 2: Duplicate detection
Input: "Implement semantic search for projects"
Existing: "MAPAI-200: Add semantic search to find related work"
Output:
{
  "decision": "consolidate",
  "confidence": 0.82,
  "consolidate_with": ["MAPAI-200"],
  "reasoning": "This is 82% similar to existing MAPAI-200. Suggest consolidating.",
  "suggested_action": "Link to MAPAI-200 instead of creating new issue",
  "alignment_score": 0.90
}

EXAMPLE 3: Filter out (personal task)
Input: "Buy curtain rods and door covers from Chinese store"
Output:
{
  "decision": "filter",
  "confidence": 0.98,
  "reasoning": "Personal household shopping task. Not mapache.app work.",
  "suggested_action": "Archive. This belongs in Google Tasks, not Linear.",
  "alignment_score": 0.0,
  "tags": ["personal_household"]
}

EXAMPLE 4: Ask for clarification
Input: "Improve stuff"
Output:
{
  "decision": "clarify",
  "confidence": 0.30,
  "reasoning": "Description too vague. Need specifics to evaluate.",
  "suggested_action": "Ask user: 'What specifically needs improvement? What's the expected outcome? Which mapache component?'",
  "alignment_score": 0.40
}
"""

# Few-shot examples for prompt
EXAMPLES_VALID_MAPACHE = [
  "Build Slack MCP server integration",
  "Implement semantic gap detection in Linear agent",
  "Set up Vertex AI RAG corpus for embeddings",
  "Create A2UI message format documentation",
  "Deploy agent to Vertex AI Agent Runtime",
  "Implement task creation automation via MCP",
]

EXAMPLES_FILTER_OUT = [
  "Buy furniture for home office",
  "Learn Temporal.io workflow orchestration",
  "Explore Neo4j vs Firestore options",
  "Study Stoic philosophy",
  "Digital well-being: break phone addiction",
  "Personal task: fix awning on porch",
]

EXAMPLES_DUPLICATES = [
  ("Implement semantic search", "MAPAI-200: Add semantic search to find related work", 0.82),
  ("GitHub MCP optimization", "MAPAI-145: Reduce GitHub MCP token usage", 0.78),
]

CLARIFICATION_PROMPTS = {
  "vague": "Can you be more specific? What exactly needs to be done? What's the expected outcome?",
  "missing_context": "Which mapache.app component does this relate to? Is this for core platform, SaaS integration, or intelligence features?",
  "personal": "This seems like a personal task. Is it related to building mapache.app? If not, please store it in Google Tasks instead.",
}
```

#### 3.9 src/config/constants.py

```python
"""
Magic numbers, thresholds, and configuration constants.
"""

IMPLEMENTATION REQUIREMENTS:

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
```

#### 3.10 src/integrations/linear_mcp.py

```python
"""
Linear MCP Server client via Composio.
Implements authenticated access to Linear API.
"""

IMPLEMENTATION REQUIREMENTS:

CLASS: LinearMCPClient

__init__(mcp_url: str, composio_api_key: str, composio_config: dict):
  - Initialize Composio OAuth client
  - Store Linear MCP URL
  - Setup request session with auth

ASYNC METHODS:

async def authenticate():
  """
  Setup OAuth flow with Composio.
  Use dynamic client registration.
  """
  - Initialize OAuth 2.1 dynamic registration
  - Use LINEAR_API_KEY from environment
  - Return auth token

async def list_projects() -> List[dict]:
  """
  Fetch all projects from Linear.
  Returns: [
    {
      "id": "proj_123",
      "name": "Mapache Infrastructure",
      "description": "...",
      "team": "Mapache Solutions",
      "status": "active",
      "lead": {...},
      "created_at": "...",
      "updated_at": "..."
    }
  ]
  """
  - Call Linear MCP tool: list_projects
  - Parse response
  - Cache in Firestore
  - Return typed list

async def get_project(project_id: str) -> dict:
  """Get detailed project information"""
  
async def list_issues(project_id: str = None) -> List[dict]:
  """
  List issues, optionally filtered by project.
  Return: [
    {
      "id": "MAPAI-123",
      "title": "...",
      "description": "...",
      "status": "Backlog",
      "project_id": "...",
      "priority": 1,
      "created_at": "..."
    }
  ]
  """

async def search_issues(query: str) -> List[dict]:
  """Full-text search across issues"""

async def create_issue(project_id: str, data: dict) -> str:
  """
  Create new issue in Linear.
  Input: {
    "title": str,
    "description": str,
    "priority": int (1-4),
    "assignee": str (optional),
    "labels": list[str] (optional)
  }
  Return: issue_id
  """

async def update_issue(issue_id: str, data: dict):
  """Update existing issue"""

async def link_issues(source_id: str, target_id: str, relationship: str):
  """
  Create relationship between issues.
  relationship: "duplicate_of", "relates_to", "blocks", "depends_on"
  """

# Error Handling
class LinearMCPError(Exception): pass
class LinearAuthError(LinearMCPError): pass
class LinearAPIError(LinearMCPError): pass

async def _call_mcp_tool(tool_name: str, params: dict) -> dict:
  """
  Generic MCP tool caller with retry logic.
  - Implement exponential backoff
  - Log all calls
  - Handle authentication errors
  """
```

---

### 4. DEPLOYMENT CONFIGURATION

#### 4.1 cloudbuild.yaml

```yaml
steps:
  # Step 1: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: 
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/linear-semantic-agent:$SHORT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/linear-semantic-agent:latest'
      - '-f'
      - 'docker/Dockerfile'
      - '.'
    id: 'build-image'

  # Step 2: Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/linear-semantic-agent:$SHORT_SHA'
    id: 'push-image'

  # Step 3: Deploy to Vertex AI Agent Runtime
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - 'run'
      - '--filename=kubernetes/'
      - '--image=gcr.io/$PROJECT_ID/linear-semantic-agent:$SHORT_SHA'
      - '--location=us-central1'
      - '--cluster=mapache-agents'
    env:
      - 'GCP_PROJECT=$PROJECT_ID'
    id: 'deploy-agent'

# Build configuration
options:
  machineType: 'N1_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
  
# Timeout
timeout: '1800s'

# Images to push
images:
  - 'gcr.io/$PROJECT_ID/linear-semantic-agent:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/linear-semantic-agent:latest'
```

#### 4.2 docker/Dockerfile

```dockerfile
# Multi-stage build

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels

# Copy requirements
COPY requirements.txt .

# Install from wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY src/ ./src
COPY docs/ ./docs
COPY .env.example ./

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run agent
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 4.3 kubernetes/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: linear-semantic-agent
  namespace: mapache
  labels:
    app: linear-semantic-agent
    version: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: linear-semantic-agent
  template:
    metadata:
      labels:
        app: linear-semantic-agent
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: linear-semantic-agent
      containers:
      - name: agent
        image: gcr.io/linear-semantic-agents/linear-semantic-agent:latest
        imagePullPolicy: IfNotPresent
        
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        
        env:
        - name: GCP_PROJECT_ID
          valueFrom:
            configMapKeyRef:
              name: agent-config
              key: gcp-project-id
        - name: VERTEX_AI_LOCATION
          valueFrom:
            configMapKeyRef:
              name: agent-config
              key: vertex-ai-location
        - name: LINEAR_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: linear-api-key
        - name: COMPOSIO_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: composio-api-key
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        
        livenessProbe:
          httpGet:
            path: /live
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
        
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      
      volumes:
      - name: tmp
        emptyDir: {}
      
      nodeSelector:
        cloud.google.com/gke-nodepool: default-pool

---
apiVersion: v1
kind: Service
metadata:
  name: linear-semantic-agent
  namespace: mapache
  labels:
    app: linear-semantic-agent
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: linear-semantic-agent

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: linear-semantic-agent
  namespace: mapache

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: linear-semantic-agent
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: linear-semantic-agent
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: linear-semantic-agent
subjects:
- kind: ServiceAccount
  name: linear-semantic-agent
  namespace: mapache
```

---

### 5. GCP SETUP & DEPLOYMENT SCRIPTS

#### 5.1 gcp_setup.sh

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ID="linear-semantic-agents"
REGION="us-central1"
CLUSTER_NAME="mapache-agents"

echo -e "${YELLOW}=== GCP Setup for Linear Semantic Agent ===${NC}"

# 1. Set project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable \
  aiplatform.googleapis.com \
  container.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  firestore.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  secretmanager.googleapis.com

# 3. Create GKE cluster (if doesn't exist)
echo -e "${YELLOW}Creating GKE cluster...${NC}"
if ! gcloud container clusters describe $CLUSTER_NAME --region=$REGION &>/dev/null; then
  gcloud container clusters create $CLUSTER_NAME \
    --region=$REGION \
    --num-nodes=1 \
    --machine-type=n1-standard-4 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=3 \
    --enable-stackdriver-kubernetes \
    --addons=HttpLoadBalancing,HorizontalPodAutoscaling
fi

# 4. Get cluster credentials
echo -e "${YELLOW}Getting cluster credentials...${NC}"
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# 5. Create namespace
echo -e "${YELLOW}Creating Kubernetes namespace...${NC}"
kubectl create namespace mapache --dry-run=client -o yaml | kubectl apply -f -

# 6. Create Firestore database (if doesn't exist)
echo -e "${YELLOW}Creating Firestore database...${NC}"
gcloud firestore databases create --region=$REGION || true

# 7. Create secrets
echo -e "${YELLOW}Creating Kubernetes secrets...${NC}"
echo "Enter your Linear API Key (from https://linear.app/settings/api):"
read LINEAR_API_KEY

echo "Enter your Composio API Key:"
read COMPOSIO_API_KEY

kubectl create secret generic agent-secrets \
  --from-literal=linear-api-key="$LINEAR_API_KEY" \
  --from-literal=composio-api-key="$COMPOSIO_API_KEY" \
  --namespace=mapache \
  --dry-run=client -o yaml | kubectl apply -f -

# 8. Create ConfigMap
echo -e "${YELLOW}Creating ConfigMap...${NC}"
kubectl create configmap agent-config \
  --from-literal=gcp-project-id=$PROJECT_ID \
  --from-literal=vertex-ai-location=$REGION \
  --namespace=mapache \
  --dry-run=client -o yaml | kubectl apply -f -

# 9. Grant service account permissions
echo -e "${YELLOW}Granting IAM permissions...${NC}"
SA_EMAIL="linear-semantic-agent@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create linear-semantic-agent \
  --display-name="Linear Semantic Agent" || true

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user"

echo -e "${GREEN}✓ GCP setup complete!${NC}"
echo -e "${GREEN}✓ Ready for deployment.${NC}"
```

#### 5.2 deploy.sh

```bash
#!/bin/bash
set -e

PROJECT_ID="linear-semantic-agents"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/linear-semantic-agent"

echo "=== Deploying Linear Semantic Agent ==="

# 1. Build image
echo "Building Docker image..."
docker build \
  -t $IMAGE_NAME:latest \
  -f docker/Dockerfile \
  .

# 2. Push to Container Registry
echo "Pushing image to Container Registry..."
docker push $IMAGE_NAME:latest

# 3. Deploy to Kubernetes
echo "Deploying to GKE..."
kubectl apply -f kubernetes/

# 4. Wait for rollout
echo "Waiting for deployment..."
kubectl rollout status deployment/linear-semantic-agent \
  -n mapache \
  --timeout=5m

# 5. Get service endpoint
echo "Getting service endpoint..."
SERVICE_IP=$(kubectl get svc linear-semantic-agent \
  -n mapache \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "=== Deployment Complete ==="
echo "Service IP: $SERVICE_IP"
echo "API endpoint: http://$SERVICE_IP/docs (Swagger UI)"
```

---

### 6. TESTING FRAMEWORK

#### 6.1 tests/test_agent.py

```python
"""
Unit tests for agent core logic.
Uses pytest and pytest-asyncio for async testing.
"""

IMPLEMENTATION REQUIREMENTS:

TEST CLASSES:

1. TestAgentInitialization
   - test_init_with_valid_config()
   - test_init_missing_credentials()
   - test_context_loads_on_init()

2. TestTaskEvaluation
   - test_evaluate_valid_mapache_task()
   - test_evaluate_personal_task()
   - test_evaluate_learning_task()
   - test_evaluate_task_with_similarity_match()
   - test_evaluate_task_with_duplicate()
   - test_evaluate_vague_task_requests_clarification()

3. TestDuplicateDetection
   - test_detect_obvious_duplicate()
   - test_detect_near_duplicate()
   - test_no_duplicate_for_different_tasks()

4. TestSimilarityMatching
   - test_similarity_above_threshold()
   - test_similarity_below_threshold()
   - test_cosine_similarity_calculation()

5. TestContextFiltering
   - test_filter_personal_tasks()
   - test_filter_learning_experiments()
   - test_filter_deprecated_platforms()
   - test_accept_core_platform_work()
   - test_accept_saaS_integrations()

FIXTURES:
- @pytest.fixture sample_task()
- @pytest.fixture sample_projects()
- @pytest.fixture mock_linear_client()
- @pytest.fixture agent_instance()
```

#### 6.2 tests/test_reasoning.py

```python
"""
Tests for semantic reasoning engine.
Focus on decision logic, scoring, and alignment validation.
"""

TEST CLASSES:

1. TestFilterScore
   - test_filter_score_valid_mapache()
   - test_filter_score_personal_household()
   - test_filter_score_learning_experiment()

2. TestDuplicateScore
   - test_dup_score_exact_duplicate()
   - test_dup_score_similar_projects()
   - test_dup_score_different_projects()

3. TestClarityScore
   - test_clarity_empty_description()
   - test_clarity_vague_description()
   - test_clarity_detailed_description()

4. TestAlignmentScore
   - test_alignment_weighted_combination()
   - test_alignment_threshold_logic()

5. TestDecisionLogic
   - test_decision_add_for_valid_work()
   - test_decision_filter_for_personal()
   - test_decision_consolidate_for_duplicate()
   - test_decision_clarify_for_vague()
```

---

### 7. DOCUMENTATION

#### 7.1 agent_interface.md (A2A Protocol)

```markdown
# Linear Semantic Agent - A2A Protocol Specification

## Endpoint: POST /evaluate-task

### Request
\`\`\`json
{
  "task_description": "string (required)",
  "source": "linear|clickup|trello|google_tasks (required)",
  "task_id": "string (required - for cross-reference)",
  "metadata": {
    "created_at": "ISO8601",
    "priority": "high|medium|low",
    "assigned_to": "email (optional)"
  }
}
\`\`\`

### Response
\`\`\`json
{
  "decision": "add|filter|consolidate|clarify",
  "confidence": 0.75,
  "mapped_project": "MAPAI-123",
  "mapped_issue": "MAPAI-123-1",
  "consolidate_with": ["MAPAI-115", "MAPAI-120"],
  "reasoning": "This is 82% similar to existing project MAPAI-115",
  "suggested_action": "Review existing project MAPAI-115 and decide if consolidation makes sense",
  "alignment_score": 0.85,
  "tags": ["core_platform", "agent_runtime"],
  "blocking_issues": ["MAPAI-100"],
  "clarification_questions": ["What is the specific goal of this task?"]
}
\`\`\`

## Decision Types

### "add"
- Task is valid mapache.app work
- No duplicates found
- Description is clear
- Action: Create new Linear project/issue

### "filter"
- Task does NOT align with mapache.app
- Personal, learning, or off-topic
- Action: Archive/ignore, store in Google Tasks instead

### "consolidate"
- Task is similar to existing project (similarity >= 0.80)
- Action: Link to existing project, don't duplicate

### "clarify"
- Description is too vague or missing context
- Need more information before deciding
- Action: Ask user for clarification

## Other Endpoints

### GET /health
Health check endpoint. Returns 200 if healthy.

### GET /live
Liveness probe. Returns 200 if agent is running.

### GET /ready
Readiness probe. Returns 200 if agent is ready to accept requests.

### GET /metrics
Prometheus metrics endpoint. Returns metrics in Prometheus format.

### GET /docs
Swagger UI documentation.
```

---

## IMPLEMENTATION TIMELINE & BREAKDOWN

**Total Scope**: Complete, production-ready implementation  
**Estimated Claude Code Time**: 6-8 hours for experienced developer

### Phase 1: Setup & Models (1 hour)
1. Create project structure
2. Implement data models (Task, Project, Decision, MapacheContext)
3. Setup configuration management
4. Create tests fixtures

### Phase 2: Core Agent Logic (2 hours)
1. Implement ReasoningEngine
2. Implement similarity matching
3. Implement filtering logic
4. Implement decision logic

### Phase 3: Integrations (2 hours)
1. Linear MCP client
2. Vertex AI Embeddings client
3. Firestore client
4. Error handling & retries

### Phase 4: API & Main (1 hour)
1. FastAPI application
2. Request/response handling
3. Health checks
4. Logging

### Phase 5: Deployment (1 hour)
1. Docker configuration
2. Kubernetes manifests
3. GCP setup scripts
4. Cloud Build config

### Phase 6: Testing (1 hour)
1. Unit tests for all components
2. Integration tests
3. Example test data

---

## SUCCESS CRITERIA

✅ **Agent successfully deployed when:**

1. **Functionality**
   - Agent correctly identifies valid mapache.app work (≥90% accuracy on test cases)
   - Agent filters personal/learning tasks correctly (≥95% accuracy)
   - Agent detects duplicates with 0.75+ confidence threshold
   - Agent generates clear reasoning for every decision
   - Agent operates as callable A2A sub-agent

2. **Performance**
   - Response time < 5 seconds for typical task (including API calls)
   - Handles 100+ concurrent requests
   - Caching works correctly (embeddings, projects)
   - Memory usage < 1GB

3. **Integration**
   - Connects to Linear MCP via Composio
   - Authenticates via OAuth
   - Reads/writes Firestore successfully
   - Calls Vertex AI Embeddings API

4. **Reliability**
   - Health checks pass (live, ready endpoints)
   - Handles API failures gracefully
   - Retries transient failures
   - Logs all operations

5. **Testing**
   - All unit tests pass
   - Test coverage > 80%
   - Example test cases work correctly
   - Manual testing validates decisions

---

## NEXT STEPS AFTER DEPLOYMENT

**Once agent is running, follow these steps:**

1. **Test with Real Data**
   - Run agent against 10-20 sample tasks from ClickUp/Trello
   - Validate decisions manually
   - Adjust thresholds if needed (0.75 similarity, etc.)

2. **Feed Conversation Exports**
   - Parse Claude/ChatGPT conversation files from GitHub repos
   - Summarize each conversation (1-3 sentences)
   - Feed summaries to agent
   - Generate reconciliation report

3. **Consolidate Task Sources**
   - Import 791 ClickUp tasks
   - Import 89 Trello cards
   - Import personal Google Tasks
   - Consolidate duplicates in Linear

4. **Iterate & Improve**
   - Adjust confidence thresholds based on real usage
   - Add new filtering rules based on patterns
   - Fine-tune prompts based on actual decisions
   - Measure decision accuracy against manual review

---

## CRITICAL IMPLEMENTATION NOTES

1. **mapache.app Context is CORE**
   - Every decision flows through the context document
   - If agent misses something, update context, not code
   - Context drives 40% of alignment score

2. **Similarity Threshold is NOT Magic**
   - 0.75 is starting point, not final
   - May need adjustment based on real usage
   - Document any threshold changes

3. **Firestore Caching is Critical**
   - Project list fetched once per hour
   - Embeddings cached for 30 days
   - Decisions logged for learning
   - Dramatically improves performance

4. **Error Handling > Features**
   - Always retry transient failures
   - Log every decision for audit
   - Never silently fail
   - Expose errors to user clearly

5. **A2A Protocol is Standard**
   - Don't invent new response formats
   - Use provided JSON schema
   - Other agents depend on consistency

---

## DOCUMENTATION IN CODEBASE

- README.md: Overview & quick start
- docs/deployment_guide.md: Step-by-step deployment
- docs/examples.md: Example interactions
- docs/agent_interface.md: A2A protocol spec
- docs/mapache_context.md: Embedded context
- Code comments: Inline explanations of complex logic
- Docstrings: Every function documented with examples

---

**READY FOR CLAUDE CODE EXECUTION**

This specification is complete and detailed enough for Claude Code to:
1. Create all file structures
2. Implement all functionality
3. Deploy to GCP
4. Write comprehensive tests
5. Generate documentation

No additional clarification needed. Proceed with implementation.
