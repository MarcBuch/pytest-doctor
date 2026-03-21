---
name: pytest-doctor
description: A skill to use pytest-doctor for diagnosing and fixing test suite issues. Use this when asked to analyze or improve test health.
---

# pytest-doctor Skill

Use pytest-doctor to diagnose and fix test suite issues.

## Workflow

1. Run: `uv run pytest-doctor . --fix`
2. Parse the JSON output to get structured suggestions
3. Fix issues based on recommendations in each suggestion
4. Re-run to verify health score improves

## Output Structure

The `--fix` flag outputs JSON with:

- `context.health_score`: Current score (0-100)
- `suggestions`: Array of issues to fix with:
  - `file_path` and `line_number`: Where to fix
  - `rule_id`: Type of issue
  - `recommendation`: What to do
  - `severity`: critical, warning, or info

## Analysis Areas

- **Linting**: Code style, security, performance
- **Dead Code**: Unused fixtures and utilities
- **Test Quality**: Isolation issues, untested code paths, slow tests
