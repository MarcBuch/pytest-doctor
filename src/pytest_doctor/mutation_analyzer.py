"""Mutation testing analysis for detecting weak assertions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pytest_doctor.models import Issue, IssueSource, MutationStats, Severity

if TYPE_CHECKING:
    from pytest_doctor.models import Mutation

logger = logging.getLogger(__name__)


class MutationAnalyzer:
    """Analyzes mutations to identify weak assertions."""

    def __init__(self) -> None:
        """Initialize the mutation analyzer."""
        self.logger = logger

    def analyze_mutations(self, mutations: list[Mutation]) -> list[Issue]:
        """
        Analyze mutations and generate issues for survived mutations.

        Identifies mutations that were not caught by tests (survived=True)
        and creates weak assertion issues for each.

        Args:
            mutations: List of Mutation objects from mutation testing

        Returns:
            List of Issue objects for survived mutations
        """
        issues: list[Issue] = []

        for mutation in mutations:
            # Only report mutations that survived (killed=False)
            if not mutation.killed:
                issue = self._create_weak_assertion_issue(mutation)
                issues.append(issue)

        return issues

    def calculate_mutation_stats(self, mutations: list[Mutation]) -> MutationStats:
        """
        Calculate statistics from mutation testing results.

        Args:
            mutations: List of Mutation objects

        Returns:
            MutationStats object with aggregated statistics
        """
        if not mutations:
            return MutationStats(
                total_mutations=0,
                killed_count=0,
                survival_rate=0.0,
                time_ms=0,
            )

        total = len(mutations)
        killed_count = sum(1 for m in mutations if m.killed)
        survival_rate = (total - killed_count) / total if total > 0 else 0.0

        return MutationStats(
            total_mutations=total,
            killed_count=killed_count,
            survival_rate=survival_rate,
            time_ms=0,  # Time aggregation would require timing data in Mutation
        )

    def _create_weak_assertion_issue(self, mutation: Mutation) -> Issue:
        """
        Create a weak assertion issue from a survived mutation.

        Args:
            mutation: A Mutation object that survived testing

        Returns:
            An Issue object representing the weak assertion
        """
        # Parse source_location (format: "file:line")
        file_path = "unknown"
        line_number = 0

        if ":" in mutation.source_location:
            parts = mutation.source_location.rsplit(":", 1)
            file_path = parts[0]
            try:
                line_number = int(parts[1])
            except (ValueError, IndexError):
                line_number = 0
        else:
            file_path = mutation.source_location

        return Issue(
            file_path=file_path,
            line_number=line_number,
            rule_id="weak-assertion",
            rule_name="Weak Assertion - Mutation Survived",
            message=(
                f"Mutation '{mutation.mutation_type}' at "
                f"{mutation.source_location} was not caught by tests"
            ),
            severity=Severity.WARNING,
            source=IssueSource.MUTATION_TESTING,
            recommendation=(
                f"Add test case or strengthen assertion to catch "
                f"'{mutation.mutation_type}' mutations"
            ),
        )
