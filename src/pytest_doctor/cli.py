"""CLI entry point for pytest-doctor."""

import json
import sys
from pathlib import Path
from typing import Callable, Optional, Union

import click

from pytest_doctor import __version__
from pytest_doctor.agent_output import AgentOutputFormatter
from pytest_doctor.aggregation import AggregatedIssues, ResultsAggregator
from pytest_doctor.analyzers import GapAnalyzer, QualityAnalyzer, RuffAnalyzer, VultureAnalyzer
from pytest_doctor.config import load_config
from pytest_doctor.git_utils import GitDiffHandler
from pytest_doctor.models import AnalysisResult, DiagnosticReport
from pytest_doctor.parallel import run_analyses_parallel
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
                    "info": "i",
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

    # Show initial message if not JSON output or fix flag
    if not (output_json or output or fix):
        click.echo(f"Scanning: {path}")
        if config.verbose:
            click.echo("Verbose mode enabled")
        if diff:
            click.echo(f"Scanning changed files relative to: {diff}")

    # Run all analysis engines
    try:
        # Prepare analysis functions for parallel execution
        analysis_functions: list[tuple[Callable[[], Union[AnalysisResult, None]], str]] = []

        if config.lint:
            ruff_analyzer = RuffAnalyzer(config)

            def ruff_fn() -> Union[AnalysisResult, None]:
                return ruff_analyzer.analyze(path)

            analysis_functions.append((ruff_fn, "ruff"))

        if config.dead_code:
            vulture_analyzer = VultureAnalyzer(config)

            def vulture_fn() -> Union[AnalysisResult, None]:
                return vulture_analyzer.analyze(path)

            analysis_functions.append((vulture_fn, "vulture"))

        if config.test_analysis:
            quality_analyzer = QualityAnalyzer(config)

            def quality_fn() -> Union[AnalysisResult, None]:
                return quality_analyzer.analyze(path)

            analysis_functions.append((quality_fn, "quality"))

        if config.coverage_gaps:
            gap_analyzer = GapAnalyzer(config)

            def gap_fn() -> Union[AnalysisResult, None]:
                return gap_analyzer.analyze(path)

            analysis_functions.append((gap_fn, "gap"))

        # Run analyses in parallel
        if config.verbose:
            click.echo(
                f"Running {len(analysis_functions)} analysis engines in parallel...",
                err=True,
            )
        results = run_analyses_parallel(analysis_functions)

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
        if fix:
            # Agent-friendly output with deeplinks and structured recommendations
            formatter = AgentOutputFormatter()
            agent_output = formatter.format_for_agent(diagnostic, aggregated)
            output_dict = agent_output.to_dict()
            output_dict["version"] = __version__
            output_str = json.dumps(output_dict, indent=2)

            if output:
                Path(output).write_text(output_str)
                click.echo(f"Agent output written to {output}")
            else:
                # Create .pytest-doctor directory and write diagnostics.json
                diagnostics_dir = Path(path) / ".pytest-doctor"
                diagnostics_dir.mkdir(parents=True, exist_ok=True)
                diagnostics_file = diagnostics_dir / "diagnostics.json"
                diagnostics_file.write_text(output_str)

                # Output the result
                click.echo(output_str)
        elif output_json or output:
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
