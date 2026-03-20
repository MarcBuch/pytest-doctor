# pytest-doctor: Python API

See [OVERVIEW.md](./OVERVIEW.md) for overview and [CLI.md](./CLI.md) for command-line usage.

Use pytest-doctor programmatically in Python applications.

## Installation

```bash
pip install pytest-doctor
```

## Basic Usage

```python
from pytest_doctor import diagnose

# Analyze test suite
result = diagnose("./tests")

# Check results
print(f"Score: {result.score.value}/100")
print(f"Label: {result.score.label}")
print(f"Gaps found: {len(result.gaps)}")
print(f"Quality issues: {len(result.diagnostics)}")
```

## Core API

### `diagnose()`

Main function to analyze test suite.

```python
def diagnose(
    path: str,
    config: Optional[ConfigDict] = None,
    coverage_data: Optional[CoverageData] = None,
) -> Results:
    """
    Analyze test suite and return comprehensive results.
    
    Args:
        path: Path to test directory or Python package
        config: Optional configuration dict (overrides config file)
        coverage_data: Optional pre-measured coverage data
    
    Returns:
        Results object with score, diagnostics, gaps, coverage
    
    Raises:
        DirectoryNotFoundError: If path doesn't exist
        InvalidConfigError: If config is invalid
    """
```

### Results

```python
@dataclass
class Results:
    """Complete analysis results"""
    
    # Overall score (0-100)
    score: Score
    
    # All diagnostics (gaps + quality issues)
    diagnostics: List[Diagnostic]
    
    # Coverage gaps
    gaps: List[Gap]
    
    # Code coverage metrics
    coverage: CoverageStats
    
    # Project information
    project_info: ProjectInfo
    
    # Additional metadata
    metadata: Dict[str, Any]
    
    # Timestamps
    started_at: datetime
    completed_at: datetime
```

#### Score

```python
@dataclass
class Score:
    """Health score 0-100"""
    
    value: float  # 0-100
    label: str  # "Excellent", "Needs Work", "Critical"
    breakdown: Dict[str, float]  # "coverage", "quality", "gaps"
```

#### Diagnostic

```python
@dataclass
class Diagnostic:
    """Single diagnostic finding"""
    
    type: str  # "gap", "quality"
    category: str  # "gap/untested-functions", "assertions/missing-messages"
    file: str  # Path to file
    line: int
    column: int
    severity: str  # "error", "warning", "info"
    message: str  # Human-readable message
    help: str  # Detailed explanation
    suggestion: Optional[str]  # How to fix
```

#### Gap

```python
@dataclass
class Gap:
    """Represents a gap in test coverage"""
    
    category: str  # "untested-functions", "uncovered-branches"
    location: Location  # File, function, line
    description: str
    severity: str
    test_suggestion: TestSuggestion
```

#### CoverageStats

```python
@dataclass
class CoverageStats:
    """Code coverage metrics"""
    
    overall: float  # Overall coverage percentage
    by_file: Dict[str, float]  # Coverage per file
    by_function: Dict[str, float]  # Coverage per function
    lines_total: int
    lines_covered: int
    branches_total: int
    branches_covered: int
```

## Examples

### Basic Analysis

```python
from pytest_doctor import diagnose

result = diagnose("./tests")

# Print summary
print(f"Test Suite Score: {result.score.value}")
print(f"Coverage: {result.coverage.overall}%")
print(f"Gaps found: {len(result.gaps)}")
```

### Iterating Diagnostics

```python
# Find all errors
errors = [d for d in result.diagnostics if d.severity == "error"]
print(f"Critical issues: {len(errors)}")

for diagnostic in errors:
    print(f"\n{diagnostic.category}")
    print(f"  File: {diagnostic.file}:{diagnostic.line}")
    print(f"  Message: {diagnostic.message}")
    print(f"  Suggestion: {diagnostic.suggestion}")
```

### Filtering by Category

```python
# Get all gap diagnostics
gaps = [d for d in result.diagnostics if d.type == "gap"]

# Get specific gap type
untested_funcs = [
    d for d in gaps 
    if d.category == "gap/untested-functions"
]

for gap in untested_funcs:
    print(f"Untested function: {gap.file}:{gap.line}")
```

### Coverage Analysis

```python
# Overall coverage
print(f"Overall coverage: {result.coverage.overall}%")

# Find low-coverage files
for file, coverage in result.coverage.by_file.items():
    if coverage < 80:
        print(f"Low coverage: {file} ({coverage}%)")

# Find untested functions
untested = {
    func: 0 for func, cov in result.coverage.by_function.items()
    if cov == 0
}
print(f"Untested functions: {list(untested.keys())}")
```

### Gap Analysis

```python
# Find all gaps
for gap in result.gaps:
    print(f"\nGap: {gap.category}")
    print(f"  Location: {gap.location.file}:{gap.location.line}")
    print(f"  Function: {gap.location.function}")
    print(f"  Severity: {gap.severity}")
    print(f"  Description: {gap.description}")
    
    if gap.test_suggestion:
        print(f"  Suggested test: {gap.test_suggestion.test_name}")
```

### Score Breakdown

```python
# See score calculation breakdown
breakdown = result.score.breakdown

print(f"Total Score: {result.score.value}/100")
print(f"Breakdown:")
print(f"  Coverage penalty: -{breakdown['coverage']}")
print(f"  Quality penalty: -{breakdown['quality']}")
print(f"  Gap penalty: -{breakdown['gaps']}")

# Determine what needs most attention
if breakdown['gaps'] > breakdown['quality']:
    print("Priority: Add missing tests")
elif breakdown['quality'] > 20:
    print("Priority: Improve test quality")
else:
    print("Priority: Increase coverage")
```

### Custom Configuration

```python
result = diagnose(
    "./tests",
    config={
        "gaps": {
            "enabled": True,
            "minimum_coverage": 85
        },
        "ignore": {
            "rules": ["assertions/multiple-assertions"],
            "files": ["tests/fixtures/**"]
        }
    }
)
```

### Handling Errors

```python
from pytest_doctor import diagnose, DirectoryNotFoundError, InvalidConfigError

try:
    result = diagnose("./nonexistent")
except DirectoryNotFoundError:
    print("Test directory not found")
except InvalidConfigError as e:
    print(f"Invalid configuration: {e}")
except Exception as e:
    print(f"Analysis failed: {e}")
else:
    print(f"Analysis succeeded: {result.score.value}/100")
```

### Integration with Testing Workflow

```python
import sys
from pytest_doctor import diagnose

# Analyze
result = diagnose("./tests")

# Fail if score too low
if result.score.value < 75:
    print(f"Test quality score too low: {result.score.value}/100")
    
    # Print details
    for gap in result.gaps[:5]:
        print(f"  - {gap.description}")
    
    sys.exit(1)

print(f"✅ Tests passed quality check: {result.score.value}/100")
```

### Exporting Results

```python
import json
from datetime import datetime

result = diagnose("./tests")

# Export to JSON
export_data = {
    "timestamp": datetime.now().isoformat(),
    "score": {
        "value": result.score.value,
        "label": result.score.label,
        "breakdown": result.score.breakdown
    },
    "coverage": {
        "overall": result.coverage.overall,
        "by_file": result.coverage.by_file
    },
    "gaps_count": len(result.gaps),
    "quality_issues": len(
        [d for d in result.diagnostics if d.type == "quality"]
    )
}

with open("report.json", "w") as f:
    json.dump(export_data, f, indent=2)
```

### Programmatic Gap Suggestions

```python
from pytest_doctor import diagnose

result = diagnose("./tests")

# Generate test code suggestions for gaps
for gap in result.gaps:
    if gap.test_suggestion:
        suggestion = gap.test_suggestion
        
        print(f"def {suggestion.test_name}():")
        print(f'    """{suggestion.description}"""')
        
        # Generate test code from template
        test_code = suggestion.code_template.format(
            **suggestion.inputs
        )
        print(f"    {test_code}")
```

### Multi-Package Analysis (Monorepo)

```python
from pytest_doctor import diagnose

packages = ["web", "api", "cli"]
results = {}

for package in packages:
    results[package] = diagnose(f"packages/{package}/tests")
    print(f"{package}: {results[package].score.value}/100")

# Find package with lowest score
lowest_package = min(
    results.items(),
    key=lambda x: x[1].score.value
)
print(f"Needs most work: {lowest_package[0]}")
```

### Continuous Monitoring

```python
from pytest_doctor import diagnose
import json
from datetime import datetime

def log_test_quality():
    """Log test quality metrics for monitoring"""
    result = diagnose("./tests")
    
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "score": result.score.value,
        "coverage": result.coverage.overall,
        "gaps": len(result.gaps),
        "errors": len(
            [d for d in result.diagnostics if d.severity == "error"]
        ),
        "warnings": len(
            [d for d in result.diagnostics if d.severity == "warning"]
        )
    }
    
    # Write to metrics file or monitoring system
    with open("test_metrics.jsonl", "a") as f:
        f.write(json.dumps(metrics) + "\n")
    
    return metrics

# Schedule this to run regularly
# e.g., via cron, scheduled CI job, etc.
```

## Advanced API

### Analyzing Specific Files

```python
from pytest_doctor.analyzers import CodeAnalyzer, TestAnalyzer

code_analyzer = CodeAnalyzer()
test_analyzer = TestAnalyzer()

# Analyze specific files
code_metrics = code_analyzer.analyze_directory("src/")
test_metrics = test_analyzer.analyze_directory("tests/")

# Use results
print(f"Functions: {len(code_metrics.functions)}")
print(f"Tests: {len(test_metrics.test_functions)}")
```

### Custom Rule Implementation

```python
from pytest_doctor import Rule, Diagnostic

class CustomRule(Rule):
    """Custom diagnostic rule"""
    
    category = "custom/my-rule"
    severity = "warning"
    
    def check(self, test_info) -> List[Diagnostic]:
        """Check test and return diagnostics"""
        diagnostics = []
        
        if condition_not_met(test_info):
            diagnostics.append(
                Diagnostic(
                    type="quality",
                    category=self.category,
                    file=test_info.file,
                    line=test_info.line,
                    severity=self.severity,
                    message="Custom rule violation",
                    help="Explanation of the issue"
                )
            )
        
        return diagnostics
```

## Type Hints

All functions and classes are fully typed for IDE autocomplete:

```python
from pytest_doctor import diagnose, Results, Score, Gap, Diagnostic

# IDE provides autocompletion and type checking
result: Results = diagnose("./tests")
score: Score = result.score
gaps: List[Gap] = result.gaps
diagnostics: List[Diagnostic] = result.diagnostics
```

## Performance

For large test suites:

```python
# Disable expensive analyses if not needed
result = diagnose(
    "./tests",
    config={
        "coverage": {"enabled": False},
        "gaps": {"enabled": False}
    }
)
# Runs much faster, only checks quality rules
```

## See Also

- [OVERVIEW.md](./OVERVIEW.md) - Quick start
- [CLI.md](./CLI.md) - Command-line usage
- [CONFIG.md](./CONFIG.md) - Configuration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
