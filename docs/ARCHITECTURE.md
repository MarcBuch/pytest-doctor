# pytest-doctor: Minimal Architecture

See [OVERVIEW.md](./OVERVIEW.md) for product-level introduction.

## Goal

Keep pytest-doctor small and reliable by reusing proven Python tools instead of building custom analyzers for everything.

## Design Principles

1. Reuse mature tooling first (`coverage`, `ruff`, `vulture`, etc.)
2. Normalize all tool output into one diagnostic contract
3. Keep only a few analysis passes with clear ownership
4. Prefer configuration over bespoke analyzer code
5. Score based on diagnostics, not internal implementation details

## Minimal Pipeline

pytest-doctor runs four passes and merges the results:

1. **Lint/Quality pass**
   - Primary tools: `ruff`, optional `flake8-pytest-style`
   - Focus: pytest style, correctness, maintainability, common anti-patterns

2. **Coverage/Gaps pass**
   - Primary tools: `coverage` (via `pytest-cov`)
   - Focus: line and branch coverage, untested modules/functions/paths

3. **Dead code pass**
   - Primary tools: `vulture`, `pytest-deadfixtures`
   - Focus: unused code and unused fixtures

4. **Complexity pass**
   - Primary tool: `radon`
   - Focus: high-complexity functions that should have stronger tests

These passes run independently where possible and are merged into one result.

## Tooling Map

| Concern | Preferred Tool | Why |
|---|---|---|
| Test/code quality | `ruff` | Fast, widely adopted, rich ruleset |
| Pytest-specific style | `flake8-pytest-style` (optional) | Mature pytest lint coverage |
| Coverage and branches | `coverage` + `pytest-cov` | Ecosystem standard |
| Dead code | `vulture` | Practical unused symbol detection |
| Dead fixtures | `pytest-deadfixtures` | Purpose-built for pytest suites |
| Complexity | `radon` | Standard cyclomatic complexity metrics |

## Unified Diagnostic Contract

All pass outputs should be converted to a common shape:

```python
Diagnostic(
    type="quality|gap|coverage|dead-code|complexity",
    category="tool/rule-or-check",
    file="path/to/file.py",
    line=12,
    column=1,
    severity="error|warning|info",
    message="Human-readable issue",
    help="Why this matters",
    suggestion="How to fix (optional)",
)
```

This keeps CLI, JSON output, and scoring decoupled from specific tools.

## Scoring Model

Start from 100 and subtract weighted penalties by severity:

- `error`: high penalty
- `warning`: medium penalty
- `info`: low penalty

Optional category multipliers:

- `gap/*` diagnostics weighted higher than style-only warnings
- `dead-code/*` and `complexity/*` weighted medium

The score is then clamped to `0..100` and mapped to labels:

- `75-100`: Excellent
- `50-74`: Needs Work
- `<50`: Critical

## Runtime Flow

```text
Project Path
  -> discover context (source roots, tests, config)
  -> run enabled passes (parallel where safe)
  -> normalize tool output -> Diagnostic[]
  -> apply ignore filters (rules/files)
  -> compute score + breakdown
  -> emit text/json report
```

## Minimal Configuration Surface

Recommended baseline:

```json
{
  "lint": true,
  "coverage": true,
  "deadCode": true,
  "complexity": true,
  "minimum_score": 75,
  "ignore": {
    "rules": ["ruff/F401"],
    "files": ["tests/fixtures/**"]
  }
}
```

Keep advanced options optional and tool-specific only when needed.

## Why This Is Simpler

- No need for many custom AST analyzers with overlapping responsibilities
- Easier maintenance by delegating rule correctness to upstream tools
- Faster iteration: upgrade tool versions to gain new checks
- More predictable output and fewer internal edge cases

## Implementation Notes

Recommended internal modules:

- `passes/lint_pass.py`
- `passes/coverage_pass.py`
- `passes/dead_code_pass.py`
- `passes/complexity_pass.py`
- `engine.py` (orchestrates passes + merge)
- `adapters/` (tool output to `Diagnostic` mapping)
- `scoring.py` (single scoring policy)

## Future Extensions

Optional additions that do not change the core design:

- Add `mypy` diagnostics as a separate optional pass
- Add `bandit`/`pip-audit` security diagnostics
- Add `--diff` mode using changed files from git

The architecture remains stable because these are just new adapters + pass toggles.
