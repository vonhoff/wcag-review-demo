"""Unit tests for the Claude Client module."""

from unittest.mock import Mock, patch

import pytest
from anthropic.types import Message, TextBlock

from src.claude_client import ClaudeClient


class TestClaudeClient:
    """Test suite for ClaudeClient class."""

    def test_init_with_valid_api_key(self) -> None:
        """Test initialization with valid API key."""
        client = ClaudeClient("test_api_key")
        assert client.model == ClaudeClient.DEFAULT_MODEL
        assert client.max_tokens == ClaudeClient.DEFAULT_MAX_TOKENS

    def test_init_with_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        client = ClaudeClient(
            "test_api_key",
            model="claude-3-opus-20240229",
            max_tokens=8192,
        )
        assert client.model == "claude-3-opus-20240229"
        assert client.max_tokens == 8192

    def test_init_with_empty_api_key(self) -> None:
        """Test initialization with empty API key raises ValueError."""
        with pytest.raises(ValueError, match="Anthropic API key cannot be empty"):
            ClaudeClient("")

    @patch("src.claude_client.anthropic.Anthropic")
    def test_analyze_diff_success(self, mock_anthropic: Mock) -> None:
        """Test successful diff analysis."""
        # Setup mock response
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.type = "text"
        mock_text_block.text = "This is a good change"

        mock_message = Mock(spec=Message)
        mock_message.content = [mock_text_block]

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client_instance

        # Test
        client = ClaudeClient("test_api_key")
        diff = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"
        result = client.analyze_diff(diff)

        assert result == "This is a good change"
        mock_client_instance.messages.create.assert_called_once()

    def test_analyze_diff_with_empty_diff(self) -> None:
        """Test analyze_diff with empty diff raises ValueError."""
        client = ClaudeClient("test_api_key")

        with pytest.raises(ValueError, match="Diff cannot be empty"):
            client.analyze_diff("")

    def test_analyze_diff_with_invalid_analysis_type(self) -> None:
        """Test analyze_diff with invalid analysis type raises ValueError."""
        client = ClaudeClient("test_api_key")
        diff = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"

        with pytest.raises(ValueError, match="Invalid analysis_type"):
            client.analyze_diff(diff, analysis_type="invalid")

    @patch("src.claude_client.anthropic.Anthropic")
    def test_analyze_diff_with_context(self, mock_anthropic: Mock) -> None:
        """Test diff analysis with context."""
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.type = "text"
        mock_text_block.text = "Analysis with context"

        mock_message = Mock(spec=Message)
        mock_message.content = [mock_text_block]

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client_instance

        client = ClaudeClient("test_api_key")
        diff = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"
        context = "This PR fixes a bug"

        result = client.analyze_diff(diff, context=context)

        assert result == "Analysis with context"
        call_args = mock_client_instance.messages.create.call_args
        assert "This PR fixes a bug" in call_args.kwargs["messages"][0]["content"]

    @patch("src.claude_client.anthropic.Anthropic")
    def test_analyze_diff_all_analysis_types(self, mock_anthropic: Mock) -> None:
        """Test all analysis types."""
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.type = "text"
        mock_text_block.text = "Analysis result"

        mock_message = Mock(spec=Message)
        mock_message.content = [mock_text_block]

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client_instance

        client = ClaudeClient("test_api_key")
        diff = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"

        for analysis_type in ["review", "summary", "security", "accessibility"]:
            result = client.analyze_diff(diff, analysis_type=analysis_type)
            assert result == "Analysis result"

    @patch("src.claude_client.anthropic.Anthropic")
    def test_send_message_success(self, mock_anthropic: Mock) -> None:
        """Test successful message sending."""
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.type = "text"
        mock_text_block.text = "Response message"

        mock_message = Mock(spec=Message)
        mock_message.content = [mock_text_block]

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client_instance

        client = ClaudeClient("test_api_key")
        result = client.send_message("Hello")

        assert result == "Response message"

    def test_send_message_with_empty_message(self) -> None:
        """Test send_message with empty message raises ValueError."""
        client = ClaudeClient("test_api_key")

        with pytest.raises(ValueError, match="Message cannot be empty"):
            client.send_message("")

    @patch("src.claude_client.anthropic.Anthropic")
    def test_send_message_with_system_prompt(self, mock_anthropic: Mock) -> None:
        """Test send_message with system prompt."""
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.type = "text"
        mock_text_block.text = "Response"

        mock_message = Mock(spec=Message)
        mock_message.content = [mock_text_block]

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client_instance

        client = ClaudeClient("test_api_key")
        result = client.send_message("Hello", system_prompt="You are helpful")

        assert result == "Response"
        call_args = mock_client_instance.messages.create.call_args
        assert call_args.kwargs["system"] == "You are helpful"

    @patch("src.claude_client.anthropic.Anthropic")
    def test_extract_response_text_multiple_blocks(self, mock_anthropic: Mock) -> None:
        """Test extracting text from multiple content blocks."""
        mock_block1 = Mock(spec=TextBlock)
        mock_block1.type = "text"
        mock_block1.text = "Part 1"

        mock_block2 = Mock(spec=TextBlock)
        mock_block2.type = "text"
        mock_block2.text = "Part 2"

        mock_message = Mock(spec=Message)
        mock_message.content = [mock_block1, mock_block2]

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client_instance

        client = ClaudeClient("test_api_key")
        diff = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"
        result = client.analyze_diff(diff)

        assert result == "Part 1Part 2"

    @patch("src.claude_client.anthropic.Anthropic")
    def test_build_prompt_for_review(self, mock_anthropic: Mock) -> None:
        """Test prompt building for review analysis."""
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.type = "text"
        mock_text_block.text = "Review"

        mock_message = Mock(spec=Message)
        mock_message.content = [mock_text_block]

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client_instance

        client = ClaudeClient("test_api_key")
        diff = "--- a/test.py\n+++ b/test.py"
        client.analyze_diff(diff, analysis_type="review")

        call_args = mock_client_instance.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "review" in prompt.lower()
        assert "code quality" in prompt.lower()

    @patch("src.claude_client.anthropic.Anthropic")
    def test_api_error_handling(self, mock_anthropic: Mock) -> None:
        """Test API error handling."""
        mock_client_instance = Mock()
        mock_client_instance.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client_instance

        client = ClaudeClient("test_api_key")
        diff = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-old\n+new"

        with pytest.raises(Exception, match="Failed to analyze diff with Claude"):
            client.analyze_diff(diff)
