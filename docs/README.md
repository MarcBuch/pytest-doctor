# pytest-doctor Documentation

Complete documentation for pytest-doctor: AI-friendly test suite analysis and improvement.

## Quick Start

**New here?** Start with [OVERVIEW.md](./OVERVIEW.md)

```bash
# Install
pip install pytest-doctor

# Scan your tests
pytest-doctor ./tests

# Get score
pytest-doctor ./tests --score
```

**For agents?** See [LLM_AGENTS.md](./LLM_AGENTS.md)

## Documentation Structure

### Core Concepts

1. **[OVERVIEW.md](./OVERVIEW.md)** - High-level introduction
   - What pytest-doctor does
   - Key features
   - Quick start examples
   - Links to detailed docs

2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design
   - Component architecture
   - Data flow through system
   - Core interfaces and classes
   - Extension points

### Analysis Features

3. **[RULES.md](./RULES.md)** - 40+ diagnostic rules
   - Test structure rules
   - Assertion quality rules
   - Fixture best practices
   - Mocking patterns
   - Performance optimization
   - Maintainability checks
   - Coverage metrics

4. **[GAP_DETECTION.md](./GAP_DETECTION.md)** - Finding untested code
   - Untested functions
   - Uncovered branches
   - Missing exception tests
   - State transition gaps
   - Partial function coverage
   - Dead test code

5. **[EDGE_CASES.md](./EDGE_CASES.md)** - Missing test scenarios
   - Numeric edge cases (zero, negative, overflow)
   - Collection edge cases (empty, single, large)
   - String edge cases (empty, unicode, special chars)
   - State & lifecycle edge cases
   - Resource & performance edge cases
   - Error path edge cases
   - Type coercion edge cases

6. **[SCORING.md](./SCORING.md)** - How results are scored
   - 0-100 health score
   - Coverage penalty calculation
   - Quality penalty calculation
   - Gap penalty calculation
   - Score ranges and labels
   - Example calculations

### Usage Guides

7. **[CLI.md](./CLI.md)** - Command-line interface
   - Installation
   - Basic usage
   - All commands and options
   - Output formats (text, JSON, HTML)
   - Diff mode for PR analysis
   - GitHub Actions integration
   - CI/CD integration examples
   - Environment variables
   - Troubleshooting

8. **[API.md](./API.md)** - Python API
   - Core `diagnose()` function
   - Results and data structures
   - Code examples
   - Error handling
   - Integration patterns
   - Performance optimization
   - Advanced usage

9. **[CONFIG.md](./CONFIG.md)** - Configuration
   - Configuration file locations
   - All configuration options
   - Rule customization
   - Ignore rules and files
   - Severity levels
   - Environment variables
   - `pyproject.toml` and `setup.cfg` support
   - Examples for different scenarios

### Agent Integration

10. **[LLM_AGENTS.md](./LLM_AGENTS.md)** - Using with AI agents
    - How agents use pytest-doctor
    - Structured output format
    - Test generation workflows
    - Example integrations (Claude, Cursor, OpenCode)
    - Agent best practices
    - Progress monitoring

## Feature Map

| Feature | Document | CLI | API |
|---------|----------|-----|-----|
| **Test Quality** | [RULES.md](./RULES.md) | `pytest-doctor .` | `diagnose()` |
| **Coverage Gaps** | [GAP_DETECTION.md](./GAP_DETECTION.md) | `--verbose` | `result.gaps` |
| **Edge Cases** | [EDGE_CASES.md](./EDGE_CASES.md) | `--verbose` | `result.gaps` |
| **Health Score** | [SCORING.md](./SCORING.md) | `--score` | `result.score` |
| **JSON Output** | [CLI.md](./CLI.md) | `--format json` | `diagnose()` |
| **Configuration** | [CONFIG.md](./CONFIG.md) | `--config` | `config` param |
| **GitHub Integration** | [CLI.md](./CLI.md) | `--github-token` | - |
| **Diff Analysis** | [CLI.md](./CLI.md) | `--diff main` | - |
| **Agent Integration** | [LLM_AGENTS.md](./LLM_AGENTS.md) | - | Structured API |

## Common Tasks

### I want to...

**...understand how pytest-doctor works**
→ Start with [OVERVIEW.md](./OVERVIEW.md), then [ARCHITECTURE.md](./ARCHITECTURE.md)

**...improve my test suite**
→ Run [CLI.md#basic-usage](./CLI.md#basic-usage) and read [RULES.md](./RULES.md)

**...find untested code**
→ See [GAP_DETECTION.md](./GAP_DETECTION.md)

**...find missing edge cases**
→ See [EDGE_CASES.md](./EDGE_CASES.md)

**...use it in my code**
→ Read [API.md](./API.md)

**...customize behavior**
→ See [CONFIG.md](./CONFIG.md)

**...integrate with GitHub Actions**
→ See [CLI.md#github-actions](./CLI.md#github-actions)

**...use it in CI/CD pipeline**
→ See [CLI.md#integration-with-cicd](./CLI.md#integration-with-cicd)

**...make an LLM agent use it**
→ Read [LLM_AGENTS.md](./LLM_AGENTS.md)

**...understand the score**
→ See [SCORING.md](./SCORING.md)

## Reference Tables

### Diagnostic Rules Summary

| Category | Rules | Document |
|----------|-------|----------|
| Structure | 7 rules | [RULES.md#1-structure-rules](./RULES.md#1-structure-rules) |
| Assertions | 6 rules | [RULES.md#2-assertion-rules](./RULES.md#2-assertion-rules) |
| Fixtures | 5 rules | [RULES.md#3-fixture-rules](./RULES.md#3-fixture-rules) |
| Mocking | 6 rules | [RULES.md#4-mocking-rules](./RULES.md#4-mocking-rules) |
| Performance | 3 rules | [RULES.md#5-performance-rules](./RULES.md#5-performance-rules) |
| Maintainability | 6 rules | [RULES.md#6-maintainability-rules](./RULES.md#6-maintainability-rules) |
| Coverage | 4 rules | [RULES.md#7-coverage-rules](./RULES.md#7-coverage-rules) |

**Total: 37 diagnostic rules** + Gap detection + Edge case detection

### Gap Types

| Type | Document | Example |
|------|----------|---------|
| Untested Functions | [GAP_DETECTION.md#1-untested-functions](./GAP_DETECTION.md#1-untested-functions) | Function with 0% coverage |
| Uncovered Branches | [GAP_DETECTION.md#2-uncovered-branches](./GAP_DETECTION.md#2-uncovered-branches) | If/else path not exercised |
| Missing Exception Tests | [GAP_DETECTION.md#3-missing-exception-tests](./GAP_DETECTION.md#3-missing-exception-tests) | Exception raised but not tested |
| State Transition Gaps | [GAP_DETECTION.md#5-state-transition-gaps](./GAP_DETECTION.md#5-state-transition-gaps) | State change not covered |
| Partial Coverage | [GAP_DETECTION.md#6-partial-function-coverage](./GAP_DETECTION.md#6-partial-function-coverage) | Some code paths untested |
| Dead Test Code | [GAP_DETECTION.md#7-dead-test-code](./GAP_DETECTION.md#7-dead-test-code) | Unreachable test code |

### Edge Case Categories

| Category | Document | Examples |
|----------|----------|----------|
| Numeric | [EDGE_CASES.md#1-numeric-edge-cases](./EDGE_CASES.md#1-numeric-edge-cases) | Zero, negative, overflow, NaN |
| Collections | [EDGE_CASES.md#2-collection-edge-cases](./EDGE_CASES.md#2-collection-edge-cases) | Empty, single, duplicates, large |
| Strings | [EDGE_CASES.md#3-string-edge-cases](./EDGE_CASES.md#3-string-edge-cases) | Empty, unicode, special chars |
| State | [EDGE_CASES.md#4-state--lifecycle-edge-cases](./EDGE_CASES.md#4-state--lifecycle-edge-cases) | Init, double init, cleanup |
| Resources | [EDGE_CASES.md#5-resource--performance-edge-cases](./EDGE_CASES.md#5-resource--performance-edge-cases) | Exhaustion, timeout, leaks |
| Errors | [EDGE_CASES.md#6-error-path-edge-cases](./EDGE_CASES.md#6-error-path-edge-cases) | Missing file, invalid format |
| Type Coercion | [EDGE_CASES.md#7-type-coercion-edge-cases](./EDGE_CASES.md#7-type-coercion-edge-cases) | None, wrong type, falsy |

### CLI Options

| Option | Document |
|--------|----------|
| All options | [CLI.md#options](./CLI.md#options) |
| Examples | [CLI.md#examples](./CLI.md#examples) |
| Exit codes | [CLI.md#exit-codes](./CLI.md#exit-codes) |
| CI/CD integration | [CLI.md#integration-with-cicd](./CLI.md#integration-with-cicd) |

### Configuration Options

| Option | Document | Values |
|--------|----------|--------|
| All options | [CONFIG.md#configuration-options](./CONFIG.md#configuration-options) | - |
| coverage | [CONFIG.md#coverage](./CONFIG.md#coverage) | `enabled`, `minimum`, `branches`, `exclude` |
| gaps | [CONFIG.md#gaps](./CONFIG.md#gaps) | `enabled`, `detection.*`, `minimum_coverage` |
| rules | [CONFIG.md#rules](./CONFIG.md#rules) | Per-rule: `enabled`, `severity` |
| ignore | [CONFIG.md#ignore](./CONFIG.md#ignore) | `rules[]`, `files[]` |
| scoring | [CONFIG.md#scoring](./CONFIG.md#scoring) | `weights.*`, `penalties.*`, `minimum_score` |

## Examples

### Running pytest-doctor

**Basic scan**
```bash
pytest-doctor ./tests
```
See [CLI.md#basic-usage](./CLI.md#basic-usage)

**With all details**
```bash
pytest-doctor ./tests --verbose
```
See [CLI.md#verbose-output](./CLI.md#verbose-output)

**Just the score**
```bash
pytest-doctor ./tests --score
```
See [CLI.md#score-only](./CLI.md#score-only)

**JSON format for scripts**
```bash
pytest-doctor ./tests --format json
```
See [CLI.md#json-output](./CLI.md#json-output)

**Changed files only (for PR)**
```bash
pytest-doctor . --diff main
```
See [CLI.md#diff-mode](./CLI.md#diff-mode)

### Using the API

**Basic analysis**
```python
from pytest_doctor import diagnose
result = diagnose("./tests")
print(result.score.value)
```
See [API.md#basic-usage](./API.md#basic-usage)

**Finding gaps**
```python
for gap in result.gaps:
    print(gap.description)
```
See [API.md#gap-analysis](./API.md#gap-analysis)

**Iterating diagnostics**
```python
errors = [d for d in result.diagnostics if d.severity == "error"]
```
See [API.md#iterating-diagnostics](./API.md#iterating-diagnostics)

**Custom config**
```python
result = diagnose("./tests", config={"coverage": {"minimum": 90}})
```
See [API.md#custom-configuration](./API.md#custom-configuration)

### Agent Integration

**Analyzing for agent**
```python
result = diagnose("./tests")
for gap in result.gaps:
    test_code = agent.generate_test(gap.test_suggestion)
```
See [LLM_AGENTS.md#workflow-1-fix-all-gaps](./LLM_AGENTS.md#workflow-1-fix-all-gaps)

**Verifying improvements**
```python
before = diagnose("./tests")
# ... agent makes changes ...
after = diagnose("./tests")
```
See [LLM_AGENTS.md#workflow-4-iterative-improvement](./LLM_AGENTS.md#workflow-4-iterative-improvement)

## Key Concepts

### Health Score (0-100)

- **75-100**: 🟢 Excellent
- **50-74**: 🟡 Needs Work  
- **<50**: 🔴 Critical

See [SCORING.md](./SCORING.md) for how it's calculated.

### Gap

Untested code path (function, branch, exception, edge case)

See [GAP_DETECTION.md](./GAP_DETECTION.md) for gap types.

### Edge Case

Missing test scenario (boundary value, special input, error condition)

See [EDGE_CASES.md](./EDGE_CASES.md) for edge case types.

### Diagnostic

Single finding from any analyzer (gap, quality issue, coverage metric)

See [RULES.md](./RULES.md) for all diagnostic rules.

## Glossary

| Term | Definition | Link |
|------|-----------|------|
| Gap | Untested code path | [GAP_DETECTION.md](./GAP_DETECTION.md) |
| Edge Case | Missing test scenario | [EDGE_CASES.md](./EDGE_CASES.md) |
| Diagnostic | Single finding | [RULES.md](./RULES.md) |
| Score | 0-100 health metric | [SCORING.md](./SCORING.md) |
| Rule | Quality check | [RULES.md](./RULES.md) |
| Severity | Issue importance (error/warning/info) | [RULES.md#severity-levels](./RULES.md#severity-levels) |

## Navigation

### By Role

**Test Engineer**
- [OVERVIEW.md](./OVERVIEW.md) - Understand the tool
- [RULES.md](./RULES.md) - See quality checks
- [CLI.md](./CLI.md) - Run analysis
- [CONFIG.md](./CONFIG.md) - Customize

**Developer**
- [API.md](./API.md) - Use programmatically
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Understand design
- [CONFIG.md](./CONFIG.md) - Configure behavior

**AI Agent Builder**
- [LLM_AGENTS.md](./LLM_AGENTS.md) - Integration guide
- [API.md](./API.md) - API details
- [GAP_DETECTION.md](./GAP_DETECTION.md) - What to fix
- [EDGE_CASES.md](./EDGE_CASES.md) - What to test

**DevOps/CI Engineer**
- [CLI.md](./CLI.md) - CI/CD integration
- [CONFIG.md](./CONFIG.md) - Configuration
- [SCORING.md](./SCORING.md) - Score thresholds

### By Task

Start here based on what you want to accomplish:

- [Want to improve tests?](./RULES.md) → See diagnostic rules
- [Want to find gaps?](./GAP_DETECTION.md) → See gap detection
- [Want to find missing tests?](./EDGE_CASES.md) → See edge cases
- [Want to automate with agents?](./LLM_AGENTS.md) → Agent guide
- [Want to configure it?](./CONFIG.md) → Configuration guide
- [Want to use in CI/CD?](./CLI.md#integration-with-cicd) → CI/CD integration
- [Want to use from Python?](./API.md) → Python API

## Versions & Compatibility

- **Python**: 3.8+
- **pytest**: 6.0+
- **coverage.py**: 6.0+

## Community & Support

- **Issues**: Report at project repository
- **Docs**: You're reading them!
- **Examples**: See [API.md](./API.md) and [LLM_AGENTS.md](./LLM_AGENTS.md)

## Full Hierarchy

```
DOCUMENTATION
├── OVERVIEW.md (start here)
├── ARCHITECTURE.md (system design)
├── RULES.md (diagnostic rules)
├── GAP_DETECTION.md (untested code)
├── EDGE_CASES.md (missing scenarios)
├── SCORING.md (health score)
├── CLI.md (command-line usage)
├── API.md (Python API)
├── CONFIG.md (configuration)
└── LLM_AGENTS.md (agent integration)
```

---

**Start with [OVERVIEW.md](./OVERVIEW.md) if you're new!**
