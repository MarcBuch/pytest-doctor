"""Smoke tests for pytest-doctor analysis pipeline."""

import pytest
from pathlib import Path
import tempfile
import shutil

from pytest_doctor import diagnose, Results
from pytest_doctor.exceptions import DirectoryNotFoundError


class TestAnalysisPipelineSmoke:
    """Smoke tests for the complete analysis pipeline."""

    def test_diagnose_function_exists(self):
        """Test that diagnose function is callable."""
        assert callable(diagnose)

    def test_diagnose_with_temp_directory(self):
        """Test diagnose with a temporary test directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple test file
            test_file = Path(tmpdir) / "test_sample.py"
            test_file.write_text(
                """
def test_example():
    assert 1 + 1 == 2
"""
            )

            # Run analysis
            result = diagnose(tmpdir)

            # Verify result structure
            assert isinstance(result, Results)
            assert result.score is not None
            assert result.score.value >= 0 and result.score.value <= 100
            assert result.score.label is not None
            assert isinstance(result.diagnostics, list)
            assert isinstance(result.gaps, list)
            assert isinstance(result.coverage, object)
            assert result.project_info is not None

    def test_diagnose_returns_results_object(self):
        """Test that diagnose returns a Results object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            result = diagnose(tmpdir)
            assert isinstance(result, Results)

    def test_diagnose_score_is_valid(self):
        """Test that returned score is valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            result = diagnose(tmpdir)
            assert 0 <= result.score.value <= 100
            assert result.score.label is not None

    def test_diagnose_has_metadata(self):
        """Test that results contain metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            result = diagnose(tmpdir)
            assert isinstance(result.metadata, dict)
            assert "analysis_version" in result.metadata
            assert "analyzers_run" in result.metadata

    def test_diagnose_with_nonexistent_path(self):
        """Test that diagnose raises error for nonexistent path."""
        with pytest.raises(DirectoryNotFoundError):
            diagnose("/nonexistent/path/to/tests")

    def test_diagnose_with_config(self):
        """Test diagnose with optional config parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            config = {"coverage": {"enabled": True}}
            result = diagnose(tmpdir, config=config)
            assert isinstance(result, Results)

    def test_diagnose_coverage_stats_present(self):
        """Test that coverage statistics are present in results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            result = diagnose(tmpdir)
            assert result.coverage is not None
            assert hasattr(result.coverage, "total_lines")
            assert hasattr(result.coverage, "covered_lines")

    def test_diagnose_project_info_present(self):
        """Test that project information is present in results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            result = diagnose(tmpdir)
            assert result.project_info is not None
            assert result.project_info.name is not None
            assert result.project_info.root_path is not None

    def test_diagnose_empty_directory(self):
        """Test diagnose with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = diagnose(tmpdir)
            assert isinstance(result, Results)
            assert result.score.value >= 0

    def test_diagnose_multiple_test_files(self):
        """Test diagnose with multiple test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_one.py").write_text("def test_first(): pass")
            Path(tmpdir).joinpath("test_two.py").write_text("def test_second(): pass")
            result = diagnose(tmpdir)
            assert isinstance(result, Results)

    def test_analysis_pipeline_completes(self):
        """Test that complete analysis pipeline executes without errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file with some content
            test_file = Path(tmpdir) / "test_pipeline.py"
            test_file.write_text(
                """
def test_basic():
    assert True

def test_with_setup():
    x = 10
    assert x == 10

class TestClass:
    def test_method(self):
        assert 1 + 1 == 2
"""
            )

            # Run diagnose - should execute full pipeline
            result = diagnose(tmpdir)

            # Verify all components of Results are present
            assert result.score is not None
            assert result.diagnostics is not None
            assert result.gaps is not None
            assert result.edge_cases is not None
            assert result.coverage is not None
            assert result.project_info is not None
            assert result.metadata is not None

    def test_score_breakdown_present(self):
        """Test that score breakdown is included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            result = diagnose(tmpdir)
            assert "breakdown" in result.score.__dict__ or hasattr(result.score, "breakdown")

    def test_analyzer_execution_tracked(self):
        """Test that analyzer execution is tracked in metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_dummy.py").write_text("def test(): pass")
            result = diagnose(tmpdir)
            analyzers = result.metadata.get("analyzers_run", [])
            assert len(analyzers) > 0
            assert "code_analyzer" in analyzers
            assert "test_analyzer" in analyzers


class TestAnalyzerImports:
    """Test that all analyzer modules can be imported."""

    def test_code_analyzer_import(self):
        """Test code analyzer module imports."""
        from pytest_doctor.analyzers.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        assert analyzer is not None

    def test_test_analyzer_import(self):
        """Test test analyzer module imports."""
        from pytest_doctor.analyzers.test_analyzer import TestAnalyzer

        analyzer = TestAnalyzer()
        assert analyzer is not None

    def test_coverage_engine_import(self):
        """Test coverage engine module imports."""
        from pytest_doctor.analyzers.coverage_engine import CoverageEngine

        engine = CoverageEngine()
        assert engine is not None

    def test_gap_detector_import(self):
        """Test gap detector module imports."""
        from pytest_doctor.analyzers.gap_detector import GapDetector

        detector = GapDetector()
        assert detector is not None

    def test_edge_case_detector_import(self):
        """Test edge case detector module imports."""
        from pytest_doctor.analyzers.edge_case_detector import EdgeCaseDetector

        detector = EdgeCaseDetector()
        assert detector is not None

    def test_quality_analyzer_import(self):
        """Test quality analyzer module imports."""
        from pytest_doctor.analyzers.quality_analyzer import TestQualityAnalyzer

        analyzer = TestQualityAnalyzer()
        assert analyzer is not None

    def test_correlation_engine_import(self):
        """Test correlation engine module imports."""
        from pytest_doctor.correlation import CorrelationEngine

        engine = CorrelationEngine()
        assert engine is not None


class TestPipelineControlFlow:
    """Test the control flow through the pipeline."""

    def test_pipeline_stages_run_sequentially(self):
        """Test that pipeline stages execute in correct order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_flow.py").write_text(
                """
def test_example():
    '''Test that verifies something'''
    result = True
    assert result is True
"""
            )
            result = diagnose(tmpdir)

            # If we get here, pipeline completed
            assert result is not None
            assert result.score is not None

    def test_pipeline_returns_valid_results_structure(self):
        """Test that pipeline returns properly structured results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("test_structure.py").write_text("def test(): pass")
            result = diagnose(tmpdir)

            # Check all required attributes exist
            required_attrs = [
                "score",
                "diagnostics",
                "gaps",
                "edge_cases",
                "coverage",
                "project_info",
                "metadata",
            ]
            for attr in required_attrs:
                assert hasattr(result, attr), f"Missing attribute: {attr}"

    def test_pipeline_with_placeholder_data(self):
        """Test pipeline execution with minimal test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal test structure
            Path(tmpdir).joinpath("__init__.py").write_text("")
            Path(tmpdir).joinpath("test_minimal.py").write_text("def test_pass(): pass")

            result = diagnose(tmpdir)

            # Should execute successfully with placeholder/minimal data
            assert isinstance(result, Results)
            assert result.score is not None


__all__ = [
    "TestAnalysisPipelineSmoke",
    "TestAnalyzerImports",
    "TestPipelineControlFlow",
]
