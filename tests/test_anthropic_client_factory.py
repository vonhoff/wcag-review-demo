"""Tests for AnthropicClientFactory."""

import json

import pytest

from src.anthropic_client_factory import AnthropicClientFactory, MockAnthropicClient


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

    def test_create_mock_client_with_test_key(self) -> None:
        """Test mock client creation with TEST API key."""
        client = AnthropicClientFactory.create_client("TEST")
        assert client is not None
        # Should be a MockAnthropicClient instance
        assert isinstance(client, MockAnthropicClient)

        # Test that the mock client returns expected response
        response = client.messages.create(
            model="test-model",
            max_tokens=1000,
            messages=[{"role": "user", "content": "test"}]
        )
        assert "content" in response
        assert len(response["content"]) == 1
        assert response["content"][0]["type"] == "text"
        # Should contain the mock JSON data
        mock_data = json.loads(response["content"][0]["text"])
        assert isinstance(mock_data, list)
        assert len(mock_data) > 0
