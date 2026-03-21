"""CLI entry point for pytest-doctor."""

import json
from pathlib import Path
from typing import Optional

import click

from pytest_doctor import __version__
from pytest_doctor.config import load_config


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

    # TODO: Implement the actual analysis logic
    if not (output_json or output):
        click.echo(f"Scanning: {path}")
        if config.verbose:
            click.echo("Verbose mode enabled")
        if config.lint:
            click.echo("Linting enabled")
        if config.dead_code:
            click.echo("Dead code detection enabled")
        if config.test_analysis:
            click.echo("Test analysis enabled")
        if fix:
            click.echo("Fix mode enabled")
        if diff:
            click.echo(f"Scanning changed files relative to: {diff}")

    # Placeholder output
    result = {
        "version": __version__,
        "path": path,
        "score": 0,
        "issues": [],
        "summary": {"critical": 0, "warning": 0, "info": 0},
    }

    if output_json or output:
        output_str = json.dumps(result, indent=2)
        if output:
            Path(output).write_text(output_str)
            click.echo(f"Results written to {output}")
        else:
            click.echo(output_str)
    else:
        click.echo("pytest-doctor initialized successfully!")
        click.echo(f"Health Score: {result['score']}/100")


if __name__ == "__main__":
    main()
