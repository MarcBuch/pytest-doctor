"""Data models for analysis results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Severity levels for issues."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class IssueSource(str, Enum):
    """Source of the issue."""

    LINTING = "linting"
    DEAD_CODE = "dead_code"
    TEST_QUALITY = "test_quality"
    COVERAGE = "coverage"
    MUTATION_TESTING = "mutation_testing"


@dataclass
class Issue:
    """Represents a single issue found during analysis."""

    file_path: str
    line_number: int
    column_number: int = 0
    rule_id: str = ""
    rule_name: str = ""
    message: str = ""
    severity: Severity = Severity.WARNING
    source: IssueSource = IssueSource.LINTING
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source.value,
            "recommendation": self.recommendation,
        }


@dataclass
class AnalysisResult:
    """Results from a single analysis engine."""

    engine: str
    issues: list[Issue] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "engine": self.engine,
            "issues": [issue.to_dict() for issue in self.issues],
            "duration_ms": self.duration_ms,
        }


@dataclass
class Mutation:
    """Represents a single mutation from mutation testing."""

    id: str
    source_location: str
    mutation_type: str
    killed: bool
    failing_tests: list[str] = field(default_factory=list)


@dataclass
class MutationStats:
    """Statistics from mutation testing."""

    total_mutations: int
    killed_count: int
    survival_rate: float
    time_ms: int


@dataclass
class DiagnosticReport:
    """Complete diagnostic report from all analysis engines."""

    path: str
    score: int
    results: list[AnalysisResult] = field(default_factory=list)
    summary: dict[str, int | float] = field(
        default_factory=lambda: {"critical": 0, "warning": 0, "info": 0}
    )
    total_issues: int = 0
    mutation_survival_rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "path": self.path,
            "score": self.score,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
            "total_issues": self.total_issues,
        }
        if self.mutation_survival_rate is not None:
            result["mutation_survival_rate"] = self.mutation_survival_rate
        return result
