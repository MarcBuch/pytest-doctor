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

    def test_agent_fix_suggestion_all_fields_file_path(self) -> None:
        """Test suggestion file path is preserved."""
        suggestion = AgentFixSuggestion(
            file_path="src/main.py",
            line_number=10,
            rule_id="critical_rule",
            rule_name="Critical Rule",
            message="Critical message",
            severity="critical",
            recommendation="Fix immediately",
        )
        result_dict = suggestion.to_dict()
        assert result_dict["file_path"] == "src/main.py"

    def test_agent_fix_suggestion_all_fields_severity(self) -> None:
        """Test suggestion severity is preserved."""
        suggestion = AgentFixSuggestion(
            file_path="src/main.py",
            line_number=10,
            rule_id="critical_rule",
            rule_name="Critical Rule",
            message="Critical message",
            severity="critical",
            recommendation="Fix immediately",
        )
        result_dict = suggestion.to_dict()
        assert result_dict["severity"] == "critical"

    def test_agent_fix_suggestion_all_fields_recommendation(self) -> None:
        """Test suggestion recommendation is preserved."""
        suggestion = AgentFixSuggestion(
            file_path="src/main.py",
            line_number=10,
            rule_id="critical_rule",
            rule_name="Critical Rule",
            message="Critical message",
            severity="critical",
            recommendation="Fix immediately",
        )
        result_dict = suggestion.to_dict()
        assert result_dict["recommendation"] == "Fix immediately"

    def test_agent_fix_suggestion_empty_context_lines(self) -> None:
        """Test suggestion with empty context lines list."""
        suggestion = AgentFixSuggestion(
            file_path="test.py",
            line_number=1,
            rule_id="rule1",
            rule_name="Test Rule",
            message="Test",
            severity="info",
            recommendation="Test rec",
            context_lines=[],
        )
        result_dict = suggestion.to_dict()
        assert result_dict["context_lines"] == []


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

    def _create_test_suggestion(self) -> AgentFixSuggestion:
        """Helper to create a test suggestion."""
        return AgentFixSuggestion(
            file_path="src/test.py",
            line_number=42,
            rule_id="TEST001",
            rule_name="Test Rule",
            message="Test message",
            severity="critical",
            recommendation="Test recommendation",
        )

    def _create_test_context(self) -> AgentContext:
        """Helper to create a test context."""
        return AgentContext(
            project_path=".",
            health_score=100,
            total_issues=0,
            critical_count=0,
            warning_count=0,
            info_count=0,
        )

    def test_agent_output_creation(self, agent_context_with_issues, single_fix_suggestion) -> None:
        """Test creating an agent output."""
        deeplinks = {"documentation": "https://example.com"}

        output = AgentOutput(
            context=agent_context_with_issues,
            suggestions=[single_fix_suggestion],
            deeplinks=deeplinks,
        )
        assert output.context.health_score == 50
        assert len(output.suggestions) == 1
        assert output.deeplinks == deeplinks

    def test_agent_output_to_dict_without_suggestions(self, agent_context_minimal) -> None:
        """Test converting empty agent output to dict."""
        output = AgentOutput(
            context=agent_context_minimal,
            suggestions=[],
            deeplinks={},
        )
        output_dict = output.to_dict()
        assert output_dict["context"]["health_score"] == 100
        assert output_dict["suggestions"] == []

    def test_agent_output_to_dict_with_suggestions(
        self, agent_context_with_issues, multiple_fix_suggestions
    ) -> None:
        """Test converting agent output with suggestions to dict."""
        deeplinks = {
            "documentation": "https://example.com",
            "fix_guide": "https://example.com/fix",
        }
        output = AgentOutput(
            context=agent_context_with_issues,
            suggestions=multiple_fix_suggestions,
            deeplinks=deeplinks,
        )
        output_dict = output.to_dict()
        assert output_dict["context"]["critical_count"] == 3
        assert len(output_dict["suggestions"]) == 2
        assert output_dict["suggestions"][0]["rule_id"] == "E501"
        assert output_dict["deeplinks"] == deeplinks

    def test_agent_output_to_dict_context_path(self) -> None:
        """Test to_dict context includes project path."""
        context = AgentContext(
            project_path="/test/path",
            health_score=50,
            total_issues=5,
            critical_count=1,
            warning_count=2,
            info_count=2,
        )
        output = AgentOutput(
            context=context,
            suggestions=[],
            deeplinks={},
        )
        output_dict = output.to_dict()
        assert output_dict["context"]["project_path"] == "/test/path"

    def test_agent_output_to_dict_context_health_score(self) -> None:
        """Test to_dict context includes health score."""
        context = AgentContext(
            project_path="/test/path",
            health_score=50,
            total_issues=5,
            critical_count=1,
            warning_count=2,
            info_count=2,
        )
        output = AgentOutput(
            context=context,
            suggestions=[],
            deeplinks={},
        )
        output_dict = output.to_dict()
        assert output_dict["context"]["health_score"] == 50

    def test_agent_output_to_dict_context_counts(self) -> None:
        """Test to_dict context includes issue counts."""
        context = AgentContext(
            project_path="/test/path",
            health_score=50,
            total_issues=5,
            critical_count=1,
            warning_count=2,
            info_count=2,
        )
        output = AgentOutput(
            context=context,
            suggestions=[],
            deeplinks={},
        )
        output_dict = output.to_dict()
        assert output_dict["context"]["critical_count"] == 1
        assert output_dict["context"]["warning_count"] == 2
        assert output_dict["context"]["info_count"] == 2

    def test_agent_output_to_dict_suggestion_file_path(self) -> None:
        """Test to_dict suggestion file path is preserved."""
        suggestion = self._create_test_suggestion()
        context = self._create_test_context()
        output = AgentOutput(
            context=context,
            suggestions=[suggestion],
            deeplinks={"doc": "https://example.com"},
        )
        output_dict = output.to_dict()
        assert output_dict["suggestions"][0]["file_path"] == "src/test.py"

    def test_agent_output_to_dict_suggestion_rule_id(self) -> None:
        """Test to_dict suggestion rule id is preserved."""
        suggestion = self._create_test_suggestion()
        context = self._create_test_context()
        output = AgentOutput(
            context=context,
            suggestions=[suggestion],
            deeplinks={},
        )
        output_dict = output.to_dict()
        assert output_dict["suggestions"][0]["rule_id"] == "TEST001"

    def test_agent_output_multiple_deeplinks_count(self) -> None:
        """Test agent output with multiple deeplinks."""
        deeplinks = {
            "documentation": "https://example.com/docs",
            "fix_guide": "https://example.com/fix",
            "critical_critical_file.py": "file:///critical_file.py#critical",
            "issue_tracker": "https://github.com/issues",
        }
        output = AgentOutput(
            context=self._create_test_context(),
            suggestions=[],
            deeplinks=deeplinks,
        )
        output_dict = output.to_dict()
        assert len(output_dict["deeplinks"]) == 4

    def test_agent_output_multiple_deeplinks_documentation(self) -> None:
        """Test deeplinks include documentation."""
        deeplinks = {
            "documentation": "https://example.com/docs",
            "fix_guide": "https://example.com/fix",
        }
        output = AgentOutput(
            context=self._create_test_context(),
            suggestions=[],
            deeplinks=deeplinks,
        )
        output_dict = output.to_dict()
        assert output_dict["deeplinks"]["documentation"] == "https://example.com/docs"


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

    def _create_critical_issue_diagnostic(self) -> tuple[DiagnosticReport, AggregatedIssues]:
        """Helper to create diagnostic with critical issue."""
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
        return diagnostic, aggregated

    def _create_aggregated_issues_from_list(self, issues: list[Issue]) -> AggregatedIssues:
        """Helper to create aggregated issues from a list."""
        summary = {"critical": 0, "warning": 0, "info": 0}
        for issue in issues:
            severity_key = issue.severity.value.lower()
            summary[severity_key] += 1
        return AggregatedIssues(
            all_issues=issues,
            by_file={},
            summary=summary,
        )

    def _create_issue(
        self,
        file_path: str,
        line_number: int,
        message: str = "Test issue",
        severity: Severity = Severity.WARNING,
        rule_id: str = "R001",
        rule_name: str = "Test Rule",
        recommendation: str = "Fix it",
    ) -> Issue:
        """Helper to create an issue with custom parameters."""
        return Issue(
            file_path=file_path,
            line_number=line_number,
            rule_id=rule_id,
            rule_name=rule_name,
            message=message,
            severity=severity,
            source=IssueSource.LINTING,
            recommendation=recommendation,
        )

    def _create_diagnostic_report(
        self, path: str = ".", score: int = 75, critical: int = 0, warning: int = 0, info: int = 0
    ) -> DiagnosticReport:
        """Helper to create a diagnostic report with custom counts."""
        total = critical + warning + info
        return DiagnosticReport(
            path=path,
            score=score,
            results=[],
            summary={"critical": critical, "warning": warning, "info": info},
            total_issues=total,
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

    def test_agent_output_to_dict(
        self, formatter_diagnostic_with_critical, formatter_aggregated_with_critical
    ) -> None:
        """Test converting agent output to dict."""
        formatter = AgentOutputFormatter()
        agent_output = formatter.format_for_agent(
            formatter_diagnostic_with_critical, formatter_aggregated_with_critical
        )
        output_dict = agent_output.to_dict()

        assert output_dict["context"]["health_score"] == 75
        assert output_dict["context"]["critical_count"] == 1

    def test_agent_output_to_dict_has_suggestions(
        self, formatter_diagnostic_with_critical, formatter_aggregated_with_critical
    ) -> None:
        """Test to_dict includes suggestions."""
        formatter = AgentOutputFormatter()
        agent_output = formatter.format_for_agent(
            formatter_diagnostic_with_critical, formatter_aggregated_with_critical
        )
        output_dict = agent_output.to_dict()

        assert len(output_dict["suggestions"]) == 1
        assert "deeplinks" in output_dict

    def test_deeplinks_are_created(
        self, formatter_diagnostic_with_critical, formatter_aggregated_with_critical
    ) -> None:
        """Test deeplinks are created."""
        formatter = AgentOutputFormatter()
        agent_output = formatter.format_for_agent(
            formatter_diagnostic_with_critical, formatter_aggregated_with_critical
        )
        assert len(agent_output.deeplinks) > 0

    def test_deeplinks_have_documentation(self) -> None:
        """Test deeplinks include documentation link."""
        formatter = AgentOutputFormatter()
        diagnostic, aggregated = self._create_critical_issue_diagnostic()
        agent_output = formatter.format_for_agent(diagnostic, aggregated)
        assert "documentation" in agent_output.deeplinks

    def test_deeplinks_have_fix_guide(self) -> None:
        """Test deeplinks include fix guide link."""
        formatter = AgentOutputFormatter()
        diagnostic, aggregated = self._create_critical_issue_diagnostic()
        agent_output = formatter.format_for_agent(diagnostic, aggregated)
        assert "fix_guide" in agent_output.deeplinks

    def test_deeplinks_include_critical_files(self) -> None:
        """Test that deeplinks include critical files."""
        formatter = AgentOutputFormatter()
        issues = [
            self._create_issue("tests/test_critical.py", 5, severity=Severity.CRITICAL),
            self._create_issue("tests/test_critical2.py", 15, severity=Severity.CRITICAL),
        ]
        diagnostic = self._create_diagnostic_report(score=30, critical=2)
        aggregated = self._create_aggregated_issues_from_list(issues)
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

    def test_format_for_agent_context_path(self) -> None:
        """Test format_for_agent preserves project path."""
        formatter = AgentOutputFormatter()
        diagnostic = self._create_diagnostic_report(path="/my/project", warning=1)
        issue = self._create_issue("test.py", 1)
        aggregated = self._create_aggregated_issues_from_list([issue])
        agent_output = formatter.format_for_agent(diagnostic, aggregated)
        assert agent_output.context.project_path == "/my/project"

    def test_format_for_agent_issue_conversion_single(self) -> None:
        """Test single issue is converted to suggestion."""
        formatter = AgentOutputFormatter()
        issue = self._create_issue("file1.py", 10, rule_id="R001", rule_name="Rule 1")
        diagnostic = self._create_diagnostic_report(score=50, warning=1)
        aggregated = self._create_aggregated_issues_from_list([issue])
        agent_output = formatter.format_for_agent(diagnostic, aggregated)
        assert len(agent_output.suggestions) == 1
        assert agent_output.suggestions[0].rule_id == "R001"

    def test_format_for_agent_issue_conversion_multiple(self) -> None:
        """Test multiple issues are converted to suggestions."""
        formatter = AgentOutputFormatter()
        issues = [
            self._create_issue("file1.py", 10, rule_id="R001", rule_name="Rule 1"),
            self._create_issue("file2.py", 20, rule_id="R002", rule_name="Rule 2", severity=Severity.INFO),
        ]
        diagnostic = self._create_diagnostic_report(score=50, warning=1, info=1)
        aggregated = self._create_aggregated_issues_from_list(issues)
        agent_output = formatter.format_for_agent(diagnostic, aggregated)
        assert len(agent_output.suggestions) == 2

    def test_format_for_agent_severity_conversion(self) -> None:
        """Test issue severity is converted to string."""
        formatter = AgentOutputFormatter()
        issue = self._create_issue("test.py", 1, severity=Severity.CRITICAL)
        diagnostic = self._create_diagnostic_report(score=50, critical=1)
        aggregated = self._create_aggregated_issues_from_list([issue])
        agent_output = formatter.format_for_agent(diagnostic, aggregated)
        assert agent_output.suggestions[0].severity == "critical"
        assert isinstance(agent_output.suggestions[0].severity, str)
