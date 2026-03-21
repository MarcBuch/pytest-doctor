"""Tests for Test Quality analyzer."""

import ast
from pathlib import Path

from pytest_doctor.analyzers.quality_analyzer import QualityAnalyzer
from pytest_doctor.config import Config, IgnoreConfig
from pytest_doctor.models import IssueSource


def test_quality_analyzer_init() -> None:
    """Test QualityAnalyzer initialization."""
    analyzer = QualityAnalyzer()
    assert analyzer.config is not None
    assert analyzer.config.test_analysis is True


def test_quality_analyzer_with_custom_config() -> None:
    """Test QualityAnalyzer with custom config."""
    config = Config(test_analysis=False)
    analyzer = QualityAnalyzer(config)
    assert analyzer.config.test_analysis is False


def test_quality_analyzer_nonexistent_path() -> None:
    """Test analyzing a non-existent path."""
    analyzer = QualityAnalyzer()
    result = analyzer.analyze("/nonexistent/path")
    assert result.engine == "test_quality"
    assert len(result.issues) == 0


def test_quality_analyzer_find_test_files(tmp_path: Path) -> None:
    """Test finding test files."""
    # Create test files
    (tmp_path / "test_example.py").write_text("def test_foo(): pass")
    (tmp_path / "example_test.py").write_text("def test_bar(): pass")
    (tmp_path / "example.py").write_text("def main(): pass")

    analyzer = QualityAnalyzer()
    test_files = analyzer._find_test_files(tmp_path)

    # Should find both test files, not the regular module
    assert len(test_files) == 2
    assert any("test_example" in str(f) for f in test_files)
    assert any("example_test" in str(f) for f in test_files)


def test_quality_analyzer_find_single_test_file(tmp_path: Path) -> None:
    """Test finding a single test file."""
    test_file = tmp_path / "test_single.py"
    test_file.write_text("def test_foo(): pass")

    analyzer = QualityAnalyzer()
    test_files = analyzer._find_test_files(test_file)

    assert len(test_files) == 1
    assert test_files[0] == test_file


def test_quality_analyzer_find_no_test_files(tmp_path: Path) -> None:
    """Test when no test files exist."""
    analyzer = QualityAnalyzer()
    test_files = analyzer._find_test_files(tmp_path)
    assert len(test_files) == 0


def test_quality_analyzer_should_ignore_file() -> None:
    """Test file ignoring logic."""
    config = Config(ignore=IgnoreConfig(files=["tests/legacy/**", "src/old/**"]))
    analyzer = QualityAnalyzer(config)

    # Should ignore files matching patterns
    assert analyzer._should_ignore_file("tests/legacy/old_test.py") is True
    assert analyzer._should_ignore_file("src/old/deprecated.py") is True

    # Should not ignore other files
    assert analyzer._should_ignore_file("tests/new_test.py") is False


def test_quality_analyzer_check_missing_parametrization(tmp_path: Path) -> None:
    """Test detecting missing parametrization."""
    test_file = tmp_path / "test_example.py"
    test_file.write_text("""
def test_multiple_values():
    for value in [1, 2, 3]:
        assert value > 0
""")

    analyzer = QualityAnalyzer()
    issues = analyzer._analyze_file(test_file)

    # Should find a missing parametrization issue
    assert any(issue.rule_id == "missing-parametrization" for issue in issues)


def test_quality_analyzer_check_large_test(tmp_path: Path) -> None:
    """Test detecting large tests."""
    test_file = tmp_path / "test_large.py"
    # Create a test with many lines
    lines = ["def test_large():"]
    for i in range(30):
        lines.append(f"    x{i} = {i}")
    lines.append("    assert True")

    test_file.write_text("\n".join(lines))

    analyzer = QualityAnalyzer()
    issues = analyzer._analyze_file(test_file)

    # Should find a large test issue
    assert any(issue.rule_id == "large-test" for issue in issues)


def test_quality_analyzer_analyze_with_real_file(tmp_path: Path) -> None:
    """Test analyzing a real test file."""
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("""
def test_simple():
    assert True

def test_multiple_cases():
    for val in [1, 2, 3]:
        assert val > 0
""")

    analyzer = QualityAnalyzer()
    result = analyzer.analyze(tmp_path)

    assert result.engine == "test_quality"
    assert result.duration_ms > 0
    # Should find the loop-based test
    assert len(result.issues) > 0


def test_quality_analyzer_syntax_error_handling(tmp_path: Path) -> None:
    """Test handling of files with syntax errors."""
    test_file = tmp_path / "test_bad.py"
    test_file.write_text("def test_foo():\n    this is not valid python")

    analyzer = QualityAnalyzer()
    result = analyzer.analyze(tmp_path)

    # Should not crash on syntax errors
    assert result.engine == "test_quality"


def test_quality_analyzer_issue_source() -> None:
    """Test that issues are marked with correct source."""
    analyzer = QualityAnalyzer()
    code = """
def test_example():
    for x in [1, 2]:
        assert x > 0
"""
    tree = ast.parse(code)
    temp_path = Path("test_file.py")

    issues = analyzer._check_missing_parametrization(tree, temp_path)

    assert len(issues) > 0
    assert all(issue.source == IssueSource.TEST_QUALITY for issue in issues)
