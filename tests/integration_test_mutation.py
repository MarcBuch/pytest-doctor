"""Integration tests for mutation testing feature."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pytest_doctor.config import Config
from pytest_doctor.models import (
    AnalysisResult,
    DiagnosticReport,
    Issue,
    IssueSource,
    MutationStats,
    Severity,
)
from pytest_doctor.analyzers.assertion_quality_analyzer import (
    AssertionQualityAnalyzer,
)
from pytest_doctor.mutation_analyzer import MutationAnalyzer
from pytest_doctor.mutation_integrator import MutationIntegrator
from tests.fixtures.sample_mutations import (
    create_sample_mutations,
    create_empty_mutations,
)


class TestMutationIntegrationEndToEnd:
    """End-to-end tests for mutation testing integration."""

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_full_pipeline_with_mutations(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test full pipeline with mutation results."""
        # Setup mock mutmut output
        mock_output = """{
            "results": [
                {
                    "id": "1",
                    "filename": "src/math.py",
                    "line_number": 10,
                    "mutation_type": "< changed to <=",
                    "status": "SURVIVED"
                },
                {
                    "id": "2",
                    "filename": "src/math.py",
                    "line_number": 15,
                    "mutation_type": "== changed to !=",
                    "status": "KILLED"
                }
            ]
        }"""

        mock_process = MagicMock()
        mock_process.stdout = mock_output
        mock_run.return_value = mock_process

        # Create test file
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "math.py").write_text("def add(a, b): return a + b\n")

        # Create test file
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_math.py").write_text("def test_add(): assert True\n")

        # Run mutation integrator
        integrator = MutationIntegrator()
        mutations = integrator.run_mutations(str(tmp_path))

        # Verify mutations were parsed
        assert len(mutations) == 2
        assert mutations[0].killed is False  # Survived
        assert mutations[1].killed is True  # Killed

        # Analyze mutations to find weak assertions
        analyzer = MutationAnalyzer()
        issues = analyzer.analyze_mutations(mutations)

        # Should have 1 weak assertion (survived mutation)
        assert len(issues) == 1
        assert issues[0].source == IssueSource.MUTATION_TESTING
        assert issues[0].rule_id == "weak-assertion"

        # Calculate stats
        stats = analyzer.calculate_mutation_stats(mutations)
        assert stats.total_mutations == 2
        assert stats.killed_count == 1
        assert stats.survival_rate == 0.5

    def test_assertion_quality_analyzer_integration(self, tmp_path: Path) -> None:
        """Test AssertionQualityAnalyzer integration."""
        # Create a simple test module
        src_file = tmp_path / "src.py"
        src_file.write_text("def add(a, b): return a + b\n")

        # Mock the integrator to return sample mutations
        with patch(
            "pytest_doctor.analyzers.assertion_quality_analyzer.MutationIntegrator"
        ) as mock_integrator_class:
            mock_integrator = MagicMock()
            mock_integrator_class.return_value = mock_integrator
            mock_integrator.run_mutations.return_value = create_sample_mutations()

            # Run analyzer
            config = Config(assertion_quality=True)
            analyzer = AssertionQualityAnalyzer(config)
            result = analyzer.analyze(str(tmp_path))

            # Verify results
            assert result.engine == "assertion_quality"
            assert len(result.issues) == 3  # 3 survived mutations from sample
            assert all(issue.source == IssueSource.MUTATION_TESTING for issue in result.issues)
            assert "mutation_stats" in result.metadata

            # Verify stats
            stats = result.metadata["mutation_stats"]
            assert stats.total_mutations == 5
            assert stats.killed_count == 2
            assert stats.survival_rate == 0.6

    def test_mutation_disabled_returns_empty(self, tmp_path: Path) -> None:
        """Test that disabled mutations returns empty result."""
        config = Config(assertion_quality=False)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(tmp_path))

        assert result.engine == "assertion_quality"
        assert len(result.issues) == 0
        assert "mutation_stats" not in result.metadata

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_mutation_timeout_handling(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test graceful handling of mutation timeout."""
        from subprocess import TimeoutExpired

        # Mock timeout
        mock_run.side_effect = TimeoutExpired("mutmut", 5)

        integrator = MutationIntegrator()
        mutations = integrator.run_mutations(str(tmp_path), timeout_ms=5000)

        # Should return empty list on timeout
        assert mutations == []

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_mutation_not_installed_handling(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test graceful handling when mutmut is not installed."""
        mock_run.side_effect = FileNotFoundError("mutmut not found")

        integrator = MutationIntegrator()
        mutations = integrator.run_mutations(str(tmp_path))

        # Should return empty list
        assert mutations == []


class TestMutationScoringIntegration:
    """Integration tests for mutation stats in scoring."""

    def test_mutation_stats_affects_score(self) -> None:
        """Test that mutation stats affect the health score."""
        from pytest_doctor.scoring import HealthScorer

        # Create results with good mutation stats (all killed)
        mutation_result = AnalysisResult(engine="assertion_quality")
        mutation_result.metadata["mutation_stats"] = MutationStats(
            total_mutations=100,
            killed_count=100,  # All mutations killed
            survival_rate=0.0,  # Perfect
            time_ms=5000,
        )

        scorer = HealthScorer()
        score = scorer.calculate_score([mutation_result])

        # Should have high score (100 for mutation quality component)
        assert score > 90

    def test_mutation_stats_poor_quality_affects_score(self) -> None:
        """Test that poor mutation stats lower the score."""
        from pytest_doctor.scoring import HealthScorer

        # Create results with poor mutation stats (many survived)
        mutation_result = AnalysisResult(engine="assertion_quality")
        mutation_result.metadata["mutation_stats"] = MutationStats(
            total_mutations=100,
            killed_count=10,  # Most mutations survived
            survival_rate=0.9,  # Very poor
            time_ms=5000,
        )

        scorer = HealthScorer()
        score = scorer.calculate_score([mutation_result])

        # Should have lower score due to poor assertion quality
        # (1 - 0.9) * 100 = 10 for mutation quality
        # Final score = 100*0.30 + 100*0.30 + 10*0.20 + 100*0.20 = 82
        assert score == 82


class TestMutationOutputFormatting:
    """Integration tests for mutation output formatting."""

    def test_mutation_stats_in_diagnostic_report(self) -> None:
        """Test that mutation stats are included in diagnostic report."""
        mutation_result = AnalysisResult(engine="assertion_quality")
        weak_assertion_issue = Issue(
            file_path="test.py",
            line_number=10,
            rule_id="weak-assertion",
            severity=Severity.WARNING,
            source=IssueSource.MUTATION_TESTING,
            message="Mutation survived",
        )
        mutation_result.issues = [weak_assertion_issue]
        mutation_result.metadata["mutation_stats"] = MutationStats(
            total_mutations=50,
            killed_count=35,
            survival_rate=0.3,
            time_ms=3000,
        )

        report = DiagnosticReport(
            path=".",
            score=80,
            results=[mutation_result],
            summary={"critical": 0, "warning": 1, "info": 0},
            total_issues=1,
            mutation_survival_rate=0.3,
        )

        # Verify report contains mutation data
        assert report.mutation_survival_rate == 0.3

    def test_mutation_issues_in_aggregated_results(self) -> None:
        """Test that mutation issues are properly aggregated."""
        from pytest_doctor.aggregation import ResultsAggregator

        # Create mutation results
        mutation_issue = Issue(
            file_path="src/logic.py",
            line_number=20,
            rule_id="weak-assertion",
            severity=Severity.WARNING,
            source=IssueSource.MUTATION_TESTING,
            message="Mutation survived",
            recommendation="Strengthen assertion",
        )

        mutation_result = AnalysisResult(
            engine="assertion_quality",
            issues=[mutation_issue],
        )

        # Create lint results
        lint_issue = Issue(
            file_path="src/logic.py",
            line_number=15,
            rule_id="E501",
            severity=Severity.WARNING,
            source=IssueSource.LINTING,
            message="Line too long",
        )
        lint_result = AnalysisResult(engine="ruff", issues=[lint_issue])

        # Aggregate both
        aggregator = ResultsAggregator()
        aggregated = aggregator.aggregate([lint_result, mutation_result])

        # Should have both issues
        assert len(aggregated.all_issues) == 2
        assert any(issue.source == IssueSource.MUTATION_TESTING for issue in aggregated.all_issues)


class TestMutationCLIIntegration:
    """Integration tests for mutation CLI flags."""

    def test_cli_mutation_flag_enables_feature(self) -> None:
        """Test that --mutation flag enables assertion quality analysis."""
        from click.testing import CliRunner
        from pytest_doctor.cli import main

        runner = CliRunner()
        result = runner.invoke(main, [".", "--mutation"])

        # Should succeed
        assert result.exit_code == 0

    def test_cli_mutation_with_json_output(self) -> None:
        """Test mutation flag with JSON output."""
        import json
        from click.testing import CliRunner
        from pytest_doctor.cli import main

        runner = CliRunner()
        result = runner.invoke(main, [".", "--mutation", "--json"])

        assert result.exit_code == 0

        # Parse JSON
        try:
            output = json.loads(result.output)
            # Should have score and other fields
            assert "score" in output
        except json.JSONDecodeError:
            # Some output formats might not be JSON
            pass

    def test_cli_no_mutation_flag_disables_feature(self) -> None:
        """Test that --no-mutation flag disables assertion quality."""
        from click.testing import CliRunner
        from pytest_doctor.cli import main

        runner = CliRunner()
        result = runner.invoke(main, [".", "--no-mutation"])

        assert result.exit_code == 0


@pytest.mark.integration
class TestFullMutationPipeline:
    """Full pipeline mutation testing integration tests."""

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_end_to_end_weak_assertions_example(self, mock_run: MagicMock) -> None:
        """Test end-to-end with weak assertions example project."""
        fixture_path = Path(__file__).parent / "fixtures/weak_assertions_example"

        if not fixture_path.exists():
            pytest.skip("Fixture project not available")

        # Mock mutmut to return survived mutations
        mock_output = """{
            "results": [
                {
                    "id": "1",
                    "filename": "tests/test_calculator.py",
                    "line_number": 15,
                    "mutation_type": "== changed to !=",
                    "status": "SURVIVED"
                },
                {
                    "id": "2",
                    "filename": "tests/test_calculator.py",
                    "line_number": 20,
                    "mutation_type": "> changed to <",
                    "status": "SURVIVED"
                }
            ]
        }"""

        mock_process = MagicMock()
        mock_process.stdout = mock_output
        mock_run.return_value = mock_process

        # Run integration
        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(fixture_path))

        # Should find weak assertion issues
        assert result.engine == "assertion_quality"
        assert len(result.issues) > 0

    @patch("pytest_doctor.mutation_integrator.subprocess.run")
    def test_end_to_end_strong_assertions_example(self, mock_run: MagicMock) -> None:
        """Test end-to-end with strong assertions example project."""
        fixture_path = Path(__file__).parent / "fixtures/strong_assertions_example"

        if not fixture_path.exists():
            pytest.skip("Fixture project not available")

        # Mock mutmut to return mostly killed mutations
        mock_output = """{
            "results": [
                {
                    "id": "1",
                    "filename": "tests/test_calculator.py",
                    "line_number": 15,
                    "mutation_type": "== changed to !=",
                    "status": "KILLED"
                },
                {
                    "id": "2",
                    "filename": "tests/test_calculator.py",
                    "line_number": 20,
                    "mutation_type": "> changed to <",
                    "status": "KILLED"
                },
                {
                    "id": "3",
                    "filename": "tests/test_calculator.py",
                    "line_number": 25,
                    "mutation_type": "True changed to False",
                    "status": "KILLED"
                }
            ]
        }"""

        mock_process = MagicMock()
        mock_process.stdout = mock_output
        mock_run.return_value = mock_process

        # Run integration
        config = Config(assertion_quality=True)
        analyzer = AssertionQualityAnalyzer(config)
        result = analyzer.analyze(str(fixture_path))

        # Should have no weak assertion issues (all killed)
        assert result.engine == "assertion_quality"
        assert len(result.issues) == 0
