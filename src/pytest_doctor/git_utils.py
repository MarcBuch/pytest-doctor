"""Git utilities for pytest-doctor."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


class GitDiffHandler:
    """Handles git diff operations to find changed files."""

    def __init__(self, repo_path: str | Path = ".") -> None:
        """
        Initialize GitDiffHandler.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)

    def get_changed_files(self, ref: str = "main", untracked: bool = False) -> set[str]:
        """
        Get files changed compared to a git reference.

        Args:
            ref: Git reference to compare against (default: main)
            untracked: Include untracked files (default: False)

        Returns:
            Set of changed file paths relative to the repository root
        """
        changed_files: set[str] = set()

        try:
            # Get diff between ref and working directory
            cmd = ["git", "diff", "--name-only", ref]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0 and result.stdout:
                # Parse the output and add to set
                changed_files.update(
                    line.strip() for line in result.stdout.strip().split("\n") if line.strip()
                )

            # Get staged changes
            cmd_staged = ["git", "diff", "--cached", "--name-only", ref]
            result_staged = subprocess.run(
                cmd_staged,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )

            if result_staged.returncode == 0 and result_staged.stdout:
                changed_files.update(
                    line.strip()
                    for line in result_staged.stdout.strip().split("\n")
                    if line.strip()
                )

            # Get untracked files if requested
            if untracked:
                cmd_untracked = [
                    "git",
                    "ls-files",
                    "--others",
                    "--exclude-standard",
                ]
                result_untracked = subprocess.run(
                    cmd_untracked,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result_untracked.returncode == 0 and result_untracked.stdout:
                    changed_files.update(
                        line.strip()
                        for line in result_untracked.stdout.strip().split("\n")
                        if line.strip()
                    )

        except subprocess.SubprocessError:
            # If git command fails, return empty set
            pass

        return changed_files

    def get_changed_lines(self, file_path: str | Path, ref: str = "main") -> set[int]:
        """
        Get line numbers changed in a specific file compared to a git reference.

        Args:
            file_path: Path to the file to check
            ref: Git reference to compare against (default: main)

        Returns:
            Set of line numbers that have been changed
        """
        changed_lines: set[int] = set()

        try:
            # Use git diff with unified format to identify changed lines
            cmd = ["git", "diff", ref, "--", str(file_path)]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0 and result.stdout:
                # Parse the unified diff format
                for line in result.stdout.split("\n"):
                    # Lines starting with @@ contain line numbers
                    if line.startswith("@@"):
                        # Format: @@ -old_start,old_count +new_start,new_count @@
                        parts = line.split(" ")
                        if len(parts) >= 3:
                            # Extract new line range (starts with +)
                            new_range = parts[2]  # e.g., "+100,5"
                            if new_range.startswith("+"):
                                range_str = new_range[1:]  # Remove the +
                                if "," in range_str:
                                    start, count = map(int, range_str.split(","))
                                else:
                                    start = int(range_str)
                                    count = 1

                                # Add all lines in this range
                                changed_lines.update(range(start, start + count))

        except subprocess.SubprocessError:
            # If git command fails, return empty set
            pass

        return changed_lines

    def is_git_repo(self) -> bool:
        """
        Check if the path is a git repository.

        Returns:
            True if the path is a git repository, False otherwise
        """
        try:
            cmd = ["git", "rev-parse", "--git-dir"]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False

    def ref_exists(self, ref: str) -> bool:
        """
        Check if a git reference (branch, tag, commit) exists.

        Args:
            ref: Git reference to check

        Returns:
            True if the reference exists, False otherwise
        """
        try:
            cmd = ["git", "rev-parse", ref]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False
