# mapache.app Context Document for Linear Semantic Agent
**Version:** 1.0 | **Date:** January 16, 2026 | **Scope:** MVP Phase

---

## 1. WHAT IS mapache.app?

**mapache.app is an AI Operating System** — a unified conversational interface that connects to and intelligently orchestrates a user's entire SaaS and software ecosystem.

### Core Value Proposition
- **Single entry point**: Talk to one "chief agent" instead of switching between dozens of tools
- **Intelligent coordination**: Multi-agent system (A2A protocol) that understands how your tools relate
- **CRUD via conversation**: Use A2UI protocol to read/write data in connected apps without opening them
- **System of Intelligence**: Cross-SaaS reasoning that learns patterns, finds gaps, and surfaces insights

### What mapache.app IS NOT
- A new SaaS tool to use separately
- A data aggregation/reporting dashboard
- A tool-specific solution (Linear tool, GitHub tool, Slack tool, etc.)
- A consumer app or learning platform
- A productivity timer or workflow tracker
- A general-purpose agent that does everything

---

## 2. CURRENT ARCHITECTURE (MVP)

### Core System Components

#### A. Agent Orchestration Layer
- **Chief Agent**: User's conversational interface, coordinates sub-agents
- **Sub-agents**: Specialized agents for specific domains
  - FTE-equivalent agents (domain experts, coding specialists)
  - SaaS specialist agents (understand specific tool semantics)
  - System intelligence agents (cross-tool reasoning)
- **Coordination Protocol**: A2A (Agent-to-Agent) via Google's ADK
- **Runtime**: Vertex AI Agent Runtime (managed, scalable)

#### B. Integration Layer (Composio + MCP)
- **MCP Servers**: Standardized protocol for tool access
- **Composio**: OAuth orchestration + MCP provider
- **Built-in MCP Servers**: Linear, GitHub, (others TBD)
- **Connection Model**: All tool integrations flow through Composio/MCP, not custom APIs

#### C. Rendering & CRUD Layer
- **A2UI Protocol**: Agent-to-UI messages define structure, data, and operations
- **CRUD Operations**: Users perform all data modifications via A2UI (not native tool UIs)
- **UI Agnostic**: A2UI can render on web, mobile, chat, etc.

#### D. Data & Persistence
- **Primary Sources**: Connected SaaS (Linear, GitHub, etc.) — real-time
- **Operational Storage**: Firestore (caching, embeddings, agent state)
- **Analytics/History**: BigQuery (long-term audit, learning)

#### E. Intelligence Layer (System of Intelligence)
- **Embeddings**: Vertex AI RAG Engine or Vertex AI Search (not yet built)
- **Semantic Understanding**: Agents understand context across SaaS boundaries
- **Learning**: Discovers patterns over time
- **Reasoning**: Multi-hop reasoning across connected systems (future)

### Technology Stack (All Google)
- **LLMs**: Gemini (latest versions)
- **Development**: Google ADK (Agent Development Kit), A2A protocol
- **Orchestration**: Vertex AI Agent Runtime
- **Embeddings/Search**: Vertex AI RAG Engine OR Vertex AI Search (TBD)
- **OAuth/Integration**: Composio (MCP provider)
- **Coding Support**: Google Jules, Claude Code, Continue (VS Code)
- **Repository**: GitHub (mapachekurt org)
- **Deployment**: Google Cloud Platform (all services)
- **Multi-tenancy**: Clerk + SaaS boilerplate

---

## 3. CURRENT PROJECT DOMAINS (mapache.app Roadmap)

### 3.1 CORE PLATFORM (Must Build)
**Focus**: Make the OS work reliably

| Domain | Description | Current Status | Examples |
|--------|-------------|-----------------|----------|
| **Agent Runtime** | Vertex AI Agent Runtime setup, A2A protocol implementation | In Progress | MAPAI-* projects, agent lifecycle tests |
| **Linear Integration** | Linear MCP server, semantic understanding of projects | In Progress | Linear Semantic Agent (THIS PROJECT) |
| **GitHub Integration** | GitHub MCP server, code sync with projects | In Progress | MAPAI-* projects with GitHub MCP |
| **A2UI Renderer** | Protocol implementation, UI message generation | Backlog | A2UI message format docs, rendering tests |
| **Composio Setup** | OAuth orchestration, MCP routing | In Progress | Composio config, OAuth flows |

### 3.2 SAAAS INTEGRATIONS (Agents for Each)
**Focus**: Turn each integrated SaaS into an agent

| SaaS | Purpose in mapache | Status | Notes |
|------|-------------------|--------|-------|
| **Linear** | Project/product management hub | MVP (in progress) | Official MCP exists |
| **GitHub** | Code repository + CI/CD | MVP (in progress) | Official MCP exists |
| **Slack** | Notifications, team updates | Planned | MCP server exists |
| **HubSpot** | CRM, customer insights | Planned | MCP server likely available |
| **Stripe** | Billing, revenue data | Planned | Needs MCP development |
| **Google Cloud** | Infrastructure, logs | Planned | Native GCP integration |
| **Others** | TBD based on user needs | TBD | Composio has 100+ pre-built MCP |

### 3.3 INTELLIGENCE FEATURES (Future)
**Focus**: System of Intelligence emerges

| Feature | Description | Status |
|---------|-------------|--------|
| **Semantic Search** | Find related work across tools | Not started |
| **Gap Detection** | Identify missing projects/tasks | Not started |
| **Duplication Detection** | Find redundant work | Not started (This is ONE use case) |
| **Predictive Insights** | What should we prioritize? | Not started |
| **Automated Workflows** | Cross-SaaS automation | Not started |

### 3.4 INTERNAL OPS (Support mapache Building)
**Focus**: Use mapache to build mapache (recursive!)

| Task Type | Examples | Status |
|-----------|----------|--------|
| **Infrastructure** | Railway/GCP setup, Docker configs | In Progress |
| **Development Setup** | Continue.json, Ollama, local dev | In Progress |
| **Team/Async Coding** | Google Jules tasks, Antigravity debugging | In Progress |
| **Dependency Management** | Renovate bot, package updates | In Progress |

---

## 4. FILTERING RULES: WHAT BELONGS IN LINEAR?

### ✅ DEFINITELY ADD TO LINEAR

**Category: Core Platform Development**
- Agent runtime implementation, A2A protocol work
- Linear semantic agent, GitHub MCP integration
- A2UI protocol work, rendering, message formats
- Composio OAuth setup, MCP routing

**Category: SaaS Integrations**
- Building/improving MCP servers for connected tools
- Integration testing, API compatibility
- OAuth flow setup for new services
- Tool-specific feature implementation

**Category: Feature Development**
- Semantic search implementation
- Gap detection algorithms
- Duplication detection logic
- Any new mapache.app capability

**Category: Infrastructure/DevOps**
- GCP project setup, API enablement
- Railway deployments, Docker configs
- GitHub repository organization
- Monitoring, logging, alerting

**Category: Documentation**
- mapache.app architecture docs
- API documentation
- Integration guides
- Agent building guides

---

### ❌ FILTER OUT (Don't Add / Archive)

**Category: Personal/Household**
- Shopping lists, furniture assembly, curtain rods
- Home maintenance, landscaping, renovations
- Personal finance, bill reminders
- Subscriptions (ChatGPT, ClickUp, etc.) unless they're BUSINESS subscriptions

**Category: Learning/Experimentation**
- "Try out n8n workflows for fun"
- "Explore Neo4j vs Firestore for knowledge graphs" (unless actively deciding for mapache)
- "Study Stoic philosophy"
- "Digital well-being: How to break phone addiction"
- Proof-of-concept testing of OTHER tools (unless evaluating for mapache integration)

**Category: Outdated/Deprecated Platforms**
- Tasks about mapache.solutions (old business model, deprecated)
- Tasks about Renovate bot that are completed or outdated
- References to platforms no longer used (old n8n setup, old SaaS evaluations)
- Experiments from 6+ months ago that led nowhere

**Category: Generic/Vague**
- "Brainstorm ideas" (too vague, add specific idea later)
- "Research X" without context (add only if actionable plan exists)
- "Fix bug" without project context
- "Untitled" tasks with no description

**Category: Duplicates/Consolidatable**
- Same task appears in ClickUp, Trello, Linear, AND Google Tasks
- Keep only ONE in Linear, archive others
- Consolidate related sub-tasks into parent task

---

## 5. QUALITY GATES FOR LINEAR PROJECTS/ISSUES

### For Issues: Minimum Viable Description
```
✅ GOOD:
Title: "Implement Linear Semantic Agent that understands mapache.app architecture"
Description: 
  - Agent must fetch Linear projects and issues via MCP
  - Agent must validate new project ideas against existing projects
  - 0.75 confidence threshold for mapping decisions
  - Deploy to Vertex AI Agent Runtime
  - Test with GCP project: linear-semantic-agents

❌ BAD:
Title: "thing"
Description: (empty)

❌ BAD:
Title: "Fix stuff"
Description: "It's broken, plz fix"
```

### For Projects: Alignment with mapache.app
```
✅ GOOD:
"GitHub MCP Optimization"
- Purpose: Reduce token usage in GitHub MCP by 50%
- Deliverable: Optimized claude_desktop_config.json
- Alignment: Improves development velocity for mapache building

❌ BAD:
"n8n Workflow Experimentation"
- Purpose: Learning how n8n works
- Alignment: None — n8n is not a mapache.app integration
```

---

## 6. SEMANTIC UNDERSTANDING FOR THE AGENT

### What the Agent MUST Know

#### Architecture Relationships
- Linear projects describe WHAT to build
- GitHub repos contain the CODE
- Agents coordinate between them
- Composio/MCP is the HOW
- A2UI is the display protocol

#### Domain Terminology
- **FTE Agent**: Agent that acts like a full-time employee (e.g., "Junior Coder", "QA Bot")
- **SaaS Agent**: Agent specialized in one tool (e.g., "Linear Expert", "GitHub Specialist")
- **Sub-agent**: Any agent called by the Chief Agent
- **A2A**: Agent-to-Agent communication protocol
- **MCP**: Model Context Protocol (standardized tool interface)
- **A2UI**: Agent-to-User-Interface protocol (how agents describe what to show)

#### Current Technology Choices
- **OAuthProvider**: Composio (not Auth0, Okta, or custom)
- **Project Management**: Linear (not Asana, Monday.com, Jira)
- **Repository**: GitHub (not GitLab, Gitea)
- **Cloud**: Google Cloud Platform (not AWS, Azure)
- **Agent Runtime**: Vertex AI (not AWS Bedrock, Azure OpenAI)
- **Embedding Model**: TBD (Vertex AI Search or RAG Engine)

#### Known Constraints
- **Solo founder**: All work is async, autonomous agents must handle it
- **5-6 hour focus window**: 6-11 AM daily, including weekends
- **MVP stage**: Not production-ready yet
- **Budget-conscious**: Focus on GCP free tier / low-cost options
- **Autonomous coding**: Google Jules, Claude Code, Continue handle most coding

---

## 7. MAPPING EXAMPLES: Is This Valid mapache Work?

### Examples: ✅ ADD TO LINEAR

**Example 1**: "Build Slack MCP Server"
- ✅ Creates a new integration for mapache.app
- ✅ Follows Composio + MCP pattern
- ✅ Enables "Slack Agent" in system

**Example 2**: "Implement semantic gap detection in Linear agent"
- ✅ Part of System of Intelligence
- ✅ Directly builds mapache.app capability
- ✅ Improves Chief Agent's decision-making

**Example 3**: "Set up Google Cloud Storage for Vertex AI RAG corpus"
- ✅ Infrastructure for mapache.app platform
- ✅ Enables embeddings/semantic search
- ✅ GCP-native, aligned with stack

**Example 4**: "Create A2UI message format documentation"
- ✅ Core protocol documentation
- ✅ Needed for other agents to build on
- ✅ Aligns with mapache architecture

---

### Examples: ❌ FILTER OUT

**Example 1**: "Try out Temporal.io for workflow orchestration"
- ❌ Learning experiment, not a mapache.app building task
- ❌ Temporal is not an integration mapache needs
- ✅ Could add IF: "Evaluate Temporal as alternative to current A2A coordination"
  (but only if seriously considering replacing Vertex AI ADK)

**Example 2**: "Fix awning on porch"
- ❌ Personal household task
- ❌ Zero relevance to mapache.app
- ❌ Archive this forever

**Example 3**: "Explore n8n as alternative to mapache.app architecture"
- ❌ mapache.app IS NOT n8n — it's a conversational OS
- ❌ n8n is a workflow platform, completely different category
- ✅ Could add IF: "Evaluate n8n as potential SaaS integration for mapache users"
  (different - evaluating for INTEGRATION, not as architecture)

**Example 4**: "Phase 3: Deploy optimized config to Claude Desktop"
- ⚠️ BORDERLINE: Is this about mapache building or about Kurt's tool setup?
- ✅ KEEP IF: It's optimizing tools needed to BUILD mapache (valid)
- ❌ ARCHIVE IF: It's just optimizing Kurt's personal Claude Desktop setup (not mapache work)
- **Decision**: Keep it if it directly improves dev velocity for mapache; archive if it's one-off optimization

---

## 8. DUPLICATE CONSOLIDATION RULES

When importing from ClickUp/Trello/Google Tasks to Linear:

1. **Check if it already exists in Linear**
   - Search by title similarity (0.75 threshold)
   - Search by description keywords
   - If found: CONSOLIDATE, don't duplicate

2. **Consolidation logic**:
   ```
   IF ClickUp task ≈ Linear issue:
       THEN: Add ClickUp context to Linear issue, close ClickUp task, link them
       ELSE: Create new Linear issue from ClickUp task
   ```

3. **What counts as duplicate**?
   - Same topic + same intended outcome = duplicate
   - Similar names but different scope = different (link as "related")
   - Same issue mentioned in multiple sources = one issue + references

---

## 9. CURRENT MAPACHE PROJECT INVENTORY

### Active Projects (Should Be in Linear)
- **Mapache Solutions Team** (main)
- **Mapache Team** (secondary)
- **GitHub MCP Tool-Specific Configuration**
- **Renovate Bot Deployment & Integration** (mostly done)
- **Linear Temporal Semantic Agent** (in planning)
- **Linear Semantic Agent with mapache Context** (THIS ONE)

### Incoming Tasks to Validate
- **From ClickUp**: 791 tasks (mostly MCP-related, needs filtering)
- **From Trello**: 89 cards (Mapache board, mostly needs triaging)
- **From Google Tasks**: Personal + mixed (filter aggressively)
- **From GitHub Conversations**: Future analysis for pattern matching

---

## 10. AGENT INSTRUCTIONS (High-Level)

When evaluating a task/project, the Linear Semantic Agent should ask itself:

```
1. Does this help build mapache.app?
   - Core platform? → YES
   - New SaaS integration? → YES
   - Intelligence feature? → YES
   - Infrastructure/DevOps? → YES
   - Documentation/Guides? → YES
   - Personal task? → NO
   - Learning experiment on unrelated tech? → NO

2. Is it already in Linear?
   - Check similarity (0.75+ threshold)
   - If yes: Suggest consolidation
   - If no: Proceed

3. Is the description clear enough?
   - Does it have acceptance criteria?
   - Can a developer understand what to do?
   - Is it specific or vague?
   - If unclear: Suggest improvements

4. Is it actionable?
   - Can work start immediately?
   - Or does it need pre-requisites?
   - Is it blocked by other tasks?

5. Where should it go?
   - New project? or existing project?
   - What team? (Mapache Solutions, Mapache, etc.)
   - What priority?
   - What cycle (if applicable)?
```

---

## 11. SYSTEM OF INTELLIGENCE USE CASES (Future)

Once the Linear Semantic Agent is solid, it enables these use cases:

### Use Case 1: Conversation Analysis
```
User: "I had a conversation with Claude about implementing semantic search across 
       projects. Should this be a Linear project?"

Chief Agent → Linear Semantic Agent:
  "Analyze this conversation and validate against mapache.app architecture"
  
Linear Semantic Agent:
  "Semantic search is a System of Intelligence feature. This maps to 
   MAPAI-200 (Semantic Understanding Layer). Suggest linking conversation
   to that project as context."
```

### Use Case 2: Deduplication
```
User: "I think I've been creating duplicate tasks. Help me clean up."

Chief Agent → Linear Semantic Agent:
  "Find duplicate or near-duplicate projects/issues across Linear, and 
   suggest consolidations."
   
Linear Semantic Agent:
  "Found 3 duplicates:
   - MAPAI-150: Phase 2 GitHub MCP (duplicate of MAPAI-145)
   - MAPSL-14: Task creation from chat (duplicate of MAPAI-120)
   - Suggest consolidating and archiving one of each pair"
```

### Use Case 3: Idea Validation
```
User: "I have a new idea: build a Jira MCP server. Is this valid for mapache?"

Chief Agent → Linear Semantic Agent:
  "Validate if this aligns with mapache.app"

Linear Semantic Agent:
  "Jira is a valid SaaS integration target. However, check first:
   1. Do you have active Jira users in mapache ecosystem?
   2. Is this higher priority than other planned SaaS integrations (Slack, HubSpot)?
   3. Suggest creating a LOW priority spike to evaluate demand first"
```

---

## 12. CONTEXT BOUNDARIES

### What This Agent DOES NOT Do
- Build mapache.app features (that's why you have coding agents)
- Manage day-to-day execution (that's why you have FTE agents)
- Handle SaaS-specific operations (that's why you have SaaS specialist agents)
- Execute code or deploy (that's why you have automation agents)

### What This Agent ONLY Does
- Validates project/task alignment with mapache.app
- Identifies duplicates and suggests consolidation
- Ensures Linear is the source of truth for mapache building
- Helps reason about what should be a Linear project
- Can be called by other agents to validate sub-tasks

---

## 13. SUCCESS CRITERIA FOR THIS AGENT

✅ **Agent is working well when:**
1. New project ideas are validated quickly (< 1 minute)
2. Duplicates are detected (≥ 0.75 confidence)
3. Personal/junk tasks are filtered out automatically
4. Incoming tasks from ClickUp/Trello are triaged correctly
5. Linear becomes the single source of truth for mapache.app work
6. Other agents can call this as a sub-agent reliably
7. No outdated/personal tasks pollute the mapache project space

❌ **Red flags:**
- Personal tasks keep appearing in Linear
- Duplicates are missed (< 0.70 detection rate)
- Valid mapache work is filtered out
- Agent can't help other agents make decisions
- Linear becomes out-of-sync with actual mapache work

---

## 14. QUICK REFERENCE: mapache.app Tech Stack

```
┌─ ORCHESTRATION ─────────────────┐
│ Google ADK                      │
│ Vertex AI Agent Runtime         │
│ A2A Protocol (Agent-to-Agent)  │
└─────────────────────────────────┘

┌─ INTEGRATION ───────────────────┐
│ Composio (OAuth + MCP Provider) │
│ MCP Servers (Linear, GitHub)   │
│ OAuth 2.1 (Dynamic registration)│
└─────────────────────────────────┘

┌─ RENDERING ────────────────────┐
│ A2UI Protocol                   │
│ (Agent messages → UI elements)  │
└─────────────────────────────────┘

┌─ DATA ─────────────────────────┐
│ Firestore (operational/cache)   │
│ BigQuery (analytics/history)    │
│ SaaS sources (Linear, GitHub)   │
└────────────────────────────────┘

┌─ AI/ML ────────────────────────┐
│ Gemini (LLM)                    │
│ Vertex AI RAG Engine (embeddings)
│ [System of Intelligence TBD]    │
└────────────────────────────────┘

┌─ DEPLOYMENT ───────────────────┐
│ Google Cloud Platform (all)     │
│ Clerk (Multi-tenancy)           │
│ SaaS Boilerplate (app shell)    │
└────────────────────────────────┘
```

---

**END OF CONTEXT DOCUMENT**

*This document should be embedded in the Linear Semantic Agent's system prompt. Update as architecture evolves.*
