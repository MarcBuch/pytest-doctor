"""Tests for scoring module."""

import pytest

from pytest_doctor.models import AnalysisResult, Issue, IssueSource, Severity
from pytest_doctor.scoring import HealthScorer, ScoreWeights


def test_score_weights_defaults() -> None:
    """Test default score weights."""
    weights = ScoreWeights()
    assert weights.linting == 0.25
    assert weights.dead_code == 0.25
    assert weights.test_quality == 0.3
    assert weights.coverage == 0.2
    assert sum([weights.linting, weights.dead_code, weights.test_quality, weights.coverage]) == 1.0


def test_score_weights_validation() -> None:
    """Test that weights must sum to 1.0."""
    with pytest.raises(ValueError, match=r"must sum to 1\.0"):
        ScoreWeights(linting=0.5, dead_code=0.5, test_quality=0.5, coverage=0.0)


def test_health_scorer_init() -> None:
    """Test HealthScorer initialization."""
    scorer = HealthScorer()
    assert scorer.weights is not None


def test_health_scorer_custom_weights() -> None:
    """Test HealthScorer with custom weights."""
    weights = ScoreWeights(linting=0.5, dead_code=0.3, test_quality=0.1, coverage=0.1)
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
    assert score == 100


def test_health_scorer_with_info_issues() -> None:
    """Test scoring with info-level issues."""
    result = AnalysisResult(engine="ruff")
    result.issues = [
        Issue(
            file_path="test.py",
            line_number=1,
            message="test",
            severity=Severity.INFO,
            source=IssueSource.LINTING,
        ),
    ]
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # 1 info issue = 1 point deducted
    # linting weight = 0.25, so 1 * 0.25 = 0.25 deducted from 100
    assert score < 100
    assert score > 95


def test_health_scorer_with_warning_issues() -> None:
    """Test scoring with warning-level issues."""
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
    # 1 warning issue = 5 points deducted
    assert score < 100


def test_health_scorer_with_critical_issues() -> None:
    """Test scoring with critical-level issues."""
    result = AnalysisResult(engine="ruff")
    result.issues = [
        Issue(
            file_path="test.py",
            line_number=1,
            message="test",
            severity=Severity.CRITICAL,
            source=IssueSource.LINTING,
        ),
    ]
    scorer = HealthScorer()
    score = scorer.calculate_score([result])
    # 1 critical issue = 10 points deducted
    # linting weight = 0.25, so 10 * 0.25 = 2.5 deducted
    assert score < 100


def test_health_scorer_multiple_engines() -> None:
    """Test scoring with multiple analysis engines."""
    ruff_result = AnalysisResult(engine="ruff")
    ruff_result.issues = [
        Issue(
            file_path="test.py",
            line_number=1,
            message="test",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
        ),
    ]

    vulture_result = AnalysisResult(engine="vulture")
    vulture_result.issues = [
        Issue(
            file_path="test.py",
            line_number=2,
            message="test",
            severity=Severity.INFO,
            source=IssueSource.DEAD_CODE,
        ),
    ]

    scorer = HealthScorer()
    score = scorer.calculate_score([ruff_result, vulture_result])
    assert score < 100


def test_health_scorer_get_weight_for_engine() -> None:
    """Test getting weight for different engines."""
    scorer = HealthScorer()

    assert scorer._get_weight_for_engine("ruff") == 0.25
    assert scorer._get_weight_for_engine("linting") == 0.25
    assert scorer._get_weight_for_engine("vulture") == 0.25
    assert scorer._get_weight_for_engine("dead_code") == 0.25
    assert scorer._get_weight_for_engine("test_quality") == 0.3
    assert scorer._get_weight_for_engine("coverage") == 0.2


def test_health_scorer_categorize_score() -> None:
    """Test score categorization."""
    scorer = HealthScorer()

    assert scorer.categorize_score(40) == "critical"
    assert scorer.categorize_score(50) == "needs_work"
    assert scorer.categorize_score(60) == "needs_work"
    assert scorer.categorize_score(75) == "good"
    assert scorer.categorize_score(90) == "good"


def test_health_scorer_score_range() -> None:
    """Test that score stays within 0-100 range."""
    result = AnalysisResult(engine="ruff")
    # Create many critical issues
    for _ in range(50):
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
