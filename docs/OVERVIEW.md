# pytest-doctor: Overview

**pytest-doctor** is a diagnostic tool that analyzes Python pytest test suites to identify quality issues, coverage gaps, dead code, and risky complexity. It outputs a **0-100 health score** with actionable diagnostics designed for LLM coding agents.

> See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design.

## What It Does

pytest-doctor runs a minimal multi-pass pipeline by reusing established Python tools.

### Reused Tools

- **ruff** for lint and quality diagnostics
- **coverage + pytest-cov** for line/branch coverage and gap signals
- **vulture** for dead code detection
- **pytest-deadfixtures** for unused fixture detection
- **radon** for complexity heuristics

### Analysis Passes

pytest-doctor performs four focused passes:

### 1. Test Quality Analysis
Scans for best practice violations in test structure, assertions, fixtures, and mocking.

**Example:**
```
⚠️  assertions/missing-messages (warning)
    tests/auth_test.py:25
    assert token is not None
    └─ Assertion lacks descriptive message for debugging
```

> See [RULES.md](./RULES.md) for diagnostic categories and examples.

### 2. Coverage Gap Detection
Identifies untested functions, uncovered branches, and missing exception handling tests.

**Example:**
```
❌ gap/missing-exception-tests (error)
    src/auth.py::validate_token
    └─ Function raises TokenExpiredException but never tested
```

> See [GAP_DETECTION.md](./GAP_DETECTION.md) for gap detection strategy.

### 3. Dead Code Analysis
Detects unused symbols and unused fixtures that reduce test clarity and confidence.

**Example:**
```
⚠️  dead-code/unused-function (warning)
    src/helpers.py:18
    └─ Function `normalize_data` appears unused
```

### 4. Complexity Analysis
Flags high-complexity functions where additional tests are strongly recommended.

**Example:**
```
⚠️  complexity/high-cyclomatic-complexity (warning)
    src/auth.py::validate_token
    └─ Complexity score 14 exceeds threshold 10
```

## Health Score

A single **0-100 score** summarizes test suite quality:

- **75-100**: Excellent (Great test coverage and quality)
- **50-74**: Needs Work (Some gaps and quality issues)
- **<50**: Critical (Major improvements needed)

> See [SCORING.md](./SCORING.md) for scoring algorithm details.

## Quick Start

### CLI Usage
```bash
# Basic scan
pytest-doctor .

# Verbose with file details
pytest-doctor . --verbose

# Only show score
pytest-doctor . --score

# Skip coverage pass
pytest-doctor . --no-coverage
```

> See [CLI.md](./CLI.md) for all available commands.

### Python API
```python
from pytest_doctor import diagnose

result = diagnose("./tests")
print(result.score)         # {"score": 72, "label": "Needs work"}
print(result.diagnostics)   # List of gaps and issues
```

> See [API.md](./API.md) for API reference.

### Configuration
```json
{
  "minimum_score": 75,
  "lint": true,
  "coverage": true,
  "deadCode": true,
  "complexity": true,
  "ignore": {
    "rules": ["ruff/F401"],
    "files": ["tests/fixtures/**"]
  }
}
```

> See [CONFIG.md](./CONFIG.md) for configuration options.

## For LLM Agents

pytest-doctor provides structured output ideal for LLM coding agents to:

1. **Identify gaps** in test coverage
2. **Understand requirements** for new tests
3. **Generate missing tests** with edge cases
4. **Improve test quality** following best practices
5. **Verify improvements** with rescanning

### Example Agent Integration
```python
# Agent receives structured diagnostics
diagnostics = run_pytest_doctor()

for gap in diagnostics.gaps:
    # Generate test based on gap description
    test_code = agent.generate_test(gap)
    # Write and verify
    save_test(test_code)
    # Rescan to verify gap fixed
    new_result = run_pytest_doctor()
```

> See [LLM_AGENTS.md](./LLM_AGENTS.md) for agent integration guide.

## Architecture

pytest-doctor consists of:

1. **Pass Runner**: Orchestrates enabled passes (parallel where possible)
2. **Tool Adapters**: Converts external tool output into unified diagnostics
3. **Scorer**: Calculates 0-100 health score from severity-weighted findings
4. **Reporter**: Formats results for CLI and APIs

> See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture.

## Features

- ✅ **Quality diagnostics** powered by Ruff and pytest tooling
- ✅ **Coverage and gap detection** powered by coverage.py
- ✅ **Dead code and unused fixture detection**
- ✅ **Complexity-driven test risk signals**
- ✅ **LLM-ready output** structured for coding agents
- ✅ **Configurable** via pytest_doctor.config.json
- ✅ **CLI and Python API** for flexibility
- ✅ **GitHub Actions** integration
- ✅ **Diff mode** for only changed files

## Examples

```bash
# See results for your test suite
pytest-doctor tests/ --verbose

# Only check specific project in monorepo
pytest-doctor . --project my-package

# Check only changes vs main branch
pytest-doctor . --diff main

# Integration with CI/CD
pytest-doctor . --github-token $GITHUB_TOKEN
```

> See [EXAMPLES.md](./EXAMPLES.md) for more usage examples.

## Next Steps

- [Architecture Overview](./ARCHITECTURE.md) - Understand the system design
- [Diagnostic Rules](./RULES.md) - See all quality checks
- [Gap Detection](./GAP_DETECTION.md) - Learn about coverage gap detection
- [Edge Cases](./EDGE_CASES.md) - Explore edge case categories
- [Configuration](./CONFIG.md) - Customize behavior
- [CLI Guide](./CLI.md) - Complete command reference
- [Python API](./API.md) - Use programmatically
- [LLM Integration](./LLM_AGENTS.md) - Build agent workflows
