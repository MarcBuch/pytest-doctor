# pytest-doctor

`pytest-doctor` is a CLI tool that diagnoses weak or broken pytest suites and provides a **0–100 health score** with actionable recommendations.

It combines linting, dead code detection, and test quality analysis to pinpoint gaps in test coverage, isolation issues, and performance problems—then integrates with coding agents for automated fixes.

## Core Capabilities

- **Gap analysis**: highlights what your tests miss (logic paths, edge cases, and risk areas)
- **Test quality checks**: detects fixture usage issues, isolation problems, missing parametrization
- **Dead code detection**: finds unused test utilities, fixtures, and helper functions
- **Scoring system**: 0–100 health metric (Critical <50, Needs work 50–74, Good 75+)
- **Agent-friendly output**: structured recommendations that coding agents can apply directly

## Installation

Install pytest-doctor with uv:

```bash
uv pip install pytest-doctor
```

Or with pip:

```bash
pip install pytest-doctor
```

## Quick Start

```bash
# Scan your project
pytest-doctor .

# Verbose mode with detailed paths and recommendations
pytest-doctor . --verbose

# Scan only changed files (requires git)
pytest-doctor . --diff main

# Output results as JSON
pytest-doctor . --json

# Save JSON results to a file
pytest-doctor . --output results.json

# Request automated fixes via agent
pytest-doctor . --fix
```

## CLI Flags

- **PATH**: Directory to scan (default: current directory)
- **--verbose, -v**: Enable verbose output with detailed recommendations
- **--fix**: Generate agent-friendly output for automated fixes
- **--diff REF**: Scan only files changed compared to a git reference (e.g., `main`, `HEAD~1`)
- **--json**: Output complete diagnostics in JSON format to stdout
- **--output FILE**: Write JSON diagnostics to the specified file
- **--version**: Show version and exit
- **-h, --help**: Show help message

## Configuration

Configure via `pytest-doctor.config.json`, `pyproject.toml`, or CLI flags:

### pytest-doctor.config.json

```json
{
  "ignore": {
    "rules": ["E501", "custom/slow-test"],
    "files": ["tests/legacy/**", "tests/generated/**"]
  },
  "lint": true,
  "deadCode": true,
  "testAnalysis": true,
  "verbose": false
}
```

### pyproject.toml

```toml
[tool.pytest-doctor]
lint = true
deadCode = true
testAnalysis = true
verbose = false

[tool.pytest-doctor.ignore]
rules = ["E501", "custom/slow-test"]
files = ["tests/legacy/**", "tests/generated/**"]
```

### Configuration Options

- **lint** (bool): Enable ruff linting for test files (default: true)
- **deadCode** (bool): Enable vulture dead code detection (default: true)
- **testAnalysis** (bool): Enable test quality analysis (default: true)
- **verbose** (bool): Enable verbose output (default: false)
- **ignore.rules** (list): Rule IDs to ignore (e.g., "E501", "RUF001")
- **ignore.files** (list): File glob patterns to ignore

### Configuration Precedence

CLI flags override `pyproject.toml` settings, which override `pytest-doctor.config.json`, which override defaults.

## Architecture

The tool runs **three parallel analysis passes**:

1. **Linting** (ruff) – detects correctness, performance, security, and async issues
2. **Dead code detection** (vulture) – finds unused test utilities and fixtures
3. **Test quality** – flags isolation issues, missing parametrization, slow tests

Results are aggregated, scored, and rendered with actionable recommendations.

## Output Formats

### Human-Readable Output (default)

```
============================================================
pytest-doctor Diagnostic Report
============================================================

Health Score: 75/100 [⚠ NEEDS WORK]

Summary:
  Critical: 0
  Warning:  3
  Info:     12
  Total:    15

Findings:
------------------------------------------------------------

tests/test_example.py
  ⚠ Line 45: Line too long (120 > 100 characters) [E501]
  ℹ Line 67: Test test_example has 30 lines (>20 is a code smell) [large-test]
    → Break test into smaller, focused tests
...
```

Health score meanings:
- **75-100**: Good - Few issues found
- **50-74**: Needs Work - Multiple issues should be addressed
- **<50**: Critical - Suite requires significant improvements

### JSON Output

Use `--json` flag to output complete diagnostics:

```bash
pytest-doctor . --json
```

JSON Schema:

```json
{
  "version": "0.1.0",
  "path": ".",
  "score": 75,
  "summary": {
    "critical": 0,
    "warning": 3,
    "info": 12
  },
  "total_issues": 15,
  "results": [
    {
      "engine": "ruff",
      "issues": [
        {
          "file_path": "tests/test_example.py",
          "line_number": 45,
          "column_number": 100,
          "rule_id": "E501",
          "rule_name": "Line too long",
          "message": "Line too long (120 > 100 characters)",
          "severity": "warning",
          "source": "linting",
          "recommendation": "Break line into multiple lines"
        }
      ],
      "duration_ms": 125.45
    }
  ],
  "all_issues": [...],
  "issues": {
    "tests/test_example.py": [...]
  }
}
```

### Filtering by Changed Files

Scan only files changed relative to a git reference:

```bash
# Compare to main branch
pytest-doctor . --diff main

# Compare to a specific commit
pytest-doctor . --diff abc123

# Compare to previous version
pytest-doctor . --diff HEAD~1
```

This is useful for CI/CD pipelines to report only issues in changed code.

## Agent Integration

### JSON-Based Integration

For local or remote coding agents, use JSON output:

```bash
# Pipe diagnostics to your agent
pytest-doctor . --json | your-agent --fix

# Or save to file
pytest-doctor . --output diagnostics.json
your-agent diagnostics.json --fix
```

The JSON output includes:
- All issues with file paths, line numbers, and severity
- Actionable recommendations for each issue
- Health score and summary statistics
- Source information (which analyzer found the issue)

### Integration Examples

**Python-based agent:**

```python
import json
import subprocess

# Get diagnostics
result = subprocess.run(['pytest-doctor', '.', '--json'], 
                       capture_output=True, text=True)
diagnostics = json.loads(result.stdout)

# Process issues
for issue in diagnostics['all_issues']:
    print(f"Fix {issue['rule_id']} in {issue['file_path']}:{issue['line_number']}")
    print(f"Recommendation: {issue['recommendation']}")
```

**Shell-based agent:**

```bash
#!/bin/bash
pytest-doctor . --json | jq '.all_issues[] | 
  {file: .file_path, line: .line_number, msg: .recommendation}'
```

---

**Goal**: let agents not only make tests pass, but make tests trustworthy.

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Code Coverage

```bash
uv run pytest tests/ --cov=src/pytest_doctor --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## License

MIT
