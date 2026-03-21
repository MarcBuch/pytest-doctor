"""Results aggregation and deduplication for pytest-doctor."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pytest_doctor.models import AnalysisResult, Issue, Severity


@dataclass
class AggregatedIssues:
    """Aggregated and deduplicated issues grouped by file."""

    by_file: dict[str, list[Issue]] = field(default_factory=dict)
    all_issues: list[Issue] = field(default_factory=list)
    summary: dict[str, int] = field(
        default_factory=lambda: {"critical": 0, "warning": 0, "info": 0}
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "by_file": {
                filepath: [issue.to_dict() for issue in issues]
                for filepath, issues in self.by_file.items()
            },
            "all_issues": [issue.to_dict() for issue in self.all_issues],
            "summary": self.summary,
            "total_issues": len(self.all_issues),
        }


class ResultsAggregator:
    """Aggregates results from multiple analysis engines."""

    def __init__(self) -> None:
        """Initialize the results aggregator."""
        pass

    def aggregate(self, results: list[AnalysisResult]) -> AggregatedIssues:
        """
        Aggregate results from all analysis engines.

        Combines issues from all engines, deduplicates, and prioritizes by severity.

        Args:
            results: List of AnalysisResult from all analysis engines

        Returns:
            AggregatedIssues with deduplicated, prioritized issues grouped by file
        """
        # Collect all issues from all engines
        all_issues = self._collect_all_issues(results)

        # Deduplicate issues
        deduplicated = self._deduplicate_issues(all_issues)

        # Sort by severity (critical first)
        sorted_issues = self._sort_by_severity(deduplicated)

        # Group by file
        by_file = self._group_by_file(sorted_issues)

        # Calculate summary
        summary = self._calculate_summary(sorted_issues)

        return AggregatedIssues(by_file=by_file, all_issues=sorted_issues, summary=summary)

    def _collect_all_issues(self, results: list[AnalysisResult]) -> list[Issue]:
        """Collect all issues from all analysis results."""
        all_issues: list[Issue] = []
        for result in results:
            all_issues.extend(result.issues)
        return all_issues

    def _deduplicate_issues(self, issues: list[Issue]) -> list[Issue]:
        """
        Deduplicate issues based on file, line, column, and rule.

        Keeps the first occurrence of each unique issue.

        Args:
            issues: List of issues to deduplicate

        Returns:
            List of deduplicated issues
        """
        seen: set[tuple[str, int, int, str]] = set()
        deduplicated: list[Issue] = []

        for issue in issues:
            # Create a unique key for each issue
            key = (issue.file_path, issue.line_number, issue.column_number, issue.rule_id)

            if key not in seen:
                seen.add(key)
                deduplicated.append(issue)

        return deduplicated

    def _sort_by_severity(self, issues: list[Issue]) -> list[Issue]:
        """
        Sort issues by severity (critical first, then warning, then info).

        Args:
            issues: List of issues to sort

        Returns:
            Sorted list of issues
        """
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.WARNING: 1,
            Severity.INFO: 2,
        }

        return sorted(
            issues,
            key=lambda issue: (
                severity_order.get(issue.severity, 3),
                issue.file_path,
                issue.line_number,
            ),
        )

    def _group_by_file(self, issues: list[Issue]) -> dict[str, list[Issue]]:
        """
        Group issues by file path.

        Args:
            issues: List of issues to group

        Returns:
            Dictionary mapping file paths to lists of issues
        """
        by_file: dict[str, list[Issue]] = {}

        for issue in issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)

        return by_file

    def _calculate_summary(self, issues: list[Issue]) -> dict[str, int]:
        """
        Calculate summary counts by severity.

        Args:
            issues: List of issues to summarize

        Returns:
            Dictionary with counts of critical, warning, and info issues
        """
        summary = {"critical": 0, "warning": 0, "info": 0}

        for issue in issues:
            severity_key = issue.severity.value
            if severity_key in summary:
                summary[severity_key] += 1

        return summary
