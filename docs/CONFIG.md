# pytest-doctor: Configuration

See [OVERVIEW.md](./OVERVIEW.md) for quick start and [ARCHITECTURE.md](./ARCHITECTURE.md) for pass design.

pytest-doctor intentionally keeps configuration small. Most behavior comes from reused tools.

## Config File Search Order

1. `--config` flag
2. `PYTEST_DOCTOR_CONFIG` environment variable
3. `pytest_doctor.config.json` in project root
4. `[tool.pytest-doctor]` in `pyproject.toml`
5. Built-in defaults

## Minimal Recommended Config

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

## Options

| Key | Type | Default | Description |
|---|---|---|---|
| `lint` | bool | `true` | Enable lint/quality pass |
| `coverage` | bool | `true` | Enable coverage/gap pass |
| `deadCode` | bool | `true` | Enable dead code pass |
| `complexity` | bool | `true` | Enable complexity pass |
| `minimum_score` | int | `75` | Failing threshold for exit code |
| `ignore.rules` | string[] | `[]` | Ignore diagnostic categories/rules |
| `ignore.files` | string[] | `[]` | Ignore files via glob patterns |
| `output.format` | string | `text` | `text` or `json` |
| `output.verbose` | bool | `false` | Show expanded findings |

## Tool-Specific Overrides (Optional)

Use these only when needed. Keep defaults otherwise.

```json
{
  "tools": {
    "ruff": {
      "args": ["--select", "E,F,PT"]
    },
    "coverage": {
      "branch": true,
      "min": 85
    },
    "vulture": {
      "min_confidence": 80
    },
    "radon": {
      "max_cc": 10
    }
  }
}
```

## Environment Variables

| Variable | Description |
|---|---|
| `PYTEST_DOCTOR_CONFIG` | Path to config file |
| `PYTEST_DOCTOR_VERBOSE` | Force verbose mode |
| `PYTEST_DOCTOR_FORMAT` | Force `text` or `json` output |
| `PYTEST_DOCTOR_COVERAGE_MIN` | Override coverage threshold |

## `pyproject.toml` Example

```toml
[tool.pytest-doctor]
lint = true
coverage = true
deadCode = true
complexity = true
minimum_score = 75

[tool.pytest-doctor.ignore]
rules = ["ruff/F401"]
files = ["tests/fixtures/**"]

[tool.pytest-doctor.output]
format = "text"
verbose = false
```

## Practical Profiles

### Fast local iteration

```json
{
  "coverage": false,
  "deadCode": false,
  "complexity": false,
  "lint": true
}
```

### Strict CI gate

```json
{
  "minimum_score": 85,
  "lint": true,
  "coverage": true,
  "deadCode": true,
  "complexity": true
}
```

## Notes

- CLI flags should override config values.
- Keep ignored rules explicit and documented in your repo.
- Prefer configuring underlying tools (`ruff.toml`, coverage config) for deep rule tuning.

## See Also

- [CLI.md](./CLI.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SCORING.md](./SCORING.md)
