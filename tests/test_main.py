"""Unit tests for the main module."""

import os
from unittest.mock import Mock, patch

import pytest

from src.main import PRDiffAnalyzer, load_environment


class TestPRDiffAnalyzer:
    """Test suite for PRDiffAnalyzer class."""

    @patch("src.main.ClaudeClient")
    @patch("src.main.DiffFilter")
    @patch("src.main.GitHubDiffFetcher")
    def test_init(
        self, mock_fetcher: Mock, mock_filter: Mock, mock_claude: Mock
    ) -> None:
        """Test initialization of PRDiffAnalyzer."""
        PRDiffAnalyzer(
            github_token="test_token",
            repository_name="owner/repo",
            anthropic_api_key="test_api_key",
        )

        mock_fetcher.assert_called_once_with("test_token", "owner/repo")
        mock_filter.assert_called_once()
        mock_claude.assert_called_once()

    @patch("src.main.ClaudeClient")
    @patch("src.main.DiffFilter")
    @patch("src.main.GitHubDiffFetcher")
    def test_analyze_pr_success(
        self, mock_fetcher_class: Mock, mock_filter_class: Mock, mock_claude_class: Mock
    ) -> None:
        """Test successful PR analysis."""
        # Setup mocks
        mock_fetcher = Mock()
        mock_fetcher.fetch_pr_diff.return_value = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"
        mock_fetcher.get_pr_info.return_value = {
            "title": "Test PR",
            "description": "Test description",
        }
        mock_fetcher_class.return_value = mock_fetcher

        mock_filter = Mock()
        mock_filter.filter_diff.return_value = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"
        mock_filter.get_summary.return_value = {
            "files_changed": 1,
            "additions": 1,
            "deletions": 1,
            "total_changes": 2,
        }
        mock_filter_class.return_value = mock_filter

        mock_claude = Mock()
        mock_claude.analyze_diff.return_value = "Good changes"
        mock_claude_class.return_value = mock_claude

        # Test
        analyzer = PRDiffAnalyzer(
            github_token="test_token",
            repository_name="owner/repo",
            anthropic_api_key="test_api_key",
        )
        result = analyzer.analyze_pr(1)

        assert result["pr_number"] == "1"
        assert result["analysis_type"] == "review"
        assert result["analysis"] == "Good changes"
        assert result["summary"]["files_changed"] == 1

    @patch("src.main.ClaudeClient")
    @patch("src.main.DiffFilter")
    @patch("src.main.GitHubDiffFetcher")
    def test_analyze_pr_with_empty_filtered_diff(
        self, mock_fetcher_class: Mock, mock_filter_class: Mock, mock_claude_class: Mock
    ) -> None:
        """Test PR analysis when filtered diff is empty."""
        mock_fetcher = Mock()
        mock_fetcher.fetch_pr_diff.return_value = "some diff"
        mock_fetcher_class.return_value = mock_fetcher

        mock_filter = Mock()
        mock_filter.filter_diff.return_value = ""
        mock_filter_class.return_value = mock_filter

        mock_claude_class.return_value = Mock()

        analyzer = PRDiffAnalyzer(
            github_token="test_token",
            repository_name="owner/repo",
            anthropic_api_key="test_api_key",
        )
        result = analyzer.analyze_pr(1)

        assert "error" in result
        assert result["error"] == "No changes matched the filter criteria"

    @patch("src.main.ClaudeClient")
    @patch("src.main.DiffFilter")
    @patch("src.main.GitHubDiffFetcher")
    def test_analyze_pr_without_pr_info(
        self, mock_fetcher_class: Mock, mock_filter_class: Mock, mock_claude_class: Mock
    ) -> None:
        """Test PR analysis without including PR info."""
        mock_fetcher = Mock()
        mock_fetcher.fetch_pr_diff.return_value = "diff"
        mock_fetcher_class.return_value = mock_fetcher

        mock_filter = Mock()
        mock_filter.filter_diff.return_value = "filtered diff"
        mock_filter.get_summary.return_value = {
            "files_changed": 1,
            "additions": 1,
            "deletions": 1,
            "total_changes": 2,
        }
        mock_filter_class.return_value = mock_filter

        mock_claude = Mock()
        mock_claude.analyze_diff.return_value = "Analysis"
        mock_claude_class.return_value = mock_claude

        analyzer = PRDiffAnalyzer(
            github_token="test_token",
            repository_name="owner/repo",
            anthropic_api_key="test_api_key",
        )
        analyzer.analyze_pr(1, include_pr_info=False)

        mock_fetcher.get_pr_info.assert_not_called()
        mock_claude.analyze_diff.assert_called_once()
        call_args = mock_claude.analyze_diff.call_args
        assert call_args.kwargs["context"] is None

    @patch("src.main.ClaudeClient")
    @patch("src.main.DiffFilter")
    @patch("src.main.GitHubDiffFetcher")
    def test_context_manager(
        self, mock_fetcher_class: Mock, mock_filter_class: Mock, mock_claude_class: Mock
    ) -> None:
        """Test context manager usage."""
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_filter_class.return_value = Mock()
        mock_claude_class.return_value = Mock()

        with PRDiffAnalyzer(
            github_token="test_token",
            repository_name="owner/repo",
            anthropic_api_key="test_api_key",
        ) as analyzer:
            assert analyzer is not None

        mock_fetcher.close.assert_called_once()


class TestLoadEnvironment:
    """Test suite for load_environment function."""

    @patch.dict(os.environ, {
        "GITHUB_TOKEN": "test_token",
        "GITHUB_REPOSITORY": "owner/repo",
        "ANTHROPIC_API_KEY": "test_api_key",
        "CLAUDE_MODEL": "claude-3-opus-20240229",
        "MAX_TOKENS": "8192",
    })
    def test_load_environment_success(self) -> None:
        """Test successful environment loading."""
        config = load_environment()

        assert config["github_token"] == "test_token"
        assert config["repository_name"] == "owner/repo"
        assert config["anthropic_api_key"] == "test_api_key"
        assert config["claude_model"] == "claude-3-opus-20240229"
        assert config["max_tokens"] == 8192

    @patch.dict(os.environ, {
        "GITHUB_TOKEN": "test_token",
        "GITHUB_REPOSITORY": "owner/repo",
        "ANTHROPIC_API_KEY": "test_api_key",
    })
    def test_load_environment_with_defaults(self) -> None:
        """Test environment loading with default values."""
        config = load_environment()

        assert config["github_token"] == "test_token"
        assert config["repository_name"] == "owner/repo"
        assert config["anthropic_api_key"] == "test_api_key"
        assert config["claude_model"] is None
        assert config["max_tokens"] == 4096

    @patch.dict(os.environ, {
        "GITHUB_TOKEN": "test_token",
        "GITHUB_REPOSITORY": "owner/repo",
    }, clear=True)
    def test_load_environment_missing_required_var(self) -> None:
        """Test environment loading with missing required variable."""
        with pytest.raises(ValueError, match="Missing required environment variables"):
            load_environment()

    @patch.dict(os.environ, {
        "GITHUB_TOKEN": "",
        "GITHUB_REPOSITORY": "owner/repo",
        "ANTHROPIC_API_KEY": "test_api_key",
    })
    def test_load_environment_empty_required_var(self) -> None:
        """Test environment loading with empty required variable."""
        with pytest.raises(ValueError, match="Missing required environment variables"):
            load_environment()
