"""Parallel execution utilities for analysis engines."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from pytest_doctor.models import AnalysisResult


def run_analyses_parallel(
    analysis_functions: list[tuple[Callable[[], AnalysisResult | None], str]],
    max_workers: int = 4,
) -> list[AnalysisResult]:
    """
    Run analysis functions in parallel using a thread pool.

    Args:
        analysis_functions: List of (callable, name) tuples where callable returns
                          AnalysisResult or None. The name is for tracking which
                          analysis completed.
        max_workers: Maximum number of worker threads (default: 4)

    Returns:
        List of non-None AnalysisResult objects, in order of completion
    """
    results: list[AnalysisResult] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_name = {executor.submit(func): name for func, name in analysis_functions}

        # Collect results as they complete
        for future in as_completed(future_to_name):
            result = future.result()
            if result is not None:
                results.append(result)

    return results


def run_analyses_sequential(
    analysis_functions: list[tuple[Callable[[], AnalysisResult | None], str]],
) -> list[AnalysisResult]:
    """
    Run analysis functions sequentially.

    Args:
        analysis_functions: List of (callable, name) tuples where callable returns
                          AnalysisResult or None.

    Returns:
        List of non-None AnalysisResult objects
    """
    results: list[AnalysisResult] = []

    for func, _name in analysis_functions:
        result = func()
        if result is not None:
            results.append(result)

    return results


def benchmark_parallel_vs_sequential(
    analysis_functions: list[tuple[Callable[[], AnalysisResult | None], str]],
) -> tuple[float, float]:
    """
    Benchmark parallel vs sequential execution.

    Args:
        analysis_functions: List of (callable, name) tuples

    Returns:
        Tuple of (parallel_time_ms, sequential_time_ms)
    """
    # Benchmark parallel
    start = time.time()
    run_analyses_parallel(analysis_functions)
    parallel_time = (time.time() - start) * 1000

    # Benchmark sequential
    start = time.time()
    run_analyses_sequential(analysis_functions)
    sequential_time = (time.time() - start) * 1000

    return parallel_time, sequential_time
