"""Tests for CLI functionality."""

import json
from pathlib import Path

from click.testing import CliRunner

from pytest_doctor.cli import main


def test_cli_version() -> None:
    """Test --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_basic_run() -> None:
    """Test basic CLI run without flags."""
    runner = CliRunner()
    result = runner.invoke(main, ["."])
    assert result.exit_code == 0
    assert "Scanning" in result.output


def test_cli_verbose_flag() -> None:
    """Test --verbose flag."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--verbose"])
    assert result.exit_code == 0
    assert "Verbose mode enabled" in result.output


def test_cli_json_output() -> None:
    """Test --json flag output."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--json"])
    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.output)
    assert "version" in output
    assert "path" in output
    assert "score" in output
    assert "issues" in output
    assert "summary" in output


def test_cli_json_to_file(tmp_path: Path) -> None:
    """Test --output flag writes to file."""
    output_file = tmp_path / "results.json"
    runner = CliRunner()
    result = runner.invoke(main, [".", "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()

    # Verify file contains valid JSON
    data = json.loads(output_file.read_text())
    assert "version" in data
    assert "path" in data


def test_cli_diff_flag() -> None:
    """Test --diff flag."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--diff", "main"])
    assert result.exit_code == 0
    assert "Scanning changed files relative to: main" in result.output


def test_cli_fix_flag() -> None:
    """Test --fix flag generates agent-friendly JSON."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--fix"])
    assert result.exit_code == 0
    # --fix flag outputs JSON, not plain text
    output = json.loads(result.output)
    assert "context" in output
    assert "suggestions" in output
    assert "deeplinks" in output


def test_cli_fix_flag_detailed_output() -> None:
    """Test --fix flag output structure."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--fix"])
    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.output)

    # Check context structure
    context = output["context"]
    assert "health_score" in context
    assert "total_issues" in context
    assert "critical_count" in context
    assert "warning_count" in context
    assert "info_count" in context

    # Check suggestions is a list
    assert isinstance(output["suggestions"], list)

    # Check deeplinks is a dict
    assert isinstance(output["deeplinks"], dict)

    # Verify version is included
    assert "version" in output


def test_cli_fix_flag_with_output_file(tmp_path: Path) -> None:
    """Test --fix flag with --output file."""
    output_file = tmp_path / "agent_output.json"
    runner = CliRunner()
    result = runner.invoke(main, [".", "--fix", "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()

    # Verify file contains valid agent-friendly JSON
    data = json.loads(output_file.read_text())
    assert "context" in data
    assert "suggestions" in data
    assert "deeplinks" in data


def test_cli_mutation_flag() -> None:
    """Test --mutation flag enables mutation testing."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--mutation"])
    assert result.exit_code == 0
    # Note: Actual mutation testing requires mutmut to be installed
    # This test just verifies the flag is accepted


def test_cli_mutation_no_mutation_flag() -> None:
    """Test --no-mutation flag disables mutation testing."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--no-mutation"])
    assert result.exit_code == 0


def test_cli_mutation_depth_light() -> None:
    """Test --mutation-depth light option."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--mutation", "--mutation-depth", "light"])
    assert result.exit_code == 0


def test_cli_mutation_depth_standard() -> None:
    """Test --mutation-depth standard option."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--mutation", "--mutation-depth", "standard"])
    assert result.exit_code == 0


def test_cli_mutation_depth_deep() -> None:
    """Test --mutation-depth deep option."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--mutation", "--mutation-depth", "deep"])
    assert result.exit_code == 0


def test_cli_mutation_timeout() -> None:
    """Test --mutation-timeout option with milliseconds."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--mutation", "--mutation-timeout", "3000"])
    assert result.exit_code == 0


def test_cli_mutation_with_json_output() -> None:
    """Test --mutation flag with --json output."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--mutation", "--json"])
    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.output)
    assert "version" in output
    assert "path" in output
    assert "score" in output


def test_cli_mutation_with_fix_flag() -> None:
    """Test --mutation flag with --fix flag."""
    runner = CliRunner()
    result = runner.invoke(main, [".", "--mutation", "--fix"])
    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.output)
    assert "context" in output
    assert "suggestions" in output
    assert "deeplinks" in output
