# pytest-doctor: CLI Guide

See [OVERVIEW.md](./OVERVIEW.md) for overview and [API.md](./API.md) for Python API.

Command-line interface for running pytest-doctor analysis.

## Installation

```bash
pip install pytest-doctor
```

Or use with pipx:

```bash
pipx install pytest-doctor
```

## Basic Usage

```bash
# Scan test suite in current directory
pytest-doctor .

# Scan specific directory
pytest-doctor ./tests

# Scan with verbose output (show all files)
pytest-doctor . --verbose
```

## Commands

### scan (default)

Analyzes test suite and outputs results.

```bash
pytest-doctor <directory> [options]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--verbose` | `-v` | flag | false | Show detailed output with file:line |
| `--score` | `-s` | flag | false | Output only the health score |
| `--format` | `-f` | string | `text` | Output format: text, json, html |
| `--diff` | | string | none | Only scan changed files vs branch |
| `--project` | `-p` | string | all | Scan specific project (monorepo) |
| `--output` | `-o` | string | stdout | Write output to file |
| `--no-coverage` | | flag | false | Skip coverage analysis |
| `--no-gaps` | | flag | false | Skip gap detection |
| `--no-rules` | | flag | false | Skip quality rule checks |
| `--github-token` | | string | none | Enable GitHub PR comment posting |
| `--config` | `-c` | string | auto | Path to config file |
| `--help` | `-h` | flag | false | Show help |
| `--version` | | flag | false | Show version |

### Examples

#### Basic scan
```bash
pytest-doctor tests/
```

Output:
```
pytest-doctor Report
====================

📊 Score: 72/100 (Needs Work)

GAPS & MISSING EDGE CASES (Critical)
────────────────────────────────────
❌ auth.py::validate_token
   └─ Missing exception test: TokenExpiredException

QUALITY ISSUES (12)
──────────────────
⚠️  assertions/missing-messages (8 issues)
⚠️  fixtures/unused-fixtures (4 issues)

COVERAGE SUMMARY
────────────────
Overall: 82% | Excellent
By file:
  - src/auth.py:        95% ✅
  - src/database.py:    78% ⚠️
  - src/email.py:       42% ❌
```

#### Verbose output
```bash
pytest-doctor tests/ --verbose
```

Shows file paths and line numbers:

```
GAPS & MISSING EDGE CASES (Critical)
────────────────────────────────────
❌ gap/missing-exception-tests (error)
   src/auth.py:45:validate_token
   └─ TokenExpiredException never tested
   └─ Suggestion: test_validate_token_raises_on_expired

QUALITY ISSUES
──────────────
⚠️  assertions/missing-messages (8 issues)
   tests/test_auth.py:12: assert token is not None
   tests/test_auth.py:25: assert user.email == "user@example.com"
   tests/test_user.py:8: assert username is not None
   ... (5 more)
```

#### Score only
```bash
pytest-doctor tests/ --score
```

Output:
```
72
```

Perfect for scripts and CI/CD:

```bash
SCORE=$(pytest-doctor tests/ --score)
if [ "$SCORE" -lt 75 ]; then
    echo "Test coverage score too low: $SCORE/100"
    exit 1
fi
```

#### JSON output
```bash
pytest-doctor tests/ --format json
```

Output (for programmatic use):
```json
{
  "score": {
    "value": 72,
    "label": "Needs Work",
    "breakdown": {
      "coverage": 10,
      "quality": 12,
      "gaps": 6
    }
  },
  "coverage": {
    "overall": 82,
    "by_file": {
      "src/auth.py": 95,
      "src/database.py": 78,
      "src/email.py": 42
    }
  },
  "gaps": [
    {
      "type": "gap/missing-exception-tests",
      "file": "src/auth.py",
      "function": "validate_token",
      "line": 45,
      "severity": "error",
      "message": "TokenExpiredException never tested",
      "suggestion": "test_validate_token_raises_on_expired"
    }
  ],
  "diagnostics": [
    {
      "type": "quality",
      "category": "assertions/missing-messages",
      "file": "tests/test_auth.py",
      "line": 12,
      "severity": "warning",
      "message": "Assert lacks message for debugging"
    }
  ]
}
```

#### Diff mode
```bash
# Only analyze files changed vs main branch
pytest-doctor . --diff main

# Only analyze files changed vs origin/main
pytest-doctor . --diff origin/main

# Auto-detect base branch
pytest-doctor . --diff
```

Perfect for pull request analysis - only check changed test files.

#### Specific project (monorepo)
```bash
pytest-doctor . --project web
pytest-doctor . --project api,web
```

#### HTML report
```bash
pytest-doctor tests/ --format html --output report.html
```

Creates interactive HTML report (opens in browser).

#### GitHub integration
```bash
pytest-doctor . --github-token $GITHUB_TOKEN
```

Posts results as PR comment on GitHub Actions.

Requires:
- Running in GitHub Actions
- `GITHUB_TOKEN` environment variable set
- Pull request event

Comment will show:
- Overall score
- Top gaps to fix
- Critical issues

#### Custom config
```bash
pytest-doctor . --config custom_config.json
```

### Configuration File

See [CONFIG.md](./CONFIG.md) for full configuration reference.

File search order:
1. `--config` flag value
2. `pytest_doctor.config.json` in project root
3. `pytest_doctor.config` key in `pyproject.toml`
4. `tool.pytest-doctor` in `pyproject.toml`
5. Default configuration

## Exit Codes

- `0`: Success (score >= minimum, or minimum disabled)
- `1`: Failure (score < minimum)
- `2`: Error (invalid arguments, file not found, etc.)

Example:
```bash
pytest-doctor tests/
if [ $? -eq 0 ]; then
    echo "Tests passed quality threshold"
else
    echo "Tests need improvement"
    exit 1
fi
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PYTEST_DOCTOR_CONFIG` | Path to config file (overrides `--config`) |
| `PYTEST_DOCTOR_VERBOSE` | Enable verbose output |
| `PYTEST_DOCTOR_FORMAT` | Output format (text, json, html) |
| `PYTEST_DOCTOR_COVERAGE_MIN` | Minimum coverage threshold |

Example:
```bash
export PYTEST_DOCTOR_CONFIG=/etc/pytest-doctor.json
export PYTEST_DOCTOR_VERBOSE=1
pytest-doctor tests/
```

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Run pytest-doctor
  uses: your-org/pytest-doctor@v1
  with:
    directory: tests
    verbose: true
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

### GitLab CI

```yaml
test-quality:
  script:
    - pip install pytest-doctor
    - pytest-doctor tests/ --format json --output report.json
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: report.json
```

### Jenkins

```groovy
stage('Test Quality') {
    steps {
        sh 'pip install pytest-doctor'
        sh 'pytest-doctor tests/ --format json --output report.json'
        publishHTML([
            allowMissing: false,
            alwaysLinkToLastBuild: true,
            keepAll: true,
            reportDir: '.',
            reportFiles: 'report.html',
            reportName: 'pytest-doctor'
        ])
    }
}
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-doctor
        name: pytest-doctor
        entry: pytest-doctor tests/ --score
        language: system
        pass_filenames: false
        stages: [commit]
```

## Troubleshooting

### "No test files found"

```bash
# Explicit path
pytest-doctor ./tests

# Check directory structure
ls -la tests/
```

### Coverage data not found

```bash
# Run tests first
pytest tests/ --cov=src

# Then analyze
pytest-doctor tests/
```

### Config file not loading

```bash
# Check path
pytest-doctor . --config /path/to/config.json

# Validate JSON
python -m json.tool pytest_doctor.config.json
```

### Tests run very slowly

```bash
# Skip coverage to speed up
pytest-doctor . --no-coverage

# Check for expensive fixtures
pytest-doctor . --verbose | grep "slow"
```

## Output Colors

When outputting to terminal:

- 🟢 Green: Excellent/good
- 🟡 Yellow: Warning/needs attention
- 🔴 Red: Error/critical

Disable colors:
```bash
pytest-doctor tests/ | cat  # pipe disables colors
NO_COLOR=1 pytest-doctor tests/
```

## See Also

- [OVERVIEW.md](./OVERVIEW.md) - Quick start
- [API.md](./API.md) - Python API
- [CONFIG.md](./CONFIG.md) - Configuration
- [LLM_AGENTS.md](./LLM_AGENTS.md) - Agent integration
