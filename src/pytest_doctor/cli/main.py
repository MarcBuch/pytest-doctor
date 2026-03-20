"""Main CLI command execution for pytest-doctor."""

import sys
from pathlib import Path
from typing import Any, Optional

from .. import diagnose
from ..exceptions import DirectoryNotFoundError, InvalidConfigError
from ..models import Results
from .parser import parse_arguments


class CLIExitCode:
    """Exit codes for pytest-doctor CLI."""

    SUCCESS = 0
    FAILURE = 1
    ERROR = 2


def format_score_only(results: Results) -> str:
    """Format output as score-only (single number).

    Args:
        results: Analysis results

    Returns:
        Score as string
    """
    return str(int(results.score.value))


def _format_score_section(results: Results) -> list[str]:
    """Format the score section of text output.

    Args:
        results: Analysis results

    Returns:
        List of formatted lines
    """
    lines = []
    score_emoji = "✅" if results.score.value >= 75 else "⚠️" if results.score.value >= 50 else "❌"
    lines.append(
        f"📊 Score: {results.score.value:.0f}/100 ({results.score.label.value}) {score_emoji}"
    )
    lines.append("")

    if results.score.breakdown:
        lines.append("Score Breakdown:")
        for key, value in results.score.breakdown.items():
            lines.append(f"  {key}: -{value:.1f} points")
        lines.append("")

    return lines


def _format_coverage_section(results: Results) -> list[str]:
    """Format the coverage section of text output.

    Args:
        results: Analysis results

    Returns:
        List of formatted lines
    """
    lines = []
    if results.coverage:
        lines.append("Coverage Summary")
        lines.append("────────────────")
        lines.append(f"Lines: {results.coverage.line_coverage_percent:.1f}%")
        lines.append(f"Branches: {results.coverage.branch_coverage_percent:.1f}%")
        lines.append("")
    return lines


def _format_gaps_section(results: Results, verbose: bool = False) -> list[str]:
    """Format the gaps section of text output.

    Args:
        results: Analysis results
        verbose: Include detailed file:line information

    Returns:
        List of formatted lines
    """
    lines = []
    if results.gaps:
        lines.append(f"Gaps & Missing Edge Cases ({len(results.gaps)})")
        lines.append("─" * 40)
        for gap in results.gaps[:10]:  # Limit to first 10
            severity_emoji = "❌" if gap.severity.value == "error" else "⚠️"
            lines.append(f"{severity_emoji} {gap.category.value}")
            lines.append(f"   {gap.description}")
            if verbose:
                lines.append(f"   Location: {gap.location.file}:{gap.location.line}")
        if len(results.gaps) > 10:
            lines.append(f"... and {len(results.gaps) - 10} more gaps")
        lines.append("")
    return lines


def _format_edge_cases_section(results: Results, verbose: bool = False) -> list[str]:
    """Format the edge cases section of text output.

    Args:
        results: Analysis results
        verbose: Include detailed function information

    Returns:
        List of formatted lines
    """
    lines = []
    if results.edge_cases:
        lines.append(f"Missing Edge Cases ({len(results.edge_cases)})")
        lines.append("─" * 40)
        for edge_case in results.edge_cases[:10]:  # Limit to first 10
            lines.append(f"⚠️  {edge_case.category.value}")
            lines.append(f"   {edge_case.description}")
            if verbose:
                lines.append(f"   Function: {edge_case.function_name} ({edge_case.function_file})")
        if len(results.edge_cases) > 10:
            lines.append(f"... and {len(results.edge_cases) - 10} more edge cases")
        lines.append("")
    return lines


def _format_diagnostics_section(results: Results, verbose: bool = False) -> list[str]:
    """Format the diagnostics/quality section of text output.

    Args:
        results: Analysis results
        verbose: Include detailed file:line information

    Returns:
        List of formatted lines
    """
    lines = []
    if results.diagnostics:
        lines.append(f"Quality Issues ({len(results.diagnostics)})")
        lines.append("─" * 40)
        for diag in results.diagnostics[:10]:  # Limit to first 10
            severity_emoji = "❌" if diag.severity.value == "error" else "⚠️"
            lines.append(f"{severity_emoji} {diag.category}")
            lines.append(f"   {diag.message}")
            if verbose:
                lines.append(f"   Location: {diag.file}:{diag.line}")
                if diag.suggestion:
                    lines.append(f"   Suggestion: {diag.suggestion}")
        if len(results.diagnostics) > 10:
            lines.append(f"... and {len(results.diagnostics) - 10} more issues")
        lines.append("")
    return lines


def format_text(results: Results, verbose: bool = False) -> str:
    """Format output as human-readable text.

    Args:
        results: Analysis results
        verbose: Include detailed file:line information

    Returns:
        Formatted text output
    """
    lines = []

    # Header
    lines.append("pytest-doctor Report")
    lines.append("====================")
    lines.append("")

    # Add sections
    lines.extend(_format_score_section(results))
    lines.extend(_format_coverage_section(results))
    lines.extend(_format_gaps_section(results, verbose))
    lines.extend(_format_edge_cases_section(results, verbose))
    lines.extend(_format_diagnostics_section(results, verbose))

    return "\n".join(lines)


def format_json(results: Results) -> str:
    """Format output as JSON.

    Args:
        results: Analysis results

    Returns:
        JSON formatted output
    """
    return results.to_json()


def format_html(results: Results) -> str:
    """Format output as HTML (stub).

    Args:
        results: Analysis results

    Returns:
        HTML formatted output
    """
    # TODO: Implement full HTML report generation
    return f"""
    <html>
    <head>
        <title>pytest-doctor Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .score {{ font-size: 24px; font-weight: bold; }}
            .excellent {{ color: green; }}
            .needs-work {{ color: orange; }}
            .critical {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>pytest-doctor Report</h1>
        <div class="score {results.score.label.value.lower().replace(" ", "-")}">
            Score: {results.score.value:.0f}/100
        </div>
        <p>Full HTML reporting to be implemented.</p>
    </body>
    </html>
    """


def run_analysis(
    path: str,
    config_path: Optional[str] = None,
    projects: Optional[list[str]] = None,
    skip_coverage: bool = False,
    skip_gaps: bool = False,
    skip_rules: bool = False,
) -> Results:
    """Run the analysis pipeline.

    Args:
        path: Path to analyze
        config_path: Optional path to config file
        projects: Optional list of projects to analyze (for monorepos)
        skip_coverage: Skip coverage analysis
        skip_gaps: Skip gap detection
        skip_rules: Skip quality rule checks

    Returns:
        Analysis results

    Raises:
        DirectoryNotFoundError: If path doesn't exist
        InvalidConfigError: If config is invalid
    """
    # Validate path exists
    target_path = Path(path)
    if not target_path.exists():
        raise DirectoryNotFoundError(f"Path does not exist: {path}")

    if not target_path.is_dir():
        raise DirectoryNotFoundError(f"Path is not a directory: {path}")

    # TODO: Load and merge config if provided
    config: dict[str, Any] = {}
    if config_path:
        # Config loading will be implemented in T6
        pass

    # TODO: Handle monorepo project filtering
    if projects:
        pass

    # TODO: Handle skip flags
    config["skip_coverage"] = skip_coverage
    config["skip_gaps"] = skip_gaps
    config["skip_rules"] = skip_rules

    # Run analysis
    results = diagnose(str(target_path), config=config)

    return results


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    try:
        # Parse arguments
        args = parse_arguments(argv)

        # Validate path exists
        target_path = Path(args.path)
        if not target_path.exists():
            print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
            return CLIExitCode.ERROR

        if not target_path.is_dir():
            print(f"Error: Path is not a directory: {args.path}", file=sys.stderr)
            return CLIExitCode.ERROR

        # Run analysis
        results = run_analysis(
            args.path,
            config_path=args.config,
            projects=args.project.split(",") if args.project else None,
            skip_coverage=args.no_coverage,
            skip_gaps=args.no_gaps,
            skip_rules=args.no_rules,
        )

        # Format and output results
        return _format_and_output_results(results, args)

    except DirectoryNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return CLIExitCode.ERROR
    except InvalidConfigError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return CLIExitCode.ERROR
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return CLIExitCode.ERROR
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return CLIExitCode.ERROR


def _format_and_output_results(results: Results, args: Any) -> int:
    """Format results based on requested format and output to file or stdout.

    Args:
        results: Analysis results
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    # Format output based on requested format
    if args.score:
        output = format_score_only(results)
    elif args.format == "json":
        output = format_json(results)
    elif args.format == "html":
        output = format_html(results)
    else:
        output = format_text(results, verbose=args.verbose)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Determine exit code based on score
    # TODO: Load minimum score threshold from config
    minimum_score = 50.0
    if results.score.value < minimum_score:
        return CLIExitCode.FAILURE

    return CLIExitCode.SUCCESS
