"""Tests for parallel execution utilities."""

import time
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest

from pytest_doctor.models import AnalysisResult
from pytest_doctor.parallel import run_analyses_parallel, run_analyses_sequential
from pytest_doctor.analyzers.assertion_quality_analyzer import (
    AssertionQualityAnalyzer,
)
from pytest_doctor.config import Config


def slow_analysis_1() -> AnalysisResult:
    """Simulate a slow analysis."""
    time.sleep(0.2)
    return AnalysisResult(engine="slow1")


def slow_analysis_2() -> AnalysisResult:
    """Simulate another slow analysis."""
    time.sleep(0.2)
    return AnalysisResult(engine="slow2")


def slow_analysis_3() -> AnalysisResult:
    """Simulate a third slow analysis."""
    time.sleep(0.2)
    return AnalysisResult(engine="slow3")


def fast_analysis() -> AnalysisResult:
    """Simulate a fast analysis."""
    return AnalysisResult(engine="fast")


def none_analysis() -> None:
    """Simulate an analysis that returns None."""
    return None


class TestRunAnalysesParallel:
    """Tests for run_analyses_parallel function."""

    def test_parallel_execution_basic(self) -> None:
        """Test basic parallel execution."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (slow_analysis_1, "slow1"),
            (slow_analysis_2, "slow2"),
        ]
        results = run_analyses_parallel(functions)
        assert len(results) == 2
        assert all(isinstance(r, AnalysisResult) for r in results)

    def test_parallel_execution_multiple(self) -> None:
        """Test parallel execution with multiple analyses."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (slow_analysis_1, "slow1"),
            (slow_analysis_2, "slow2"),
            (slow_analysis_3, "slow3"),
        ]
        results = run_analyses_parallel(functions)
        assert len(results) == 3

    def test_parallel_execution_with_none(self) -> None:
        """Test that None results are filtered out."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (slow_analysis_1, "slow1"),
            (none_analysis, "none"),
            (slow_analysis_2, "slow2"),
        ]
        results = run_analyses_parallel(functions)
        assert len(results) == 2
        assert all(r is not None for r in results)

    def test_parallel_execution_single(self) -> None:
        """Test parallel execution with single analysis."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (fast_analysis, "fast"),
        ]
        results = run_analyses_parallel(functions)
        assert len(results) == 1
        assert results[0].engine == "fast"

    def test_parallel_execution_empty(self) -> None:
        """Test parallel execution with empty function list."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = []
        results = run_analyses_parallel(functions)
        assert len(results) == 0

    def test_parallel_execution_custom_workers(self) -> None:
        """Test parallel execution with custom worker count."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (fast_analysis, "fast1"),
            (fast_analysis, "fast2"),
            (fast_analysis, "fast3"),
        ]
        results = run_analyses_parallel(functions, max_workers=2)
        assert len(results) == 3

    def test_parallel_execution_is_concurrent(self) -> None:
        """Test that parallel execution is actually concurrent."""
        # Three slow analyses should take ~0.2s in parallel, not 0.6s
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (slow_analysis_1, "slow1"),
            (slow_analysis_2, "slow2"),
            (slow_analysis_3, "slow3"),
        ]
        start = time.time()
        results = run_analyses_parallel(functions)
        elapsed = time.time() - start

        assert len(results) == 3
        # Should be faster than sequential (0.6s), allow 0.5s as a reasonable threshold
        # Adding some buffer for overhead
        assert elapsed < 0.5, f"Parallel execution took {elapsed}s, should be <0.5s"


class TestRunAnalysesSequential:
    """Tests for run_analyses_sequential function."""

    def test_sequential_execution_basic(self) -> None:
        """Test basic sequential execution."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (fast_analysis, "fast1"),
            (fast_analysis, "fast2"),
        ]
        results = run_analyses_sequential(functions)
        assert len(results) == 2

    def test_sequential_execution_with_none(self) -> None:
        """Test that None results are filtered out."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (fast_analysis, "fast1"),
            (none_analysis, "none"),
            (fast_analysis, "fast2"),
        ]
        results = run_analyses_sequential(functions)
        assert len(results) == 2

    def test_sequential_execution_order(self) -> None:
        """Test that results are in execution order."""

        def analysis_a() -> AnalysisResult:
            return AnalysisResult(engine="a")

        def analysis_b() -> AnalysisResult:
            return AnalysisResult(engine="b")

        def analysis_c() -> AnalysisResult:
            return AnalysisResult(engine="c")

        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (analysis_a, "a"),
            (analysis_b, "b"),
            (analysis_c, "c"),
        ]
        results = run_analyses_sequential(functions)
        assert len(results) == 3
        assert results[0].engine == "a"
        assert results[1].engine == "b"
        assert results[2].engine == "c"

    def test_sequential_execution_empty(self) -> None:
        """Test sequential execution with empty function list."""
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = []
        results = run_analyses_sequential(functions)
        assert len(results) == 0


class TestAssertionQualityAnalyzerIntegration:
    """Tests for AssertionQualityAnalyzer in parallel execution."""

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_assertion_quality_in_parallel(
        self, mock_integrator_class: MagicMock, tmp_path
    ) -> None:
        """Test that AssertionQualityAnalyzer can be included in parallel execution."""
        # Mock the integrator
        mock_integrator = MagicMock()
        mock_integrator_class.return_value = mock_integrator
        mock_integrator.run_mutations.return_value = []

        # Create analyzer with mutation enabled
        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)

        # Create a function that uses the analyzer
        def analyze_assertions() -> AnalysisResult:
            return analyzer.analyze(str(tmp_path))

        # Include in parallel execution
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (fast_analysis, "fast"),
            (analyze_assertions, "assertions"),
            (slow_analysis_1, "slow"),
        ]

        results = run_analyses_parallel(functions, max_workers=3)

        # Should get results from all three
        assert len(results) == 3
        engines = {r.engine for r in results}
        assert "assertion_quality" in engines

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_assertion_quality_disabled_in_parallel(
        self, mock_integrator_class: MagicMock, tmp_path
    ) -> None:
        """Test that disabled assertion quality returns empty result."""
        config = Config(assertion_quality=False)
        analyzer = AssertionQualityAnalyzer(config)

        def analyze_assertions() -> AnalysisResult:
            return analyzer.analyze(str(tmp_path))

        results = run_analyses_parallel(
            [(analyze_assertions, "assertions"), (fast_analysis, "fast")]
        )

        assert len(results) == 2
        assertions_result = next(r for r in results if r.engine == "assertion_quality")
        assert len(assertions_result.issues) == 0

    def test_mutation_analyzer_doesnt_block_others(self, tmp_path) -> None:
        """Test that slow mutation analysis doesn't block other analyzers."""

        def slow_mutation_analyzer() -> AnalysisResult:
            time.sleep(0.2)
            return AnalysisResult(engine="slow_mutations")

        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (slow_mutation_analyzer, "mutations"),
            (fast_analysis, "fast1"),
            (fast_analysis, "fast2"),
        ]

        start = time.time()
        results = run_analyses_parallel(functions, max_workers=3)
        elapsed = time.time() - start

        # With parallel execution, should complete around 0.2s
        # not 0.2 + (2 * fast_analysis time)
        assert len(results) == 3
        assert elapsed < 0.4
