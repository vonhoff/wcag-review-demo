"""Factory for creating configured Anthropic Claude API clients."""

import anthropic


class AnthropicClientFactory:
    """Factory for creating configured Anthropic API clients."""

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_MAX_TOKENS = 8192

    @staticmethod
    def create_client(api_key: str) -> anthropic.Anthropic:
        """Create and return a configured Anthropic client.

        Args:
            api_key: Anthropic API key

        Returns:
            Configured Anthropic client instance

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("Anthropic API key cannot be empty")

        return anthropic.Anthropic(api_key=api_key)

    @staticmethod
    def get_default_model() -> str:
        """Return the default Claude model."""
        return AnthropicClientFactory.DEFAULT_MODEL

    @staticmethod
    def get_default_max_tokens() -> int:
        """Return the default max tokens."""
        return AnthropicClientFactory.DEFAULT_MAX_TOKENS
