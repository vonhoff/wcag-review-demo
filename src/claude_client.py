"""Claude Client Module.

This module provides functionality to interact with the Anthropic Claude API
for sending diffs and receiving AI-powered analysis.
"""


import anthropic


class ClaudeClient:
    """Client for interacting with the Anthropic Claude API.

    This class follows the Single Responsibility Principle by focusing solely
    on Claude API interactions. It uses Dependency Inversion by depending on
    the anthropic library abstraction.

    Attributes:
        client: Anthropic API client instance.
        model: The Claude model to use for completions.
        max_tokens: Maximum tokens in the response.
    """

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_MAX_TOKENS = 4096

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """Initialize the Claude client.

        Args:
            api_key: Anthropic API key for authentication.
            model: The Claude model to use. Defaults to claude-3-5-sonnet-20241022.
            max_tokens: Maximum tokens in the response. Defaults to 4096.

        Raises:
            ValueError: If api_key is empty.
        """
        if not api_key:
            raise ValueError("Anthropic API key cannot be empty")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

    def analyze_diff(
        self,
        diff: str,
        context: str | None = None,
        analysis_type: str = "review",
    ) -> str:
        """Analyze a git diff using Claude.

        Args:
            diff: The git diff to analyze.
            context: Optional context about the changes (e.g., PR description).
            analysis_type: Type of analysis to perform. Options: 'review',
                'summary', 'security', 'accessibility'.

        Returns:
            Claude's analysis as a string.

        Raises:
            ValueError: If diff is empty or analysis_type is invalid.
            Exception: If the API call fails.
        """
        if not diff.strip():
            raise ValueError("Diff cannot be empty")

        valid_types = ["review", "summary", "security", "accessibility"]
        if analysis_type not in valid_types:
            raise ValueError(f"Invalid analysis_type. Must be one of: {valid_types}")

        # Build the prompt based on analysis type
        prompt = self._build_prompt(diff, context, analysis_type)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract text content from the response
            return self._extract_response_text(response)

        except Exception as e:
            raise Exception(f"Failed to analyze diff with Claude: {e!s}") from e

    def _build_prompt(self, diff: str, context: str | None, analysis_type: str) -> str:
        """Build the prompt for Claude based on analysis type.

        Args:
            diff: The git diff to analyze.
            context: Optional context about the changes.
            analysis_type: Type of analysis to perform.

        Returns:
            The formatted prompt string.
        """
        prompts = {
            "review": (
                "Please review the following git diff and provide constructive feedback. "
                "Focus on code quality, potential bugs, best practices, and improvements.\n\n"
            ),
            "summary": (
                "Please provide a concise summary of the changes in the following git diff. "
                "Explain what was changed and why it might be significant.\n\n"
            ),
            "security": (
                "Please analyze the following git diff for security vulnerabilities. "
                "Identify potential security issues, vulnerabilities, and suggest fixes.\n\n"
            ),
            "accessibility": (
                "Please analyze the following git diff for accessibility (WCAG) issues. "
                "Identify potential accessibility problems and suggest improvements.\n\n"
            ),
        }

        prompt_parts = [prompts[analysis_type]]

        if context:
            prompt_parts.append(f"Context: {context}\n\n")

        prompt_parts.append(f"Git Diff:\n```diff\n{diff}\n```")

        return "".join(prompt_parts)

    def _extract_response_text(self, response: anthropic.types.Message) -> str:
        """Extract text content from Claude's response.

        Args:
            response: The response object from Claude API.

        Returns:
            The extracted text content.
        """
        text_parts = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)

        return "".join(text_parts)

    def send_message(
        self,
        message: str,
        system_prompt: str | None = None,
    ) -> str:
        """Send a generic message to Claude.

        Args:
            message: The message to send.
            system_prompt: Optional system prompt to set context.

        Returns:
            Claude's response as a string.

        Raises:
            ValueError: If message is empty.
            Exception: If the API call fails.
        """
        if not message.strip():
            raise ValueError("Message cannot be empty")

        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": message}],
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            return self._extract_response_text(response)

        except Exception as e:
            raise Exception(f"Failed to send message to Claude: {e!s}") from e
