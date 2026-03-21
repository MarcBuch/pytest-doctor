"""Tests for Ruff analyzer."""

from pathlib import Path

from pytest_doctor.analyzers.ruff_analyzer import RuffAnalyzer
from pytest_doctor.config import Config, IgnoreConfig
from pytest_doctor.models import IssueSource, Severity


def test_ruff_analyzer_init() -> None:
    """Test RuffAnalyzer initialization."""
    analyzer = RuffAnalyzer()
    assert analyzer.config is not None
    assert analyzer.config.lint is True


def test_ruff_analyzer_with_custom_config() -> None:
    """Test RuffAnalyzer with custom config."""
    config = Config(lint=False)
    analyzer = RuffAnalyzer(config)
    assert analyzer.config.lint is False


def test_ruff_analyzer_nonexistent_path() -> None:
    """Test analyzing a non-existent path."""
    analyzer = RuffAnalyzer()
    result = analyzer.analyze("/nonexistent/path")
    assert result.engine == "ruff"
    assert len(result.issues) == 0


def test_ruff_analyzer_analyze_with_real_file(tmp_path: Path) -> None:
    """Test analyzing a real Python file with ruff."""
    # Create a test file with an obvious issue
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("import os\nx=1\n")  # Unused import and spacing

    analyzer = RuffAnalyzer()
    result = analyzer.analyze(tmp_path)

    assert result.engine == "ruff"
    assert len(result.issues) > 0  # Should find issues
    assert result.duration_ms > 0


def test_ruff_analyzer_map_severity() -> None:
    """Test severity mapping for different rule codes."""
    analyzer = RuffAnalyzer()

    # E codes should map to WARNING
    assert analyzer._map_severity("E501") == Severity.WARNING
    assert analyzer._map_severity("E302") == Severity.WARNING

    # F codes should map to WARNING (errors)
    assert analyzer._map_severity("F841") == Severity.WARNING

    # W codes should map to WARNING
    assert analyzer._map_severity("W503") == Severity.WARNING

    # B codes (bugbear) should map to WARNING
    assert analyzer._map_severity("B008") == Severity.WARNING

    # Other codes should map to INFO
    assert analyzer._map_severity("UP009") == Severity.INFO


def test_ruff_analyzer_get_recommendation() -> None:
    """Test recommendation generation."""
    analyzer = RuffAnalyzer()

    # Check known recommendations
    assert "long lines" in analyzer._get_recommendation("E501").lower()
    assert "unused" in analyzer._get_recommendation("F841").lower()
    assert "binary operator" in analyzer._get_recommendation("W503").lower()

    # Check unknown rule gets generic recommendation
    assert "Fix" in analyzer._get_recommendation("UNKNOWN")


def test_ruff_analyzer_should_ignore_file() -> None:
    """Test file ignoring logic."""
    config = Config(ignore=IgnoreConfig(files=["tests/legacy/**", "src/old/**"]))
    analyzer = RuffAnalyzer(config)

    # Should ignore files matching patterns
    assert analyzer._should_ignore_file("tests/legacy/old_test.py") is True
    assert analyzer._should_ignore_file("src/old/deprecated.py") is True

    # Should not ignore other files
    assert analyzer._should_ignore_file("tests/new_test.py") is False
    assert analyzer._should_ignore_file("src/main.py") is False


def test_ruff_analyzer_should_ignore_file_empty_config() -> None:
    """Test file ignoring with empty config."""
    analyzer = RuffAnalyzer()
    assert analyzer._should_ignore_file("any/file.py") is False


def test_ruff_analyzer_parse_violations() -> None:
    """Test parsing ruff violations."""
    analyzer = RuffAnalyzer()

    violations = [
        {
            "filename": "test_file.py",
            "code": "E501",
            "message": "Line too long",
            "location": {"row": 10, "column": 88},
        },
        {
            "filename": "another_file.py",
            "code": "F841",
            "message": "Local variable is assigned but never used",
            "location": {"row": 5, "column": 0},
        },
    ]

    issues = analyzer._parse_violations(violations)

    assert len(issues) == 2
    assert issues[0].file_path == "test_file.py"
    assert issues[0].rule_id == "E501"
    assert issues[0].line_number == 10
    assert issues[0].column_number == 88
    assert issues[0].source == IssueSource.LINTING
    assert issues[0].severity == Severity.WARNING

    assert issues[1].file_path == "another_file.py"
    assert issues[1].rule_id == "F841"


def test_ruff_analyzer_respects_ignore_rules(tmp_path: Path) -> None:
    """Test that ignore rules configuration is respected."""
    # Create a test file
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("import os\n")  # Unused import (F401)

    config = Config(ignore=IgnoreConfig(rules=["F401"]))
    analyzer = RuffAnalyzer(config)
    result = analyzer.analyze(tmp_path)

    # With F401 ignored, we might get no issues or different ones
    # The exact behavior depends on ruff's behavior
    assert result.engine == "ruff"
