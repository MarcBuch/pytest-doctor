"""Test quality analysis for pytest-doctor."""

from __future__ import annotations

import ast
import time
from pathlib import Path

from pytest_doctor.config import Config
from pytest_doctor.models import AnalysisResult, Issue, IssueSource, Severity


class QualityAnalyzer:
    """Analyzes test quality for fixture isolation, parametrization, and coverage."""

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize the Test Quality analyzer.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()

    def analyze(self, path: str | Path) -> AnalysisResult:
        """
        Analyze test files for quality issues.

        Args:
            path: Directory or file path to analyze

        Returns:
            AnalysisResult containing found quality issues
        """
        start_time = time.time()
        result = AnalysisResult(engine="test_quality")

        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return result

            # Get test files to analyze
            test_files = self._find_test_files(path_obj)

            # Analyze each test file
            for test_file in test_files:
                if self._should_ignore_file(str(test_file)):
                    continue

                file_issues = self._analyze_file(test_file)
                result.issues.extend(file_issues)

        except Exception:
            # If analysis fails, return empty result
            pass
        finally:
            result.duration_ms = (time.time() - start_time) * 1000

        return result

    def _find_test_files(self, path: Path) -> list[Path]:
        """Find all test files in a directory."""
        if path.is_file():
            if path.name.startswith("test_") or path.name.endswith("_test.py"):
                return [path]
            return []

        return list(path.rglob("test_*.py")) + list(path.rglob("*_test.py"))

    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on config."""
        import pathspec

        if not self.config.ignore.files:
            return False

        spec = pathspec.PathSpec.from_lines("gitignore", self.config.ignore.files)
        return spec.match_file(file_path)

    def _analyze_file(self, file_path: Path) -> list[Issue]:
        """Analyze a single test file for quality issues."""
        issues: list[Issue] = []

        try:
            source = file_path.read_text()
            tree = ast.parse(source)

            # Check for fixture issues
            fixture_issues = self._check_fixture_isolation(tree, file_path, source)
            issues.extend(fixture_issues)

            # Check for missing parametrization
            param_issues = self._check_missing_parametrization(tree, file_path)
            issues.extend(param_issues)

            # Check for slow/large tests
            slow_issues = self._check_test_size(tree, file_path, source)
            issues.extend(slow_issues)

        except (SyntaxError, ValueError):
            # Skip files with syntax errors
            pass

        return issues

    def _check_fixture_isolation(self, tree: ast.AST, file_path: Path, source: str) -> list[Issue]:
        """Check for fixture isolation issues."""
        issues: list[Issue] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Skip non-test functions
            if not node.name.startswith("test_"):
                continue

            # Check for class-level fixtures or module-level state modification
            for item in ast.walk(node):
                if (
                    isinstance(item, ast.Attribute)
                    and isinstance(item.value, ast.Name)
                    and item.value.id in ("self", "cls")
                ):
                    # Check for self.x assignments that might indicate state
                    parent = self._find_parent_assign(tree, item)
                    if parent:
                        issues.append(
                            Issue(
                                file_path=str(file_path),
                                line_number=item.lineno or 0,
                                column_number=item.col_offset or 0,
                                rule_id="fixture-isolation",
                                rule_name="Potential fixture isolation issue",
                                message=f"Test modifies {item.attr} which may affect other tests",
                                severity=Severity.INFO,
                                source=IssueSource.TEST_QUALITY,
                                recommendation="Use fixture setup/teardown or mock external state",
                            )
                        )

        return issues

    def _check_missing_parametrization(self, tree: ast.AST, file_path: Path) -> list[Issue]:
        """Check for tests that should be parametrized."""
        issues: list[Issue] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            if not node.name.startswith("test_"):
                continue

            # Look for loops within tests (potential parametrization opportunity)
            has_loop = False
            for item in ast.walk(node):
                if isinstance(item, (ast.For, ast.While)):
                    has_loop = True
                    break

            if has_loop:
                issues.append(
                    Issue(
                        file_path=str(file_path),
                        line_number=node.lineno or 0,
                        column_number=node.col_offset or 0,
                        rule_id="missing-parametrization",
                        rule_name="Missing test parametrization",
                        message=f"Test {node.name} contains loops that could be parametrized",
                        severity=Severity.INFO,
                        source=IssueSource.TEST_QUALITY,
                        recommendation="Use @pytest.mark.parametrize decorator instead of loops",
                    )
                )

        return issues

    def _check_test_size(self, tree: ast.AST, file_path: Path, source: str) -> list[Issue]:
        """Check for tests that are too large."""
        issues: list[Issue] = []

        # Count lines per function
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            if not node.name.startswith("test_"):
                continue

            # Get function line count
            end_line = node.end_lineno or node.lineno
            start_line = node.lineno
            line_count = end_line - start_line

            # Flag tests that are too large (>20 lines is often a sign of poor organization)
            if line_count > 20:
                issues.append(
                    Issue(
                        file_path=str(file_path),
                        line_number=start_line or 0,
                        column_number=node.col_offset or 0,
                        rule_id="large-test",
                        rule_name="Test is too large",
                        message=f"Test {node.name} has {line_count} lines (>20 is a code smell)",
                        severity=Severity.INFO,
                        source=IssueSource.TEST_QUALITY,
                        recommendation="Break test into smaller, focused tests",
                    )
                )

        return issues

    def _find_parent_assign(self, tree: ast.AST, target: ast.Attribute) -> ast.Assign | None:
        """Find the assignment parent of an attribute access."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target_node in node.targets:
                    if target_node == target:
                        return node
        return None
