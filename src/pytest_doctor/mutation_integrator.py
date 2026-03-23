"""Mutation testing integration using cosmic-ray."""

from __future__ import annotations

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from pytest_doctor.models import Mutation

logger = logging.getLogger(__name__)


class MutationIntegrator:
    """Integrates cosmic-ray mutation testing tool."""

    def __init__(self) -> None:
        """Initialize the mutation integrator."""
        self.logger = logger

    def run_mutations(self, path: str, timeout_ms: int = 300000) -> list[Mutation]:
        """
        Execute cosmic-ray and parse results.

        Args:
            path: Directory or file path to analyze with cosmic-ray
            timeout_ms: Timeout in milliseconds for cosmic-ray execution

        Returns:
            List of Mutation objects parsed from cosmic-ray output
        """
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                self.logger.debug(f"Path does not exist: {path}")
                return []

            # Convert milliseconds to seconds for subprocess timeout
            timeout_seconds = timeout_ms / 1000.0

            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                config_path = self._create_config(path_obj, tmpdir_path)
                session_db = tmpdir_path / ".cosmic-ray.sqlite"

                # Step 1: Initialize cosmic-ray session
                if not self._init_session(config_path, session_db, timeout_seconds):
                    self.logger.debug("Failed to initialize cosmic-ray session")
                    return []

                # Step 2: Run baseline tests
                if not self._run_baseline(config_path, session_db, timeout_seconds):
                    self.logger.debug("Baseline tests failed")
                    return []

                # Step 3: Execute mutations
                self._exec_mutations(config_path, session_db, timeout_seconds)

                # Step 4: Parse results
                mutations = self._parse_cosmic_ray_output(session_db)
                self.logger.debug(f"Found {len(mutations)} mutations in {path}")
                return mutations

        except subprocess.TimeoutExpired:
            self.logger.warning(f"Mutation testing timed out after {timeout_ms}ms for {path}")
            return []
        except FileNotFoundError:
            self.logger.debug("cosmic-ray is not installed")
            return []
        except Exception as e:
            self.logger.warning(
                f"Error running mutation testing on {path}: {type(e).__name__}: {e}"
            )
            return []

    def _create_config(self, path: Path, tmpdir: Path) -> Path:
        """
        Create cosmic-ray TOML config.

        Args:
            path: Path to analyze
            tmpdir: Temporary directory for config

        Returns:
            Path to created config file
        """
        config_path = tmpdir / "cosmic-ray.toml"

        test_command = self._get_test_command(path)

        config_content = f"""[cosmic-ray]
module-path = "{path}"
test-command = "{test_command}"

[distributor]
name = "local"
"""

        config_path.write_text(config_content)
        self.logger.debug(f"Created cosmic-ray config at {config_path}")
        return config_path

    def _get_test_command(self, path: Path) -> str:
        """
        Detect test command for the project.

        Args:
            path: Path to analyze

        Returns:
            Test command string
        """
        # Check for pytest configuration
        if (path / "pytest.ini").exists() or (path / "pyproject.toml").exists():
            return "pytest {relative_path}"

        # Check for setup.py or setup.cfg
        if (path / "setup.py").exists() or (path / "setup.cfg").exists():
            return "pytest {relative_path}"

        # Default to pytest
        return "pytest {relative_path}"

    def _init_session(self, config_path: Path, session_db: Path, timeout_seconds: float) -> bool:
        """
        Initialize cosmic-ray session.

        Args:
            config_path: Path to cosmic-ray config
            session_db: Path to session database
            timeout_seconds: Timeout in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                "cosmic-ray",
                "init",
                str(config_path),
                str(session_db),
            ]

            self.logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

            if result.returncode != 0:
                self.logger.debug(f"cosmic-ray init failed: {result.stderr}")
                return False

            return True

        except Exception as e:
            self.logger.debug(f"Error initializing cosmic-ray session: {e}")
            return False

    def _run_baseline(self, config_path: Path, session_db: Path, timeout_seconds: float) -> bool:
        """
        Run baseline tests to ensure they pass.

        Args:
            config_path: Path to cosmic-ray config
            session_db: Path to session database
            timeout_seconds: Timeout in seconds

        Returns:
            True if baseline tests pass, False otherwise
        """
        try:
            cmd = [
                "cosmic-ray",
                "baseline",
                "--session-file",
                str(session_db),
                str(config_path),
            ]

            self.logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

            if result.returncode != 0:
                self.logger.debug(f"cosmic-ray baseline failed: {result.stderr}")
                return False

            return True

        except Exception as e:
            self.logger.debug(f"Error running cosmic-ray baseline: {e}")
            return False

    def _exec_mutations(self, config_path: Path, session_db: Path, timeout_seconds: float) -> None:
        """
        Execute mutation testing with cosmic-ray.

        Args:
            config_path: Path to cosmic-ray config
            session_db: Path to session database
            timeout_seconds: Timeout in seconds
        """
        try:
            cmd = [
                "cosmic-ray",
                "exec",
                str(config_path),
                str(session_db),
            ]

            self.logger.debug(f"Running: {' '.join(cmd)}")

            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

        except Exception as e:
            self.logger.debug(f"Error executing mutations: {e}")

    def _parse_cosmic_ray_output(self, session_db: Path) -> list[Mutation]:
        """
        Parse cosmic-ray results from session database.

        Args:
            session_db: Path to cosmic-ray session database

        Returns:
            List of Mutation objects
        """
        mutations: list[Mutation] = []

        try:
            cmd = ["cosmic-ray", "dump", str(session_db)]

            self.logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode != 0 or not result.stdout:
                self.logger.debug("No cosmic-ray output to parse")
                return []

            # Parse newline-delimited JSON
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                try:
                    work_item = json.loads(line)
                    mutation = self._parse_mutation(work_item)
                    if mutation is not None:
                        mutations.append(mutation)
                except json.JSONDecodeError:
                    self.logger.debug(f"Failed to parse JSON line: {line}")

        except Exception as e:
            self.logger.debug(f"Error parsing cosmic-ray output: {e}")

        return mutations

    def _parse_mutation(self, work_item: dict[str, Any]) -> Mutation | None:
        """
        Parse a single mutation record from cosmic-ray output.

        Args:
            work_item: Single work item from cosmic-ray JSON

        Returns:
            Mutation object or None if record is invalid
        """
        try:
            # Extract required fields
            job_id = str(work_item.get("job_id", work_item.get("id", 0)))

            # Get mutation info
            mutations_list = work_item.get("mutations", [])
            if not mutations_list or not isinstance(mutations_list, list):
                return None

            mutation_info = mutations_list[0]  # Use first mutation in the work item

            # Build source location
            filename = str(mutation_info.get("module", ""))
            line_number = mutation_info.get("line_number", mutation_info.get("lineno", 0))
            source_location = f"{filename}:{line_number}" if filename else "unknown:0"

            mutation_type = str(mutation_info.get("operator", "unknown"))

            # Determine if mutation was killed
            worker_outcome = work_item.get("worker_outcome", "").upper()
            test_outcome = work_item.get("test_outcome", "").upper()

            # Mutation is killed if worker outcome is NORMAL (survived) or if test outcome indicates failure
            killed = worker_outcome == "NORMAL" and test_outcome == "FAILED"

            return Mutation(
                id=job_id,
                source_location=source_location,
                mutation_type=mutation_type,
                killed=killed,
                failing_tests=[],
            )

        except (KeyError, ValueError, TypeError) as e:
            self.logger.debug(f"Failed to parse mutation record: {e}")
            return None
