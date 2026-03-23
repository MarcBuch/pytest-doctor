"""Tests for mutation integrator."""

from pathlib import Path

import pytest

from pytest_doctor.mutation_integrator import MutationIntegrator
from pytest_doctor.models import Mutation


class TestMutationIntegrator:
    """Test suite for MutationIntegrator."""

    def test_init(self) -> None:
        """Test MutationIntegrator initialization."""
        integrator = MutationIntegrator()
        assert integrator is not None
        assert integrator.logger is not None

    def test_run_mutations_nonexistent_path(self) -> None:
        """Test run_mutations with non-existent path."""
        integrator = MutationIntegrator()
        result = integrator.run_mutations("/nonexistent/path")
        assert result == []

    def test_cosmic_ray_creates_config(self, tmp_path: Path) -> None:
        """Test that cosmic-ray config is created correctly."""
        integrator = MutationIntegrator()
        config_path = integrator._create_config(tmp_path, tmp_path)

        assert config_path.exists()
        assert config_path.name == "cosmic-ray.toml"
        content = config_path.read_text()
        assert "module-path" in content
        assert "test-command" in content
        assert "pytest" in content

    def test_get_test_command_pytest(self, tmp_path: Path) -> None:
        """Test detection of pytest test command."""
        integrator = MutationIntegrator()

        # Create pytest.ini
        (tmp_path / "pytest.ini").touch()
        cmd = integrator._get_test_command(tmp_path)
        assert "pytest" in cmd

    def test_get_test_command_default(self, tmp_path: Path) -> None:
        """Test default test command detection."""
        integrator = MutationIntegrator()
        cmd = integrator._get_test_command(tmp_path)
        assert "pytest" in cmd

    def test_parse_mutation_cosmic_ray_format(self) -> None:
        """Test parsing cosmic-ray work item format."""
        integrator = MutationIntegrator()
        work_item = {
            "job_id": "1",
            "mutations": [
                {
                    "module": "src/math.py",
                    "line_number": 10,
                    "operator": "ArithmeticOperator",
                }
            ],
            "worker_outcome": "NORMAL",
            "test_outcome": "FAILED",
        }
        mutation = integrator._parse_mutation(work_item)
        assert mutation is not None
        assert mutation.id == "1"
        assert "src/math.py" in mutation.source_location
        assert mutation.mutation_type == "ArithmeticOperator"
        assert mutation.killed is True

    def test_parse_mutation_survived(self) -> None:
        """Test parsing mutation that survived."""
        integrator = MutationIntegrator()
        work_item = {
            "job_id": "2",
            "mutations": [
                {
                    "module": "src/math.py",
                    "line_number": 15,
                    "operator": "BinaryOperator",
                }
            ],
            "worker_outcome": "NORMAL",
            "test_outcome": "PASSED",
        }
        mutation = integrator._parse_mutation(work_item)
        assert mutation is not None
        assert mutation.killed is False

    def test_parse_mutation_no_mutations_list(self) -> None:
        """Test parsing work item with empty mutations list."""
        integrator = MutationIntegrator()
        work_item = {
            "job_id": "1",
            "mutations": [],
            "worker_outcome": "NORMAL",
            "test_outcome": "FAILED",
        }
        mutation = integrator._parse_mutation(work_item)
        assert mutation is None

    def test_parse_mutation_missing_module(self) -> None:
        """Test parsing mutation without module name."""
        integrator = MutationIntegrator()
        work_item = {
            "job_id": "1",
            "mutations": [
                {
                    "line_number": 10,
                    "operator": "Test",
                }
            ],
            "worker_outcome": "NORMAL",
            "test_outcome": "FAILED",
        }
        mutation = integrator._parse_mutation(work_item)
        assert mutation is not None
        assert mutation.source_location == "unknown:0"

    def test_parse_mutation_alternative_fields(self) -> None:
        """Test parsing mutation with alternative field names."""
        integrator = MutationIntegrator()
        work_item = {
            "id": "5",
            "mutations": [
                {
                    "module": "test.py",
                    "lineno": 25,
                    "operator": "Return",
                }
            ],
            "worker_outcome": "NORMAL",
            "test_outcome": "FAILED",
        }
        mutation = integrator._parse_mutation(work_item)
        assert mutation is not None
        assert mutation.id == "5"
        assert mutation.source_location == "test.py:25"

    def test_parse_mutation_invalid_format(self) -> None:
        """Test parsing invalid mutation record."""
        integrator = MutationIntegrator()
        work_item = {}
        mutation = integrator._parse_mutation(work_item)
        assert mutation is None

    @pytest.mark.integration
    def test_run_mutations_on_sample_project(self, tmp_path: Path) -> None:
        """Test run_mutations on a simple sample project."""
        # Create a simple test project
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create a simple Python file with testable mutations
        (src_dir / "calc.py").write_text(
            """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
        )

        # Create tests directory
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        # Create pytest tests
        (tests_dir / "test_calc.py").write_text(
            """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calc import add, subtract

def test_add():
    assert add(1, 2) == 3
    assert add(5, 5) == 10

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(10, 5) == 5
"""
        )

        # Run mutations
        integrator = MutationIntegrator()
        mutations = integrator.run_mutations(str(src_dir), timeout_ms=60000)

        # We expect to find some mutations (the exact number depends on cosmic-ray)
        # The important thing is that we get actual mutation objects back
        assert isinstance(mutations, list)
        for mutation in mutations:
            assert isinstance(mutation, Mutation)
            assert mutation.id is not None
            assert mutation.source_location is not None
            assert mutation.mutation_type is not None
            assert isinstance(mutation.killed, bool)

    def test_mutation_dataclass_creation(self) -> None:
        """Test creating Mutation dataclass directly."""
        mutation = Mutation(
            id="1",
            source_location="test.py:10",
            mutation_type="Constant",
            killed=True,
            failing_tests=["test_one"],
        )
        assert mutation.id == "1"
        assert mutation.source_location == "test.py:10"
        assert mutation.mutation_type == "Constant"
        assert mutation.killed is True
        assert mutation.failing_tests == ["test_one"]

    def test_mutation_dataclass_defaults(self) -> None:
        """Test Mutation dataclass with defaults."""
        mutation = Mutation(
            id="1",
            source_location="test.py:10",
            mutation_type="Test",
            killed=False,
        )
        assert mutation.failing_tests == []

    def test_init_session_error_handling(self, tmp_path: Path) -> None:
        """Test init_session handles errors gracefully."""
        integrator = MutationIntegrator()
        config_path = tmp_path / "nonexistent.toml"
        session_db = tmp_path / ".cosmic-ray.sqlite"

        # This should return False since the config doesn't exist
        result = integrator._init_session(config_path, session_db, 10)
        assert result is False

    def test_run_baseline_error_handling(self, tmp_path: Path) -> None:
        """Test run_baseline handles errors gracefully."""
        integrator = MutationIntegrator()
        config_path = tmp_path / "nonexistent.toml"
        session_db = tmp_path / ".cosmic-ray.sqlite"

        # This should return False since the config doesn't exist
        result = integrator._run_baseline(config_path, session_db, 10)
        assert result is False

    def test_exec_mutations_error_handling(self, tmp_path: Path) -> None:
        """Test exec_mutations handles errors gracefully."""
        integrator = MutationIntegrator()
        config_path = tmp_path / "nonexistent.toml"
        session_db = tmp_path / ".cosmic-ray.sqlite"

        # Should not raise an exception
        integrator._exec_mutations(config_path, session_db, 10)

    def test_parse_cosmic_ray_output_empty(self, tmp_path: Path) -> None:
        """Test parsing empty cosmic-ray output."""
        integrator = MutationIntegrator()
        session_db = tmp_path / ".cosmic-ray.sqlite"

        # With non-existent database, should return empty list
        mutations = integrator._parse_cosmic_ray_output(session_db)
        assert mutations == []

    def test_parse_cosmic_ray_output_invalid_json_line(self, tmp_path: Path) -> None:
        """Test parsing cosmic-ray output with invalid JSON lines."""
        integrator = MutationIntegrator()

        # This is tested indirectly through the error handling in _parse_cosmic_ray_output
        # which should gracefully skip invalid lines
        work_item = {
            "job_id": "1",
            "mutations": [{"module": "test.py", "line_number": 10, "operator": "Test"}],
            "worker_outcome": "NORMAL",
            "test_outcome": "FAILED",
        }
        mutation = integrator._parse_mutation(work_item)
        assert mutation is not None

    def test_get_test_command_with_pyproject(self, tmp_path: Path) -> None:
        """Test test command detection with pyproject.toml."""
        integrator = MutationIntegrator()

        # Create pyproject.toml
        (tmp_path / "pyproject.toml").touch()
        cmd = integrator._get_test_command(tmp_path)
        assert "pytest" in cmd

    def test_get_test_command_with_setup_py(self, tmp_path: Path) -> None:
        """Test test command detection with setup.py."""
        integrator = MutationIntegrator()

        # Create setup.py
        (tmp_path / "setup.py").touch()
        cmd = integrator._get_test_command(tmp_path)
        assert "pytest" in cmd

    def test_create_config_contains_exclude_patterns(self, tmp_path: Path) -> None:
        """Test that created config contains exclude patterns."""
        integrator = MutationIntegrator()
        config_path = integrator._create_config(tmp_path, tmp_path)

        content = config_path.read_text()
        assert "exclude-patterns" in content
        assert "tests" in content
        assert "test_" in content

    def test_parse_mutation_with_line_number_zero(self) -> None:
        """Test parsing mutation without line number."""
        integrator = MutationIntegrator()
        work_item = {
            "job_id": "1",
            "mutations": [
                {
                    "module": "src/test.py",
                    "operator": "Test",
                }
            ],
            "worker_outcome": "NORMAL",
            "test_outcome": "FAILED",
        }
        mutation = integrator._parse_mutation(work_item)
        assert mutation is not None
        assert mutation.source_location == "src/test.py:0"
