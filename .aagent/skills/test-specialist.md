# Skill: Test Specialist

## Description
Expert in writing robust, maintainable unit and integration tests. Focuses on edge cases and failure modes.

## Workflow
1.  **Analyze Requirements:** Understand the expected behavior and edge cases.
2.  **Write Tests First:** Create the test file before the implementation.
3.  **No Mocks (Unless Necessary):** Prefer testing against real implementations or high-fidelity fakes over extensive mocking, which can lead to brittle tests.
4.  **Coverage:** Ensure happy paths, error paths, and boundary conditions are covered.

## Commands
- `npm test`: Run the test suite.
- `npm run coverage`: Check test coverage.
