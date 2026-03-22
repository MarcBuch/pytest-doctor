"""Mutation testing integration using mutmut."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from pytest_doctor.models import Mutation

logger = logging.getLogger(__name__)


class MutationIntegrator:
    """Integrates mutmut mutation testing tool."""

    def __init__(self) -> None:
        """Initialize the mutation integrator."""
        self.logger = logger

    def run_mutations(self, path: str, timeout_ms: int = 300000) -> list[Mutation]:
        """
        Execute mutmut and parse results.

        Args:
            path: Directory or file path to analyze with mutmut
            timeout_ms: Timeout in milliseconds for mutmut execution

        Returns:
            List of Mutation objects parsed from mutmut output
        """
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                self.logger.debug(f"Path does not exist: {path}")
                return []

            # Convert milliseconds to seconds for subprocess timeout
            timeout_seconds = timeout_ms / 1000.0

            # Run mutmut with JSON output
            cmd: list[str] = [
                "mutmut",
                "run",
                "--json",
                str(path_obj),
            ]

            self.logger.debug(f"Running mutation testing: {' '.join(cmd)}")

            output = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

            # Parse JSON output
            if output.stdout:
                mutations = self._parse_mutmut_output(output.stdout)
                self.logger.debug(f"Found {len(mutations)} mutations in {path}")
                return mutations

            self.logger.debug("No mutations found or mutmut produced no output")
            return []

        except subprocess.TimeoutExpired:
            self.logger.warning(f"Mutation testing timed out after {timeout_ms}ms for {path}")
            return []
        except FileNotFoundError:
            self.logger.debug("mutmut is not installed")
            return []
        except Exception as e:
            self.logger.warning(
                f"Error running mutation testing on {path}: {type(e).__name__}: {e}"
            )
            return []

    def _parse_mutmut_output(self, json_output: str) -> list[Mutation]:
        """
        Parse mutmut JSON output into Mutation objects.

        Args:
            json_output: JSON string from mutmut --json output

        Returns:
            List of Mutation objects
        """
        mutations: list[Mutation] = []

        try:
            data = json.loads(json_output)

            # mutmut JSON structure can vary, handle both dict and list formats
            if isinstance(data, dict):
                # If it's a dict, look for 'results' key or similar
                results = data.get("results", data.get("mutations", []))
                if not isinstance(results, list):
                    results = []
            elif isinstance(data, list):
                results = data
            else:
                self.logger.warning(f"Unexpected mutmut JSON structure: {type(data)}")
                return []

            for result in results:
                if not isinstance(result, dict):
                    continue

                mutation = self._parse_mutation_record(result)
                if mutation is not None:
                    mutations.append(mutation)

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse mutmut JSON: {e}")
            return []

        return mutations

    def _parse_mutation_record(self, record: dict[str, Any]) -> Mutation | None:
        """
        Parse a single mutation record from mutmut output.

        Args:
            record: Single mutation record from mutmut JSON

        Returns:
            Mutation object or None if record is invalid
        """
        try:
            # Extract required fields, with fallbacks
            mutation_id = str(record.get("id", record.get("index", 0)))

            # Build source location from available fields
            filename = str(record.get("filename", ""))
            line_number = record.get("line_number", record.get("lineno", 0))
            source_location = f"{filename}:{line_number}" if filename else "unknown:0"

            mutation_type = str(record.get("mutation_type", "unknown"))

            # Determine if mutation was killed (survived=False means killed=True)
            status = str(record.get("status", "")).lower()
            killed = (
                status == "killed"
                or status == "KILLED"
                or record.get("killed", False) is True
                or record.get("survived", True) is False
            )

            failing_tests: list[str] = []
            if "failing_tests" in record:
                tests = record["failing_tests"]
                if isinstance(tests, list):
                    failing_tests = [str(t) for t in tests]
                elif isinstance(tests, str):
                    failing_tests = [tests]

            return Mutation(
                id=mutation_id,
                source_location=source_location,
                mutation_type=mutation_type,
                killed=killed,
                failing_tests=failing_tests,
            )

        except (KeyError, ValueError, TypeError) as e:
            self.logger.debug(f"Failed to parse mutation record: {e}")
            return None
