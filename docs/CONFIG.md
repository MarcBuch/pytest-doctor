# pytest-doctor: Configuration

See [OVERVIEW.md](./OVERVIEW.md) for quick start.

Customize pytest-doctor behavior with `pytest_doctor.config.json` or environment variables.

## Configuration File Location

pytest-doctor searches for config in this order:

1. `--config` CLI flag
2. `pytest_doctor.config.json` in project root
3. `[tool.pytest-doctor]` in `pyproject.toml`
4. `[tool.pytest_doctor]` in `setup.cfg`
5. Built-in defaults

## Basic Configuration

### Minimal Config

```json
{
  "gaps": {
    "enabled": true,
    "minimum_coverage": 85
  }
}
```

### Full Config Example

```json
{
  "coverage": {
    "enabled": true,
    "minimum": 85,
    "branches": true,
    "exclude": [
      "tests/**",
      "**/*_pb2.py",
      "**/*.pyi"
    ]
  },
  
  "gaps": {
    "enabled": true,
    "detection": {
      "untested_functions": true,
      "uncovered_branches": true,
      "missing_exceptions": true,
      "state_transitions": true,
      "edge_cases": true
    },
    "minimum_coverage": 85
  },
  
  "rules": {
    "structure/test-file-naming": {
      "enabled": true,
      "severity": "warning"
    },
    "assertions/multiple-assertions-per-test": {
      "enabled": true,
      "severity": "warning",
      "max_assertions": 5
    }
  },
  
  "ignore": {
    "rules": [
      "performance/slow-tests",
      "structure/descriptive-test-names"
    ],
    "files": [
      "tests/integration/**",
      "tests/fixtures/**",
      "**/*_fixtures.py"
    ]
  },
  
  "scoring": {
    "weights": {
      "coverage": 1.0,
      "quality": 0.8,
      "gaps": 1.2
    },
    "minimum_score": 75
  }
}
```

## Configuration Options

### `coverage`

Code coverage settings.

```json
{
  "coverage": {
    "enabled": true,
    "minimum": 80,
    "branches": true,
    "exclude": [
      "tests/**",
      "**/conftest.py"
    ]
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | true | Enable coverage analysis |
| `minimum` | int | 80 | Minimum coverage % threshold |
| `branches` | bool | true | Measure branch coverage |
| `exclude` | string[] | [] | File patterns to exclude |

### `gaps`

Gap detection settings.

```json
{
  "gaps": {
    "enabled": true,
    "detection": {
      "untested_functions": true,
      "uncovered_branches": true,
      "missing_exceptions": true,
      "state_transitions": true,
      "edge_cases": true
    },
    "minimum_coverage": 85,
    "suggest_tests": true
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | true | Enable gap detection |
| `detection.untested_functions` | bool | true | Detect untested functions |
| `detection.uncovered_branches` | bool | true | Detect uncovered branches |
| `detection.missing_exceptions` | bool | true | Detect untested exceptions |
| `detection.state_transitions` | bool | true | Detect untested state transitions |
| `detection.edge_cases` | bool | true | Detect missing edge cases |
| `minimum_coverage` | int | 85 | Minimum coverage for functions |
| `suggest_tests` | bool | true | Generate test suggestions |

### `rules`

Control individual diagnostic rules.

```json
{
  "rules": {
    "structure/test-file-naming": {
      "enabled": true,
      "severity": "warning"
    },
    "assertions/multiple-assertions-per-test": {
      "enabled": true,
      "severity": "warning",
      "max_assertions": 5
    },
    "assertions/float-comparison-equality": {
      "enabled": true,
      "severity": "error"
    }
  }
}
```

**Rule-specific options:**

- `structure/test-file-naming`: (no options)
- `assertions/multiple-assertions-per-test`: `max_assertions` (default: 3)
- `fixtures/complex-fixture-dependencies`: `max_depth` (default: 3)
- `performance/slow-tests`: `max_duration_ms` (default: 1000)

See [RULES.md](./RULES.md) for all available rules.

### `ignore`

Exclude specific rules and files from analysis.

```json
{
  "ignore": {
    "rules": [
      "performance/slow-tests",
      "structure/descriptive-test-names"
    ],
    "files": [
      "tests/integration/**",
      "tests/e2e/**",
      "**/conftest.py",
      "**/*_fixtures.py"
    ]
  }
}
```

File patterns support glob syntax:
- `*` - Match any characters
- `**` - Match any directories
- `?` - Match single character
- `[abc]` - Match any in brackets

### `scoring`

Scoring algorithm customization.

```json
{
  "scoring": {
    "weights": {
      "coverage": 1.0,
      "quality": 0.8,
      "gaps": 1.2
    },
    "penalties": {
      "error": 5,
      "warning": 2,
      "info": 0.5
    },
    "gap_penalties": {
      "untested_function": 5,
      "uncovered_branch": 3,
      "missing_exception": 4,
      "missing_edge_case": 1
    },
    "minimum_score": 75
  }
}
```

See [SCORING.md](./SCORING.md) for scoring details.

### `output`

Output formatting options.

```json
{
  "output": {
    "format": "text",
    "colors": true,
    "verbose": false,
    "show_metadata": true,
    "max_diagnostics": 50
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `format` | string | "text" | Output format: text, json, html |
| `colors` | bool | true | Use colored output |
| `verbose` | bool | false | Show detailed output |
| `show_metadata` | bool | true | Show timing and metadata |
| `max_diagnostics` | int | 50 | Max diagnostics to show |

### `github`

GitHub Actions integration.

```json
{
  "github": {
    "post_comment": true,
    "fail_on_score": 75,
    "fail_on_gaps": true,
    "fail_on_errors": true
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `post_comment` | bool | true | Post PR comment |
| `fail_on_score` | int | 75 | Fail if score < threshold |
| `fail_on_gaps` | bool | true | Fail if gaps detected |
| `fail_on_errors` | bool | true | Fail if errors found |

### `monorepo`

Monorepo project settings.

```json
{
  "monorepo": {
    "enabled": true,
    "projects": [
      {
        "name": "web",
        "path": "packages/web",
        "coverage_minimum": 85
      },
      {
        "name": "api",
        "path": "packages/api",
        "coverage_minimum": 90
      }
    ]
  }
}
```

## Severity Levels

```json
{
  "rules": {
    "my-rule": {
      "severity": "error"     // Critical issue (red, -5 points)
    },
    "other-rule": {
      "severity": "warning"   // Important issue (yellow, -2 points)
    },
    "nice-rule": {
      "severity": "info"      // Nice-to-have (blue, -0.5 points)
    }
  }
}
```

## Environment Variables

Override config with environment variables (higher priority):

| Variable | Description |
|----------|-------------|
| `PYTEST_DOCTOR_CONFIG` | Path to config file |
| `PYTEST_DOCTOR_COVERAGE_MIN` | Minimum coverage % |
| `PYTEST_DOCTOR_VERBOSE` | Enable verbose output |
| `PYTEST_DOCTOR_FORMAT` | Output format |
| `PYTEST_DOCTOR_NO_COLOR` | Disable colors |

Example:
```bash
export PYTEST_DOCTOR_COVERAGE_MIN=90
export PYTEST_DOCTOR_VERBOSE=1
pytest-doctor tests/
```

## pyproject.toml

Configure in `pyproject.toml`:

```toml
[tool.pytest-doctor]
verbose = true

[tool.pytest-doctor.coverage]
enabled = true
minimum = 85

[tool.pytest-doctor.gaps]
enabled = true
minimum_coverage = 85

[tool.pytest-doctor.ignore]
rules = [
  "performance/slow-tests",
  "structure/descriptive-test-names"
]
files = [
  "tests/integration/**",
  "tests/fixtures/**"
]

[tool.pytest-doctor.scoring]
minimum_score = 75
```

## setup.cfg

Configure in `setup.cfg`:

```ini
[pytest-doctor]
verbose = true
coverage_minimum = 85

[pytest-doctor:coverage]
enabled = true
branches = true

[pytest-doctor:gaps]
enabled = true
minimum_coverage = 85

[pytest-doctor:ignore]
rules =
    performance/slow-tests
    structure/descriptive-test-names
files =
    tests/integration/**
    tests/fixtures/**
```

## Config Precedence

1. **CLI flags** (highest priority)
   ```bash
   pytest-doctor . --coverage-min 90
   ```

2. **Environment variables**
   ```bash
   export PYTEST_DOCTOR_COVERAGE_MIN=90
   ```

3. **Config file** (`--config` flag)
   ```bash
   pytest-doctor . --config custom.json
   ```

4. **Local config files** (in order)
   - `pytest_doctor.config.json`
   - `pyproject.toml`
   - `setup.cfg`

5. **Built-in defaults** (lowest priority)

## Examples

### Strict Testing Standards

```json
{
  "coverage": {
    "minimum": 95
  },
  "gaps": {
    "enabled": true,
    "minimum_coverage": 95
  },
  "scoring": {
    "minimum_score": 85
  }
}
```

### Startup Project

```json
{
  "coverage": {
    "minimum": 60
  },
  "gaps": {
    "enabled": true,
    "minimum_coverage": 60
  },
  "ignore": {
    "rules": ["performance/slow-tests"],
    "files": ["tests/integration/**"]
  }
}
```

### Legacy Project Migration

```json
{
  "coverage": {
    "minimum": 40,
    "exclude": ["src/legacy/**"]
  },
  "gaps": {
    "minimum_coverage": 40
  },
  "ignore": {
    "rules": [
      "structure/descriptive-test-names",
      "assertions/missing-assertion-message"
    ],
    "files": [
      "tests/legacy/**",
      "tests/old_code_test.py"
    ]
  }
}
```

### Monorepo

```json
{
  "monorepo": {
    "enabled": true,
    "projects": [
      {
        "name": "web",
        "path": "packages/web",
        "coverage_minimum": 85
      },
      {
        "name": "api",
        "path": "packages/api",
        "coverage_minimum": 90
      },
      {
        "name": "cli",
        "path": "packages/cli",
        "coverage_minimum": 75
      }
    ]
  }
}
```

## Validating Config

```bash
# Check if config is valid
python -m json.tool pytest_doctor.config.json

# Test config with dry-run
pytest-doctor . --config pytest_doctor.config.json --verbose
```

## See Also

- [OVERVIEW.md](./OVERVIEW.md) - Quick start
- [RULES.md](./RULES.md) - Diagnostic rules
- [SCORING.md](./SCORING.md) - Scoring details
- [CLI.md](./CLI.md) - CLI usage
