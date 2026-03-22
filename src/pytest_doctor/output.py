"""Human-readable output rendering for diagnostic reports."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from pytest_doctor.aggregation import AggregatedIssues
    from pytest_doctor.models import DiagnosticReport


def render_report(
    diagnostic: DiagnosticReport,
    aggregated: AggregatedIssues,
    verbose: bool,
) -> None:
    """
    Render a human-readable diagnostic report with mutation stats.

    Args:
        diagnostic: The diagnostic report containing analysis results
        aggregated: Aggregated issues grouped by file
        verbose: Whether to show verbose output with recommendations
    """
    # Print header with score
    click.echo("\n" + "=" * 60)
    click.echo("pytest-doctor Diagnostic Report")
    click.echo("=" * 60)

    # Print score with color coding
    score = diagnostic.score
    if score >= 75:
        status = "✓ GOOD"
    elif score >= 50:
        status = "⚠ NEEDS WORK"
    else:
        status = "✗ CRITICAL"

    click.echo(f"\nHealth Score: {score}/100 [{status}]")

    # Print summary
    click.echo("\nSummary:")
    click.echo(f"  Critical: {aggregated.summary['critical']}")
    click.echo(f"  Warning:  {aggregated.summary['warning']}")
    click.echo(f"  Info:     {aggregated.summary['info']}")
    click.echo(f"  Total:    {len(aggregated.all_issues)}")

    # Print mutation statistics if available
    if diagnostic.mutation_survival_rate is not None:
        _render_mutation_stats(diagnostic)

    # Print issues by file if there are any
    if aggregated.all_issues:
        click.echo("\nFindings:")
        click.echo("-" * 60)

        for file_path, issues in aggregated.by_file.items():
            click.echo(f"\n{file_path}")
            for issue in issues:
                severity_symbol = {
                    "critical": "✗",
                    "warning": "⚠",
                    "info": "i",
                }.get(issue.severity.value, "•")

                rule_info = f"[{issue.rule_id}]" if issue.rule_id else ""
                click.echo(
                    f"  {severity_symbol} Line {issue.line_number}: {issue.message} {rule_info}"
                )

                if verbose and issue.recommendation:
                    click.echo(f"    → {issue.recommendation}")

    click.echo("\n" + "=" * 60 + "\n")


def _render_mutation_stats(diagnostic: DiagnosticReport) -> None:
    """
    Render mutation testing statistics.

    Args:
        diagnostic: The diagnostic report containing mutation stats
    """
    # Extract mutation stats from assertion_quality result
    mutation_stats = None
    for result in diagnostic.results:
        if result.engine == "assertion_quality" and "mutation_stats" in result.metadata:
            mutation_stats = result.metadata["mutation_stats"]
            break

    if mutation_stats is None:
        return

    # Calculate assertion quality score (0-100 based on survival rate)
    # Lower survival rate = higher score
    survival_rate = mutation_stats.survival_rate
    assertion_quality_score = int((1.0 - survival_rate) * 100)

    click.echo(f"\n  Assertion Quality Score: {assertion_quality_score}/100")
    click.echo(f"    Total Mutations: {mutation_stats.total_mutations}")
    click.echo(f"    Killed: {mutation_stats.killed_count}")
    survived = mutation_stats.total_mutations - mutation_stats.killed_count
    click.echo(f"    Survived: {survived} ({int(survival_rate * 100)}%)")
