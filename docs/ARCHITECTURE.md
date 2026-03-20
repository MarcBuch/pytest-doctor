# pytest-doctor: Architecture

See [OVERVIEW.md](./OVERVIEW.md) for high-level introduction.

## System Design

pytest-doctor is composed of interconnected analyzers that process code and tests independently, then correlate findings to identify gaps.

```
┌─────────────────────────────────────────────────────────────┐
│                    pytest-doctor Engine                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Code Analyzer│  │ Test Analyzer│  │ Coverage Data│       │
│  │   (AST)      │  │   (AST)      │  │  (coverage.py)       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                  │                │
│         └─────────────────┼──────────────────┘                │
│                           │                                   │
│                    ┌──────▼────────┐                          │
│                    │ Correlation   │                          │
│                    │  Engine       │                          │
│                    └──────┬────────┘                          │
│                           │                                   │
│         ┌─────────────────┼─────────────────┐                │
│         │                 │                 │                │
│    ┌────▼─────┐  ┌────────▼──────┐  ┌──────▼─────┐          │
│    │ Test     │  │ Gap Detection │  │ Edge Case  │          │
│    │ Quality  │  │ Engine        │  │ Detector   │          │
│    │ Analyzer │  │               │  │            │          │
│    └────┬─────┘  └────────┬──────┘  └──────┬─────┘          │
│         │                 │                 │                │
│         └─────────────────┼─────────────────┘                │
│                           │                                   │
│                    ┌──────▼────────┐                          │
│                    │ Scoring       │                          │
│                    │ Engine        │                          │
│                    └──────┬────────┘                          │
│                           │                                   │
│                    ┌──────▼────────┐                          │
│                    │ Reporter      │                          │
│                    │ (CLI/JSON)    │                          │
│                    └───────────────┘                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Code Analyzer

**Location**: `pytest_doctor/analyzers/code_analyzer.py`

Uses Python's `ast` module to parse source code and extract:

- **Functions**: Name, signature, return type, decorators
- **Classes**: Hierarchy, methods, properties
- **Branches**: If/else paths, try/except blocks, loops
- **Exceptions**: Raised exceptions, custom exception types
- **State**: Class attributes, initialization patterns
- **Complexity**: Cyclomatic complexity metrics

**Key Methods**:
```python
class CodeAnalyzer:
    def analyze_directory(path: str) -> CodeMetrics
    def extract_functions(ast_tree) -> List[FunctionInfo]
    def extract_exceptions(ast_tree) -> List[ExceptionInfo]
    def find_branches(ast_tree) -> List[BranchInfo]
    def calculate_complexity(function) -> int
```

See [CODE_ANALYZER.md](./internals/CODE_ANALYZER.md) for detailed specification.

### 2. Test Analyzer

**Location**: `pytest_doctor/analyzers/test_analyzer.py`

Parses test files and identifies:

- **Test functions**: Names, decorators, parameters
- **Test structure**: Arrange-Act-Assert patterns
- **Assertions**: Types, messages, count
- **Fixtures**: Usage, dependencies, scope
- **Mocks/Patches**: Mock definitions, patching patterns
- **Coverage targets**: What code each test covers

**Key Methods**:
```python
class TestAnalyzer:
    def analyze_tests(path: str) -> TestMetrics
    def find_test_functions(ast_tree) -> List[TestInfo]
    def extract_assertions(test_function) -> List[AssertionInfo]
    def find_fixture_usage(ast_tree) -> Dict[str, List[FunctionName]]
    def detect_mock_patches(ast_tree) -> List[PatchInfo]
```

See [TEST_ANALYZER.md](./internals/TEST_ANALYZER.md) for detailed specification.

### 3. Coverage Engine

**Location**: `pytest_doctor/analyzers/coverage_engine.py`

Integrates with coverage.py to map test coverage to source code:

- Runs coverage collection if needed
- Maps lines/branches to test functions
- Calculates per-function coverage metrics
- Identifies fully uncovered vs partially covered code

**Key Methods**:
```python
class CoverageEngine:
    def measure_coverage(test_dir: str) -> CoverageData
    def get_function_coverage(func: FunctionInfo) -> CoverageStats
    def get_branch_coverage(branch: BranchInfo) -> CoverageStats
    def find_uncovered_lines(file: str) -> List[int]
    def correlate_tests_to_code() -> TestCoverageMap
```

See [COVERAGE_ENGINE.md](./internals/COVERAGE_ENGINE.md) for detailed specification.

### 4. Gap Detection Engine

**Location**: `pytest_doctor/analyzers/gap_detector.py`

Identifies untested code paths by correlating code and coverage:

- **Untested functions**: Functions with 0% coverage
- **Uncovered branches**: If/else paths never exercised
- **Missing exception tests**: Exceptions raised but never tested
- **Untested state transitions**: State changes not covered
- **Dead test code**: Unreachable test code

**Key Methods**:
```python
class GapDetector:
    def find_untested_functions() -> List[Gap]
    def find_uncovered_branches() -> List[Gap]
    def find_missing_exception_tests() -> List[Gap]
    def find_state_transition_gaps() -> List[Gap]
    def find_dead_test_code() -> List[Gap]
```

See [GAP_DETECTION.md](./GAP_DETECTION.md) for detailed strategy.

### 5. Edge Case Detector

**Location**: `pytest_doctor/analyzers/edge_case_detector.py`

Analyzes function signatures and implementation to suggest missing edge cases:

- **Boundary values**: Min/max for numeric types
- **Empty inputs**: Empty strings, lists, dicts
- **Special characters**: Unicode, emoji, control chars
- **Resource limits**: Very large inputs, timeouts
- **State transitions**: Invalid state combinations
- **Type coercion**: Implicit type conversions

**Key Methods**:
```python
class EdgeCaseDetector:
    def find_numeric_edge_cases(func: FunctionInfo) -> List[EdgeCase]
    def find_collection_edge_cases(func: FunctionInfo) -> List[EdgeCase]
    def find_string_edge_cases(func: FunctionInfo) -> List[EdgeCase]
    def find_state_edge_cases(func: FunctionInfo) -> List[EdgeCase]
    def find_resource_edge_cases(func: FunctionInfo) -> List[EdgeCase]
    def generate_test_suggestions(edge_cases: List[EdgeCase]) -> List[TestSuggestion]
```

See [EDGE_CASES.md](./EDGE_CASES.md) for edge case categories.

### 6. Test Quality Analyzer

**Location**: `pytest_doctor/analyzers/quality_analyzer.py`

Checks against 40+ diagnostic rules for test quality:

- **Structure**: Naming, organization, docstrings
- **Assertions**: Message presence, clarity, count
- **Fixtures**: Usage, scope, dependencies
- **Mocking**: Mock spec, patch paths, unmocked calls
- **Performance**: Test speed, parametrization opportunities
- **Maintainability**: Magic numbers, duplication, clarity

**Key Methods**:
```python
class TestQualityAnalyzer:
    def check_structure_rules() -> List[Diagnostic]
    def check_assertion_rules() -> List[Diagnostic]
    def check_fixture_rules() -> List[Diagnostic]
    def check_mocking_rules() -> List[Diagnostic]
    def check_performance_rules() -> List[Diagnostic]
    def check_maintainability_rules() -> List[Diagnostic]
```

See [RULES.md](./RULES.md) for all diagnostic rules.

### 7. Correlation Engine

**Location**: `pytest_doctor/correlation.py`

Connects outputs from multiple analyzers:

- Maps tests to functions they cover
- Identifies gaps by comparing what's tested vs what exists
- Correlates test quality issues to coverage
- Generates unified diagnostics

```python
class CorrelationEngine:
    def correlate_tests_to_code() -> TestCoverageMap
    def identify_untested_code() -> List[Gap]
    def identify_partial_coverage() -> List[Gap]
    def merge_diagnostics(*sources) -> List[Diagnostic]
```

### 8. Scoring Engine

**Location**: `pytest_doctor/scoring.py`

Calculates a single 0-100 health score based on all diagnostics:

```python
class ScoringEngine:
    def calculate_score(diagnostics: List[Diagnostic]) -> Score
    def weight_by_severity(diagnostic: Diagnostic) -> float
    def calculate_coverage_score() -> float
    def calculate_gap_score() -> float
    def calculate_quality_score() -> float
```

See [SCORING.md](./SCORING.md) for scoring algorithm.

### 9. Reporter

**Location**: `pytest_doctor/reporter.py`

Formats results for different outputs:

- CLI with color formatting
- JSON for API consumption
- GitHub PR comments
- HTML reports

```python
class Reporter:
    def report_cli(results: Results) -> str
    def report_json(results: Results) -> dict
    def report_github_comment(results: Results) -> str
    def report_html(results: Results) -> str
```

## Data Flow

### 1. Analysis Phase

```
Source Code + Tests
       ↓
   ┌───┴────┐
   │        │
CodeAnalyzer  TestAnalyzer
   │        │
   └───┬────┘
       ↓
CodeMetrics + TestMetrics + CoverageData
```

### 2. Gap Detection Phase

```
CodeMetrics + TestMetrics + CoverageData
       ↓
   ┌───┴────┐
   │        │
GapDetector  EdgeCaseDetector
   │        │
   └───┬────┘
       ↓
Gaps + EdgeCases + Suggestions
```

### 3. Quality Analysis Phase

```
TestMetrics + CodeMetrics
       ↓
TestQualityAnalyzer
       ↓
QualityDiagnostics
```

### 4. Correlation Phase

```
Gaps + EdgeCases + QualityDiagnostics
       ↓
CorrelationEngine
       ↓
UnifiedDiagnostics
```

### 5. Scoring Phase

```
UnifiedDiagnostics
       ↓
ScoringEngine
       ↓
Score (0-100) + Results Summary
```

### 6. Reporting Phase

```
UnifiedDiagnostics + Score
       ↓
Reporter
       ↓
CLI Output / JSON / GitHub / HTML
```

## Key Interfaces

### Diagnostic

```python
@dataclass
class Diagnostic:
    """Single diagnostic finding"""
    type: str  # "gap", "quality", "coverage"
    category: str  # "gap/untested-functions", "assertions/missing-messages"
    file: str
    line: int
    column: int
    severity: str  # "error", "warning", "info"
    message: str
    help: str  # Detailed explanation
    suggestion: Optional[str]  # How to fix
```

See [DIAGNOSTICS.md](./internals/DIAGNOSTICS.md) for full schema.

### Gap

```python
@dataclass
class Gap:
    """Represents a gap in test coverage"""
    category: str  # "untested-functions", "uncovered-branches"
    location: Location  # File, function, line
    description: str
    severity: str  # "error" or "warning"
    test_suggestion: TestSuggestion
```

See [GAP_DETECTION.md](./GAP_DETECTION.md) for gap types.

### EdgeCase

```python
@dataclass
class EdgeCase:
    """Represents a missing edge case test"""
    category: str  # "boundary-value", "empty-input"
    description: str
    function: FunctionInfo
    test_inputs: Dict
    expected_behavior: str
```

See [EDGE_CASES.md](./EDGE_CASES.md) for edge case types.

### Results

```python
@dataclass
class Results:
    """Complete analysis results"""
    score: Score
    diagnostics: List[Diagnostic]
    gaps: List[Gap]
    coverage: CoverageStats
    project_info: ProjectInfo
    metadata: Dict
```

## Extension Points

### Adding New Rules

1. Create rule in `pytest_doctor/rules/{category}.py`
2. Implement `Rule` interface
3. Register in `pytest_doctor/rules/__init__.py`

See [ADDING_RULES.md](./internals/ADDING_RULES.md) for details.

### Adding New Gap Types

1. Create detector in `pytest_doctor/gaps/{type}.py`
2. Implement `GapDetector` interface
3. Register in gap detector

See [ADDING_GAPS.md](./internals/ADDING_GAPS.md) for details.

### Custom Reporters

1. Create reporter in `pytest_doctor/reporters/{format}.py`
2. Implement `Reporter` interface
3. Register in reporter registry

See [CUSTOM_REPORTERS.md](./internals/CUSTOM_REPORTERS.md) for details.

## Performance Considerations

- **Parallel analysis**: Code and test analysis run independently
- **Incremental mode**: Only analyze changed files (with `--diff`)
- **Lazy loading**: Only load coverage data if needed
- **Caching**: Cache AST parsing results for repeated runs

## Integration Points

- **Coverage.py**: Real coverage data
- **pytest**: Test discovery and execution
- **LLM APIs**: For intelligent suggestions
- **GitHub Actions**: CI/CD integration
- **CI/CD systems**: Generic integration via CLI

See [INTEGRATIONS.md](./internals/INTEGRATIONS.md) for details.

## Next Steps

- [Diagnostic Rules](./RULES.md) - See all 40+ quality checks
- [Gap Detection Strategy](./GAP_DETECTION.md) - How gaps are found
- [Edge Cases](./EDGE_CASES.md) - Edge case categories
- [CLI Guide](./CLI.md) - Command-line usage
- [API Reference](./API.md) - Python API
