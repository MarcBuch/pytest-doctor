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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "engine": self.engine,
            "issues": [issue.to_dict() for issue in self.issues],
            "duration_ms": self.duration_ms,
        }


@dataclass
class DiagnosticReport:
    """Complete diagnostic report from all analysis engines."""

    path: str
    score: int
    results: list[AnalysisResult] = field(default_factory=list)
    summary: dict[str, int] = field(
        default_factory=lambda: {"critical": 0, "warning": 0, "info": 0}
    )
    total_issues: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "score": self.score,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
            "total_issues": self.total_issues,
        }
