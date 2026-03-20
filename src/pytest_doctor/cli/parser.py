"""Argument parsing for pytest-doctor CLI."""

import argparse
from typing import Optional

from .. import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="pytest-doctor",
        description="Analyzes pytest test runs to identify gaps, edge cases, and coverage issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pytest-doctor tests/                    # Scan test suite
  pytest-doctor . --verbose               # Show detailed output
  pytest-doctor . --score                 # Output only health score
  pytest-doctor . --format json           # Output as JSON
  pytest-doctor . --diff main             # Only analyze changed files
  pytest-doctor . --config custom.json    # Use custom config

For more information, visit: https://github.com/pytest-doctor/pytest-doctor
        """,
    )

    # Positional argument
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to test directory or Python package (default: current directory)",
    )

    # Output options
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output with file:line references",
    )

    parser.add_argument(
        "-s",
        "--score",
        action="store_true",
        help="Output only the health score (0-100)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Write output to file instead of stdout",
    )

    # Analysis options
    parser.add_argument(
        "--diff",
        type=str,
        nargs="?",
        const="",
        help="Only analyze files changed vs branch (auto-detects base branch if not specified)",
    )

    parser.add_argument(
        "-p",
        "--project",
        type=str,
        help="Scan specific project in monorepo (comma-separated for multiple)",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to configuration file (overrides auto-detection)",
    )

    # Analyzer control flags
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage analysis",
    )

    parser.add_argument(
        "--no-gaps",
        action="store_true",
        help="Skip gap detection",
    )

    parser.add_argument(
        "--no-rules",
        action="store_true",
        help="Skip quality rule checks",
    )

    # Integration options
    parser.add_argument(
        "--github-token",
        type=str,
        help="Enable GitHub PR comment posting (requires GITHUB_TOKEN environment variable)",
    )

    # Version and help
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def parse_arguments(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: List of arguments to parse (defaults to sys.argv[1:])

    Returns:
        Parsed arguments namespace
    """
    parser = create_parser()
    return parser.parse_args(args)
