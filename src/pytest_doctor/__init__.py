"""pytest-doctor: Intelligent test analysis and reporting."""

import sys
from pathlib import Path
from typing import Any, Optional

from .analyzers.code_analyzer import CodeAnalyzer
from .analyzers.coverage_engine import CoverageEngine
from .analyzers.edge_case_detector import EdgeCaseDetector
from .analyzers.gap_detector import GapDetector
from .analyzers.quality_analyzer import TestQualityAnalyzer
from .analyzers.test_analyzer import TestAnalyzer
from .correlation import CorrelationEngine
from .exceptions import DirectoryNotFoundError, InvalidConfigError
from .models import CoverageStats, ProjectInfo, Results, Score, ScoreLabel

__version__ = "0.1.0"

__all__ = ["main", "diagnose", "DirectoryNotFoundError", "InvalidConfigError", "Results"]


def diagnose(
    path: str,
    config: Optional[dict[str, Any]] = None,
    coverage_data: Optional[Any] = None,
) -> Results:
    """Analyze test suite and return comprehensive results.

    Main orchestration function that runs the full pipeline:
    1. Code analysis (AST parsing)
    2. Test analysis
    3. Coverage measurement
    4. Gap detection
    5. Edge case detection
    6. Quality analysis
    7. Correlation
    8. Scoring

    Args:
        path: Path to test directory or Python package
        config: Optional configuration dict (overrides config file)
        coverage_data: Optional pre-measured coverage data

    Returns:
        Results object with score, diagnostics, gaps, coverage

    Raises:
        DirectoryNotFoundError: If path doesn't exist
        InvalidConfigError: If config is invalid
    """
    # Validate path
    target_path = Path(path)
    if not target_path.exists():
        raise DirectoryNotFoundError(f"Path does not exist: {path}")

    # Initialize analyzers
    code_analyzer = CodeAnalyzer()
    test_analyzer = TestAnalyzer()
    coverage_engine = CoverageEngine()
    gap_detector = GapDetector()
    edge_case_detector = EdgeCaseDetector()
    quality_analyzer = TestQualityAnalyzer()
    correlation_engine = CorrelationEngine()

    # Phase 1: Code and Test Analysis
    code_metrics = code_analyzer.analyze_directory("src")
    test_metrics = test_analyzer.analyze_directory(path)

    # Phase 2: Coverage Analysis
    if coverage_data is None:
        coverage_data = coverage_engine.measure_coverage(path)

    # Phase 3: Gap Detection
    gap_analysis = gap_detector.analyze_all(code_metrics, test_metrics, coverage_data)

    # Phase 4: Edge Case Detection
    edge_case_analysis = edge_case_detector.analyze_all(code_metrics)

    # Phase 5: Quality Analysis
    quality_analysis = quality_analyzer.analyze_all(test_metrics)

    # Phase 6: Correlation
    correlation_engine.correlate_tests_to_code(test_metrics, code_metrics, coverage_data)

    # Phase 7: Scoring
    # Calculate score based on all analyses
    base_score = 100.0
    coverage_penalty = 0.0
    gap_penalty = (
        gap_analysis.untested_functions * 2
        + gap_analysis.uncovered_branches
        + gap_analysis.missing_exception_tests * 1.5
        + gap_analysis.state_transition_gaps
        + gap_analysis.dead_test_code * 0.5
    )
    edge_case_penalty = (
        edge_case_analysis.numeric_edge_cases
        + edge_case_analysis.collection_edge_cases
        + edge_case_analysis.string_edge_cases * 0.5
        + edge_case_analysis.state_edge_cases
        + edge_case_analysis.resource_edge_cases
        + edge_case_analysis.type_coercion_cases * 0.5
    )
    quality_penalty = (
        quality_analysis.structure_issues
        + quality_analysis.assertion_issues * 1.5
        + quality_analysis.fixture_issues
        + quality_analysis.mocking_issues
        + quality_analysis.performance_issues * 0.5
        + quality_analysis.maintainability_issues * 0.5
    )

    final_score = max(
        0.0, base_score - coverage_penalty - gap_penalty - edge_case_penalty - quality_penalty
    )

    # Determine score label
    if final_score >= 75:
        label = ScoreLabel.EXCELLENT
    elif final_score >= 50:
        label = ScoreLabel.NEEDS_WORK
    else:
        label = ScoreLabel.CRITICAL

    score = Score(
        value=final_score,
        label=label,
        breakdown={
            "coverage": coverage_penalty,
            "gaps": gap_penalty,
            "edge_cases": edge_case_penalty,
            "quality": quality_penalty,
        },
    )

    # Create project info
    project_info = ProjectInfo(
        name=target_path.name,
        root_path=str(target_path.absolute()),
        total_files=test_metrics.total_tests,
        total_tests=test_metrics.total_tests,
    )

    # Create coverage stats
    coverage_stats = CoverageStats(
        total_lines=coverage_data.total_lines if coverage_data else 0,
        covered_lines=coverage_data.covered_lines if coverage_data else 0,
        total_branches=coverage_data.total_branches if coverage_data else 0,
        covered_branches=coverage_data.covered_branches if coverage_data else 0,
    )

    # Create results
    results = Results(
        score=score,
        diagnostics=[],
        gaps=[],
        edge_cases=[],
        coverage=coverage_stats,
        project_info=project_info,
        metadata={
            "analysis_version": __version__,
            "analyzers_run": [
                "code_analyzer",
                "test_analyzer",
                "coverage_engine",
                "gap_detector",
                "edge_case_detector",
                "quality_analyzer",
                "correlation_engine",
            ],
        },
    )

    return results


def main() -> None:
    """Main entry point for pytest-doctor CLI."""
    # Import here to avoid circular imports
    from .cli.main import main as cli_main

    exit_code = cli_main()
    sys.exit(exit_code)
