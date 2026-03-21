"""CLI entry point for pytest-doctor."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from pytest_doctor import __version__
from pytest_doctor.aggregation import AggregatedIssues, ResultsAggregator
from pytest_doctor.analyzers import GapAnalyzer, QualityAnalyzer, RuffAnalyzer, VultureAnalyzer
from pytest_doctor.config import load_config
from pytest_doctor.git_utils import GitDiffHandler
from pytest_doctor.models import DiagnosticReport
from pytest_doctor.scoring import HealthScorer


def _print_report(
    diagnostic: DiagnosticReport, aggregated: AggregatedIssues, verbose: bool
) -> None:
    """Print a human-readable diagnostic report."""
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
                    "info": "ℹ",
                }.get(issue.severity.value, "•")

                rule_info = f"[{issue.rule_id}]" if issue.rule_id else ""
                click.echo(
                    f"  {severity_symbol} Line {issue.line_number}: {issue.message} {rule_info}"
                )

                if verbose and issue.recommendation:
                    click.echo(f"    → {issue.recommendation}")

    click.echo("\n" + "=" * 60 + "\n")


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output with detailed information")
@click.option("--fix", is_flag=True, help="Generate agent-friendly fix recommendations")
@click.option("--diff", type=str, default=None, help="Scan only changed files (e.g., --diff main)")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
@click.option("--output", type=click.Path(), default=None, help="Write JSON output to file")
@click.option("--version", is_flag=True, help="Show version and exit")
def main(
    path: str,
    verbose: bool,
    fix: bool,
    diff: Optional[str],
    output_json: bool,
    output: Optional[str],
    version: bool,
) -> None:
    """
    Diagnose weak or broken pytest suites.

    Provides a 0-100 health score with actionable recommendations.

    PATH: Directory to scan (default: current directory)
    """
    if version:
        click.echo(f"pytest-doctor {__version__}")
        return

    # Load configuration from files and merge with CLI flags
    config = load_config(path, verbose=verbose)

    # Show initial message if not JSON output
    if not (output_json or output):
        click.echo(f"Scanning: {path}")
        if config.verbose:
            click.echo("Verbose mode enabled")
        if fix:
            click.echo("Fix mode enabled")
        if diff:
            click.echo(f"Scanning changed files relative to: {diff}")

    # Run all analysis engines
    try:
        results = []

        if config.lint:
            if config.verbose:
                click.echo("Running ruff linting analysis...", err=True)
            ruff_analyzer = RuffAnalyzer(config)
            results.append(ruff_analyzer.analyze(path))

        if config.dead_code:
            if config.verbose:
                click.echo("Running vulture dead code analysis...", err=True)
            vulture_analyzer = VultureAnalyzer(config)
            results.append(vulture_analyzer.analyze(path))

        if config.test_analysis:
            if config.verbose:
                click.echo("Running test quality analysis...", err=True)
            quality_analyzer = QualityAnalyzer(config)
            results.append(quality_analyzer.analyze(path))

        if config.coverage_gaps:
            if config.verbose:
                click.echo("Running coverage gap analysis...", err=True)
            gap_analyzer = GapAnalyzer(config)
            results.append(gap_analyzer.analyze(path))

        # Aggregate results
        aggregator = ResultsAggregator()
        aggregated = aggregator.aggregate([r for r in results if r is not None])

        # Filter by changed files if --diff flag is used
        if diff:
            git_handler = GitDiffHandler(path)

            # Check if git is available and ref exists
            if git_handler.is_git_repo():
                if git_handler.ref_exists(diff):
                    changed_files = git_handler.get_changed_files(diff)
                    if changed_files:
                        if config.verbose:
                            click.echo(f"Found {len(changed_files)} changed files", err=True)
                        aggregated = aggregator.filter_by_files(aggregated, changed_files)
                    else:
                        if config.verbose:
                            click.echo(
                                f"No changed files found relative to {diff}",
                                err=True,
                            )
                else:
                    if not (output_json or output):
                        click.echo(f"Warning: Git ref '{diff}' not found", err=True)
            else:
                if not (output_json or output):
                    click.echo("Warning: Not a git repository", err=True)

        # Calculate health score
        scorer = HealthScorer()
        score = scorer.calculate_score([r for r in results if r is not None])

        # Create diagnostic report
        diagnostic = DiagnosticReport(
            path=path,
            score=score,
            results=results,
            summary=aggregated.summary,
            total_issues=len(aggregated.all_issues),
        )

        # Output results
        if output_json or output:
            output_dict = diagnostic.to_dict()
            # Add version and other metadata
            output_dict["version"] = __version__
            # Add aggregated issues by file
            output_dict["issues"] = aggregated.to_dict()["by_file"]
            output_dict["all_issues"] = [issue.to_dict() for issue in aggregated.all_issues]

            output_str = json.dumps(output_dict, indent=2)
            if output:
                Path(output).write_text(output_str)
                click.echo(f"Results written to {output}")
            else:
                click.echo(output_str)
        else:
            # Human-readable output
            _print_report(diagnostic, aggregated, config.verbose)

    except Exception as e:
        if config.verbose:
            click.echo(f"Error during analysis: {e}", err=True)
            import traceback

            traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
