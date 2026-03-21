"""Pytest fixtures for test suite."""

import pytest

from pytest_doctor.agent_output import AgentContext, AgentFixSuggestion, AgentOutput
from pytest_doctor.aggregation import AggregatedIssues
from pytest_doctor.models import AnalysisResult, DiagnosticReport, Issue, IssueSource, Severity


@pytest.fixture
def agent_context_minimal():
    """Fixture for minimal agent context."""
    return AgentContext(
        project_path=".",
        health_score=100,
        total_issues=0,
        critical_count=0,
        warning_count=0,
        info_count=0,
    )


@pytest.fixture
def agent_context_with_issues():
    """Fixture for agent context with issues."""
    return AgentContext(
        project_path=".",
        health_score=50,
        total_issues=10,
        critical_count=3,
        warning_count=4,
        info_count=3,
    )


@pytest.fixture
def agent_context_critical():
    """Fixture for agent context with critical issues."""
    return AgentContext(
        project_path="/some/path",
        health_score=30,
        total_issues=10,
        critical_count=5,
        warning_count=3,
        info_count=2,
    )


@pytest.fixture
def single_fix_suggestion():
    """Fixture for a single fix suggestion."""
    return AgentFixSuggestion(
        file_path="src/main.py",
        line_number=5,
        rule_id="E501",
        rule_name="Line too long",
        message="Line is too long",
        severity="critical",
        recommendation="Shorten the line",
    )


@pytest.fixture
def multiple_fix_suggestions():
    """Fixture for multiple fix suggestions."""
    return [
        AgentFixSuggestion(
            file_path="src/main.py",
            line_number=5,
            rule_id="E501",
            rule_name="Line too long",
            message="Line is too long",
            severity="critical",
            recommendation="Shorten the line",
        ),
        AgentFixSuggestion(
            file_path="src/utils.py",
            line_number=15,
            rule_id="F401",
            rule_name="Unused import",
            message="Import is unused",
            severity="warning",
            recommendation="Remove import",
        ),
    ]


@pytest.fixture
def diagnostic_report_minimal():
    """Fixture for minimal diagnostic report."""
    return DiagnosticReport(
        path=".",
        score=100,
        results=[],
        summary={"critical": 0, "warning": 0, "info": 0},
        total_issues=0,
    )


@pytest.fixture
def diagnostic_report_with_issues():
    """Fixture for diagnostic report with issues."""
    return DiagnosticReport(
        path=".",
        score=50,
        results=[],
        summary={"critical": 2, "warning": 3, "info": 5},
        total_issues=10,
    )


@pytest.fixture
def single_issue():
    """Fixture for a single issue."""
    return Issue(
        file_path="tests/test_example.py",
        line_number=10,
        message="Test message",
        severity=Severity.WARNING,
        source=IssueSource.LINTING,
        recommendation="Test recommendation",
    )


@pytest.fixture
def multiple_issues():
    """Fixture for multiple issues."""
    return [
        Issue(
            file_path="tests/test_example.py",
            line_number=10,
            message="Test message",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
            recommendation="Test recommendation",
        ),
        Issue(
            file_path="tests/test_example.py",
            line_number=20,
            message="Another message",
            severity=Severity.INFO,
            source=IssueSource.LINTING,
            recommendation="Another recommendation",
        ),
        Issue(
            file_path="src/main.py",
            line_number=30,
            message="Critical issue",
            severity=Severity.CRITICAL,
            source=IssueSource.DEAD_CODE,
            recommendation="Fix immediately",
        ),
    ]


@pytest.fixture
def aggregated_issues_empty():
    """Fixture for empty aggregated issues."""
    return AggregatedIssues(
        all_issues=[],
        by_file={},
        summary={"critical": 0, "warning": 0, "info": 0},
    )


@pytest.fixture
def aggregated_issues_with_data(multiple_issues):
    """Fixture for aggregated issues with data."""
    return AggregatedIssues(
        all_issues=multiple_issues,
        by_file={
            "tests/test_example.py": multiple_issues[:2],
            "src/main.py": [multiple_issues[2]],
        },
        summary={"critical": 1, "warning": 1, "info": 1},
    )


@pytest.fixture
def issue_warning():
    """Fixture for a warning-level issue."""
    return Issue(
        file_path="test_example.py",
        line_number=10,
        rule_id="E501",
        severity=Severity.WARNING,
        source=IssueSource.LINTING,
    )


@pytest.fixture
def issue_info():
    """Fixture for an info-level issue."""
    return Issue(
        file_path="test_example.py",
        line_number=15,
        rule_id="unused_fixture",
        severity=Severity.INFO,
        source=IssueSource.DEAD_CODE,
    )


@pytest.fixture
def issue_critical():
    """Fixture for a critical-level issue."""
    return Issue(
        file_path="test_example.py",
        line_number=20,
        rule_id="critical_error",
        severity=Severity.CRITICAL,
        source=IssueSource.LINTING,
    )


@pytest.fixture
def analysis_result_with_warning(issue_warning):
    """Fixture for analysis result with warning."""
    return AnalysisResult(engine="ruff", issues=[issue_warning])


@pytest.fixture
def analysis_result_with_info(issue_info):
    """Fixture for analysis result with info."""
    return AnalysisResult(engine="vulture", issues=[issue_info])


@pytest.fixture
def analysis_result_with_critical(issue_critical):
    """Fixture for analysis result with critical issue."""
    return AnalysisResult(engine="ruff", issues=[issue_critical])
