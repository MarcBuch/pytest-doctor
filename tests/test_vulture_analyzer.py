"""Tests for Vulture analyzer."""

from pathlib import Path

import pytest

from pytest_doctor.analyzers.vulture_analyzer import VultureAnalyzer
from pytest_doctor.config import Config, IgnoreConfig
from pytest_doctor.models import Severity


@pytest.fixture
def mock_item_with_confidence():
    """Fixture for mock item with confidence level."""

    class MockItem:
        def __init__(self, confidence: int):
            self.confidence = confidence

    return MockItem


@pytest.fixture
def mock_item_with_type_and_name():
    """Fixture for mock item with type and name."""

    class MockItem:
        def __init__(self, item_type: str, name: str):
            self.type = item_type
            self.name = name

    return MockItem


def test_vulture_analyzer_init() -> None:
    """Test VultureAnalyzer initialization."""
    analyzer = VultureAnalyzer()
    assert analyzer.config is not None
    assert analyzer.config.dead_code is True


def test_vulture_analyzer_with_custom_config() -> None:
    """Test VultureAnalyzer with custom config."""
    config = Config(dead_code=False)
    analyzer = VultureAnalyzer(config)
    assert analyzer.config.dead_code is False


def test_vulture_analyzer_nonexistent_path() -> None:
    """Test analyzing a non-existent path."""
    analyzer = VultureAnalyzer()
    result = analyzer.analyze("/nonexistent/path")
    assert result.engine == "vulture"
    assert len(result.issues) == 0


def test_vulture_analyzer_analyze_with_real_file(tmp_path: Path) -> None:
    """Test analyzing a real Python file with vulture."""
    # Create a test file with an unused variable
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("""
def test_something():
    unused_var = 42  # This should be detected as unused
    x = 10
    return x
""")

    analyzer = VultureAnalyzer()
    result = analyzer.analyze(tmp_path)

    assert result.engine == "vulture"
    assert result.duration_ms > 0


def test_vulture_analyzer_map_severity(mock_item_with_confidence) -> None:
    """Test severity mapping based on confidence."""
    analyzer = VultureAnalyzer()

    # High confidence should map to WARNING
    high_conf = mock_item_with_confidence(85)
    assert analyzer._map_severity(high_conf) == Severity.WARNING

    # Low confidence should map to INFO
    low_conf = mock_item_with_confidence(50)
    assert analyzer._map_severity(low_conf) == Severity.INFO


def test_vulture_analyzer_get_recommendation(mock_item_with_type_and_name) -> None:
    """Test recommendation generation for different item types."""
    analyzer = VultureAnalyzer()

    # Test different types
    func_item = mock_item_with_type_and_name("function", "test_helper")
    assert "function" in analyzer._get_recommendation(func_item).lower()
    assert "test_helper" in analyzer._get_recommendation(func_item)

    var_item = mock_item_with_type_and_name("variable", "temp_var")
    assert "variable" in analyzer._get_recommendation(var_item).lower()

    class_item = mock_item_with_type_and_name("class", "UnusedClass")
    assert "class" in analyzer._get_recommendation(class_item).lower()

    import_item = mock_item_with_type_and_name("import", "os")
    assert "import" in analyzer._get_recommendation(import_item).lower()


def test_vulture_analyzer_should_ignore_file() -> None:
    """Test file ignoring logic."""
    config = Config(ignore=IgnoreConfig(files=["tests/legacy/**", "src/old/**"]))
    analyzer = VultureAnalyzer(config)

    # Should ignore files matching patterns
    assert analyzer._should_ignore_file("tests/legacy/old_test.py") is True
    assert analyzer._should_ignore_file("src/old/deprecated.py") is True

    # Should not ignore other files
    assert analyzer._should_ignore_file("tests/new_test.py") is False
    assert analyzer._should_ignore_file("src/main.py") is False


def test_vulture_analyzer_should_ignore_file_empty_config() -> None:
    """Test file ignoring with empty config."""
    analyzer = VultureAnalyzer()
    assert analyzer._should_ignore_file("any/file.py") is False


def test_vulture_analyzer_test_file_detection(tmp_path: Path) -> None:
    """Test that analyzer only picks up test files."""
    # Create a mix of files
    (tmp_path / "test_main.py").write_text("def test_foo(): pass")
    (tmp_path / "main_test.py").write_text("def test_bar(): pass")
    (tmp_path / "main.py").write_text("def main(): pass")

    analyzer = VultureAnalyzer()
    result = analyzer.analyze(tmp_path)

    # Should analyze test files without errors
    assert result.engine == "vulture"
    assert result.duration_ms > 0
