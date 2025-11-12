"""Tests for AnthropicPromptService."""

from src.anthropic_prompt_service import AnthropicPromptService


class TestAnthropicPromptService:
    """Test suite for AnthropicPromptService."""

    def test_build_accessibility_prompt_without_context(self) -> None:
        """Test accessibility prompt building without context."""
        diff = "--- a/test.html\n+++ b/test.html\n@@ -1,1 +1,1 @@\n-<div></div>\n+<div>test</div>"
        prompt = AnthropicPromptService.build_accessibility_prompt(diff)

        assert "accessibility expert" in prompt.lower()
        assert "WCAG" in prompt
        assert diff in prompt
        assert "JSON" in prompt

    def test_build_accessibility_prompt_with_context(self) -> None:
        """Test accessibility prompt building with context."""
        diff = "test diff"
        context = "Fix button accessibility"

        prompt = AnthropicPromptService.build_accessibility_prompt(diff, context)

        assert "accessibility expert" in prompt.lower()
        assert context in prompt
        assert diff in prompt

    def test_build_code_review_prompt_without_context(self) -> None:
        """Test code review prompt building without context."""
        diff = "--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,1 @@\n-x = 1\n+x = 2"
        prompt = AnthropicPromptService.build_code_review_prompt(diff)

        assert "code reviewer" in prompt.lower()
        assert diff in prompt
        assert "JSON" in prompt

    def test_build_code_review_prompt_with_context(self) -> None:
        """Test code review prompt building with context."""
        diff = "test diff"
        context = "Refactor data processing"

        prompt = AnthropicPromptService.build_code_review_prompt(diff, context)

        assert "code reviewer" in prompt.lower()
        assert context in prompt
        assert diff in prompt

    def test_accessibility_prompt_includes_wcag_criteria(self) -> None:
        """Test that accessibility prompt mentions WCAG criteria."""
        diff = "test"
        prompt = AnthropicPromptService.build_accessibility_prompt(diff)

        assert "wcag_criteria" in prompt
        assert "ARIA" in prompt

    def test_code_review_prompt_includes_category(self) -> None:
        """Test that code review prompt mentions category."""
        diff = "test"
        prompt = AnthropicPromptService.build_code_review_prompt(diff)

        assert "category" in prompt
        assert "bug" in prompt
