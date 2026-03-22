"""Tests for mutation integrator."""

from pathlib import Path
from unittest.mock import MagicMock, patch

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

    def test_run_mutations_mutmut_not_installed(self) -> None:
        """Test run_mutations when mutmut is not installed."""
        integrator = MutationIntegrator()
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("mutmut not found")
            result = integrator.run_mutations(".")
            assert result == []

    def test_run_mutations_timeout(self, tmp_path: Path) -> None:
        """Test run_mutations with timeout."""
        integrator = MutationIntegrator()
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")

        with patch("subprocess.run") as mock_run:
            from subprocess import TimeoutExpired
            mock_run.side_effect = TimeoutExpired("mutmut", 5)
            result = integrator.run_mutations(str(tmp_path), timeout_ms=5000)
            assert result == []

    def test_run_mutations_subprocess_error(self, tmp_path: Path) -> None:
        """Test run_mutations with subprocess error."""
        integrator = MutationIntegrator()
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = RuntimeError("Subprocess failed")
            result = integrator.run_mutations(str(tmp_path))
            assert result == []

    def test_parse_mutmut_output_empty(self) -> None:
        """Test parsing empty mutmut output."""
        integrator = MutationIntegrator()
        result = integrator._parse_mutmut_output("[]")
        assert result == []

    def test_parse_mutmut_output_dict_format(self) -> None:
        """Test parsing mutmut output in dict format with results."""
        integrator = MutationIntegrator()
        json_output = """{
            "results": [
                {
                    "id": "1",
                    "filename": "test.py",
                    "line_number": 10,
                    "mutation_type": "AssertEqual",
                    "status": "KILLED"
                }
            ]
        }"""
        result = integrator._parse_mutmut_output(json_output)
        assert len(result) == 1
        assert result[0].id == "1"
        assert result[0].source_location == "test.py:10"
        assert result[0].mutation_type == "AssertEqual"
        assert result[0].killed is True

    def test_parse_mutmut_output_list_format(self) -> None:
        """Test parsing mutmut output in list format."""
        integrator = MutationIntegrator()
        json_output = """[
            {
                "id": "1",
                "filename": "test.py",
                "line_number": 10,
                "mutation_type": "AssertEqual",
                "survived": false
            }
        ]"""
        result = integrator._parse_mutmut_output(json_output)
        assert len(result) == 1
        assert result[0].killed is True

    def test_parse_mutmut_output_invalid_json(self) -> None:
        """Test parsing invalid JSON."""
        integrator = MutationIntegrator()
        result = integrator._parse_mutmut_output("not valid json")
        assert result == []

    def test_parse_mutmut_output_invalid_structure(self) -> None:
        """Test parsing JSON with invalid structure."""
        integrator = MutationIntegrator()
        result = integrator._parse_mutmut_output('{"invalid": "structure"}')
        assert result == []

    def test_parse_mutation_record_minimal(self) -> None:
        """Test parsing minimal mutation record."""
        integrator = MutationIntegrator()
        record = {
            "id": "42",
            "filename": "test.py",
            "line_number": 5,
            "mutation_type": "ArithmeticOperator",
            "status": "killed",
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.id == "42"
        assert mutation.source_location == "test.py:5"
        assert mutation.mutation_type == "ArithmeticOperator"
        assert mutation.killed is True
        assert mutation.failing_tests == []

    def test_parse_mutation_record_with_failing_tests(self) -> None:
        """Test parsing mutation with failing tests."""
        integrator = MutationIntegrator()
        record = {
            "id": "10",
            "filename": "tests/test_math.py",
            "line_number": 20,
            "mutation_type": "BinaryOperator",
            "status": "KILLED",
            "failing_tests": ["test_add", "test_subtract"],
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.id == "10"
        assert mutation.failing_tests == ["test_add", "test_subtract"]

    def test_parse_mutation_record_failing_tests_as_string(self) -> None:
        """Test parsing mutation with failing tests as single string."""
        integrator = MutationIntegrator()
        record = {
            "id": "10",
            "filename": "tests/test_math.py",
            "line_number": 20,
            "mutation_type": "BinaryOperator",
            "status": "KILLED",
            "failing_tests": "test_add",
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.failing_tests == ["test_add"]

    def test_parse_mutation_record_killed_field(self) -> None:
        """Test parsing mutation with killed field."""
        integrator = MutationIntegrator()
        record = {
            "id": "5",
            "filename": "test.py",
            "line_number": 10,
            "mutation_type": "Constant",
            "killed": True,
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.killed is True

    def test_parse_mutation_record_survived_field(self) -> None:
        """Test parsing mutation with survived field."""
        integrator = MutationIntegrator()
        # survived=true means killed=false
        record = {
            "id": "5",
            "filename": "test.py",
            "line_number": 10,
            "mutation_type": "Constant",
            "survived": True,
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.killed is False

    def test_parse_mutation_record_no_filename(self) -> None:
        """Test parsing mutation without filename."""
        integrator = MutationIntegrator()
        record = {
            "id": "1",
            "line_number": 10,
            "mutation_type": "Test",
            "status": "killed",
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.source_location == "unknown:0"

    def test_parse_mutation_record_alternative_fields(self) -> None:
        """Test parsing mutation with alternative field names."""
        integrator = MutationIntegrator()
        record = {
            "index": "7",
            "filename": "src/main.py",
            "lineno": 25,
            "mutation_type": "Return",
            "status": "killed",
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.id == "7"
        assert mutation.source_location == "src/main.py:25"

    def test_parse_mutation_record_invalid(self) -> None:
        """Test parsing invalid mutation record."""
        integrator = MutationIntegrator()
        record = {}
        mutation = integrator._parse_mutation_record(record)
        # Should still create a mutation with defaults
        assert mutation is not None
        assert mutation.source_location == "unknown:0"
        assert mutation.killed is False

    def test_run_mutations_with_mocked_output(self, tmp_path: Path) -> None:
        """Test run_mutations with mocked mutmut output."""
        integrator = MutationIntegrator()
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")

        mock_json = """{
            "results": [
                {
                    "id": "1",
                    "filename": "test.py",
                    "line_number": 10,
                    "mutation_type": "AssertEqual",
                    "status": "KILLED",
                    "failing_tests": ["test_one"]
                },
                {
                    "id": "2",
                    "filename": "test.py",
                    "line_number": 15,
                    "mutation_type": "Constant",
                    "status": "SURVIVED"
                }
            ]
        }"""

        with patch("subprocess.run") as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = mock_json
            mock_process.returncode = 0
            mock_run.return_value = mock_process

            result = integrator.run_mutations(str(tmp_path))

            assert len(result) == 2
            assert result[0].id == "1"
            assert result[0].killed is True
            assert result[0].failing_tests == ["test_one"]
            assert result[1].id == "2"
            assert result[1].killed is False

    def test_run_mutations_empty_stdout(self, tmp_path: Path) -> None:
        """Test run_mutations with empty stdout."""
        integrator = MutationIntegrator()
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")

        with patch("subprocess.run") as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = ""
            mock_run.return_value = mock_process

            result = integrator.run_mutations(str(tmp_path))
            assert result == []

    def test_run_mutations_with_timeout_parameter(self, tmp_path: Path) -> None:
        """Test run_mutations respects timeout parameter."""
        integrator = MutationIntegrator()
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")

        with patch("subprocess.run") as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "[]"
            mock_run.return_value = mock_process

            integrator.run_mutations(str(tmp_path), timeout_ms=1000)

            # Verify timeout was passed correctly (1000ms = 1.0s)
            call_args = mock_run.call_args
            assert call_args is not None
            assert call_args.kwargs["timeout"] == 1.0

    def test_run_mutations_calls_mutmut_with_json(self, tmp_path: Path) -> None:
        """Test that run_mutations calls mutmut with --json flag."""
        integrator = MutationIntegrator()
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")

        with patch("subprocess.run") as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "[]"
            mock_run.return_value = mock_process

            integrator.run_mutations(str(tmp_path))

            # Verify the command was called correctly
            call_args = mock_run.call_args
            assert call_args is not None
            cmd = call_args[0][0]
            assert cmd[0] == "mutmut"
            assert cmd[1] == "run"
            assert cmd[2] == "--json"
            assert str(tmp_path) in cmd

    def test_parse_mutation_record_status_variations(self) -> None:
        """Test parsing mutations with different status formats."""
        integrator = MutationIntegrator()

        # Test lowercase killed
        record = {
            "id": "1",
            "filename": "test.py",
            "line_number": 10,
            "mutation_type": "Test",
            "status": "killed",
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.killed is True

        # Test uppercase KILLED
        record["status"] = "KILLED"
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.killed is True

        # Test survived status
        record["status"] = "SURVIVED"
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.killed is False

    def test_parse_mutmut_output_with_dict_mutations_key(self) -> None:
        """Test parsing mutmut output with 'mutations' key instead of results."""
        integrator = MutationIntegrator()
        json_output = """{
            "mutations": [
                {
                    "id": "1",
                    "filename": "test.py",
                    "line_number": 10,
                    "mutation_type": "Test",
                    "status": "KILLED"
                }
            ]
        }"""
        result = integrator._parse_mutmut_output(json_output)
        assert len(result) == 1
        assert result[0].id == "1"

    def test_parse_mutation_record_complete(self) -> None:
        """Test parsing a complete mutation record."""
        integrator = MutationIntegrator()
        record = {
            "id": "42",
            "filename": "src/utils.py",
            "line_number": 100,
            "mutation_type": "BinaryOperator",
            "status": "KILLED",
            "failing_tests": [
                "tests/test_utils.py::test_add",
                "tests/test_utils.py::test_subtract",
            ],
        }
        mutation = integrator._parse_mutation_record(record)
        assert mutation is not None
        assert mutation.id == "42"
        assert mutation.source_location == "src/utils.py:100"
        assert mutation.mutation_type == "BinaryOperator"
        assert mutation.killed is True
        assert len(mutation.failing_tests) == 2
        assert "test_add" in mutation.failing_tests[0]

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
