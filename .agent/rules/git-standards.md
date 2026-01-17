# Git & Version Control Standards

## Commit Messages
Follow the Conventional Commits specification:
- `feat: ` for new features
- `fix: ` for bug fixes
- `docs: ` for documentation changes
- `style: ` for formatting changes (missing semi-colons, etc)
- `refactor: ` for code refactoring
- `test: ` for adding missing tests
- `chore: ` for maintenance tasks

## Workflow
- **Atomic Commits:** Commit often. Each commit should handle one logical change.
- **TDD Enforcement:** When doing TDD, commit the *failing test* before the implementation. This proves the test monitors the correct behavior.
