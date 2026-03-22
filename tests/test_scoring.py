"""Tests for scoring module."""

import pytest

from pytest_doctor.models import (
    AnalysisResult,
    Issue,
    IssueSource,
    MutationStats,
    Severity,
)
from pytest_doctor.scoring import HealthScorer, ScoreWeights


def test_score_weights_defaults() -> None:
    """Test default score weights."""
    weights = ScoreWeights()
    assert weights.code_quality == 0.30
    assert weights.coverage_gaps == 0.30
    assert weights.assertion_quality == 0.20
    assert weights.test_isolation == 0.20
    total = (
        weights.code_quality
        + weights.coverage_gaps
        + weights.assertion_quality
        + weights.test_isolation
    )
    assert abs(total - 1.0) < 0.01


def test_score_weights_validation() -> None:
    """Test that weights must sum to 1.0."""
    with pytest.raises(ValueError, match=r"must sum to 1\.0"):
        ScoreWeights(
            code_quality=0.5,
            coverage_gaps=0.5,
            assertion_quality=0.5,
            test_isolation=0.0,
        )


def test_health_scorer_init() -> None:
    """Test HealthScorer initialization."""
    scorer = HealthScorer()
    assert scorer.weights is not None


def test_health_scorer_custom_weights() -> None:
    """Test HealthScorer with custom weights."""
    weights = ScoreWeights(
        code_quality=0.5,
        coverage_gaps=0.25,
        assertion_quality=0.15,
        test_isolation=0.1,
    )
    scorer = HealthScorer(weights)
    assert scorer.weights == weights


def test_health_scorer_empty_results() -> None:
    """Test scoring with no results."""
    scorer = HealthScorer()
    score = scorer.calculate_score([])
    assert score == 100


def test_health_scorer_no_issues() -> None:
    """Test scoring when there are no issues."""
    result = AnalysisResult(engine="ruff")
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # Only ruff (code quality): 100*0.30 + 100*0.30 + 50*0.20 + 100*0.20 = 90
    assert score == 90


def test_health_scorer_code_quality_with_linting_issues() -> None:
    """Test scoring with linting issues."""
    result = AnalysisResult(engine="ruff")
    result.issues = [
        Issue(
            file_path="test.py",
            line_number=1,
            message="test",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        ),
    ]
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # Code quality is 30% of the score. With 1 warning (5 points),
    # the quality score will be 95, which should be reflected
    assert score < 100


def test_health_scorer_coverage_gaps() -> None:
    """Test scoring with coverage gap issues."""
    result = AnalysisResult(engine="gap")
    result.issues = [
        Issue(
            file_path="test.py",
            line_number=1,
            message="function not covered",
            severity=Severity.INFO,
            source=IssueSource.COVERAGE,
        ),
    ]
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # 1 info issue = 1 point penalty = 99 score
    # Final = 100*0.30 + 99*0.30 + 50*0.20 + 100*0.20 = 89.7
    assert score < 100
    assert score >= 89


def test_health_scorer_assertion_quality_with_mutation_stats() -> None:
    """Test scoring with mutation testing results."""
    result = AnalysisResult(engine="assertion_quality")
    # 65% survival rate = 35% assertion quality score
    stats = MutationStats(
        total_mutations=100,
        killed_count=35,
        survival_rate=0.65,
        time_ms=5000,
    )
    result.metadata["mutation_stats"] = stats

    # Expected: (1 - 0.65) * 100 = 35 for assertion quality
    # Final score = 100*0.30 + 100*0.30 + 35*0.20 + 100*0.20
    #            = 30 + 30 + 7 + 20 = 87
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    assert score == 87


def test_health_scorer_assertion_quality_without_stats() -> None:
    """Test scoring when assertion quality engine ran but has no stats."""
    result = AnalysisResult(engine="assertion_quality")
    # No mutation stats, no issues - should return neutral 50 for assertion_quality
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # With only assertion_quality engine and no data, it returns 100 (all defaults perfect)
    assert score == 100


def test_health_scorer_assertion_quality_disabled() -> None:
    """Test scoring when assertion quality is not enabled."""
    # Only ruff result, no assertion quality
    result = AnalysisResult(engine="ruff")
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # Code quality perfect (ruff), others default
    # Final = 100*0.30 + 100*0.30 + 50*0.20 + 100*0.20 = 90
    assert score == 90


def test_health_scorer_weak_assertions_as_issues() -> None:
    """Test scoring with weak assertion issues (no stats)."""
    result = AnalysisResult(engine="assertion_quality")
    result.issues = [
        Issue(
            file_path="test.py",
            line_number=10,
            rule_id="weak-assertion",
            message="Mutation survived",
            severity=Severity.WARNING,
            source=IssueSource.MUTATION_TESTING,
        ),
    ]
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # Assertion quality: 1 warning = 5 points penalty = 95 score
    # Final = 100*0.30 + 100*0.30 + 95*0.20 + 100*0.20 = 99 (98 due to rounding)
    assert 97 <= score <= 100


def test_health_scorer_multiple_engines() -> None:
    """Test scoring with all analysis engines."""
    ruff_result = AnalysisResult(engine="ruff")
    ruff_result.issues = [
        Issue(
            file_path="test.py",
            line_number=1,
            message="test",
            severity=Severity.INFO,
            source=IssueSource.LINTING,
        ),
    ]

    gap_result = AnalysisResult(engine="gap")
    gap_result.issues = [
        Issue(
            file_path="test.py",
            line_number=2,
            message="uncovered",
            severity=Severity.INFO,
            source=IssueSource.COVERAGE,
        ),
    ]

    quality_result = AnalysisResult(engine="quality")
    # No issues for isolation

    assertion_result = AnalysisResult(engine="assertion_quality")
    # Use mutation stats
    stats = MutationStats(
        total_mutations=100,
        killed_count=80,
        survival_rate=0.20,
        time_ms=3000,
    )
    assertion_result.metadata["mutation_stats"] = stats

    scorer = HealthScorer()
    score = scorer.calculate_score([ruff_result, gap_result, quality_result, assertion_result])
    # Code quality: 1 info = 1 point, penalty = 1/100 = 0.01 → score 99.99
    # Coverage: 1 info = 1 point, penalty = 1/100 = 0.01 → score 99.99
    # Assertion: (1-0.20)*100 = 80
    # Isolation: 100 (perfect)
    # Final ≈ 99.99*0.30 + 99.99*0.30 + 80*0.20 + 100*0.20 ≈ 96
    assert score >= 95


def test_health_scorer_categorize_score() -> None:
    """Test score categorization."""
    scorer = HealthScorer()

    assert scorer.categorize_score(40) == "critical"
    assert scorer.categorize_score(50) == "needs_work"
    assert scorer.categorize_score(60) == "needs_work"
    assert scorer.categorize_score(75) == "good"
    assert scorer.categorize_score(90) == "good"


@pytest.mark.parametrize("num_issues", [1, 10, 25, 50, 100])
def test_health_scorer_score_range(num_issues: int) -> None:
    """Test that score stays within 0-100 range."""
    result = AnalysisResult(engine="ruff")
    # Create issues
    for _ in range(num_issues):
        result.issues.append(
            Issue(
                file_path="test.py",
                line_number=1,
                message="test",
                severity=Severity.CRITICAL,
                source=IssueSource.LINTING,
            )
        )

    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    assert 0 <= score <= 100


def test_health_scorer_backward_compatibility() -> None:
    """Test that scoring works without mutation data (backward compat)."""
    # Only traditional analyzers
    ruff_result = AnalysisResult(engine="ruff")
    gap_result = AnalysisResult(engine="gap")
    quality_result = AnalysisResult(engine="quality")

    scorer = HealthScorer()
    score = scorer.calculate_score([ruff_result, gap_result, quality_result])
    # Code quality (ruff): 100, Coverage (gap): 100, Assertion: 50 (default),
    # Isolation (quality): 100
    # All perfect: 100*0.30 + 100*0.30 + 50*0.20 + 100*0.20 = 90
    assert score == 90


def test_health_scorer_is_quality_engine() -> None:
    """Test identification of quality engines."""
    scorer = HealthScorer()

    assert scorer._is_quality_engine("ruff") is True
    assert scorer._is_quality_engine("linting") is True
    assert scorer._is_quality_engine("vulture") is True
    assert scorer._is_quality_engine("dead_code") is True
    assert scorer._is_quality_engine("gap") is False
    assert scorer._is_quality_engine("quality") is False
    assert scorer._is_quality_engine("assertion_quality") is False


def test_health_scorer_perfect_score_example() -> None:
    """Test perfect score with all engines perfect."""
    ruff = AnalysisResult(engine="ruff")
    gap = AnalysisResult(engine="gap")
    quality = AnalysisResult(engine="quality")
    assertion = AnalysisResult(engine="assertion_quality")
    # Mutation stats with 0% survival (all mutations killed)
    stats = MutationStats(
        total_mutations=100,
        killed_count=100,
        survival_rate=0.0,
        time_ms=5000,
    )
    assertion.metadata["mutation_stats"] = stats

    scorer = HealthScorer()
    score = scorer.calculate_score([ruff, gap, quality, assertion])
    # 100*0.30 + 100*0.30 + 100*0.20 + 100*0.20 = 100
    assert score == 100


def test_health_scorer_worst_case_example() -> None:
    """Test worst case with many critical issues."""
    ruff = AnalysisResult(engine="ruff")
    for _ in range(50):
        ruff.issues.append(
            Issue(
                file_path="test.py",
                line_number=1,
                message="test",
                severity=Severity.CRITICAL,
                source=IssueSource.LINTING,
            )
        )

    # High mutation survival rate
    assertion = AnalysisResult(engine="assertion_quality")
    stats = MutationStats(
        total_mutations=100,
        killed_count=10,
        survival_rate=0.90,
        time_ms=5000,
    )
    assertion.metadata["mutation_stats"] = stats

    scorer = HealthScorer()
    score = scorer.calculate_score([ruff, assertion])
    # Code quality: 50*10 = 500 points, capped at 100 = 100 penalty → 0 score
    # Coverage: 100 (default)
    # Assertion: (1-0.90)*100 = 10
    # Isolation: 100 (default)
    # Final = 0*0.30 + 100*0.30 + 10*0.20 + 100*0.20 = 52
    assert score == 52
