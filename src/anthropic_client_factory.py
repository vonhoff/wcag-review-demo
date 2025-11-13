"""Factory for creating configured Anthropic Claude API clients."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import anthropic


class MockAnthropicClient:
    """Mock Anthropic client for testing purposes."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._mock_response = self._load_mock_response()

    def _load_mock_response(self) -> dict[str, Any]:
        """Load mock response data from file."""
        mock_file = Path(__file__).parent.parent / "data" / "mock_api_response.json"
        with mock_file.open(encoding="utf-8") as f:
            data = json.load(f)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(data, indent=2)
                }
            ]
        }

    class MockMessages:
        def __init__(self, mock_response: dict[str, Any]):
            self.mock_response = mock_response

        def create(self, **_kwargs: Any) -> dict[str, Any]:
            """Return mock response instead of calling API."""
            return self.mock_response

    @property
    def messages(self) -> MockAnthropicClient.MockMessages:
        return self.MockMessages(self._mock_response)


class AnthropicClientFactory:
    """Factory for creating configured Anthropic API clients."""

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_MAX_TOKENS = 8192

    @staticmethod
    def create_client(api_key: str) -> anthropic.Anthropic | MockAnthropicClient:
        """Create and return a configured Anthropic client.

        Args:
            api_key: Anthropic API key (use "TEST" for mock responses)

        Returns:
            Configured Anthropic client instance (or mock client for testing)

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("Anthropic API key cannot be empty")

        if api_key == "TEST":
            return MockAnthropicClient(api_key)  # type: ignore[return-value]

        return anthropic.Anthropic(api_key=api_key)

    @staticmethod
    def get_default_model() -> str:
        """Return the default Claude model."""
        return AnthropicClientFactory.DEFAULT_MODEL

    @staticmethod
    def get_default_max_tokens() -> int:
        """Return the default max tokens."""
        return AnthropicClientFactory.DEFAULT_MAX_TOKENS
