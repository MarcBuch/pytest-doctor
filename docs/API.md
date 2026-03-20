# pytest-doctor: Python API

See [OVERVIEW.md](./OVERVIEW.md) for product overview and [ARCHITECTURE.md](./ARCHITECTURE.md) for pass design.

Use pytest-doctor programmatically to run a minimal, tool-backed analysis pipeline.

## Installation

```bash
pip install pytest-doctor
```

## Core API

### `diagnose()`

```python
from typing import Any
from pytest_doctor import diagnose

result = diagnose(
    path=".",
    config={
        "lint": True,
        "coverage": True,
        "deadCode": True,
        "complexity": True,
    },
)
```

`diagnose()` orchestrates passes, normalizes diagnostics, computes a score, and returns a `Results` object.

## Result Model

### `Results`

```python
@dataclass
class Results:
    score: Score
    diagnostics: list[Diagnostic]
    gaps: list[Gap]
    edge_cases: list[EdgeCase]
    coverage: CoverageStats
    project_info: ProjectInfo
    metadata: dict[str, Any]
```

Notes:

- `diagnostics` is the canonical output list across all passes.
- `gaps`/`edge_cases` are optional convenience views derived from diagnostics.

### `Diagnostic`

```python
@dataclass
class Diagnostic:
    type: str        # quality|gap|coverage|dead-code|complexity
    category: str    # e.g. ruff/F401, gap/untested-function
    file: str
    line: int
    column: int
    severity: str    # error|warning|info
    message: str
    help: str
    suggestion: str | None = None
```

### `Score`

```python
@dataclass
class Score:
    value: float
    label: str       # Excellent|Needs Work|Critical
    breakdown: dict[str, float]  # coverage|quality|gaps|dead_code|complexity
```

## Passes and Metadata

The API is pass-oriented. Typical metadata contains pass and tool execution context:

```python
print(result.metadata)
# {
#   "analysis_version": "...",
#   "passes_run": ["lint", "coverage", "dead_code", "complexity"],
#   "tools": ["ruff", "coverage", "vulture", "pytest-deadfixtures", "radon"]
# }
```

## Examples

### 1) Basic summary

```python
from pytest_doctor import diagnose

result = diagnose(".")
print(result.score.value, result.score.label)
print("diagnostics:", len(result.diagnostics))
```

### 2) Filter by severity

```python
errors = [d for d in result.diagnostics if d.severity == "error"]
warnings = [d for d in result.diagnostics if d.severity == "warning"]
print(len(errors), len(warnings))
```

### 3) Filter by pass category

```python
dead_code_issues = [d for d in result.diagnostics if d.type == "dead-code"]
complexity_issues = [d for d in result.diagnostics if d.type == "complexity"]
```

### 4) Coverage-focused run

```python
result = diagnose(
    ".",
    config={
        "lint": False,
        "coverage": True,
        "deadCode": False,
        "complexity": False,
    },
)
```

### 5) Lint-only fast run

```python
result = diagnose(
    ".",
    config={
        "lint": True,
        "coverage": False,
        "deadCode": False,
        "complexity": False,
    },
)
```

### 6) CI quality gate

```python
import sys
from pytest_doctor import diagnose

result = diagnose(".", config={"minimum_score": 80})

if result.score.value < 80:
    for d in result.diagnostics[:20]:
        print(f"{d.severity}: {d.category} {d.file}:{d.line} {d.message}")
    sys.exit(1)
```

## Error Handling

```python
from pytest_doctor import diagnose
from pytest_doctor.exceptions import DirectoryNotFoundError, InvalidConfigError

try:
    result = diagnose("./tests")
except DirectoryNotFoundError:
    print("Path not found")
except InvalidConfigError as exc:
    print(f"Invalid config: {exc}")
```

## Serialization

```python
payload = result.to_dict()
json_text = result.to_json()
```

## API Design Notes

- pytest-doctor is an orchestrator, not a replacement for Ruff/Coverage/Vulture/Radon.
- Deep tuning should happen in underlying tool configs, while pytest-doctor focuses on normalization and scoring.

## See Also

- [CLI.md](./CLI.md)
- [CONFIG.md](./CONFIG.md)
- [SCORING.md](./SCORING.md)
