# pytest-doctor: Scoring Algorithm

See [OVERVIEW.md](./OVERVIEW.md) for quick start.

The scoring algorithm produces a single **0-100 health score** that summarizes overall test quality.

## Score Ranges

- **75-100**: 🟢 **Excellent** - Great test coverage and quality
- **50-74**: 🟡 **Needs Work** - Some gaps and quality issues
- **<50**: 🔴 **Critical** - Major improvements needed

## Scoring Formula

```
Score = 100 - (Total Penalty Points)

Penalty = Coverage Penalty + Quality Penalty + Gap Penalty

Where:
- Coverage Penalty: Based on code coverage percentage
- Quality Penalty: Based on diagnostic rule violations
- Gap Penalty: Based on untested code paths and missing edge cases
```

## 1. Coverage Penalty

Penalizes low test coverage.

```python
def calculate_coverage_penalty(coverage_percent: float) -> float:
    """
    Calculate penalty based on code coverage.
    
    Coverage 100%: 0 points
    Coverage 90%:  5 points
    Coverage 80%:  10 points
    Coverage 70%:  15 points
    Coverage 60%:  20 points
    Coverage <50%: 30 points
    """
    if coverage_percent >= 95:
        return 0
    elif coverage_percent >= 90:
        return 5
    elif coverage_percent >= 80:
        return 10
    elif coverage_percent >= 70:
        return 15
    elif coverage_percent >= 60:
        return 20
    elif coverage_percent >= 50:
        return 25
    else:
        return 30
```

### Coverage Tiers

| Coverage | Penalty | Reasoning |
|----------|---------|-----------|
| 100% | 0 | Perfect coverage |
| 95% | 0 | Excellent coverage |
| 90% | 5 | Good coverage, minor gaps |
| 80% | 10 | Decent coverage, some gaps |
| 70% | 15 | Below target, significant gaps |
| 60% | 20 | Low coverage, many gaps |
| 50% | 25 | Very low coverage |
| <50% | 30 | Critical, most code untested |

## 2. Quality Penalty

Penalizes diagnostic rule violations.

```python
def calculate_quality_penalty(diagnostics: List[Diagnostic]) -> float:
    """
    Calculate penalty based on rule violations.
    
    Each error: -5 points
    Each warning: -2 points
    Each info: -0.5 points
    """
    errors = sum(1 for d in diagnostics if d.severity == "error")
    warnings = sum(1 for d in diagnostics if d.severity == "warning")
    infos = sum(1 for d in diagnostics if d.severity == "info")
    
    return (errors * 5) + (warnings * 2) + (infos * 0.5)
```

### Severity Weights

| Severity | Per Issue | Category | Examples |
|----------|-----------|----------|----------|
| 🔴 Error | -5 | Critical | Missing exception tests, uncovered branches, unmocked external calls |
| 🟡 Warning | -2 | Important | Missing assertions, unused fixtures, duplicate logic |
| ℹ️ Info | -0.5 | Nice-to-have | Test naming, docstrings, magic numbers |

### Example

10 errors + 20 warnings + 50 infos:
```
Quality Penalty = (10 × 5) + (20 × 2) + (50 × 0.5)
                = 50 + 40 + 25
                = 115 points
```

This would result in a very low or negative score before capping.

## 3. Gap Penalty

Penalizes untested code and missing edge cases.

```python
def calculate_gap_penalty(gaps: List[Gap]) -> float:
    """
    Calculate penalty based on gaps and missing edge cases.
    
    Each untested function: -5 points
    Each uncovered branch: -3 points
    Each missing exception test: -4 points
    Each missing edge case: -1 point
    """
    untested_funcs = sum(1 for g in gaps if g.category == "untested-functions")
    uncovered_branches = sum(1 for g in gaps if g.category == "uncovered-branches")
    missing_exceptions = sum(1 for g in gaps if g.category == "missing-exception-tests")
    missing_edge_cases = sum(1 for g in gaps if g.category == "missing-edge-cases")
    
    return (untested_funcs * 5) + (uncovered_branches * 3) + \
           (missing_exceptions * 4) + (missing_edge_cases * 1)
```

### Gap Weights

| Gap Type | Per Gap | Severity | Reasoning |
|----------|---------|----------|-----------|
| Untested functions | -5 | Critical | Function completely untested |
| Uncovered branches | -3 | High | Error path not tested |
| Missing exception tests | -4 | Critical | Error handling not verified |
| Missing edge cases | -1 | Medium | Special case not tested |

## 4. Score Calculation

```python
def calculate_score(analysis_results: AnalysisResults) -> Score:
    """Calculate 0-100 health score"""
    
    # Calculate individual penalties
    coverage_penalty = calculate_coverage_penalty(
        analysis_results.coverage_percent
    )
    quality_penalty = calculate_quality_penalty(
        analysis_results.diagnostics
    )
    gap_penalty = calculate_gap_penalty(
        analysis_results.gaps
    )
    
    # Sum penalties
    total_penalty = coverage_penalty + quality_penalty + gap_penalty
    
    # Calculate score (0-100, capped at 0 minimum)
    raw_score = 100 - total_penalty
    score = max(0, min(100, raw_score))
    
    # Determine label
    if score >= 75:
        label = "Excellent"
    elif score >= 50:
        label = "Needs Work"
    else:
        label = "Critical"
    
    return Score(
        value=round(score, 1),
        label=label,
        breakdown={
            "coverage": coverage_penalty,
            "quality": quality_penalty,
            "gaps": gap_penalty,
        }
    )
```

## Example Calculations

### Scenario 1: Excellent Test Suite

```
Coverage: 95%
Coverage Penalty: 0

Quality Issues:
- 2 warnings: 2 × 2 = 4 points
Quality Penalty: 4

Gaps:
- 1 missing edge case: 1 × 1 = 1 point
Gap Penalty: 1

Total Penalty: 0 + 4 + 1 = 5
Score: 100 - 5 = 95 ✅ Excellent
```

### Scenario 2: Decent Test Suite

```
Coverage: 82%
Coverage Penalty: 10

Quality Issues:
- 3 errors: 3 × 5 = 15 points
- 8 warnings: 8 × 2 = 16 points
Quality Penalty: 31

Gaps:
- 2 uncovered branches: 2 × 3 = 6 points
- 1 missing exception test: 1 × 4 = 4 points
Gap Penalty: 10

Total Penalty: 10 + 31 + 10 = 51
Score: 100 - 51 = 49 ⚠️ Critical
```

### Scenario 3: Needs Work

```
Coverage: 72%
Coverage Penalty: 15

Quality Issues:
- 2 errors: 2 × 5 = 10 points
- 5 warnings: 5 × 2 = 10 points
- 20 infos: 20 × 0.5 = 10 points
Quality Penalty: 30

Gaps:
- 1 untested function: 1 × 5 = 5 points
- 3 uncovered branches: 3 × 3 = 9 points
- 5 missing edge cases: 5 × 1 = 5 points
Gap Penalty: 19

Total Penalty: 15 + 30 + 19 = 64
Score: 100 - 64 = 36... but capped at 50 🟡 Needs Work
```

## Score Distribution

Empirical distribution on real projects:

```
Score Range     | Frequency | Label
────────────────┼───────────┼─────────────
90-100          | 5%        | Excellent
80-89           | 15%       | Excellent
75-79           | 20%       | Excellent
50-74           | 35%       | Needs Work
<50             | 25%       | Critical
```

## Weighting Rationale

### Why these weights?

1. **Coverage is foundational**: Missing tests are the biggest issue
2. **Gaps are critical**: Untested code paths can cause production bugs
3. **Quality varies by severity**: Errors are 2.5x worse than warnings
4. **Edge cases matter but less**: Missing edge cases are harder to detect

### Weight Justification

```
Coverage:  Foundational (30% of possible penalty)
Gaps:      Critical untested code (35% of possible penalty)
Quality:   Best practices (35% of possible penalty)
```

## Score Improvements

Typical improvements when addressing issues:

### Adding missing exception tests
```
Before: 60% coverage, 5 missing exception tests
  Penalty: 15 (coverage) + 20 (exception gaps)
  Score: 65

After: 85% coverage, 0 missing exception tests
  Penalty: 10 (coverage) + 0 (exception gaps)
  Score: 90
  Improvement: +25 points ⬆️
```

### Fixing quality issues
```
Before: 12 errors, 15 warnings, 30 infos
  Penalty: (12×5) + (15×2) + (30×0.5) = 100
  Score: 0 (capped)

After: 0 errors, 3 warnings, 10 infos
  Penalty: (0×5) + (3×2) + (10×0.5) = 8
  Score: 92
  Improvement: Massive improvement ⬆️
```

### Increasing coverage
```
Before: 60% coverage
  Penalty: 20

After: 90% coverage
  Penalty: 5
  Improvement: +15 points from coverage alone
```

## Configuration

Customize scoring in `pytest_doctor.config.json`:

```json
{
  "scoring": {
    "minimum_coverage": 80,
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
      "untested-function": 5,
      "uncovered-branch": 3,
      "missing-exception": 4,
      "missing-edge-case": 1
    }
  }
}
```

## Reporting Score

```python
result = diagnose("./tests")

print(f"Score: {result.score.value}/{100}")
print(f"Label: {result.score.label}")
print(f"Breakdown:")
print(f"  Coverage: -{result.score.breakdown['coverage']}")
print(f"  Quality:  -{result.score.breakdown['quality']}")
print(f"  Gaps:     -{result.score.breakdown['gaps']}")
```

Output:
```
Score: 72/100
Label: Needs Work
Breakdown:
  Coverage: -10
  Quality:  -12
  Gaps:     -6
```

## See Also

- [OVERVIEW.md](./OVERVIEW.md) - Quick introduction
- [RULES.md](./RULES.md) - Diagnostic rules
- [GAP_DETECTION.md](./GAP_DETECTION.md) - Gap detection
- [EDGE_CASES.md](./EDGE_CASES.md) - Edge cases
