"""Tests for pytest-doctor CLI."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pytest_doctor.cli.main import (
    CLIExitCode,
    format_json,
    format_score_only,
    format_text,
    main,
    run_analysis,
)
from pytest_doctor.cli.parser import create_parser, parse_arguments
from pytest_doctor.models import (
    CoverageStats,
    Diagnostic,
    DiagnosticType,
    Gap,
    GapCategory,
    Location,
    ProjectInfo,
    Results,
    Score,
    ScoreLabel,
    Severity,
)


class TestParser:
    """Tests for argument parser."""

    def test_parser_help(self) -> None:
        """Test that --help flag produces help text."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_parser_version(self) -> None:
        """Test that --version flag produces version."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_parse_default_path(self) -> None:
        """Test that default path is current directory."""
        args = parse_arguments([])
        assert args.path == "."

    def test_parse_custom_path(self) -> None:
        """Test parsing custom path."""
        args = parse_arguments(["tests/"])
        assert args.path == "tests/"

    def test_parse_verbose_flag(self) -> None:
        """Test verbose flag parsing."""
        args = parse_arguments(["--verbose"])
        assert args.verbose is True

        args = parse_arguments(["-v"])
        assert args.verbose is True

    def test_parse_score_flag(self) -> None:
        """Test score flag parsing."""
        args = parse_arguments(["--score"])
        assert args.score is True

        args = parse_arguments(["-s"])
        assert args.score is True

    def test_parse_format_option(self) -> None:
        """Test format option parsing."""
        args = parse_arguments(["--format", "json"])
        assert args.format == "json"

        args = parse_arguments(["-f", "html"])
        assert args.format == "html"

    def test_parse_output_option(self) -> None:
        """Test output file option."""
        args = parse_arguments(["--output", "report.txt"])
        assert args.output == "report.txt"

    def test_parse_config_option(self) -> None:
        """Test config file option."""
        args = parse_arguments(["--config", "custom.json"])
        assert args.config == "custom.json"

    def test_parse_project_option(self) -> None:
        """Test project option for monorepos."""
        args = parse_arguments(["--project", "web"])
        assert args.project == "web"

    def test_parse_skip_flags(self) -> None:
        """Test analyzer skip flags."""
        args = parse_arguments(["--no-coverage", "--no-gaps", "--no-rules"])
        assert args.no_coverage is True
        assert args.no_gaps is True
        assert args.no_rules is True


class TestFormatting:
    """Tests for output formatting."""

    def create_sample_results(self) -> Results:
        """Create sample results for testing."""
        return Results(
            score=Score(
                value=75.5,
                label=ScoreLabel.EXCELLENT,
                breakdown={"coverage": 5.0, "gaps": 10.0, "quality": 9.5},
            ),
            diagnostics=[
                Diagnostic(
                    type=DiagnosticType.QUALITY,
                    category="assertions/missing-messages",
                    file="tests/test_example.py",
                    line=12,
                    column=8,
                    severity=Severity.WARNING,
                    message="Assert missing message",
                    help="Add descriptive messages to assertions",
                )
            ],
            gaps=[
                Gap(
                    category=GapCategory.UNTESTED_FUNCTIONS,
                    location=Location(file="src/example.py", line=45),
                    description="Function `validate` is untested",
                    severity=Severity.ERROR,
                )
            ],
            coverage=CoverageStats(
                total_lines=100, covered_lines=82, total_branches=50, covered_branches=42
            ),
            project_info=ProjectInfo(name="test-project", root_path="/tmp/test"),
        )

    def test_format_score_only(self) -> None:
        """Test score-only formatting."""
        results = self.create_sample_results()
        output = format_score_only(results)
        assert output == "75"

    def test_format_json(self) -> None:
        """Test JSON formatting."""
        results = self.create_sample_results()
        output = format_json(results)
        assert '"score"' in output
        assert '"value": 75.5' in output
        assert '"label": "Excellent"' in output

    def test_format_text_basic(self) -> None:
        """Test text formatting."""
        results = self.create_sample_results()
        output = format_text(results)
        assert "pytest-doctor Report" in output
        assert "Excellent" in output
        assert "Coverage Summary" in output

    def test_format_text_verbose(self) -> None:
        """Test verbose text formatting."""
        results = self.create_sample_results()
        output = format_text(results, verbose=True)
        assert "pytest-doctor Report" in output
        assert "Location:" in output


class TestCLIExecution:
    """Tests for CLI execution."""

    def test_cli_invalid_path(self) -> None:
        """Test CLI with invalid path."""
        with patch("sys.stderr"):
            exit_code = main(["/nonexistent/path"])
        assert exit_code == CLIExitCode.ERROR

    def test_cli_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test CLI help output."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_cli_version(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test CLI version output."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    @patch("pytest_doctor.cli.main.run_analysis")
    def test_cli_success(self, mock_run_analysis: MagicMock, tmp_path: Path) -> None:
        """Test successful CLI execution."""
        # Create a temporary directory
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        # Mock the analysis results
        mock_results = Results(
            score=Score(value=75.0, label=ScoreLabel.EXCELLENT),
            coverage=CoverageStats(total_lines=100, covered_lines=75),
            project_info=ProjectInfo(name="test"),
        )
        mock_run_analysis.return_value = mock_results

        exit_code = main([str(test_dir)])
        assert exit_code == CLIExitCode.SUCCESS

    @patch("pytest_doctor.cli.main.run_analysis")
    def test_cli_failure(self, mock_run_analysis: MagicMock, tmp_path: Path) -> None:
        """Test CLI with low score (failure)."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        # Mock low score results
        mock_results = Results(
            score=Score(value=40.0, label=ScoreLabel.CRITICAL),
            coverage=CoverageStats(),
            project_info=ProjectInfo(name="test"),
        )
        mock_run_analysis.return_value = mock_results

        exit_code = main([str(test_dir)])
        assert exit_code == CLIExitCode.FAILURE

    @patch("pytest_doctor.cli.main.run_analysis")
    def test_cli_score_only(
        self, mock_run_analysis: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test CLI with --score flag."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        mock_results = Results(
            score=Score(value=72.5, label=ScoreLabel.NEEDS_WORK),
            coverage=CoverageStats(),
            project_info=ProjectInfo(name="test"),
        )
        mock_run_analysis.return_value = mock_results

        exit_code = main([str(test_dir), "--score"])
        # Score is 72, which is >= 50 (default minimum), so it should be SUCCESS
        assert exit_code == CLIExitCode.SUCCESS

        captured = capsys.readouterr()
        assert "72" in captured.out

    @patch("pytest_doctor.cli.main.run_analysis")
    def test_cli_json_format(
        self, mock_run_analysis: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test CLI with JSON format."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        mock_results = Results(
            score=Score(value=75.0, label=ScoreLabel.EXCELLENT),
            coverage=CoverageStats(),
            project_info=ProjectInfo(name="test"),
        )
        mock_run_analysis.return_value = mock_results

        exit_code = main([str(test_dir), "--format", "json"])
        assert exit_code == CLIExitCode.SUCCESS

        captured = capsys.readouterr()
        assert '"score"' in captured.out

    @patch("pytest_doctor.cli.main.run_analysis")
    def test_cli_verbose_flag(self, mock_run_analysis: MagicMock, tmp_path: Path) -> None:
        """Test CLI with verbose flag."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        mock_results = Results(
            score=Score(value=75.0, label=ScoreLabel.EXCELLENT),
            diagnostics=[
                Diagnostic(
                    type=DiagnosticType.QUALITY,
                    category="test",
                    file="test.py",
                    line=10,
                    column=0,
                    severity=Severity.WARNING,
                    message="Test",
                    help="Help",
                )
            ],
            coverage=CoverageStats(),
            project_info=ProjectInfo(name="test"),
        )
        mock_run_analysis.return_value = mock_results

        exit_code = main([str(test_dir), "--verbose"])
        assert exit_code == CLIExitCode.SUCCESS

    @patch("pytest_doctor.cli.main.run_analysis")
    def test_cli_output_file(self, mock_run_analysis: MagicMock, tmp_path: Path) -> None:
        """Test CLI with output file."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        output_file = tmp_path / "report.txt"

        mock_results = Results(
            score=Score(value=75.0, label=ScoreLabel.EXCELLENT),
            coverage=CoverageStats(),
            project_info=ProjectInfo(name="test"),
        )
        mock_run_analysis.return_value = mock_results

        exit_code = main([str(test_dir), "--output", str(output_file)])
        assert exit_code == CLIExitCode.SUCCESS
        assert output_file.exists()

    def test_cli_keyboard_interrupt(self, tmp_path: Path) -> None:
        """Test CLI graceful handling of keyboard interrupt."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        with patch("pytest_doctor.cli.main.run_analysis", side_effect=KeyboardInterrupt()):
            exit_code = main([str(test_dir)])
        assert exit_code == CLIExitCode.ERROR


class TestRunAnalysis:
    """Tests for run_analysis function."""

    def test_run_analysis_invalid_path(self) -> None:
        """Test run_analysis with invalid path."""
        with pytest.raises(Exception):
            run_analysis("/nonexistent/path")

    @patch("pytest_doctor.cli.main.diagnose")
    def test_run_analysis_with_config(self, mock_diagnose: MagicMock, tmp_path: Path) -> None:
        """Test run_analysis with config file."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        mock_diagnose.return_value = Results(
            score=Score(value=75.0, label=ScoreLabel.EXCELLENT),
            coverage=CoverageStats(),
            project_info=ProjectInfo(name="test"),
        )

        run_analysis(str(test_dir), config_path="config.json")
        mock_diagnose.assert_called_once()

    @patch("pytest_doctor.cli.main.diagnose")
    def test_run_analysis_skip_flags(self, mock_diagnose: MagicMock, tmp_path: Path) -> None:
        """Test run_analysis with skip flags."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        mock_diagnose.return_value = Results(
            score=Score(value=75.0, label=ScoreLabel.EXCELLENT),
            coverage=CoverageStats(),
            project_info=ProjectInfo(name="test"),
        )

        run_analysis(
            str(test_dir),
            skip_coverage=True,
            skip_gaps=True,
            skip_rules=True,
        )
        mock_diagnose.assert_called_once()
