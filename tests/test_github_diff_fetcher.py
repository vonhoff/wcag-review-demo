"""Unit tests for the GitHub Diff Fetcher module."""

from unittest.mock import Mock, patch

import pytest
from github import GithubException

from src.github_diff_fetcher import GitHubDiffFetcher


class TestGitHubDiffFetcher:
    """Test suite for GitHubDiffFetcher class."""

    def test_init_with_valid_credentials(self) -> None:
        """Test initialization with valid credentials."""
        fetcher = GitHubDiffFetcher("test_token", "owner/repo")
        assert fetcher.repository_name == "owner/repo"
        assert fetcher.github_client is not None

    def test_init_with_empty_token(self) -> None:
        """Test initialization with empty token raises ValueError."""
        with pytest.raises(ValueError, match="GitHub token cannot be empty"):
            GitHubDiffFetcher("", "owner/repo")

    def test_init_with_empty_repository(self) -> None:
        """Test initialization with empty repository raises ValueError."""
        with pytest.raises(ValueError, match="Repository name cannot be empty"):
            GitHubDiffFetcher("test_token", "")

    @patch("src.github_diff_fetcher.Github")
    def test_fetch_pr_diff_success(self, mock_github: Mock) -> None:
        """Test successful PR diff fetching."""
        # Setup mocks
        mock_file = Mock()
        mock_file.filename = "test.py"
        mock_file.patch = "@@ -1,3 +1,3 @@\n-old line\n+new line"

        mock_pr = Mock()
        mock_pr.get_files.return_value = [mock_file]

        mock_repo = Mock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test
        fetcher = GitHubDiffFetcher("test_token", "owner/repo")
        diff = fetcher.fetch_pr_diff(1)

        assert "--- a/test.py" in diff
        assert "+++ b/test.py" in diff
        assert "-old line" in diff
        assert "+new line" in diff

    def test_fetch_pr_diff_with_invalid_pr_number(self) -> None:
        """Test fetch_pr_diff with invalid PR number."""
        fetcher = GitHubDiffFetcher("test_token", "owner/repo")

        with pytest.raises(ValueError, match="PR number must be a positive integer"):
            fetcher.fetch_pr_diff(0)

        with pytest.raises(ValueError, match="PR number must be a positive integer"):
            fetcher.fetch_pr_diff(-1)

    @patch("src.github_diff_fetcher.Github")
    def test_fetch_pr_diff_with_api_error(self, mock_github: Mock) -> None:
        """Test fetch_pr_diff handles API errors."""
        mock_github_instance = Mock()
        mock_github_instance.get_repo.side_effect = GithubException(404, "Not found", None)
        mock_github.return_value = mock_github_instance

        fetcher = GitHubDiffFetcher("test_token", "owner/repo")

        with pytest.raises(Exception, match="Failed to fetch PR"):
            fetcher.fetch_pr_diff(1)

    @patch("src.github_diff_fetcher.Github")
    def test_get_pr_info_success(self, mock_github: Mock) -> None:
        """Test successful PR info retrieval."""
        mock_pr = Mock()
        mock_pr.title = "Test PR"
        mock_pr.body = "Test description"
        mock_pr.base.ref = "main"
        mock_pr.head.ref = "feature"
        mock_pr.state = "open"
        mock_pr.html_url = "https://github.com/owner/repo/pull/1"

        mock_repo = Mock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        fetcher = GitHubDiffFetcher("test_token", "owner/repo")
        info = fetcher.get_pr_info(1)

        assert info["title"] == "Test PR"
        assert info["description"] == "Test description"
        assert info["base_branch"] == "main"
        assert info["head_branch"] == "feature"
        assert info["state"] == "open"

    @patch("src.github_diff_fetcher.Github")
    def test_context_manager(self, mock_github: Mock) -> None:
        """Test context manager usage."""
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        with GitHubDiffFetcher("test_token", "owner/repo") as fetcher:
            assert fetcher is not None

        mock_github_instance.close.assert_called_once()

    @patch("src.github_diff_fetcher.Github")
    def test_fetch_pr_diff_with_multiple_files(self, mock_github: Mock) -> None:
        """Test fetching diff with multiple files."""
        mock_file1 = Mock()
        mock_file1.filename = "file1.py"
        mock_file1.patch = "@@ -1,1 +1,1 @@\n-old1\n+new1"

        mock_file2 = Mock()
        mock_file2.filename = "file2.py"
        mock_file2.patch = "@@ -1,1 +1,1 @@\n-old2\n+new2"

        mock_pr = Mock()
        mock_pr.get_files.return_value = [mock_file1, mock_file2]

        mock_repo = Mock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        fetcher = GitHubDiffFetcher("test_token", "owner/repo")
        diff = fetcher.fetch_pr_diff(1)

        assert "file1.py" in diff
        assert "file2.py" in diff
        assert "-old1" in diff
        assert "-old2" in diff

    @patch("src.github_diff_fetcher.Github")
    def test_fetch_pr_diff_excludes_binary_files(self, mock_github: Mock) -> None:
        """Test that binary files without patches are excluded."""
        mock_text_file = Mock()
        mock_text_file.filename = "text.py"
        mock_text_file.patch = "@@ -1,1 +1,1 @@\n-old\n+new"

        mock_binary_file = Mock()
        mock_binary_file.filename = "image.png"
        mock_binary_file.patch = None  # Binary files don't have patches

        mock_pr = Mock()
        mock_pr.get_files.return_value = [mock_text_file, mock_binary_file]

        mock_repo = Mock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        fetcher = GitHubDiffFetcher("test_token", "owner/repo")
        diff = fetcher.fetch_pr_diff(1)

        assert "text.py" in diff
        assert "image.png" not in diff
