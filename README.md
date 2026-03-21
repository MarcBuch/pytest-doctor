# pytest-doctor

`pytest-doctor` is a CLI tool that diagnoses weak or broken pytest suites and provides a **0–100 health score** with actionable recommendations.

It combines linting, dead code detection, and test quality analysis to pinpoint gaps in test coverage, isolation issues, and performance problems—then integrates with coding agents for automated fixes.

## Core Capabilities

- **Gap analysis**: highlights what your tests miss (logic paths, edge cases, and risk areas)
- **Test quality checks**: detects fixture usage issues, isolation problems, missing parametrization
- **Dead code detection**: finds unused test utilities, fixtures, and helper functions
- **Scoring system**: 0–100 health metric (Critical <50, Needs work 50–74, Good 75+)
- **Agent-friendly output**: structured recommendations that coding agents can apply directly

## Quick Start

```bash
# Scan your project
pytest-doctor .

# Verbose mode with detailed paths
pytest-doctor . --verbose

# Scan only changed files
pytest-doctor . --diff main

# Request automated fixes via agent
pytest-doctor . --fix
```

## Configuration

Configure via `pytest-doctor.config.json`, `pyproject.toml`, or CLI flags:

```json
{
  "ignore": {
    "rules": ["custom/slow-test", "E501"],
    "files": ["tests/legacy/**"]
  },
  "lint": true,
  "deadCode": true,
  "testAnalysis": true,
  "verbose": false
}
```

## Architecture

The tool runs **three parallel analysis passes**:

1. **Linting** (ruff) – detects correctness, performance, security, and async issues
2. **Dead code detection** (vulture) – finds unused test utilities and fixtures
3. **Test quality** – flags isolation issues, missing parametrization, slow tests

Results are aggregated, scored, and rendered with actionable recommendations.

## Agent Integration

### Deeplinks (Remote Agents)

Generates deeplinks for remote coding agents to apply fixes automatically:

```bash
pytest-doctor . --fix
# Opens agent with diagnostics and project context
```

### Local Agent Integration

For local coding agents, use structured JSON output via stdin:

```bash
# Pipe diagnostics to your local agent
pytest-doctor . --json | your-agent --fix

# Or write to a temporary file
pytest-doctor . --output /tmp/diagnostics.json
your-agent /tmp/diagnostics.json --fix
```

The `--json` flag outputs complete diagnostics (issues, severity, file paths, line numbers) in a structured format that any agent can parse and act on.

---

**Goal**: let agents not only make tests pass, but make tests trustworthy.
