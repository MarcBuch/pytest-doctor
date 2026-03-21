"""Tests for data models."""

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

    def test_issue_source_variants(self) -> None:
        """Test issue with different sources."""
        sources = [
            IssueSource.LINTING,
            IssueSource.DEAD_CODE,
            IssueSource.TEST_QUALITY,
            IssueSource.COVERAGE,
        ]
        for source in sources:
            issue = Issue(
                file_path="test.py",
                line_number=1,
                source=source,
            )
            assert issue.source == source


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

    def test_analysis_result_to_dict_with_issues(self) -> None:
        """Test converting analysis result with issues to dict."""
        issues = [
            Issue(
                file_path="src/main.py",
                line_number=5,
                rule_id="E501",
                severity=Severity.WARNING,
            ),
            Issue(
                file_path="src/utils.py",
                line_number=15,
                rule_id="F401",
                severity=Severity.INFO,
            ),
        ]
        result = AnalysisResult(
            engine="ruff",
            issues=issues,
            duration_ms=250.0,
        )
        result_dict = result.to_dict()
        assert result_dict["engine"] == "ruff"
        assert len(result_dict["issues"]) == 2
        assert result_dict["duration_ms"] == 250.0
        assert result_dict["issues"][0]["rule_id"] == "E501"


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
        """Test converting diagnostic report to dict with all fields."""
        result = AnalysisResult(
            engine="ruff",
            issues=[
                Issue(
                    file_path="test.py",
                    line_number=1,
                    rule_id="E501",
                ),
            ],
            duration_ms=100.0,
        )
        report = DiagnosticReport(
            path="/project",
            score=60,
            results=[result],
            summary={"critical": 0, "warning": 1, "info": 0},
            total_issues=1,
        )
        report_dict = report.to_dict()
        assert report_dict["path"] == "/project"
        assert report_dict["score"] == 60
        assert len(report_dict["results"]) == 1
        assert report_dict["results"][0]["engine"] == "ruff"
        assert report_dict["summary"]["warning"] == 1
        assert report_dict["total_issues"] == 1

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
