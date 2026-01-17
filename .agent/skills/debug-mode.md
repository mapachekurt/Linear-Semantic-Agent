---
name: debug-mode
description: A systematic, evidence-based approach to solving complex bugs.
---

# Skill: Debug Mode

## Description
A systematic, evidence-based approach to solving complex bugs.

## Workflow
1.  **Hypothesize:** State clear hypotheses about what is causing the bug.
2.  **Instrument:** Add targeted logging (`console.log`, `print`, or specialized logger) to capture runtime state at critical failure points.
3.  **Reproduce:** Run the code to generate the logs.
4.  **Analyze:** precise the root cause based on log evidence, not guesses.
5.  **Fix:** Implement the fix.
6.  **Verify:** Remove instrumentation and run tests to confirm the fix.
