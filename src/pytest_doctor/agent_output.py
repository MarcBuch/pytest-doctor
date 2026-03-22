"""Agent-friendly output formatting for automated fixes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pytest_doctor.aggregation import AggregatedIssues
from pytest_doctor.models import DiagnosticReport


@dataclass
class MutationStats:
    """Mutation testing statistics."""

    total_mutations: int
    killed: int
    survival_rate: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_mutations": self.total_mutations,
            "killed": self.killed,
            "survival_rate": self.survival_rate,
        }


@dataclass
class AgentContext:
    """Context information for agent processing."""

    project_path: str
    health_score: int
    total_issues: int
    critical_count: int
    warning_count: int
    info_count: int
    assertion_quality_score: int | None = None
    mutation_stats: MutationStats | None = None


@dataclass
class MutationEvidence:
    """Evidence from mutation testing for weak assertions."""

    mutation_type: str
    location: str
    survived_by_tests: list[str]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mutation_type": self.mutation_type,
            "location": self.location,
            "survived_by_tests": self.survived_by_tests,
            "recommendation": self.recommendation,
        }


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
    mutation_evidence: MutationEvidence | None = None  # Mutation testing evidence

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "message": self.message,
            "severity": self.severity,
            "recommendation": self.recommendation,
            "context_lines": self.context_lines or [],
        }
        if self.mutation_evidence is not None:
            result["mutation_evidence"] = self.mutation_evidence.to_dict()
        return result


@dataclass
class AgentOutput:
    """Agent-friendly output structure."""

    context: AgentContext
    suggestions: list[AgentFixSuggestion]
    deeplinks: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        context_dict: dict[str, Any] = {
            "project_path": self.context.project_path,
            "health_score": self.context.health_score,
            "total_issues": self.context.total_issues,
            "critical_count": self.context.critical_count,
            "warning_count": self.context.warning_count,
            "info_count": self.context.info_count,
        }
        if self.context.assertion_quality_score is not None:
            context_dict["assertion_quality_score"] = self.context.assertion_quality_score
        if self.context.mutation_stats is not None:
            context_dict["mutation_stats"] = self.context.mutation_stats.to_dict()

        return {
            "context": context_dict,
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
        # Extract mutation stats if available
        mutation_stats_obj = None
        assertion_quality_score = None
        mutation_stats_data = None
        for result in diagnostic.results:
            if result.engine == "assertion_quality" and "mutation_stats" in result.metadata:
                mutation_stats_data = result.metadata["mutation_stats"]
                total = mutation_stats_data.total_mutations
                killed = mutation_stats_data.killed_count
                survival = mutation_stats_data.survival_rate
                mutation_stats_obj = MutationStats(
                    total_mutations=total,
                    killed=killed,
                    survival_rate=survival,
                )
                # Calculate assertion quality score (0-100, inverse of survival rate)
                assertion_quality_score = int((1.0 - survival) * 100)
                break

        # Create context
        context = AgentContext(
            project_path=diagnostic.path,
            health_score=diagnostic.score,
            total_issues=diagnostic.total_issues,
            critical_count=aggregated.summary["critical"],
            warning_count=aggregated.summary["warning"],
            info_count=aggregated.summary["info"],
            assertion_quality_score=assertion_quality_score,
            mutation_stats=mutation_stats_obj,
        )

        # Create fix suggestions with mutation evidence for weak assertions
        suggestions: list[AgentFixSuggestion] = []
        for issue in aggregated.all_issues:
            mutation_evidence = None
            # Add mutation evidence for weak-assertion issues
            if issue.rule_id == "weak-assertion" and mutation_stats_data is not None:
                # Extract mutation type from message (e.g., "< changed to <=")
                mutation_type = self._extract_mutation_type(issue.message)
                mutation_evidence = MutationEvidence(
                    mutation_type=mutation_type,
                    location=f"{issue.file_path}:{issue.line_number}",
                    survived_by_tests=[],  # Would be populated if we track test details
                    recommendation=(
                        "Strengthen assertion to catch all mutations or add boundary tests"
                    ),
                )

            suggestion = AgentFixSuggestion(
                file_path=issue.file_path,
                line_number=issue.line_number,
                rule_id=issue.rule_id,
                rule_name=issue.rule_name,
                message=issue.message,
                severity=issue.severity.value,
                recommendation=issue.recommendation,
                mutation_evidence=mutation_evidence,
            )
            suggestions.append(suggestion)

        # Create deeplinks
        deeplinks = self._create_deeplinks(diagnostic, aggregated)

        return AgentOutput(
            context=context,
            suggestions=suggestions,
            deeplinks=deeplinks,
        )

    def _extract_mutation_type(self, message: str) -> str:
        """
        Extract mutation type from issue message.

        Args:
            message: The issue message

        Returns:
            The mutation type description
        """
        # Try to extract from message like:
        # "Mutation '< changed to <=' at src/user.py:23 was not caught by tests"
        if "'" in message:
            parts = message.split("'")
            if len(parts) >= 2:
                return parts[1]
        return "mutation survived"

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
