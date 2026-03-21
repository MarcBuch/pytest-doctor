"""Coverage gap analysis for pytest-doctor."""

from __future__ import annotations

import ast
import time
from pathlib import Path

from pytest_doctor.config import Config
from pytest_doctor.models import AnalysisResult, Issue, IssueSource, Severity


class GapAnalyzer:
    """Analyzes test coverage gaps and identifies untested code paths."""

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize the Gap Analysis engine.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()

    def analyze(self, path: str | Path) -> AnalysisResult:
        """
        Analyze the project for test coverage gaps.

        Args:
            path: Directory or file path to analyze

        Returns:
            AnalysisResult containing found coverage gaps
        """
        start_time = time.time()
        result = AnalysisResult(engine="coverage_gaps")

        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return result

            # Analyze source files for untested patterns
            source_files = self._find_source_files(path_obj)
            test_files = self._find_test_files(path_obj)

            # Build a map of tested functions/classes from test files
            tested_entities = self._extract_tested_entities(test_files)

            # Analyze source files for coverage gaps
            for source_file in source_files:
                if self._should_ignore_file(str(source_file)):
                    continue

                file_issues = self._analyze_source_file(source_file, tested_entities)
                result.issues.extend(file_issues)

        except Exception:
            # If analysis fails, return empty result
            pass
        finally:
            result.duration_ms = (time.time() - start_time) * 1000

        return result

    def _find_source_files(self, path: Path) -> list[Path]:
        """Find all Python source files in a directory (excluding tests)."""
        if path.is_file():
            if path.suffix == ".py" and not (
                path.name.startswith("test_") or path.name.endswith("_test.py")
            ):
                return [path]
            return []

        # Find all .py files except test files
        all_py_files = list(path.rglob("*.py"))
        source_files = [
            f
            for f in all_py_files
            if not (f.name.startswith("test_") or f.name.endswith("_test.py"))
            and f.parts[-2:] != ("tests",)  # Skip files in 'tests' directory
            and "tests" not in f.parts
        ]
        return source_files

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

    def _extract_tested_entities(self, test_files: list[Path]) -> dict[str, set[str]]:
        """
        Extract function and class names that are tested.

        Args:
            test_files: List of test file paths

        Returns:
            Dictionary mapping module paths to sets of tested entity names
        """
        tested_entities: dict[str, set[str]] = {}

        for test_file in test_files:
            try:
                source = test_file.read_text()
                tree = ast.parse(source)

                # Extract what's being tested by analyzing test names and imports
                module_path = str(test_file)
                tested = set()

                for node in ast.walk(tree):
                    # Functions that start with test_ indicate testing of something
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        # Extract the tested entity from the function name
                        tested_name = node.name[5:]  # Remove 'test_' prefix
                        tested.add(tested_name)

                    # Also extract from docstrings (e.g., """Test ClassName.method""")
                    if isinstance(node, ast.FunctionDef):
                        docstring = ast.get_docstring(node)
                        if docstring:
                            # Extract entity names from docstring
                            extracted = self._extract_entities_from_docstring(docstring)
                            tested.update(extracted)

                if tested:
                    tested_entities[module_path] = tested

            except (SyntaxError, ValueError):
                # Skip files with syntax errors
                pass

        return tested_entities

    def _extract_entities_from_docstring(self, docstring: str) -> set[str]:
        """Extract entity names from test docstrings."""
        import re

        entities = set()

        # Look for patterns like "Test ClassName" or "Tests method_name"
        pattern = r"[Tt]est[s]?\s+(\w+)"
        matches = re.findall(pattern, docstring)
        entities.update(matches)

        return entities

    def _analyze_source_file(
        self, source_file: Path, tested_entities: dict[str, set[str]]
    ) -> list[Issue]:
        """Analyze a source file for coverage gaps."""
        issues: list[Issue] = []

        try:
            source = source_file.read_text()
            tree = ast.parse(source)

            # Check for untested public functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):  # Public function
                    gap_issues = self._check_untested_function(node, source_file, tested_entities)
                    issues.extend(gap_issues)

                elif (
                    isinstance(node, ast.ClassDef) and not node.name.startswith("_")  # Public class
                ):
                    gap_issues = self._check_untested_class(node, source_file, tested_entities)
                    issues.extend(gap_issues)

            # Check for high-risk patterns
            risk_issues = self._check_high_risk_patterns(tree, source_file, source)
            issues.extend(risk_issues)

            # Check for edge case opportunities
            edge_issues = self._check_edge_cases(tree, source_file)
            issues.extend(edge_issues)

        except (SyntaxError, ValueError):
            # Skip files with syntax errors
            pass

        return issues

    def _check_untested_function(
        self,
        node: ast.FunctionDef,
        source_file: Path,
        tested_entities: dict[str, set[str]],
    ) -> list[Issue]:
        """Check if a function appears to be tested."""
        issues: list[Issue] = []

        # Check if function name appears in any tested entities
        is_tested = any(node.name in entities for entities in tested_entities.values())

        # Check for complex functions without tests (more than one path)
        complexity = self._calculate_cyclomatic_complexity(node)

        if not is_tested and complexity > 1:
            issues.append(
                Issue(
                    file_path=str(source_file),
                    line_number=node.lineno or 0,
                    column_number=node.col_offset or 0,
                    rule_id="untested-function",
                    rule_name="Function appears untested",
                    message=f"Function '{node.name}' with {complexity} code paths may not be tested",
                    severity=Severity.WARNING,
                    source=IssueSource.COVERAGE,
                    recommendation=f"Add test case(s) for {node.name} covering all branches",
                )
            )

        return issues

    def _check_untested_class(
        self,
        node: ast.ClassDef,
        source_file: Path,
        tested_entities: dict[str, set[str]],
    ) -> list[Issue]:
        """Check if a class appears to be tested."""
        issues: list[Issue] = []

        # Check if class name appears in any tested entities
        is_tested = any(node.name in entities for entities in tested_entities.values())

        if not is_tested:
            # Count public methods
            public_methods = [
                m.name
                for m in node.body
                if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
            ]

            if public_methods:
                issues.append(
                    Issue(
                        file_path=str(source_file),
                        line_number=node.lineno or 0,
                        column_number=node.col_offset or 0,
                        rule_id="untested-class",
                        rule_name="Class appears untested",
                        message=f"Class '{node.name}' with {len(public_methods)} public methods may not be tested",
                        severity=Severity.WARNING,
                        source=IssueSource.COVERAGE,
                        recommendation=f"Add test cases for {node.name} and its public methods",
                    )
                )

        return issues

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _check_high_risk_patterns(
        self, tree: ast.AST, source_file: Path, source: str
    ) -> list[Issue]:
        """Check for high-risk patterns in code."""
        issues: list[Issue] = []

        for node in ast.walk(tree):
            # Flag exception handling without tests
            if isinstance(node, ast.ExceptHandler) and (
                node.type is None
                or (isinstance(node.type, ast.Name) and node.type.id == "Exception")
            ):
                issues.append(
                    Issue(
                        file_path=str(source_file),
                        line_number=node.lineno or 0,
                        column_number=node.col_offset or 0,
                        rule_id="broad-exception-handler",
                        rule_name="Broad exception handling",
                        message="Generic exception handling may hide errors without tests",
                        severity=Severity.INFO,
                        source=IssueSource.COVERAGE,
                        recommendation="Add test cases for error conditions in this except block",
                    )
                )

            # Flag nested conditionals (complex branching)
            if isinstance(node, ast.FunctionDef):
                max_nesting = self._get_max_nesting_depth(node)
                if max_nesting > 3:
                    issues.append(
                        Issue(
                            file_path=str(source_file),
                            line_number=node.lineno or 0,
                            column_number=node.col_offset or 0,
                            rule_id="high-complexity-function",
                            rule_name="High complexity function",
                            message=f"Function '{node.name}' has {max_nesting} levels of nesting",
                            severity=Severity.INFO,
                            source=IssueSource.COVERAGE,
                            recommendation="Reduce complexity and add comprehensive test coverage",
                        )
                    )

        return issues

    def _get_max_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth in a node."""
        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._get_max_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._get_max_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _check_edge_cases(self, tree: ast.AST, source_file: Path) -> list[Issue]:
        """Check for edge cases that might not be tested."""
        issues: list[Issue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for list/dict operations that might have edge cases
                for child in ast.walk(node):
                    # Flag indexing operations (potential IndexError)
                    if isinstance(child, ast.Subscript):
                        issues.append(
                            Issue(
                                file_path=str(source_file),
                                line_number=child.lineno or 0,
                                column_number=child.col_offset or 0,
                                rule_id="untested-index-access",
                                rule_name="Potential indexing edge case",
                                message="Direct indexing may raise IndexError - consider edge case tests",
                                severity=Severity.INFO,
                                source=IssueSource.COVERAGE,
                                recommendation="Add test cases for empty collections and boundary indices",
                            )
                        )
                        break  # Only report once per function

                    # Flag division (potential ZeroDivisionError)
                    if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Div):
                        issues.append(
                            Issue(
                                file_path=str(source_file),
                                line_number=child.lineno or 0,
                                column_number=child.col_offset or 0,
                                rule_id="untested-division",
                                rule_name="Potential division by zero",
                                message="Division operation without zero-check - add edge case test",
                                severity=Severity.INFO,
                                source=IssueSource.COVERAGE,
                                recommendation="Add test case for divisor equals zero",
                            )
                        )
                        break  # Only report once per function

        return issues
