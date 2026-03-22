"""Tests for the assertion quality analyzer."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pytest_doctor.analyzers.assertion_quality_analyzer import (
    AssertionQualityAnalyzer,
)
from pytest_doctor.config import Config
from pytest_doctor.models import Mutation
from tests.fixtures.sample_mutations import (
    create_sample_mutations,
    create_single_survived_mutation,
    create_empty_mutations,
)


class TestAssertionQualityAnalyzerInit:
    """Test AssertionQualityAnalyzer initialization."""

    def test_assertion_quality_analyzer_init(self) -> None:
        """Test basic initialization."""
        analyzer = AssertionQualityAnalyzer()
        assert analyzer.config is not None

    def test_assertion_quality_analyzer_with_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        assert analyzer.config == config
        assert analyzer.config.assertion_quality is True

    def test_assertion_quality_analyzer_default_config(self) -> None:
        """Test that assertion_quality is disabled by default."""
        analyzer = AssertionQualityAnalyzer()
        assert analyzer.config.assertion_quality is False


class TestAssertionQualityAnalyzerAnalyze:
    """Test analyze method."""

    def test_analyze_nonexistent_path(self) -> None:
        """Test analysis with nonexistent path."""
        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze("/nonexistent/path")

        assert result.engine == "assertion_quality"
        assert len(result.issues) == 0
        assert result.duration_ms >= 0

    def test_analyze_disabled_feature(self, tmp_path: Path) -> None:
        """Test that analysis returns empty result when disabled."""
        config = Config(assertion_quality=False)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(tmp_path))

        assert result.engine == "assertion_quality"
        assert len(result.issues) == 0

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_analyze_with_mutations(self, mock_integrator_class: MagicMock, tmp_path: Path) -> None:
        """Test analysis with mutations."""
        # Setup mock
        mock_integrator = MagicMock()
        mock_integrator_class.return_value = mock_integrator
        mock_integrator.run_mutations.return_value = create_sample_mutations()

        config = Config(assertion_quality=True, mutation_timeout_ms=5000)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(tmp_path))

        assert result.engine == "assertion_quality"
        # Should have 3 survived mutations (from sample mutations)
        assert len(result.issues) == 3
        # Verify timeout was passed to integrator
        mock_integrator.run_mutations.assert_called_once_with(str(tmp_path), timeout_ms=5000)

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_analyze_no_mutations(self, mock_integrator_class: MagicMock, tmp_path: Path) -> None:
        """Test analysis when mutmut returns no mutations."""
        # Setup mock to return empty list (mutmut not available)
        mock_integrator = MagicMock()
        mock_integrator_class.return_value = mock_integrator
        mock_integrator.run_mutations.return_value = []

        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(tmp_path))

        assert result.engine == "assertion_quality"
        assert len(result.issues) == 0

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_analyze_exception_handling(
        self, mock_integrator_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test that exceptions are handled gracefully."""
        # Setup mock to raise exception
        mock_integrator = MagicMock()
        mock_integrator_class.return_value = mock_integrator
        mock_integrator.run_mutations.side_effect = RuntimeError("Test error")

        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(tmp_path))

        # Should return empty result, not raise
        assert result.engine == "assertion_quality"
        assert len(result.issues) == 0

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_analyze_custom_timeout(self, mock_integrator_class: MagicMock, tmp_path: Path) -> None:
        """Test that custom timeout is passed to integrator."""
        mock_integrator = MagicMock()
        mock_integrator_class.return_value = mock_integrator
        mock_integrator.run_mutations.return_value = []

        custom_timeout = 30000
        config = Config(assertion_quality=True, mutation_timeout_ms=custom_timeout)
        analyzer = AssertionQualityAnalyzer(config)
        analyzer.analyze(str(tmp_path))

        mock_integrator.run_mutations.assert_called_once()
        call_kwargs = mock_integrator.run_mutations.call_args[1]
        assert call_kwargs["timeout_ms"] == custom_timeout


class TestAssertionQualityAnalyzerFindTestFiles:
    """Test finding test files."""

    def test_find_test_files(self, tmp_path: Path) -> None:
        """Test finding test files."""
        # Create test files
        test_file1 = tmp_path / "test_example.py"
        test_file1.write_text("def test_foo(): pass")

        test_file2 = tmp_path / "example_test.py"
        test_file2.write_text("def test_bar(): pass")

        analyzer = AssertionQualityAnalyzer()
        test_files = analyzer._find_test_files(tmp_path)
        assert len(test_files) == 2

    def test_find_test_files_single_file(self, tmp_path: Path) -> None:
        """Test finding test files with single test file."""
        test_file = tmp_path / "test_example.py"
        test_file.write_text("def test_foo(): pass")

        analyzer = AssertionQualityAnalyzer()
        test_files = analyzer._find_test_files(test_file)
        assert len(test_files) == 1

    def test_find_test_files_non_test_file(self, tmp_path: Path) -> None:
        """Test finding test files with non-test file."""
        src_file = tmp_path / "example.py"
        src_file.write_text("def foo(): pass")

        analyzer = AssertionQualityAnalyzer()
        test_files = analyzer._find_test_files(src_file)
        assert len(test_files) == 0


class TestAssertionQualityAnalyzerIgnore:
    """Test file ignoring functionality."""

    def test_should_ignore_file_venv(self) -> None:
        """Test ignoring virtualenv files."""
        analyzer = AssertionQualityAnalyzer()
        assert analyzer._should_ignore_file(".venv/lib/python3.9/site-packages/foo.py")

    def test_should_ignore_file_empty_config(self) -> None:
        """Test with empty ignore list."""
        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        assert not analyzer._should_ignore_file("src/module.py")

    def test_should_ignore_file_custom_pattern(self) -> None:
        """Test custom ignore patterns."""
        from pytest_doctor.config import IgnoreConfig

        ignore = IgnoreConfig(files=["vendor/**", "node_modules/**"])
        config = Config(assertion_quality=True, ignore=ignore)
        analyzer = AssertionQualityAnalyzer(config)

        assert analyzer._should_ignore_file("vendor/file.py")
        assert analyzer._should_ignore_file("node_modules/package.js")
        assert not analyzer._should_ignore_file("src/module.py")


class TestAssertionQualityAnalyzerDurationTracking:
    """Test that analysis duration is tracked."""

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_analyze_duration_ms(self, mock_integrator_class: MagicMock, tmp_path: Path) -> None:
        """Test that duration_ms is set."""
        mock_integrator = MagicMock()
        mock_integrator_class.return_value = mock_integrator
        mock_integrator.run_mutations.return_value = []

        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(tmp_path))

        # Duration should be set and non-negative
        assert result.duration_ms >= 0

    def test_analyze_duration_nonexistent_path(self) -> None:
        """Test duration is still set for nonexistent paths."""
        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze("/nonexistent/path")

        # Duration should be set even if path doesn't exist
        assert result.duration_ms >= 0
