"""Agent-friendly output formatting for automated fixes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pytest_doctor.aggregation import AggregatedIssues
from pytest_doctor.models import DiagnosticReport


@dataclass
class AgentContext:
    """Context information for agent processing."""

    project_path: str
    health_score: int
    total_issues: int
    critical_count: int
    warning_count: int
    info_count: int


@dataclass
class AgentFixSuggestion:
    """A single fix suggestion for an agent."""

    file_path: str
    line_number: int
    rule_id: str
    rule_name: str
    message: str
    severity: str
    recommendation: str
    context_lines: list[str] | None = None  # Source code context

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "message": self.message,
            "severity": self.severity,
            "recommendation": self.recommendation,
            "context_lines": self.context_lines or [],
        }


@dataclass
class AgentOutput:
    """Agent-friendly output structure."""

    context: AgentContext
    suggestions: list[AgentFixSuggestion]
    deeplinks: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "context": {
                "project_path": self.context.project_path,
                "health_score": self.context.health_score,
                "total_issues": self.context.total_issues,
                "critical_count": self.context.critical_count,
                "warning_count": self.context.warning_count,
                "info_count": self.context.info_count,
            },
            "suggestions": [s.to_dict() for s in self.suggestions],
            "deeplinks": self.deeplinks,
        }


class AgentOutputFormatter:
    """Formats diagnostic results for agent consumption."""

    def __init__(self) -> None:
        """Initialize the formatter."""
        pass

    def format_for_agent(
        self,
        diagnostic: DiagnosticReport,
        aggregated: AggregatedIssues,
    ) -> AgentOutput:
        """
        Format diagnostic results for agent consumption.

        Args:
            diagnostic: The diagnostic report
            aggregated: The aggregated issues

        Returns:
            AgentOutput ready for agent processing
        """
        # Create context
        context = AgentContext(
            project_path=diagnostic.path,
            health_score=diagnostic.score,
            total_issues=diagnostic.total_issues,
            critical_count=aggregated.summary["critical"],
            warning_count=aggregated.summary["warning"],
            info_count=aggregated.summary["info"],
        )

        # Create fix suggestions
        suggestions: list[AgentFixSuggestion] = []
        for issue in aggregated.all_issues:
            suggestion = AgentFixSuggestion(
                file_path=issue.file_path,
                line_number=issue.line_number,
                rule_id=issue.rule_id,
                rule_name=issue.rule_name,
                message=issue.message,
                severity=issue.severity.value,
                recommendation=issue.recommendation,
            )
            suggestions.append(suggestion)

        # Create deeplinks
        deeplinks = self._create_deeplinks(diagnostic, aggregated)

        return AgentOutput(
            context=context,
            suggestions=suggestions,
            deeplinks=deeplinks,
        )

    def _create_deeplinks(
        self,
        diagnostic: DiagnosticReport,
        aggregated: AggregatedIssues,
    ) -> dict[str, str]:
        """
        Create deeplinks for agent integration.

        Deeplinks provide URLs or references that agents can use to jump to
        specific issues in the codebase or documentation.

        Args:
            diagnostic: The diagnostic report
            aggregated: The aggregated issues

        Returns:
            Dictionary of deeplink references
        """
        deeplinks: dict[str, str] = {}

        # Add a link to the diagnostics summary
        diagnostics_path = Path(diagnostic.path).resolve() / ".pytest-doctor" / "diagnostics.json"
        deeplinks["diagnostics_summary"] = f"file://{diagnostics_path}"

        # Add links to critical issues
        if aggregated.summary["critical"] > 0:
            critical_files = set()
            for issue in aggregated.all_issues:
                if issue.severity.value == "critical":
                    critical_files.add(issue.file_path)

            for file_path in critical_files:
                deeplinks[f"critical_{file_path}"] = f"file://{file_path}#critical"

        # Add documentation links
        deeplinks["documentation"] = (
            "https://github.com/pytest-doctor/pytest-doctor#agent-integration"
        )
        deeplinks["fix_guide"] = "https://github.com/pytest-doctor/pytest-doctor#fixing-issues"

        return deeplinks
