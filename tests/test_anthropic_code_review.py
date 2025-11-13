"""Tests for AnthropicCodeReview."""

from pathlib import Path
from unittest.mock import Mock, patch

from src.anthropic_code_review import AnthropicCodeReview


class TestAnthropicCodeReview:
    """Test suite for AnthropicCodeReview."""

    @patch("src.anthropic_code_review.AnthropicClientFactory")
    @patch("src.anthropic_code_review.GitHubDiffFetcher")
    def test_init(self, mock_fetcher: Mock, mock_factory: Mock) -> None:
        """Test initialization."""
        mock_factory.create_client.return_value = Mock()
        mock_factory.get_default_model.return_value = "test-model"
        mock_factory.get_default_max_tokens.return_value = 8192

        reviewer = AnthropicCodeReview(
            github_token="token",
            repository_name="owner/repo",
            anthropic_api_key="api_key",
        )

        assert reviewer is not None
        mock_fetcher.assert_called_once()

    @patch("src.anthropic_code_review.AnthropicClientFactory")
    @patch("src.anthropic_code_review.GitHubDiffFetcher")
    def test_review_pr_unified(self, mock_fetcher_class: Mock, mock_factory: Mock) -> None:
        """Test unified accessibility-focused code review."""
        mock_client = Mock()
        mock_client.messages.create.return_value = Mock(
            content=[Mock(type="text", text='[{"file":"test.html","line":1,"issue":"Missing alt text","suggestion":"Add alt attribute","severity":"high","category":"accessibility","wcag_criteria":"1.1.1"},{"file":"app.js","line":10,"issue":"Bug","suggestion":"Fix it","severity":"critical","category":"bug","wcag_criteria":null}]')]
        )
        mock_factory.create_client.return_value = mock_client
        mock_factory.get_default_model.return_value = "test-model"
        mock_factory.get_default_max_tokens.return_value = 8192

        mock_fetcher = Mock()
        mock_fetcher.get_pr_info.return_value = {"title": "Test PR", "description": "Test"}
        mock_fetcher.fetch_pr_diff.return_value = "--- a/test.html\n+++ b/test.html\n@@ -1 +1 @@\n-old\n+new"
        mock_fetcher_class.return_value = mock_fetcher

        reviewer = AnthropicCodeReview(
            github_token="token",
            repository_name="owner/repo",
            anthropic_api_key="api_key",
        )

        comments, html = reviewer.review_pr(123)

        assert len(comments) == 2
        assert comments[0].file == "test.html"
        assert comments[0].category == "accessibility"
        assert comments[0].wcag_criteria == "1.1.1"
        assert comments[1].category == "bug"
        assert comments[1].wcag_criteria is None
        assert "test.html" in html

    @patch("src.anthropic_code_review.AnthropicClientFactory")
    @patch("src.anthropic_code_review.GitHubDiffFetcher")
    def test_filter_diff_excludes_patterns(
        self, mock_fetcher_class: Mock, mock_factory: Mock
    ) -> None:
        """Test diff filtering excludes specified patterns."""
        mock_factory.create_client.return_value = Mock()
        mock_factory.get_default_model.return_value = "test-model"
        mock_factory.get_default_max_tokens.return_value = 8192
        mock_fetcher_class.return_value = Mock()

        reviewer = AnthropicCodeReview(
            github_token="token",
            repository_name="owner/repo",
            anthropic_api_key="api_key",
        )

        diff = "--- a/package-lock.json\n+++ b/package-lock.json\n@@ -1 +1 @@\n-old\n+new"
        filtered = reviewer._filter_diff(diff)

        assert "package-lock.json" not in filtered

    @patch("src.anthropic_code_review.AnthropicClientFactory")
    @patch("src.anthropic_code_review.GitHubDiffFetcher")
    def test_filter_diff_truncates_large_diffs(
        self, mock_fetcher_class: Mock, mock_factory: Mock
    ) -> None:
        """Test diff filtering truncates large diffs."""
        mock_factory.create_client.return_value = Mock()
        mock_factory.get_default_model.return_value = "test-model"
        mock_factory.get_default_max_tokens.return_value = 8192
        mock_fetcher_class.return_value = Mock()

        reviewer = AnthropicCodeReview(
            github_token="token",
            repository_name="owner/repo",
            anthropic_api_key="api_key",
        )

        large_diff = "x" * 100000
        filtered = reviewer._filter_diff(large_diff)

        assert len(filtered) <= reviewer.MAX_DIFF_SIZE

    @patch("src.anthropic_code_review.AnthropicClientFactory")
    @patch("src.anthropic_code_review.GitHubDiffFetcher")
    def test_save_report(self, mock_fetcher_class: Mock, mock_factory: Mock, tmp_path: Path) -> None:
        """Test report saving."""
        mock_factory.create_client.return_value = Mock()
        mock_factory.get_default_model.return_value = "test-model"
        mock_factory.get_default_max_tokens.return_value = 8192
        mock_fetcher_class.return_value = Mock()

        reviewer = AnthropicCodeReview(
            github_token="token",
            repository_name="owner/repo",
            anthropic_api_key="api_key",
        )

        report_path = tmp_path / "test_report.html"
        reviewer.save_report("<html>Test</html>", report_path)

        assert report_path.exists()
        assert report_path.read_text() == "<html>Test</html>"

    @patch("src.anthropic_code_review.AnthropicClientFactory")
    @patch("src.anthropic_code_review.GitHubDiffFetcher")
    def test_context_manager(self, mock_fetcher_class: Mock, mock_factory: Mock) -> None:
        """Test context manager usage."""
        mock_factory.create_client.return_value = Mock()
        mock_factory.get_default_model.return_value = "test-model"
        mock_factory.get_default_max_tokens.return_value = 8192

        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher

        with AnthropicCodeReview(
            github_token="token",
            repository_name="owner/repo",
            anthropic_api_key="api_key",
        ) as reviewer:
            assert reviewer is not None

        mock_fetcher.close.assert_called_once()
