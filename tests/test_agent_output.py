"""Tests for agent output formatting."""

from pytest_doctor.agent_output import AgentOutputFormatter, AgentFixSuggestion
from pytest_doctor.aggregation import AggregatedIssues, ResultsAggregator
from pytest_doctor.models import AnalysisResult, DiagnosticReport, Issue, IssueSource, Severity


class TestAgentFixSuggestion:
    """Tests for AgentFixSuggestion."""

    def test_agent_fix_suggestion_creation(self) -> None:
        """Test creating a fix suggestion."""
        suggestion = AgentFixSuggestion(
            file_path="tests/test_example.py",
            line_number=45,
            rule_id="E501",
            rule_name="Line too long",
            message="Line too long (120 > 100 characters)",
            severity="warning",
            recommendation="Break line into multiple lines",
        )
        assert suggestion.file_path == "tests/test_example.py"
        assert suggestion.line_number == 45
        assert suggestion.rule_id == "E501"

    def test_agent_fix_suggestion_to_dict(self) -> None:
        """Test converting suggestion to dict."""
        suggestion = AgentFixSuggestion(
            file_path="tests/test_example.py",
            line_number=45,
            rule_id="E501",
            rule_name="Line too long",
            message="Line too long (120 > 100 characters)",
            severity="warning",
            recommendation="Break line into multiple lines",
        )
        result_dict = suggestion.to_dict()
        assert result_dict["file_path"] == "tests/test_example.py"
        assert result_dict["line_number"] == 45
        assert result_dict["rule_id"] == "E501"
        assert result_dict["recommendation"] == "Break line into multiple lines"

    def test_agent_fix_suggestion_with_context_lines(self) -> None:
        """Test suggestion with context lines."""
        context = ["line 44: def test_foo():", "line 45:     some_very_long_line = 1"]
        suggestion = AgentFixSuggestion(
            file_path="tests/test_example.py",
            line_number=45,
            rule_id="E501",
            rule_name="Line too long",
            message="Line too long",
            severity="warning",
            recommendation="Break line",
            context_lines=context,
        )
        result_dict = suggestion.to_dict()
        assert result_dict["context_lines"] == context


class TestAgentOutputFormatter:
    """Tests for AgentOutputFormatter."""

    def test_formatter_initialization(self) -> None:
        """Test formatter initialization."""
        formatter = AgentOutputFormatter()
        assert formatter is not None

    def test_format_for_agent_basic(self) -> None:
        """Test formatting basic diagnostic for agent."""
        formatter = AgentOutputFormatter()

        # Create a simple diagnostic report
        diagnostic = DiagnosticReport(
            path=".",
            score=75,
            results=[],
            summary={"critical": 0, "warning": 2, "info": 3},
            total_issues=5,
        )

        # Create aggregated issues
        aggregated = AggregatedIssues(
            all_issues=[
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
            ],
            by_file={"tests/test_example.py": []},
            summary={"critical": 0, "warning": 2, "info": 3},
        )

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        assert agent_output.context.health_score == 75
        assert agent_output.context.total_issues == 5
        assert agent_output.context.warning_count == 2
        assert len(agent_output.suggestions) == 2

    def test_format_for_agent_to_dict(self) -> None:
        """Test converting agent output to dict."""
        formatter = AgentOutputFormatter()

        diagnostic = DiagnosticReport(
            path=".",
            score=75,
            results=[],
            summary={"critical": 1, "warning": 2, "info": 3},
            total_issues=6,
        )

        aggregated = AggregatedIssues(
            all_issues=[
                Issue(
                    file_path="tests/test_example.py",
                    line_number=10,
                    message="Critical issue",
                    severity=Severity.CRITICAL,
                    source=IssueSource.LINTING,
                    recommendation="Fix this",
                ),
            ],
            by_file={"tests/test_example.py": []},
            summary={"critical": 1, "warning": 2, "info": 3},
        )

        agent_output = formatter.format_for_agent(diagnostic, aggregated)
        output_dict = agent_output.to_dict()

        assert output_dict["context"]["health_score"] == 75
        assert output_dict["context"]["critical_count"] == 1
        assert len(output_dict["suggestions"]) == 1
        assert "deeplinks" in output_dict

    def test_deeplinks_creation(self) -> None:
        """Test deeplink creation."""
        formatter = AgentOutputFormatter()

        diagnostic = DiagnosticReport(
            path="/project/path",
            score=50,
            results=[],
            summary={"critical": 1, "warning": 0, "info": 0},
            total_issues=1,
        )

        aggregated = AggregatedIssues(
            all_issues=[
                Issue(
                    file_path="tests/test_example.py",
                    line_number=10,
                    message="Critical issue",
                    severity=Severity.CRITICAL,
                    source=IssueSource.LINTING,
                    recommendation="Fix this",
                ),
            ],
            by_file={"tests/test_example.py": []},
            summary={"critical": 1, "warning": 0, "info": 0},
        )

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        # Check deeplinks are present
        assert len(agent_output.deeplinks) > 0
        assert "diagnostics_summary" in agent_output.deeplinks
        assert "documentation" in agent_output.deeplinks

    def test_deeplinks_include_critical_files(self) -> None:
        """Test that deeplinks include critical files."""
        formatter = AgentOutputFormatter()

        diagnostic = DiagnosticReport(
            path=".",
            score=30,
            results=[],
            summary={"critical": 2, "warning": 0, "info": 0},
            total_issues=2,
        )

        aggregated = AggregatedIssues(
            all_issues=[
                Issue(
                    file_path="tests/test_critical.py",
                    line_number=5,
                    message="Critical",
                    severity=Severity.CRITICAL,
                    source=IssueSource.LINTING,
                    recommendation="Fix",
                ),
                Issue(
                    file_path="tests/test_critical2.py",
                    line_number=15,
                    message="Critical",
                    severity=Severity.CRITICAL,
                    source=IssueSource.LINTING,
                    recommendation="Fix",
                ),
            ],
            by_file={},
            summary={"critical": 2, "warning": 0, "info": 0},
        )

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        # Check that critical file deeplinks are present
        has_critical_link = any("critical_" in key for key in agent_output.deeplinks)
        assert has_critical_link

    def test_format_with_no_issues(self) -> None:
        """Test formatting when there are no issues."""
        formatter = AgentOutputFormatter()

        diagnostic = DiagnosticReport(
            path=".",
            score=100,
            results=[],
            summary={"critical": 0, "warning": 0, "info": 0},
            total_issues=0,
        )

        aggregated = AggregatedIssues(
            all_issues=[],
            by_file={},
            summary={"critical": 0, "warning": 0, "info": 0},
        )

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        assert agent_output.context.health_score == 100
        assert agent_output.context.total_issues == 0
        assert len(agent_output.suggestions) == 0
