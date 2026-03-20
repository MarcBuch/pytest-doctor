"""Code analyzer module for pytest-doctor.

Analyzes Python source code using AST to extract structural information:
- Functions and their signatures
- Classes and inheritance
- Exception handling
- Control flow branches
- Code complexity metrics
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FunctionInfo:
    """Information about a function."""

    name: str
    file: str
    line: int
    is_async: bool = False
    decorators: list[str] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    complexity: int = 1


@dataclass
class ClassInfo:
    """Information about a class."""

    name: str
    file: str
    line: int
    bases: list[str] = field(default_factory=list)
    methods: list[FunctionInfo] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class ExceptionInfo:
    """Information about an exception."""

    exception_type: str
    file: str
    line: int
    function: Optional[str] = None


@dataclass
class BranchInfo:
    """Information about a control flow branch."""

    branch_type: str  # "if", "for", "while", "try"
    file: str
    line: int
    function: Optional[str] = None


@dataclass
class CodeMetrics:
    """Aggregated metrics from code analysis."""

    total_functions: int = 0
    total_classes: int = 0
    total_branches: int = 0
    total_exceptions: int = 0
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    exceptions: list[ExceptionInfo] = field(default_factory=list)
    branches: list[BranchInfo] = field(default_factory=list)
    avg_complexity: float = 0.0


class CodeAnalyzer:
    """Analyzes Python source code structure."""

    def __init__(self) -> None:
        """Initialize the code analyzer."""
        self.metrics = CodeMetrics()

    def analyze_directory(self, path: str) -> CodeMetrics:
        """Analyze a directory of Python files.

        Args:
            path: Path to directory containing Python source code

        Returns:
            CodeMetrics: Aggregated analysis results
        """
        # Placeholder implementation
        return self.metrics

    def analyze_file(self, file_path: str) -> CodeMetrics:
        """Analyze a single Python file.

        Args:
            file_path: Path to Python file

        Returns:
            CodeMetrics: Analysis results for the file
        """
        # Placeholder implementation
        return CodeMetrics()

    def extract_functions(self, file_path: str) -> list[FunctionInfo]:
        """Extract all functions from a file.

        Args:
            file_path: Path to Python file

        Returns:
            List of FunctionInfo objects
        """
        # Placeholder implementation
        return []

    def extract_classes(self, file_path: str) -> list[ClassInfo]:
        """Extract all classes from a file.

        Args:
            file_path: Path to Python file

        Returns:
            List of ClassInfo objects
        """
        # Placeholder implementation
        return []

    def extract_exceptions(self, file_path: str) -> list[ExceptionInfo]:
        """Extract all exceptions raised in a file.

        Args:
            file_path: Path to Python file

        Returns:
            List of ExceptionInfo objects
        """
        # Placeholder implementation
        return []

    def find_branches(self, file_path: str) -> list[BranchInfo]:
        """Find all control flow branches in a file.

        Args:
            file_path: Path to Python file

        Returns:
            List of BranchInfo objects
        """
        # Placeholder implementation
        return []

    def calculate_complexity(self, function_name: str, file_path: str) -> int:
        """Calculate cyclomatic complexity for a function.

        Args:
            function_name: Name of the function
            file_path: Path to Python file

        Returns:
            Cyclomatic complexity value
        """
        # Placeholder implementation
        return 1


__all__ = [
    "CodeAnalyzer",
    "CodeMetrics",
    "FunctionInfo",
    "ClassInfo",
    "ExceptionInfo",
    "BranchInfo",
]
