"""Tests for parallel execution utilities."""

import time
from typing import Callable

from pytest_doctor.models import AnalysisResult
from pytest_doctor.parallel import run_analyses_parallel, run_analyses_sequential


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
