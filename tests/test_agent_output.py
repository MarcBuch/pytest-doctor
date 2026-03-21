"""Tests for agent output formatting."""

from pytest_doctor.agent_output import (
    AgentContext,
    AgentFixSuggestion,
    AgentOutput,
    AgentOutputFormatter,
)
from pytest_doctor.aggregation import AggregatedIssues
from pytest_doctor.models import DiagnosticReport, Issue, IssueSource, Severity


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

    def test_agent_fix_suggestion_to_dict_without_context(self) -> None:
        """Test converting suggestion to dict without context lines."""
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
        assert result_dict["context_lines"] == []

    def test_agent_fix_suggestion_to_dict_with_context(self) -> None:
        """Test converting suggestion to dict with context lines."""
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


class TestAgentContext:
    """Tests for AgentContext."""

    def test_agent_context_creation(self) -> None:
        """Test creating an agent context."""
        context = AgentContext(
            project_path=".",
            health_score=75,
            total_issues=5,
            critical_count=0,
            warning_count=2,
            info_count=3,
        )
        assert context.project_path == "."
        assert context.health_score == 75
        assert context.total_issues == 5
        assert context.critical_count == 0
        assert context.warning_count == 2
        assert context.info_count == 3

    def test_agent_context_with_critical_issues(self) -> None:
        """Test agent context with critical issues."""
        context = AgentContext(
            project_path="/some/path",
            health_score=30,
            total_issues=10,
            critical_count=5,
            warning_count=3,
            info_count=2,
        )
        assert context.critical_count == 5
        assert context.health_score == 30


class TestAgentOutput:
    """Tests for AgentOutput."""

    def test_agent_output_creation(self) -> None:
        """Test creating an agent output."""
        context = AgentContext(
            project_path=".",
            health_score=75,
            total_issues=2,
            critical_count=0,
            warning_count=1,
            info_count=1,
        )
        suggestions = [
            AgentFixSuggestion(
                file_path="tests/test_example.py",
                line_number=10,
                rule_id="E501",
                rule_name="Line too long",
                message="Test",
                severity="warning",
                recommendation="Fix",
            ),
        ]
        deeplinks = {"documentation": "https://example.com"}

        output = AgentOutput(
            context=context,
            suggestions=suggestions,
            deeplinks=deeplinks,
        )
        assert output.context.health_score == 75
        assert len(output.suggestions) == 1
        assert output.deeplinks == deeplinks

    def test_agent_output_to_dict_without_suggestions(self) -> None:
        """Test converting empty agent output to dict."""
        context = AgentContext(
            project_path=".",
            health_score=100,
            total_issues=0,
            critical_count=0,
            warning_count=0,
            info_count=0,
        )
        output = AgentOutput(
            context=context,
            suggestions=[],
            deeplinks={},
        )
        output_dict = output.to_dict()
        assert output_dict["context"]["health_score"] == 100
        assert output_dict["suggestions"] == []

    def test_agent_output_to_dict_with_suggestions(self) -> None:
        """Test converting agent output with suggestions to dict."""
        context = AgentContext(
            project_path=".",
            health_score=50,
            total_issues=2,
            critical_count=1,
            warning_count=1,
            info_count=0,
        )
        suggestions = [
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
        deeplinks = {
            "documentation": "https://example.com",
            "fix_guide": "https://example.com/fix",
        }
        output = AgentOutput(
            context=context,
            suggestions=suggestions,
            deeplinks=deeplinks,
        )
        output_dict = output.to_dict()
        assert output_dict["context"]["critical_count"] == 1
        assert len(output_dict["suggestions"]) == 2
        assert output_dict["suggestions"][0]["rule_id"] == "E501"
        assert output_dict["deeplinks"] == deeplinks


class TestAgentOutputFormatter:
    """Tests for AgentOutputFormatter."""

    def test_formatter_initialization(self) -> None:
        """Test formatter initialization."""
        formatter = AgentOutputFormatter()
        assert formatter is not None

    def _create_basic_diagnostic(self) -> DiagnosticReport:
        """Helper to create a basic diagnostic report."""
        return DiagnosticReport(
            path=".",
            score=75,
            results=[],
            summary={"critical": 0, "warning": 2, "info": 3},
            total_issues=5,
        )

    def _create_basic_aggregated_issues(self) -> AggregatedIssues:
        """Helper to create basic aggregated issues."""
        return AggregatedIssues(
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

    def test_format_for_agent_returns_output(self) -> None:
        """Test format_for_agent returns valid AgentOutput."""
        formatter = AgentOutputFormatter()
        diagnostic = self._create_basic_diagnostic()
        aggregated = self._create_basic_aggregated_issues()

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        assert isinstance(agent_output, AgentOutput)

    def test_format_for_agent_health_score(self) -> None:
        """Test format_for_agent preserves health score."""
        formatter = AgentOutputFormatter()
        diagnostic = self._create_basic_diagnostic()
        aggregated = self._create_basic_aggregated_issues()

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        assert agent_output.context.health_score == 75

    def test_format_for_agent_total_issues(self) -> None:
        """Test format_for_agent preserves total issues count."""
        formatter = AgentOutputFormatter()
        diagnostic = self._create_basic_diagnostic()
        aggregated = self._create_basic_aggregated_issues()

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        assert agent_output.context.total_issues == 5

    def test_format_for_agent_warning_count(self) -> None:
        """Test format_for_agent preserves warning count."""
        formatter = AgentOutputFormatter()
        diagnostic = self._create_basic_diagnostic()
        aggregated = self._create_basic_aggregated_issues()

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        assert agent_output.context.warning_count == 2

    def test_format_for_agent_suggestions(self) -> None:
        """Test format_for_agent creates suggestions."""
        formatter = AgentOutputFormatter()
        diagnostic = self._create_basic_diagnostic()
        aggregated = self._create_basic_aggregated_issues()

        agent_output = formatter.format_for_agent(diagnostic, aggregated)

        assert len(agent_output.suggestions) == 2

    def test_agent_output_to_dict(self) -> None:
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

    def test_agent_output_to_dict_has_suggestions(self) -> None:
        """Test to_dict includes suggestions."""
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

        assert len(output_dict["suggestions"]) == 1
        assert "deeplinks" in output_dict

    def test_deeplinks_are_created(self) -> None:
        """Test deeplinks are created."""
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

        assert len(agent_output.deeplinks) > 0

    def test_deeplinks_have_documentation(self) -> None:
        """Test deeplinks include documentation."""
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

        has_critical_link = any("critical_" in key for key in agent_output.deeplinks)
        assert has_critical_link

    def test_format_with_no_issues_health_score(self) -> None:
        """Test formatting with no issues has perfect score."""
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

    def test_format_with_no_issues_no_suggestions(self) -> None:
        """Test formatting with no issues has no suggestions."""
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

        assert len(agent_output.suggestions) == 0
