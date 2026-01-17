# Google Antigravity System Instructions & Workflows

## 1. Core Principles
- **Plan First:** Always generate a detailed `.md` plan before writing code. Wait for user feedback via comments.
- **Context Efficiency:** Do not read entire files unless necessary. Use search/grep to find specific functions.
- **Atomic Work:** Focus on one logical unit per conversation. Reference previous Chat IDs if context is needed.

## 2. Development Workflows

### Test-Driven Development (TDD)
1. Write test cases based on requirements.
2. **User Action:** Commit tests to Git.
3. Implement code to satisfy tests WITHOUT modifying the test files.
4. Iterate until all tests pass.

### Debug Mode (Evidence-Based)
When a bug is encountered:
1. Formulate a hypothesis.
2. Add logging statements to gather evidence.
3. Create a multi-phase plan to resolve the issue based on logs.

### UI/Visual Implementation
- Analyze provided screenshots to match styling and layout exactly.
- Use images to identify UI bugs that are difficult to describe in text.

## 3. Custom Rules & Skills
- **VAG Compliance:** All frontend code must follow accessibility standards (proper labels, ARIA tags).
- **Git Standards:** All commits must follow a structured format (e.g., `feat:`, `fix:`, `docs:`).
- **Architecture:** When requested, generate a Mermaid diagram to visualize the system flow before refactoring.

## 4. Skills Library (Located in .aagent/skills/)
- **Test Specialist:** Focused on writing robust unit and integration tests.
- **Code Reviewer:** Performs automated reviews highlighting issues by severity.
