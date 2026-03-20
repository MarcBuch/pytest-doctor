"""Core data contracts and result models for pytest-doctor.

This module defines all shared dataclasses/types that analyzers and reporters use.
"""

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    """Diagnostic severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class DiagnosticType(str, Enum):
    """Types of diagnostic findings."""

    GAP = "gap"
    QUALITY = "quality"
    COVERAGE = "coverage"


class GapCategory(str, Enum):
    """Categories of gaps in test coverage."""

    UNTESTED_FUNCTIONS = "untested-functions"
    UNCOVERED_BRANCHES = "uncovered-branches"
    MISSING_EXCEPTION_TESTS = "missing-exception-tests"
    STATE_TRANSITION_GAPS = "state-transition-gaps"
    DEAD_TEST_CODE = "dead-test-code"


class EdgeCaseCategory(str, Enum):
    """Categories of missing edge cases."""

    BOUNDARY_VALUE = "boundary-value"
    EMPTY_INPUT = "empty-input"
    SPECIAL_CHARACTERS = "special-characters"
    RESOURCE_LIMITS = "resource-limits"
    STATE_TRANSITIONS = "state-transitions"
    TYPE_COERCION = "type-coercion"


class ScoreLabel(str, Enum):
    """Score health status labels."""

    EXCELLENT = "Excellent"
    NEEDS_WORK = "Needs Work"
    CRITICAL = "Critical"


@dataclass
class Location:
    """Source code location."""

    file: str
    line: int
    column: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class Diagnostic:
    """Single diagnostic finding."""

    type: DiagnosticType
    category: str
    file: str
    line: int
    column: int
    severity: Severity
    message: str
    help: str
    suggestion: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "category": self.category,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "message": self.message,
            "help": self.help,
            "suggestion": self.suggestion,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class SuggestedTest:
    """Suggestion for a test to address a gap."""

    description: str
    test_inputs: dict[str, Any] = field(default_factory=dict)
    expected_behavior: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "description": self.description,
            "test_inputs": self.test_inputs,
            "expected_behavior": self.expected_behavior,
        }


@dataclass
class Gap:
    """Represents a gap in test coverage."""

    category: GapCategory
    location: Location
    description: str
    severity: Severity
    test_suggestion: Optional[SuggestedTest] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "category": self.category.value,
            "location": self.location.to_dict(),
            "description": self.description,
            "severity": self.severity.value,
            "test_suggestion": (self.test_suggestion.to_dict() if self.test_suggestion else None),
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class EdgeCase:
    """Represents a missing edge case test."""

    category: EdgeCaseCategory
    description: str
    function_name: str
    function_file: str
    test_inputs: dict[str, Any] = field(default_factory=dict)
    expected_behavior: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "category": self.category.value,
            "description": self.description,
            "function_name": self.function_name,
            "function_file": self.function_file,
            "test_inputs": self.test_inputs,
            "expected_behavior": self.expected_behavior,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class CoverageStats:
    """Coverage statistics."""

    total_lines: int = 0
    covered_lines: int = 0
    total_branches: int = 0
    covered_branches: int = 0

    @property
    def line_coverage_percent(self) -> float:
        """Calculate line coverage percentage."""
        if self.total_lines == 0:
            return 0.0
        return (self.covered_lines / self.total_lines) * 100

    @property
    def branch_coverage_percent(self) -> float:
        """Calculate branch coverage percentage."""
        if self.total_branches == 0:
            return 0.0
        return (self.covered_branches / self.total_branches) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_lines": self.total_lines,
            "covered_lines": self.covered_lines,
            "line_coverage_percent": round(self.line_coverage_percent, 1),
            "total_branches": self.total_branches,
            "covered_branches": self.covered_branches,
            "branch_coverage_percent": round(self.branch_coverage_percent, 1),
        }


@dataclass
class Score:
    """Test quality health score."""

    value: float
    label: ScoreLabel
    breakdown: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure score is capped between 0 and 100."""
        self.value = max(0.0, min(100.0, self.value))

        # Determine label if not already set
        if not self.label:
            if self.value >= 75:
                self.label = ScoreLabel.EXCELLENT
            elif self.value >= 50:
                self.label = ScoreLabel.NEEDS_WORK
            else:
                self.label = ScoreLabel.CRITICAL

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "value": round(self.value, 1),
            "label": self.label.value,
            "breakdown": {k: round(v, 1) for k, v in self.breakdown.items()},
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class ProjectInfo:
    """Information about the analyzed project."""

    name: str = ""
    root_path: str = ""
    python_version: str = ""
    total_files: int = 0
    total_tests: int = 0
    analysis_time_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "root_path": self.root_path,
            "python_version": self.python_version,
            "total_files": self.total_files,
            "total_tests": self.total_tests,
            "analysis_time_seconds": round(self.analysis_time_seconds, 2),
        }


@dataclass
class Results:
    """Complete analysis results."""

    score: Score
    diagnostics: list[Diagnostic] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    edge_cases: list[EdgeCase] = field(default_factory=list)
    coverage: CoverageStats = field(default_factory=CoverageStats)
    project_info: ProjectInfo = field(default_factory=ProjectInfo)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "score": self.score.to_dict(),
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "gaps": [g.to_dict() for g in self.gaps],
            "edge_cases": [e.to_dict() for e in self.edge_cases],
            "coverage": self.coverage.to_dict(),
            "project_info": self.project_info.to_dict(),
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


__all__ = [
    "Severity",
    "DiagnosticType",
    "GapCategory",
    "EdgeCaseCategory",
    "ScoreLabel",
    "Location",
    "Diagnostic",
    "SuggestedTest",
    "Gap",
    "EdgeCase",
    "CoverageStats",
    "Score",
    "ProjectInfo",
    "Results",
]
