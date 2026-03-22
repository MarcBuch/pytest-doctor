"""Tests for human-readable output rendering."""

from dataclasses import dataclass

from click.testing import CliRunner

from pytest_doctor.aggregation import AggregatedIssues
from pytest_doctor.models import (
    AnalysisResult,
    DiagnosticReport,
    Issue,
    IssueSource,
    MutationStats,
    Severity,
)
from pytest_doctor.output import render_report


@dataclass
class MockAggregatedIssues:
    """Mock aggregated issues for testing."""

    summary: dict[str, int]
    all_issues: list[Issue]
    by_file: dict[str, list[Issue]]


def test_render_report_basic() -> None:
    """Test basic report rendering without mutations."""
    issues = [
        Issue(
            file_path="tests/test_example.py",
            line_number=45,
            rule_id="E501",
            rule_name="Line too long",
            message="Line too long (120 > 100)",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
            recommendation="Break line into shorter lines",
        )
    ]

    aggregated = MockAggregatedIssues(
        summary={"critical": 0, "warning": 1, "info": 0},
        all_issues=issues,
        by_file={"tests/test_example.py": issues},
    )

    diagnostic = DiagnosticReport(
        path=".",
        score=70,
        results=[],
        summary=aggregated.summary,  # type: ignore
        total_issues=len(issues),
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        # Capture output by calling render_report
        from unittest.mock import patch

        output_lines = []

        def mock_echo(msg: str, **kwargs: dict) -> None:
            output_lines.append(msg)

        with patch("pytest_doctor.output.click.echo", side_effect=mock_echo):
            render_report(diagnostic, aggregated, verbose=False)  # type: ignore

        output = "\n".join(output_lines)
        assert "pytest-doctor Diagnostic Report" in output
        assert "Health Score: 70/100" in output
        assert "⚠ NEEDS WORK" in output
        assert "Summary:" in output
        assert "Critical: 0" in output
        assert "Warning:  1" in output
        assert "Info:     0" in output


def test_render_report_with_mutations() -> None:
    """Test report rendering with mutation statistics."""
    issues = []

    aggregated = MockAggregatedIssues(
        summary={"critical": 0, "warning": 0, "info": 0},
        all_issues=issues,
        by_file={},
    )

    # Create mutation stats
    mutation_stats = MutationStats(
        total_mutations=127,
        killed_count=45,
        survival_rate=0.65,
        time_ms=5000,
    )

    assertion_result = AnalysisResult(
        engine="assertion_quality",
        issues=[],
        metadata={"mutation_stats": mutation_stats},
    )

    diagnostic = DiagnosticReport(
        path=".",
        score=70,
        results=[assertion_result],
        summary=aggregated.summary,  # type: ignore
        total_issues=0,
        mutation_survival_rate=0.65,
    )

    from unittest.mock import patch

    output_lines = []

    def mock_echo(msg: str, **kwargs: dict) -> None:
        output_lines.append(msg)

    with patch("pytest_doctor.output.click.echo", side_effect=mock_echo):
        render_report(diagnostic, aggregated, verbose=False)  # type: ignore

    output = "\n".join(output_lines)
    assert "Assertion Quality Score:" in output
    assert "35/100" in output  # 1 - 0.65 = 0.35 = 35%
    assert "Total Mutations: 127" in output
    assert "Killed: 45" in output
    assert "Survived: 82 (65%)" in output


def test_render_report_with_verbose() -> None:
    """Test verbose output includes recommendations."""
    issues = [
        Issue(
            file_path="tests/test_example.py",
            line_number=45,
            rule_id="E501",
            rule_name="Line too long",
            message="Line too long (120 > 100)",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
            recommendation="Break line into shorter lines",
        )
    ]

    aggregated = MockAggregatedIssues(
        summary={"critical": 0, "warning": 1, "info": 0},
        all_issues=issues,
        by_file={"tests/test_example.py": issues},
    )

    diagnostic = DiagnosticReport(
        path=".",
        score=75,
        results=[],
        summary=aggregated.summary,  # type: ignore
        total_issues=len(issues),
    )

    from unittest.mock import patch

    output_lines = []

    def mock_echo(msg: str, **kwargs: dict) -> None:
        output_lines.append(msg)

    with patch("pytest_doctor.output.click.echo", side_effect=mock_echo):
        render_report(diagnostic, aggregated, verbose=True)  # type: ignore

    output = "\n".join(output_lines)
    assert "Break line into shorter lines" in output


def test_render_report_good_score() -> None:
    """Test report with good health score."""
    aggregated = MockAggregatedIssues(
        summary={"critical": 0, "warning": 0, "info": 2},
        all_issues=[],
        by_file={},
    )

    diagnostic = DiagnosticReport(
        path=".",
        score=85,
        results=[],
        summary=aggregated.summary,  # type: ignore
        total_issues=2,
    )

    from unittest.mock import patch

    output_lines = []

    def mock_echo(msg: str, **kwargs: dict) -> None:
        output_lines.append(msg)

    with patch("pytest_doctor.output.click.echo", side_effect=mock_echo):
        render_report(diagnostic, aggregated, verbose=False)  # type: ignore

    output = "\n".join(output_lines)
    assert "✓ GOOD" in output


def test_render_report_critical_score() -> None:
    """Test report with critical health score."""
    aggregated = MockAggregatedIssues(
        summary={"critical": 5, "warning": 10, "info": 0},
        all_issues=[],
        by_file={},
    )

    diagnostic = DiagnosticReport(
        path=".",
        score=25,
        results=[],
        summary=aggregated.summary,  # type: ignore
        total_issues=15,
    )

    from unittest.mock import patch

    output_lines = []

    def mock_echo(msg: str, **kwargs: dict) -> None:
        output_lines.append(msg)

    with patch("pytest_doctor.output.click.echo", side_effect=mock_echo):
        render_report(diagnostic, aggregated, verbose=False)  # type: ignore

    output = "\n".join(output_lines)
    assert "✗ CRITICAL" in output
