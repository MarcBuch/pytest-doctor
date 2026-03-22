"""CLI entry point for pytest-doctor."""

import json
import sys
from pathlib import Path
from typing import Callable, Optional, Union

import click

from pytest_doctor import __version__
from pytest_doctor.agent_output import AgentOutputFormatter
from pytest_doctor.aggregation import ResultsAggregator
from pytest_doctor.analyzers import (
    AssertionQualityAnalyzer,
    GapAnalyzer,
    QualityAnalyzer,
    RuffAnalyzer,
    VultureAnalyzer,
)
from pytest_doctor.config import load_config
from pytest_doctor.git_utils import GitDiffHandler
from pytest_doctor.models import AnalysisResult, DiagnosticReport
from pytest_doctor.output import render_report
from pytest_doctor.parallel import run_analyses_parallel
from pytest_doctor.scoring import HealthScorer


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output with detailed information")
@click.option("--fix", is_flag=True, help="Generate agent-friendly fix recommendations")
@click.option("--diff", type=str, default=None, help="Scan only changed files (e.g., --diff main)")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
@click.option("--output", type=click.Path(), default=None, help="Write JSON output to file")
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option(
    "--mutation/--no-mutation",
    default=False,
    help="Enable mutation testing to detect weak assertions (slower)",
)
@click.option(
    "--mutation-depth",
    type=click.Choice(["light", "standard", "deep"]),
    default="standard",
    help="Depth of mutation testing (light=fast, deep=thorough)",
)
@click.option(
    "--mutation-timeout",
    type=int,
    default=5000,
    help="Timeout per mutation test run (milliseconds)",
)
def main(
    path: str,
    verbose: bool,
    fix: bool,
    diff: Optional[str],
    output_json: bool,
    output: Optional[str],
    version: bool,
    mutation: bool,
    mutation_depth: str,
    mutation_timeout: int,
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

    # Apply mutation testing CLI flags
    if mutation:
        config.assertion_quality = True
    config.mutation_depth = mutation_depth
    config.mutation_timeout_ms = mutation_timeout

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

        if config.assertion_quality:
            assertion_analyzer = AssertionQualityAnalyzer(config)

            def assertion_fn() -> Union[AnalysisResult, None]:
                return assertion_analyzer.analyze(path)

            analysis_functions.append((assertion_fn, "assertion_quality"))

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

        # Extract mutation stats if available
        mutation_survival_rate: Optional[float] = None
        for result in results:
            if result and result.engine == "assertion_quality":
                if "mutation_stats" in result.metadata:
                    mutation_stats = result.metadata["mutation_stats"]
                    mutation_survival_rate = mutation_stats.survival_rate
                break

        # Create diagnostic report
        diagnostic = DiagnosticReport(
            path=path,
            score=score,
            results=results,
            summary=aggregated.summary,  # type: ignore
            total_issues=len(aggregated.all_issues),
            mutation_survival_rate=mutation_survival_rate,
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
            render_report(diagnostic, aggregated, config.verbose)

    except Exception as e:
        if config.verbose:
            click.echo(f"Error during analysis: {e}", err=True)
            import traceback

            traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
