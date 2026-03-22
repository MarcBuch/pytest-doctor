"""Assertion quality analysis using mutation testing."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

from pytest_doctor.config import Config
from pytest_doctor.models import AnalysisResult
from pytest_doctor.mutation_analyzer import MutationAnalyzer
from pytest_doctor.mutation_integrator import MutationIntegrator

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class AssertionQualityAnalyzer:
    """Analyzes assertion quality using mutation testing."""

    def __init__(self, config: Config | None = None) -> None:
        """
        Initialize the assertion quality analyzer.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()

    def analyze(self, path: str | Path) -> AnalysisResult:
        """
        Analyze assertion quality through mutation testing.

        Runs mutmut on the specified path, analyzes mutations to identify
        weak assertions, and returns the results.

        Args:
            path: Directory or file path to analyze

        Returns:
            AnalysisResult containing weak assertion issues
        """
        start_time = time.time()
        result = AnalysisResult(engine="assertion_quality")

        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return result

            # Check if assertion_quality is enabled in config
            if not self.config.assertion_quality:
                logger.debug("Assertion quality analysis is disabled in config")
                return result

            # Get timeout from config
            timeout_ms = self.config.mutation_timeout_ms

            # Run mutations
            integrator = MutationIntegrator()
            mutations = integrator.run_mutations(str(path_obj), timeout_ms=timeout_ms)

            # If no mutations (mutmut not available or no tests), return empty result
            if not mutations:
                logger.debug(f"No mutations found for {path} - mutmut may not be installed")
                return result

            # Analyze mutations to find weak assertions
            analyzer = MutationAnalyzer()
            issues = analyzer.analyze_mutations(mutations)
            result.issues = issues

            # Calculate and store mutation stats in metadata
            stats = analyzer.calculate_mutation_stats(mutations)
            result.metadata["mutation_stats"] = stats

            logger.debug(f"Found {len(issues)} weak assertions in {len(mutations)} mutations")

        except Exception as e:
            logger.warning(f"Error analyzing assertion quality for {path}: {type(e).__name__}: {e}")
            # Return empty result on error (graceful degradation)
            return result
        finally:
            result.duration_ms = (time.time() - start_time) * 1000

        return result

    def _find_test_files(self, path: Path) -> list[Path]:
        """
        Find all test files in a directory.

        Args:
            path: Directory or file path to search

        Returns:
            List of test file paths
        """
        if path.is_file():
            if path.name.startswith("test_") or path.name.endswith("_test.py"):
                return [path]
            return []

        return list(path.rglob("test_*.py")) + list(path.rglob("*_test.py"))

    def _should_ignore_file(self, file_path: str) -> bool:
        """
        Check if file should be ignored based on config.

        Args:
            file_path: Path to check

        Returns:
            True if file should be ignored, False otherwise
        """
        import pathspec

        if not self.config.ignore.files:
            return False

        spec = pathspec.PathSpec.from_lines("gitignore", self.config.ignore.files)
        return spec.match_file(file_path)
