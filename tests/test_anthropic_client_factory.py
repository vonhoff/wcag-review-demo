"""Tests for AnthropicClientFactory."""

import pytest

from src.anthropic_client_factory import AnthropicClientFactory


class TestAnthropicClientFactory:
    """Test suite for AnthropicClientFactory."""

    def test_create_client_with_valid_key(self) -> None:
        """Test client creation with valid API key."""
        client = AnthropicClientFactory.create_client("test_key")
        assert client is not None

    def test_create_client_with_empty_key(self) -> None:
        """Test client creation with empty API key raises error."""
        with pytest.raises(ValueError, match="Anthropic API key cannot be empty"):
            AnthropicClientFactory.create_client("")

    def test_get_default_model(self) -> None:
        """Test default model retrieval."""
        model = AnthropicClientFactory.get_default_model()
        assert model == "claude-3-5-sonnet-20241022"

    def test_get_default_max_tokens(self) -> None:
        """Test default max tokens retrieval."""
        tokens = AnthropicClientFactory.get_default_max_tokens()
        assert tokens == 8192
