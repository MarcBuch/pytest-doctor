"""Tests for data models."""

import pytest

from pytest_doctor.models import (
    AnalysisResult,
    DiagnosticReport,
    Issue,
    IssueSource,
    Severity,
)


class TestIssue:
    """Tests for Issue model."""

    def test_issue_creation_minimal(self) -> None:
        """Test creating an issue with minimal fields."""
        issue = Issue(
            file_path="tests/test_example.py",
            line_number=10,
        )
        assert issue.file_path == "tests/test_example.py"
        assert issue.line_number == 10
        assert issue.column_number == 0
        assert issue.rule_id == ""
        assert issue.severity == Severity.WARNING
        assert issue.source == IssueSource.LINTING

    def test_issue_creation_full(self) -> None:
        """Test creating an issue with all fields."""
        issue = Issue(
            file_path="src/main.py",
            line_number=42,
            column_number=10,
            rule_id="E501",
            rule_name="Line too long",
            message="Line exceeds 100 characters",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
            recommendation="Break the line",
        )
        assert issue.file_path == "src/main.py"
        assert issue.line_number == 42
        assert issue.column_number == 10
        assert issue.rule_id == "E501"
        assert issue.rule_name == "Line too long"
        assert issue.severity == Severity.WARNING

    def test_issue_to_dict_minimal(self) -> None:
        """Test converting issue to dict with minimal fields."""
        issue = Issue(
            file_path="tests/test_example.py",
            line_number=10,
        )
        issue_dict = issue.to_dict()
        assert issue_dict["file_path"] == "tests/test_example.py"
        assert issue_dict["line_number"] == 10
        assert issue_dict["column_number"] == 0
        assert issue_dict["severity"] == "warning"
        assert issue_dict["source"] == "linting"

    def test_issue_to_dict_full(self) -> None:
        """Test converting issue to dict with all fields."""
        issue = Issue(
            file_path="src/main.py",
            line_number=42,
            column_number=5,
            rule_id="E501",
            rule_name="Line too long",
            message="Line exceeds limit",
            severity=Severity.CRITICAL,
            source=IssueSource.DEAD_CODE,
            recommendation="Fix this",
        )
        issue_dict = issue.to_dict()
        assert issue_dict["rule_id"] == "E501"
        assert issue_dict["rule_name"] == "Line too long"
        assert issue_dict["severity"] == "critical"
        assert issue_dict["source"] == "dead_code"
        assert issue_dict["recommendation"] == "Fix this"

    def test_issue_severity_critical(self) -> None:
        """Test issue with critical severity."""
        issue = Issue(
            file_path="test.py",
            line_number=1,
            severity=Severity.CRITICAL,
        )
        assert issue.severity == Severity.CRITICAL
        assert issue.to_dict()["severity"] == "critical"

    def test_issue_severity_info(self) -> None:
        """Test issue with info severity."""
        issue = Issue(
            file_path="test.py",
            line_number=1,
            severity=Severity.INFO,
        )
        assert issue.severity == Severity.INFO
        assert issue.to_dict()["severity"] == "info"

    @pytest.mark.parametrize(
        "source",
        [
            IssueSource.LINTING,
            IssueSource.DEAD_CODE,
            IssueSource.TEST_QUALITY,
            IssueSource.COVERAGE,
        ],
    )
    def test_issue_source_variants(self, source) -> None:
        """Test issue with different sources."""
        issue = Issue(
            file_path="test.py",
            line_number=1,
            source=source,
        )
        assert issue.source == source

    def test_issue_to_dict_has_file_path(self) -> None:
        """Test that to_dict includes file_path field."""
        issue = Issue(file_path="test.py", line_number=5)
        issue_dict = issue.to_dict()
        assert "file_path" in issue_dict

    def test_issue_to_dict_has_line_number(self) -> None:
        """Test that to_dict includes line_number field."""
        issue = Issue(file_path="test.py", line_number=5)
        issue_dict = issue.to_dict()
        assert "line_number" in issue_dict

    def test_issue_to_dict_has_severity(self) -> None:
        """Test that to_dict includes severity field."""
        issue = Issue(file_path="test.py", line_number=5)
        issue_dict = issue.to_dict()
        assert "severity" in issue_dict

    def test_issue_to_dict_has_source(self) -> None:
        """Test that to_dict includes source field."""
        issue = Issue(file_path="test.py", line_number=5)
        issue_dict = issue.to_dict()
        assert "source" in issue_dict

    def test_issue_with_zero_line_number(self) -> None:
        """Test issue with line number 0."""
        issue = Issue(
            file_path="test.py",
            line_number=0,
        )
        assert issue.line_number == 0

    def test_issue_with_large_line_number(self) -> None:
        """Test issue with large line number."""
        issue = Issue(
            file_path="test.py",
            line_number=999999,
        )
        assert issue.line_number == 999999


class TestAnalysisResult:
    """Tests for AnalysisResult model."""

    def test_analysis_result_creation_minimal(self) -> None:
        """Test creating analysis result with minimal fields."""
        result = AnalysisResult(engine="ruff")
        assert result.engine == "ruff"
        assert result.issues == []
        assert result.duration_ms == 0.0

    def test_analysis_result_creation_full(self) -> None:
        """Test creating analysis result with all fields."""
        issues = [
            Issue(
                file_path="test.py",
                line_number=10,
                severity=Severity.WARNING,
            ),
        ]
        result = AnalysisResult(
            engine="ruff",
            issues=issues,
            duration_ms=150.5,
        )
        assert result.engine == "ruff"
        assert len(result.issues) == 1
        assert result.duration_ms == 150.5

    def test_analysis_result_to_dict_empty(self) -> None:
        """Test converting empty analysis result to dict."""
        result = AnalysisResult(engine="vulture")
        result_dict = result.to_dict()
        assert result_dict["engine"] == "vulture"
        assert result_dict["issues"] == []
        assert result_dict["duration_ms"] == 0.0

    def test_analysis_result_to_dict_with_single_issue(self) -> None:
        """Test converting analysis result with single issue to dict."""
        issues = [
            Issue(
                file_path="src/main.py",
                line_number=5,
                rule_id="E501",
                severity=Severity.WARNING,
            ),
        ]
        result = AnalysisResult(
            engine="ruff",
            issues=issues,
            duration_ms=250.0,
        )
        result_dict = result.to_dict()
        assert result_dict["engine"] == "ruff"
        assert len(result_dict["issues"]) == 1
        assert result_dict["duration_ms"] == 250.0

    def test_analysis_result_to_dict_multiple_issues(self) -> None:
        """Test multiple issues in dict output."""
        issues = [
            Issue(file_path="src/main.py", line_number=5, rule_id="E501"),
            Issue(file_path="src/utils.py", line_number=15, rule_id="F401"),
        ]
        result = AnalysisResult(engine="ruff", issues=issues)
        result_dict = result.to_dict()
        assert len(result_dict["issues"]) == 2

    @pytest.mark.parametrize(
        "engine_name",
        ["ruff", "vulture", "coverage_gaps", "quality"],
    )
    def test_analysis_result_different_engines(self, engine_name) -> None:
        """Test analysis result with different engine names."""
        result = AnalysisResult(engine=engine_name)
        assert result.engine == engine_name

    def test_analysis_result_duration_ms_precision(self) -> None:
        """Test that duration_ms maintains precision."""
        result = AnalysisResult(
            engine="ruff",
            duration_ms=123.456789,
        )
        assert result.duration_ms == 123.456789

    def test_analysis_result_with_multiple_issues(self) -> None:
        """Test analysis result with multiple issues."""
        issues = [
            Issue(file_path=f"file{i}.py", line_number=i)
            for i in range(10)
        ]
        result = AnalysisResult(engine="ruff", issues=issues)
        assert len(result.issues) == 10
        result_dict = result.to_dict()
        assert len(result_dict["issues"]) == 10

    def test_analysis_result_to_dict_contains_all_fields(self) -> None:
        """Test that to_dict includes all fields."""
        result = AnalysisResult(
            engine="test_engine",
            issues=[],
            duration_ms=100.5,
        )
        result_dict = result.to_dict()
        assert "engine" in result_dict
        assert "issues" in result_dict
        assert "duration_ms" in result_dict
        assert result_dict["engine"] == "test_engine"
        assert result_dict["duration_ms"] == 100.5


class TestDiagnosticReport:
    """Tests for DiagnosticReport model."""

    def test_diagnostic_report_creation_minimal(self) -> None:
        """Test creating diagnostic report with minimal fields."""
        report = DiagnosticReport(
            path=".",
            score=75,
        )
        assert report.path == "."
        assert report.score == 75
        assert report.results == []
        assert report.summary == {"critical": 0, "warning": 0, "info": 0}
        assert report.total_issues == 0

    def test_diagnostic_report_creation_full(self) -> None:
        """Test creating diagnostic report with all fields."""
        result = AnalysisResult(engine="ruff")
        report = DiagnosticReport(
            path="/project",
            score=50,
            results=[result],
            summary={"critical": 1, "warning": 2, "info": 3},
            total_issues=6,
        )
        assert report.path == "/project"
        assert report.score == 50
        assert len(report.results) == 1
        assert report.summary["critical"] == 1
        assert report.total_issues == 6

    def test_diagnostic_report_to_dict_minimal(self) -> None:
        """Test converting diagnostic report to dict with minimal fields."""
        report = DiagnosticReport(
            path=".",
            score=100,
        )
        report_dict = report.to_dict()
        assert report_dict["path"] == "."
        assert report_dict["score"] == 100
        assert report_dict["results"] == []
        assert report_dict["summary"] == {"critical": 0, "warning": 0, "info": 0}
        assert report_dict["total_issues"] == 0

    def test_diagnostic_report_to_dict_full(self) -> None:
        """Test diagnostic report dict conversion."""
        result = AnalysisResult(engine="ruff")
        report = DiagnosticReport(
            path="/project",
            score=60,
            results=[result],
        )
        report_dict = report.to_dict()
        assert report_dict["path"] == "/project"
        assert report_dict["score"] == 60
        assert len(report_dict["results"]) == 1

    def test_diagnostic_report_to_dict_results_engine(self) -> None:
        """Test that results include engine in dict output."""
        result = AnalysisResult(engine="ruff")
        report = DiagnosticReport(
            path="/project",
            score=60,
            results=[result],
        )
        report_dict = report.to_dict()
        assert report_dict["results"][0]["engine"] == "ruff"

    def test_diagnostic_report_to_dict_summary(self) -> None:
        """Test that summary is preserved in dict output."""
        report = DiagnosticReport(
            path="/project",
            score=60,
            summary={"critical": 0, "warning": 1, "info": 0},
            total_issues=1,
        )
        report_dict = report.to_dict()
        assert report_dict["summary"]["warning"] == 1

    def test_diagnostic_report_with_perfect_score(self) -> None:
        """Test diagnostic report with perfect score."""
        report = DiagnosticReport(
            path=".",
            score=100,
            summary={"critical": 0, "warning": 0, "info": 0},
            total_issues=0,
        )
        assert report.score == 100
        assert report.total_issues == 0

    def test_diagnostic_report_with_critical_issues(self) -> None:
        """Test diagnostic report with critical issues."""
        report = DiagnosticReport(
            path=".",
            score=20,
            summary={"critical": 5, "warning": 3, "info": 2},
            total_issues=10,
        )
        assert report.score == 20
        assert report.summary["critical"] == 5
        assert report.total_issues == 10

    def test_diagnostic_report_with_multiple_results(self) -> None:
        """Test diagnostic report with multiple analysis results."""
        results = [
            AnalysisResult(engine="ruff"),
            AnalysisResult(engine="vulture"),
            AnalysisResult(engine="coverage_gaps"),
        ]
        report = DiagnosticReport(
            path=".",
            score=50,
            results=results,
        )
        assert len(report.results) == 3
        report_dict = report.to_dict()
        assert len(report_dict["results"]) == 3

    def test_diagnostic_report_to_dict_all_fields(self) -> None:
        """Test that to_dict includes all fields."""
        report = DiagnosticReport(
            path="/test/path",
            score=75,
            results=[],
            summary={"critical": 1, "warning": 2, "info": 3},
            total_issues=6,
        )
        report_dict = report.to_dict()
        assert "path" in report_dict
        assert "score" in report_dict
        assert "results" in report_dict
        assert "summary" in report_dict
        assert "total_issues" in report_dict
        assert report_dict["path"] == "/test/path"
        assert report_dict["score"] == 75
        assert report_dict["summary"]["critical"] == 1

    def test_diagnostic_report_with_zero_score(self) -> None:
        """Test diagnostic report with zero score."""
        report = DiagnosticReport(
            path=".",
            score=0,
            summary={"critical": 10, "warning": 10, "info": 10},
            total_issues=30,
        )
        assert report.score == 0
        assert report.total_issues == 30

    def test_diagnostic_report_summary_distribution(self) -> None:
        """Test diagnostic report with different severity distributions."""
        report = DiagnosticReport(
            path=".",
            score=50,
            summary={"critical": 5, "warning": 10, "info": 85},
            total_issues=100,
        )
        assert report.summary["critical"] == 5
        assert report.summary["warning"] == 10
        assert report.summary["info"] == 85
        assert sum(report.summary.values()) == 100
