"""Performance tests for mutation testing."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pytest_doctor.config import Config
from pytest_doctor.mutation_analyzer import MutationAnalyzer
from pytest_doctor.mutation_integrator import MutationIntegrator
from pytest_doctor.analyzers.assertion_quality_analyzer import (
    AssertionQualityAnalyzer,
)
from tests.fixtures.sample_mutations import create_sample_mutations


class TestMutationPerformance:
    """Performance tests for mutation analysis."""

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_mutation_integrator_performance(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test that mutation integrator runs within performance budget."""
        # Create mock output with many mutations
        mutations = []
        statuses = ["KILLED", "SURVIVED"]
        for i in range(100):
            mutations.append(
                f"""{{
                    "id": "{i}",
                    "filename": "src/test_{i % 10}.py",
                    "line_number": {10 + i},
                    "mutation_type": "test_mutation_{i}",
                    "status": "{statuses[i % 2]}"
                }}"""
            )

        mock_output = '{"results": [' + ",".join(mutations) + "]}"

        mock_process = MagicMock()
        mock_process.stdout = mock_output
        mock_run.return_value = mock_process

        # Time the parsing
        integrator = MutationIntegrator()
        start = time.time()
        result = integrator._parse_mutmut_output(mock_output)
        elapsed = time.time() - start

        # Should parse 100 mutations in < 100ms
        assert elapsed < 0.1
        assert len(result) == 100

    def test_mutation_analyzer_performance(self) -> None:
        """Test that mutation analyzer is fast even with many mutations."""
        mutations = create_sample_mutations()

        # Create a larger set
        large_mutations = mutations * 20  # 100 mutations

        analyzer = MutationAnalyzer()

        start = time.time()
        issues = analyzer.analyze_mutations(large_mutations)
        elapsed = time.time() - start

        # Should analyze 100 mutations in < 10ms
        assert elapsed < 0.01
        assert len(issues) == 60  # 3 survived * 20

    def test_mutation_stats_calculation_performance(self) -> None:
        """Test that stats calculation is fast."""
        mutations = create_sample_mutations() * 100  # 500 mutations

        analyzer = MutationAnalyzer()

        start = time.time()
        stats = analyzer.calculate_mutation_stats(mutations)
        elapsed = time.time() - start

        # Should calculate stats in < 5ms
        assert elapsed < 0.005
        assert stats.total_mutations == 500

    @patch("pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator")
    def test_assertion_quality_analyzer_performance(
        self, mock_integrator_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test that assertion quality analyzer completes in reasonable time."""
        mock_integrator = MagicMock()
        mock_integrator_class.return_value = mock_integrator

        # Return a moderate number of mutations
        mock_integrator.run_mutations.return_value = create_sample_mutations()

        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")

        start = time.time()
        result = analyzer.analyze(str(tmp_path))
        elapsed = time.time() - start

        # Should complete in < 100ms (including overhead)
        assert elapsed < 0.1
        assert result.engine == "assertion_quality"

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_mutation_timeout_prevents_slow_analysis(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Test that mutation timeout prevents runaway analysis."""
        from subprocess import TimeoutExpired

        # Create a mock that simulates slow mutmut
        def slow_mutmut(*args, **kwargs):
            time.sleep(0.5)  # Simulate slow mutmut
            raise TimeoutExpired("mutmut", timeout=kwargs.get("timeout", 10))

        mock_run.side_effect = slow_mutmut

        integrator = MutationIntegrator()

        start = time.time()
        result = integrator.run_mutations(str(tmp_path), timeout_ms=1000)
        elapsed = time.time() - start

        # Should timeout and return quickly (before full 5s timeout)
        assert elapsed < 2.0
        assert result == []


class TestMutationTimeoutConfiguration:
    """Tests for mutation timeout configuration."""

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_custom_timeout_passed_to_subprocess(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test that custom timeout is passed to subprocess."""
        mock_process = MagicMock()
        mock_process.stdout = "[]"
        mock_run.return_value = mock_process

        integrator = MutationIntegrator()
        integrator.run_mutations(str(tmp_path), timeout_ms=10000)

        # Verify timeout was passed correctly (10000ms = 10s)
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 10.0

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_default_timeout_is_300_seconds(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test that default timeout is 300 seconds."""
        mock_process = MagicMock()
        mock_process.stdout = "[]"
        mock_run.return_value = mock_process

        integrator = MutationIntegrator()
        integrator.run_mutations(str(tmp_path))  # No timeout specified

        # Verify default timeout is 300s (300000ms)
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 300.0

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_timeout_configuration_from_config(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test that timeout is configurable via Config."""
        mock_process = MagicMock()
        mock_process.stdout = "[]"
        mock_run.return_value = mock_process

        config = Config(assertion_quality=True, mutation_timeout_ms=30000)
        analyzer = AssertionQualityAnalyzer(config)
        analyzer.analyze(str(tmp_path))

        # Verify custom timeout was used
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 30.0


@pytest.mark.performance
class TestLargeScalePerformance:
    """Large scale performance tests."""

    def test_mutation_analyzer_with_1000_mutations(self) -> None:
        """Test mutation analyzer with 1000 mutations."""
        from tests.fixtures.sample_mutations import create_sample_mutations

        # Create 1000 mutations (50x sample set)
        mutations = create_sample_mutations() * 50
        assert len(mutations) == 250  # 5 per sample * 50

        # Extend to 1000
        for i in range(250, 1000):
            from pytest_doctor.models import Mutation

            mutations.append(
                Mutation(
                    id=str(i),
                    source_location=f"file_{i % 10}.py:{i}",
                    mutation_type=f"mutation_{i % 5}",
                    killed=(i % 3) == 0,
                    failing_tests=[],
                )
            )

        analyzer = MutationAnalyzer()

        start = time.time()
        issues = analyzer.analyze_mutations(mutations)
        stats = analyzer.calculate_mutation_stats(mutations)
        elapsed = time.time() - start

        # Should handle 1000 mutations in < 50ms
        assert elapsed < 0.05
        assert stats.total_mutations == 1000
        # About 2/3 should survive (not killed)
        assert 600 < len(issues) < 700

    def test_concurrent_mutation_analysis_performance(self) -> None:
        """Test performance of concurrent mutation analysis."""
        from typing import Callable
        from pytest_doctor.parallel import run_analyses_parallel
        from pytest_doctor.models import AnalysisResult

        def slow_analysis() -> AnalysisResult | None:
            time.sleep(0.1)
            return None

        # Create 10 slow analyses
        functions: list[tuple[Callable[[], AnalysisResult | None], str]] = [
            (slow_analysis, f"slow_{i}") for i in range(10)
        ]

        start = time.time()
        results = run_analyses_parallel(functions, max_workers=4)
        elapsed = time.time() - start

        # With 4 workers, 10 tasks at 0.1s each should take ~0.3s, not 1.0s
        assert elapsed < 0.5
        assert len(results) == 0  # All return None
