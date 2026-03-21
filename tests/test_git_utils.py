"""Tests for git utilities."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest_doctor.git_utils import GitDiffHandler


class TestGitDiffHandler:
    """Tests for GitDiffHandler."""

    def test_init_default_path(self) -> None:
        """Test GitDiffHandler initialization with default path."""
        handler = GitDiffHandler()
        assert handler.repo_path == Path(".")

    def test_init_custom_path(self) -> None:
        """Test GitDiffHandler initialization with custom path."""
        handler = GitDiffHandler("/some/path")
        assert handler.repo_path == Path("/some/path")

    @patch("subprocess.run")
    def test_get_changed_files_success(self, mock_run: MagicMock) -> None:
        """Test getting changed files successfully."""
        # Mock git diff output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "file1.py\nfile2.py\nfile3.py\n"

        mock_run.side_effect = [mock_result, MagicMock(returncode=0, stdout="")]

        handler = GitDiffHandler(".")
        changed = handler.get_changed_files("main")

        assert len(changed) >= 2
        assert "file1.py" in changed
        assert "file2.py" in changed
        assert "file3.py" in changed

    @patch("subprocess.run")
    def test_get_changed_files_git_failure(self, mock_run: MagicMock) -> None:
        """Test getting changed files when git fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # Simulate git failure

        mock_run.return_value = mock_result

        handler = GitDiffHandler(".")
        changed = handler.get_changed_files("main")

        # Should return empty set on failure
        assert changed == set()

    @patch("subprocess.run")
    def test_get_changed_files_with_untracked(self, mock_run: MagicMock) -> None:
        """Test getting changed files including untracked files."""
        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "tracked.py\n"

        mock_staged = MagicMock()
        mock_staged.returncode = 0
        mock_staged.stdout = ""

        mock_untracked = MagicMock()
        mock_untracked.returncode = 0
        mock_untracked.stdout = "untracked.py\n"

        mock_run.side_effect = [mock_diff, mock_staged, mock_untracked]

        handler = GitDiffHandler(".")
        changed = handler.get_changed_files("main", untracked=True)

        assert "tracked.py" in changed
        assert "untracked.py" in changed

    @patch("subprocess.run")
    def test_get_changed_lines_success(self, mock_run: MagicMock) -> None:
        """Test getting changed lines in a file."""
        # Mock git diff output in unified format
        diff_output = """@@ -10,3 +10,4 @@
 line 1
 line 2
-line 3
+line 3 modified
+line 4 new"""

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = diff_output

        mock_run.return_value = mock_result

        handler = GitDiffHandler(".")
        changed_lines = handler.get_changed_lines("test.py", "main")

        # Should include lines in the changed range (10-13)
        assert len(changed_lines) > 0
        assert 10 in changed_lines or 11 in changed_lines or 12 in changed_lines

    @patch("subprocess.run")
    def test_get_changed_lines_empty(self, mock_run: MagicMock) -> None:
        """Test getting changed lines when there are none."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""

        mock_run.return_value = mock_result

        handler = GitDiffHandler(".")
        changed_lines = handler.get_changed_lines("test.py", "main")

        assert changed_lines == set()

    @patch("subprocess.run")
    def test_is_git_repo_true(self, mock_run: MagicMock) -> None:
        """Test detecting a valid git repository."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        mock_run.return_value = mock_result

        handler = GitDiffHandler(".")
        assert handler.is_git_repo() is True

    @patch("subprocess.run")
    def test_is_git_repo_false(self, mock_run: MagicMock) -> None:
        """Test detecting a non-git directory."""
        mock_result = MagicMock()
        mock_result.returncode = 128  # Not a git repository

        mock_run.return_value = mock_result

        handler = GitDiffHandler(".")
        assert handler.is_git_repo() is False

    @patch("subprocess.run")
    def test_ref_exists_true(self, mock_run: MagicMock) -> None:
        """Test verifying an existing git reference."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        mock_run.return_value = mock_result

        handler = GitDiffHandler(".")
        assert handler.ref_exists("main") is True

    @patch("subprocess.run")
    def test_ref_exists_false(self, mock_run: MagicMock) -> None:
        """Test verifying a non-existent git reference."""
        mock_result = MagicMock()
        mock_result.returncode = 128  # Ref not found

        mock_run.return_value = mock_result

        handler = GitDiffHandler(".")
        assert handler.ref_exists("nonexistent") is False

    @patch("subprocess.run")
    def test_subprocess_error_handling(self, mock_run: MagicMock) -> None:
        """Test handling subprocess errors gracefully."""
        import subprocess

        mock_run.side_effect = subprocess.SubprocessError("Git failed")

        handler = GitDiffHandler(".")

        # Should handle errors gracefully
        changed = handler.get_changed_files("main")
        assert changed == set()

        changed_lines = handler.get_changed_lines("test.py", "main")
        assert changed_lines == set()

        is_repo = handler.is_git_repo()
        assert is_repo is False
