"""Service for building accessibility-focused code review prompts."""

from __future__ import annotations

from pathlib import Path


class AnthropicPromptService:
    """Builds prompts for accessibility and code review analysis."""

    @staticmethod
    def _load_template(template_name: str) -> str:
        """Load a markdown template from the data directory."""
        template_path = Path(__file__).parent.parent / "data" / f"{template_name}.md"
        with template_path.open(encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def build_prompt(diff: str) -> str:
        """Build unified prompt for accessibility-focused code review."""
        template = AnthropicPromptService._load_template("review_prompt")

        return template.format(diff=diff)
