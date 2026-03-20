# pytest-doctor: CLI Guide

See [OVERVIEW.md](./OVERVIEW.md) for product overview and [ARCHITECTURE.md](./ARCHITECTURE.md) for the minimal pass architecture.

Command-line interface for running pytest-doctor's tool-backed analysis pipeline.

## Installation

```bash
pip install pytest-doctor
```

## Basic Usage

```bash
# Scan current project
pytest-doctor .

# Verbose output with file details
pytest-doctor . --verbose

# Score only (for scripts)
pytest-doctor . --score
```

## Analysis Passes

By default, pytest-doctor runs:

- Lint/quality pass (`ruff`, optional pytest-style checks)
- Coverage/gaps pass (`coverage`, typically via `pytest-cov`)
- Dead code pass (`vulture`, `pytest-deadfixtures`)
- Complexity pass (`radon`)

You can disable passes individually.

## Options

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--verbose` | `-v` | flag | false | Show detailed diagnostics with file:line |
| `--score` | `-s` | flag | false | Output only numeric score |
| `--format` | `-f` | string | `text` | Output format: `text` or `json` |
| `--output` | `-o` | string | stdout | Write report to file |
| `--diff` |  | string | none | Analyze changed files vs base branch |
| `--project` | `-p` | string | all | Select monorepo project(s) |
| `--config` | `-c` | string | auto | Path to config file |
| `--no-lint` |  | flag | false | Skip lint/quality pass |
| `--no-coverage` |  | flag | false | Skip coverage/gaps pass |
| `--no-dead-code` |  | flag | false | Skip dead code pass |
| `--no-complexity` |  | flag | false | Skip complexity pass |
| `--help` | `-h` | flag | false | Show help |
| `--version` |  | flag | false | Show version |

## Examples

### Standard scan

```bash
pytest-doctor tests/
```

### JSON output for CI

```bash
pytest-doctor . --format json --output report.json
```

### Coverage-focused scan

```bash
pytest-doctor . --no-lint --no-dead-code --no-complexity
```

### Fast lint-only check

```bash
pytest-doctor . --no-coverage --no-dead-code --no-complexity
```

### PR diff mode

```bash
pytest-doctor . --diff main --verbose
```

## Exit Codes

- `0`: score meets threshold
- `1`: score below threshold
- `2`: runtime/configuration error

## Environment Variables

| Variable | Description |
|---|---|
| `PYTEST_DOCTOR_CONFIG` | Path to config file |
| `PYTEST_DOCTOR_VERBOSE` | Enable verbose output |
| `PYTEST_DOCTOR_FORMAT` | Force output format (`text` or `json`) |
| `PYTEST_DOCTOR_COVERAGE_MIN` | Minimum coverage threshold |

## CI/CD Example

```yaml
- name: Run pytest-doctor
  run: |
    pip install pytest-doctor
    pytest-doctor . --format json --output pytest-doctor-report.json
```

## Notes

- pytest-doctor focuses on orchestration and scoring; heavy analysis is delegated to external tools.
- Keep your toolchain pinned in CI for stable diagnostics across environments.

## See Also

- [OVERVIEW.md](./OVERVIEW.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [CONFIG.md](./CONFIG.md)
- [SCORING.md](./SCORING.md)
