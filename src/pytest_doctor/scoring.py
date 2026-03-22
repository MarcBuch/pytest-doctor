"""Health score calculation for pytest-doctor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pytest_doctor.models import AnalysisResult, Severity


@dataclass
class ScoreWeights:
    """Weights for different scoring components."""

    code_quality: float = 0.30
    coverage_gaps: float = 0.30
    assertion_quality: float = 0.20
    test_isolation: float = 0.20

    def __post_init__(self) -> None:
        """Validate that weights sum to 1.0."""
        total = (
            self.code_quality + self.coverage_gaps + self.assertion_quality + self.test_isolation
        )
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
            weights: Optional custom weights for different components
        """
        self.weights = weights or ScoreWeights()

    def calculate_score(self, results: list[AnalysisResult]) -> int:
        """
        Calculate overall health score from analysis results.

        Score ranges from 0-100, with:
        - Critical: <50
        - Needs work: 50-74
        - Good: 75+

        New scoring composition:
        - Code quality (linting, dead code): 30%
        - Coverage gaps: 30%
        - Assertion quality (mutation): 20%
        - Test isolation (fixtures): 20%

        Args:
            results: List of AnalysisResult from all analysis engines

        Returns:
            Health score between 0-100
        """
        if not results:
            return 100

        # Calculate component scores
        code_quality_score = self._calculate_code_quality_score(results)
        coverage_score = self._calculate_coverage_score(results)
        assertion_score = self._calculate_assertion_quality_score(results)
        isolation_score = self._calculate_isolation_score(results)

        # Combine scores with weights
        final_score = (
            (code_quality_score * self.weights.code_quality)
            + (coverage_score * self.weights.coverage_gaps)
            + (assertion_score * self.weights.assertion_quality)
            + (isolation_score * self.weights.test_isolation)
        )

        # Ensure score stays within 0-100 range
        return max(0, min(100, int(final_score)))

    def _calculate_code_quality_score(self, results: list[AnalysisResult]) -> float:
        """
        Calculate code quality score from linting and dead code engines.

        Returns a score from 0-100 where 100 is perfect.
        """
        quality_results = [r for r in results if self._is_quality_engine(r.engine)]

        if not quality_results:
            return 100.0

        # Calculate penalty from issues
        total_penalty = 0.0
        for result in quality_results:
            penalty = self._calculate_engine_penalty(result)
            total_penalty += penalty

        # Average penalty across quality engines
        avg_penalty = total_penalty / len(quality_results)

        # Convert penalty to score (0-100)
        return 100.0 - avg_penalty

    def _calculate_coverage_score(self, results: list[AnalysisResult]) -> float:
        """
        Calculate coverage score from gap analyzer.

        Returns a score from 0-100 where 100 is perfect.
        """
        gap_results = [r for r in results if "gap" in r.engine.lower()]

        if not gap_results:
            return 100.0

        # Calculate penalty from issues
        total_penalty = 0.0
        for result in gap_results:
            penalty = self._calculate_engine_penalty(result)
            total_penalty += penalty

        # Average penalty across gap engines
        avg_penalty = total_penalty / len(gap_results)

        # Convert penalty to score (0-100)
        return 100.0 - avg_penalty

    def _calculate_assertion_quality_score(self, results: list[AnalysisResult]) -> float:
        """
        Calculate assertion quality score from mutation testing.

        If mutation testing ran, score is (1 - survival_rate) * 100.
        If mutation testing didn't run, return neutral score of 50.

        Returns a score from 0-100 where 100 is perfect.
        """
        assertion_results = [r for r in results if "assertion" in r.engine.lower()]

        if not assertion_results:
            return 50.0  # Neutral score if no mutation data

        # Extract mutation stats if available
        for result in assertion_results:
            if "mutation_stats" in result.metadata:
                stats = result.metadata["mutation_stats"]
                survival_rate: float = stats.survival_rate
                # Lower survival rate = higher score (stronger assertions)
                return (1.0 - survival_rate) * 100.0

        # If no stats but engine ran, calculate from issues
        total_penalty = 0.0
        for result in assertion_results:
            penalty = self._calculate_engine_penalty(result)
            total_penalty += penalty

        avg_penalty = total_penalty / len(assertion_results)
        return 100.0 - avg_penalty

    def _calculate_isolation_score(self, results: list[AnalysisResult]) -> float:
        """
        Calculate test isolation score from quality analyzer.

        Returns a score from 0-100 where 100 is perfect.
        """
        quality_results = [r for r in results if "quality" in r.engine.lower()]

        if not quality_results:
            return 100.0

        # Calculate penalty from issues
        total_penalty = 0.0
        for result in quality_results:
            penalty = self._calculate_engine_penalty(result)
            total_penalty += penalty

        # Average penalty across quality engines
        avg_penalty = total_penalty / len(quality_results)

        # Convert penalty to score (0-100)
        return 100.0 - avg_penalty

    def _is_quality_engine(self, engine: str) -> bool:
        """Check if engine is code quality related (linting/dead code)."""
        engine_lower = engine.lower()
        return ("ruff" in engine_lower or "lint" in engine_lower) or (
            "vulture" in engine_lower or "dead" in engine_lower
        )

    def _calculate_engine_penalty(self, result: AnalysisResult) -> float:
        """
        Calculate penalty (0-100) for a single engine result.

        Returns 0 for no issues, 100 for severe issues.
        """
        if not result.issues:
            return 0.0

        total_points = 0.0
        for issue in result.issues:
            severity_points = self.SEVERITY_POINTS.get(issue.severity, 1)
            total_points += severity_points

        # Normalize to 0-100 scale
        # More than 20 critical issues would be 200+ points, capped at 100
        return min(100.0, total_points)

    def categorize_score(self, score: int) -> str:
        """Categorize a health score."""
        if score < 50:
            return "critical"
        elif score < 75:
            return "needs_work"
        else:
            return "good"
