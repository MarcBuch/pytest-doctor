"""Health score calculation for pytest-doctor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pytest_doctor.models import AnalysisResult, Severity


@dataclass
class ScoreWeights:
    """Weights for different issue types in scoring."""

    linting: float = 0.25
    dead_code: float = 0.25
    test_quality: float = 0.3
    coverage: float = 0.2

    def __post_init__(self) -> None:
        """Validate that weights sum to 1.0."""
        total = self.linting + self.dead_code + self.test_quality + self.coverage
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


class HealthScorer:
    """Calculates health score from analysis results."""

    # Score impact for different severity levels
    SEVERITY_POINTS: ClassVar[dict[Severity, int]] = {
        Severity.CRITICAL: 10,
        Severity.WARNING: 5,
        Severity.INFO: 1,
    }

    def __init__(self, weights: ScoreWeights | None = None) -> None:
        """
        Initialize the health scorer.

        Args:
            weights: Optional custom weights for different issue types
        """
        self.weights = weights or ScoreWeights()

    def calculate_score(self, results: list[AnalysisResult]) -> int:
        """
        Calculate overall health score from analysis results.

        Score ranges from 0-100, with:
        - Critical: <50
        - Needs work: 50-74
        - Good: 75+

        Args:
            results: List of AnalysisResult from all analysis engines

        Returns:
            Health score between 0-100
        """
        if not results:
            return 100

        # Calculate weighted score based on results
        total_score = 100.0

        for result in results:
            if not result.issues:
                continue

            # Get weight for this engine
            weight = self._get_weight_for_engine(result.engine)

            # Calculate points deducted for this engine
            points_deducted = self._calculate_points_deducted(result)

            # Apply weight and deduct from total
            weighted_deduction = points_deducted * weight
            total_score -= weighted_deduction

        # Ensure score stays within 0-100 range
        return max(0, min(100, int(total_score)))

    def _get_weight_for_engine(self, engine: str) -> float:
        """Get the weight for an analysis engine."""
        engine_lower = engine.lower()

        if "ruff" in engine_lower or "lint" in engine_lower:
            return self.weights.linting
        elif "vulture" in engine_lower or "dead" in engine_lower:
            return self.weights.dead_code
        elif "quality" in engine_lower or "test" in engine_lower:
            return self.weights.test_quality
        elif "coverage" in engine_lower:
            return self.weights.coverage

        # Default weight for unknown engines
        return 0.2

    def _calculate_points_deducted(self, result: AnalysisResult) -> float:
        """Calculate points deducted for an analysis result."""
        total_points = 0.0

        for issue in result.issues:
            severity_points = self.SEVERITY_POINTS.get(issue.severity, 1)
            total_points += severity_points

        # Normalize to 0-100 scale (max 100 points per engine)
        # More than 20 critical issues would be 200+ points
        return min(100.0, total_points)

    def categorize_score(self, score: int) -> str:
        """Categorize a health score."""
        if score < 50:
            return "critical"
        elif score < 75:
            return "needs_work"
        else:
            return "good"
