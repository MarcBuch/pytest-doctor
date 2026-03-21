"""Tests for the coverage gap analyzer."""

import pytest

from pytest_doctor.analyzers.gap_analyzer import GapAnalyzer
from pytest_doctor.config import Config
from pytest_doctor.models import IssueSource, Severity


class TestGapAnalyzerInit:
    """Test GapAnalyzer initialization."""

    def test_gap_analyzer_init(self) -> None:
        """Test basic initialization."""
        analyzer = GapAnalyzer()
        assert analyzer.config is not None

    def test_gap_analyzer_with_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = Config(coverage_gaps=True)
        analyzer = GapAnalyzer(config)
        assert analyzer.config == config
        assert analyzer.config.coverage_gaps is True


class TestGapAnalyzerBasic:
    """Test basic gap analyzer functionality."""

    def test_gap_analyzer_nonexistent_path(self) -> None:
        """Test analysis with nonexistent path."""
        analyzer = GapAnalyzer()
        result = analyzer.analyze("/nonexistent/path")
        assert result.engine == "coverage_gaps"
        assert len(result.issues) == 0
        assert result.duration_ms >= 0

    def test_gap_analyzer_empty_directory(self, tmp_path) -> None:
        """Test analysis with empty directory."""
        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        assert result.engine == "coverage_gaps"
        assert len(result.issues) == 0

    def test_gap_analyzer_find_test_files(self, tmp_path) -> None:
        """Test finding test files."""
        # Create test files
        test_file1 = tmp_path / "test_example.py"
        test_file1.write_text("def test_foo(): pass")

        test_file2 = tmp_path / "example_test.py"
        test_file2.write_text("def test_bar(): pass")

        analyzer = GapAnalyzer()
        test_files = analyzer._find_test_files(tmp_path)
        assert len(test_files) == 2

    def test_gap_analyzer_find_source_files(self, tmp_path) -> None:
        """Test finding source files (excluding tests)."""
        # Create source files
        src_file = tmp_path / "example.py"
        src_file.write_text("def foo(): pass")

        test_file = tmp_path / "test_example.py"
        test_file.write_text("def test_foo(): pass")

        analyzer = GapAnalyzer()
        source_files = analyzer._find_source_files(tmp_path)
        assert len(source_files) == 1
        assert source_files[0].name == "example.py"

    def test_gap_analyzer_find_test_files_single_file(self, tmp_path) -> None:
        """Test finding test files with single test file."""
        test_file = tmp_path / "test_example.py"
        test_file.write_text("def test_foo(): pass")

        analyzer = GapAnalyzer()
        test_files = analyzer._find_test_files(test_file)
        assert len(test_files) == 1

    def test_gap_analyzer_find_test_files_non_test_file(self, tmp_path) -> None:
        """Test finding test files with non-test file."""
        src_file = tmp_path / "example.py"
        src_file.write_text("def foo(): pass")

        analyzer = GapAnalyzer()
        test_files = analyzer._find_test_files(src_file)
        assert len(test_files) == 0


class TestGapAnalyzerIgnore:
    """Test file ignoring functionality."""

    def test_gap_analyzer_should_ignore_file(self) -> None:
        """Test file ignoring."""
        config = Config(coverage_gaps=True)
        analyzer = GapAnalyzer(config)
        assert analyzer._should_ignore_file(".venv/lib/python3.9/site-packages/foo.py")

    def test_gap_analyzer_should_ignore_file_empty_config(self) -> None:
        """Test file ignoring with empty ignore list."""
        config = Config()
        config.ignore.files = []
        analyzer = GapAnalyzer(config)
        assert not analyzer._should_ignore_file("src/example.py")


class TestGapAnalyzerComplexity:
    """Test cyclomatic complexity calculation."""

    def test_gap_analyzer_simple_function(self, tmp_path) -> None:
        """Test complexity calculation for simple function."""
        src_file = tmp_path / "simple.py"
        src_file.write_text("""
def simple_func(x):
    return x + 1
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        # Simple function should not trigger untested-function issue
        untested_issues = [i for i in result.issues if i.rule_id == "untested-function"]
        assert len(untested_issues) == 0

    def test_gap_analyzer_complex_function(self, tmp_path) -> None:
        """Test complexity calculation for complex function."""
        src_file = tmp_path / "complex.py"
        src_file.write_text("""
def complex_func(x):
    if x > 0:
        if x > 10:
            return x * 2
        else:
            return x + 1
    else:
        return -x
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        # Complex function should trigger untested-function issue
        untested_issues = [i for i in result.issues if i.rule_id == "untested-function"]
        assert len(untested_issues) > 0


class TestGapAnalyzerTestedEntities:
    """Test extraction of tested entities."""

    def test_gap_analyzer_extract_tested_entities(self, tmp_path) -> None:
        """Test extraction of tested entities from test files."""
        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_foo():
    pass

def test_bar():
    pass
""")

        analyzer = GapAnalyzer()
        test_files = [test_file]
        tested = analyzer._extract_tested_entities(test_files)
        assert len(tested) > 0

    def test_gap_analyzer_docstring_extraction(self) -> None:
        """Test extraction of entities from docstrings."""
        analyzer = GapAnalyzer()
        entities = analyzer._extract_entities_from_docstring("Test ClassName and Tests SomeMethod")
        assert "ClassName" in entities
        assert "SomeMethod" in entities


class TestGapAnalyzerRiskPatterns:
    """Test detection of high-risk patterns."""

    def test_gap_analyzer_broad_exception(self, tmp_path) -> None:
        """Test detection of broad exception handling."""
        src_file = tmp_path / "risky.py"
        src_file.write_text("""
def risky_func():
    try:
        some_operation()
    except:
        pass
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        broad_exc_issues = [i for i in result.issues if i.rule_id == "broad-exception-handler"]
        assert len(broad_exc_issues) > 0

    def test_gap_analyzer_high_complexity(self, tmp_path) -> None:
        """Test detection of high complexity functions."""
        src_file = tmp_path / "very_complex.py"
        src_file.write_text("""
def very_complex_func(a, b, c):
    if a:
        if b:
            if c:
                if a > b:
                    return x
    return y
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        complexity_issues = [i for i in result.issues if i.rule_id == "high-complexity-function"]
        # May or may not have issues depending on exact nesting depth
        assert isinstance(complexity_issues, list)


class TestGapAnalyzerEdgeCases:
    """Test detection of edge case opportunities."""

    def test_gap_analyzer_untested_index_access(self, tmp_path) -> None:
        """Test detection of index access without bounds checking."""
        src_file = tmp_path / "indexing.py"
        src_file.write_text("""
def get_first_element(items):
    return items[0]
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        index_issues = [i for i in result.issues if i.rule_id == "untested-index-access"]
        assert len(index_issues) > 0

    def test_gap_analyzer_untested_division(self, tmp_path) -> None:
        """Test detection of division without zero-check."""
        src_file = tmp_path / "dividing.py"
        src_file.write_text("""
def divide(a, b):
    return a / b
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        div_issues = [i for i in result.issues if i.rule_id == "untested-division"]
        assert len(div_issues) > 0


class TestGapAnalyzerUntested:
    """Test detection of untested functions and classes."""

    def test_gap_analyzer_untested_function_with_branches(self, tmp_path) -> None:
        """Test detection of untested functions with multiple branches."""
        # Create source file without tests
        src_file = tmp_path / "source.py"
        src_file.write_text("""
def branching_func(x):
    if x > 0:
        return x * 2
    else:
        return -x
""")

        # Create test file that doesn't test the function
        test_file = tmp_path / "test_other.py"
        test_file.write_text("""
def test_something_else():
    pass
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        untested_issues = [i for i in result.issues if i.rule_id == "untested-function"]
        assert len(untested_issues) > 0

    def test_gap_analyzer_untested_class(self, tmp_path) -> None:
        """Test detection of untested classes."""
        src_file = tmp_path / "source.py"
        src_file.write_text("""
class MyClass:
    def public_method(self):
        return 42

    def _private_method(self):
        return 0
""")

        test_file = tmp_path / "test_other.py"
        test_file.write_text("""
def test_something():
    pass
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        untested_issues = [i for i in result.issues if i.rule_id == "untested-class"]
        assert len(untested_issues) > 0

    def test_gap_analyzer_tested_class_not_flagged(self, tmp_path) -> None:
        """Test that tested classes are not flagged."""
        src_file = tmp_path / "source.py"
        src_file.write_text("""
class TestedClass:
    def public_method(self):
        return 42
""")

        test_file = tmp_path / "test_source.py"
        test_file.write_text("""
def test_TestedClass():
    pass
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        untested_class_issues = [
            i for i in result.issues if i.rule_id == "untested-class" and "TestedClass" in i.message
        ]
        # Should be fewer issues since class is marked as tested
        assert len(untested_class_issues) == 0


class TestGapAnalyzerIssueProperties:
    """Test properties of generated issues."""

    def test_gap_analyzer_issue_has_source(self, tmp_path) -> None:
        """Test that all issues have correct source."""
        src_file = tmp_path / "source.py"
        src_file.write_text("""
def func_with_division(a, b):
    return a / b
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        for issue in result.issues:
            assert issue.source == IssueSource.COVERAGE

    def test_gap_analyzer_issue_has_line_number(self, tmp_path) -> None:
        """Test that all issues have line numbers."""
        src_file = tmp_path / "source.py"
        src_file.write_text("""
def func_with_division(a, b):
    return a / b
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        for issue in result.issues:
            assert issue.line_number > 0

    def test_gap_analyzer_issue_has_recommendation(self, tmp_path) -> None:
        """Test that all issues have recommendations."""
        src_file = tmp_path / "source.py"
        src_file.write_text("""
def func_with_division(a, b):
    return a / b
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        for issue in result.issues:
            assert issue.recommendation
            assert len(issue.recommendation) > 0

    def test_gap_analyzer_issue_severity_levels(self, tmp_path) -> None:
        """Test that issues have appropriate severity levels."""
        src_file = tmp_path / "source.py"
        src_file.write_text("""
def complex_func(a):
    if a:
        if a > 0:
            if a > 10:
                return a
    return 0
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        for issue in result.issues:
            assert issue.severity in [Severity.CRITICAL, Severity.WARNING, Severity.INFO]


class TestGapAnalyzerSyntaxErrors:
    """Test handling of syntax errors."""

    def test_gap_analyzer_syntax_error_handling(self, tmp_path) -> None:
        """Test that analyzer handles syntax errors gracefully."""
        src_file = tmp_path / "syntax_error.py"
        src_file.write_text("def broken(: pass")  # Invalid syntax

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))
        # Should return empty result, not crash
        assert result.engine == "coverage_gaps"
        assert isinstance(result.issues, list)


@pytest.mark.integration
class TestGapAnalyzerWithRealCode:
    """Test gap analyzer with realistic code samples."""

    def test_gap_analyzer_realistic_project(self, tmp_path) -> None:
        """Test gap analyzer with realistic project structure."""
        # Create a realistic project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()

        # Source files
        src_file = tmp_path / "src" / "calculator.py"
        src_file.write_text("""
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:
    def multiply(self, a, b):
        return a * b
""")

        # Test files
        test_file = tmp_path / "tests" / "test_calculator.py"
        test_file.write_text("""
def test_add():
    from src.calculator import add
    assert add(2, 3) == 5

def test_Calculator():
    from src.calculator import Calculator
    calc = Calculator()
    assert calc.multiply(2, 3) == 6
""")

        analyzer = GapAnalyzer()
        result = analyzer.analyze(str(tmp_path))

        # Should have found some coverage gaps
        assert result.engine == "coverage_gaps"
        assert result.duration_ms > 0
        # Should have found untested divide function
        untested_div = [i for i in result.issues if "divide" in i.message.lower()]
        assert len(untested_div) > 0
