"""Tests for AnthropicPromptService."""

from src.anthropic_prompt_service import AnthropicPromptService


class TestAnthropicPromptService:
    """Test suite for AnthropicPromptService."""

    def test_build_prompt_without_context(self) -> None:
        """Test unified prompt building without context."""
        diff = "--- a/test.html\n+++ b/test.html\n@@ -1,1 +1,1 @@\n-<div></div>\n+<div>test</div>"
        prompt = AnthropicPromptService.build_prompt(diff)

        assert "accessibility-focused code reviewer" in prompt.lower()
        assert "WCAG" in prompt
        assert diff in prompt
        assert "JSON" in prompt

    def test_build_prompt_with_context(self) -> None:
        """Test unified prompt building with context."""
        diff = "test diff"
        context = "Fix button accessibility"

        prompt = AnthropicPromptService.build_prompt(diff, context)

        assert "accessibility-focused code reviewer" in prompt.lower()
        assert context in prompt
        assert diff in prompt

    def test_unified_prompt_includes_accessibility_and_code_quality_elements(self) -> None:
        """Test that unified prompt includes both accessibility and code quality elements."""
        diff = "test"
        prompt = AnthropicPromptService.build_prompt(diff)

        # Accessibility elements
        assert "wcag_criteria" in prompt
        assert "ARIA" in prompt

        # Code quality elements
        assert "category" in prompt
        assert "bug" in prompt
        assert "accessibility-focused" in prompt.lower()
