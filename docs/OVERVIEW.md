# pytest-doctor: Overview

**pytest-doctor** is a diagnostic tool that analyzes Python pytest test suites to identify quality issues, coverage gaps, and missing edge cases. It outputs a **0-100 health score** with actionable diagnostics designed for LLM coding agents.

> See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design.

## What It Does

pytest-doctor performs three levels of analysis:

### 1. Test Quality Analysis
Scans for best practice violations in test structure, assertions, fixtures, and mocking.

**Example:**
```
⚠️  assertions/missing-messages (warning)
    tests/auth_test.py:25
    assert token is not None
    └─ Assertion lacks descriptive message for debugging
```

> See [RULES.md](./RULES.md) for all 40+ diagnostic rules.

### 2. Coverage Gap Detection
Identifies untested functions, uncovered branches, and missing exception handling tests.

**Example:**
```
❌ gap/missing-exception-tests (error)
    src/auth.py::validate_token
    └─ Function raises TokenExpiredException but never tested
```

> See [GAP_DETECTION.md](./GAP_DETECTION.md) for gap detection strategy.

### 3. Edge Case Analysis
Detects missing boundary value tests, state transition gaps, and special case scenarios.

**Example:**
```
❌ gap/missing-boundary-tests (error)
    src/utils.py::truncate_string
    ├─ Empty string input
    ├─ Unicode character boundaries
    └─ Length equals max_length
```

> See [EDGE_CASES.md](./EDGE_CASES.md) for edge case categories.

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

# Auto-fix with agent
pytest-doctor . --fix
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
  "gaps": {
    "enabled": true,
    "minimum-coverage": 85
  },
  "ignore": {
    "rules": ["assertions/multiple-assertions"],
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

1. **Code Analyzer**: AST-based analysis of source code
2. **Test Analyzer**: Analysis of test files and structure
3. **Coverage Engine**: Integration with coverage.py data
4. **Gap Detector**: Identifies untested code paths
5. **Edge Case Detector**: Finds missing boundary/special cases
6. **Scorer**: Calculates 0-100 health score
7. **Reporter**: Formats results for CLI and APIs

> See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture.

## Features

- ✅ **40+ diagnostic rules** for test quality
- ✅ **Automatic gap detection** of untested functions and branches
- ✅ **Edge case suggestions** for boundary values and error paths
- ✅ **LLM-ready output** structured for coding agents
- ✅ **Configurable** via pytest_doctor.config.json
- ✅ **CLI and Python API** for flexibility
- ✅ **GitHub Actions** integration
- ✅ **Diff mode** for only changed files
- ✅ **Auto-fix** support with agent integration

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
