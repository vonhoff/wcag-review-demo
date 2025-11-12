"""Service for building accessibility-focused code review prompts."""


class AnthropicPromptService:
    """Builds prompts for accessibility and code review analysis."""

    @staticmethod
    def build_accessibility_prompt(diff: str, pr_context: str | None = None) -> str:
        """Build prompt for WCAG accessibility review.

        Args:
            diff: Git diff content
            pr_context: Optional PR title and description

        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "You are an accessibility expert conducting a WCAG compliance review.\n\n",
            "Review the following code changes for accessibility issues:\n",
            "- Check for WCAG 2.1 AA compliance violations\n",
            "- Identify missing ARIA labels, roles, and properties\n",
            "- Check keyboard navigation support\n",
            "- Verify color contrast and text alternatives\n",
            "- Check for semantic HTML usage\n",
            "- Identify screen reader compatibility issues\n\n",
        ]

        if pr_context:
            prompt_parts.append(f"PR Context: {pr_context}\n\n")

        prompt_parts.extend([
            "Provide your review as a JSON array of comment objects. Each comment should have:\n",
            '- "file": filename where the issue was found\n',
            '- "line": line number (or null if file-level)\n',
            '- "issue": brief description of the accessibility issue\n',
            '- "suggestion": concrete fix recommendation\n',
            '- "severity": "critical", "high", "medium", or "low"\n',
            '- "wcag_criteria": applicable WCAG criterion (e.g., "1.1.1", "2.1.1")\n\n',
            "Example format:\n",
            "```json\n",
            "[\n",
            "  {\n",
            '    "file": "index.html",\n',
            '    "line": 42,\n',
            '    "issue": "Image missing alt attribute",\n',
            '    "suggestion": "Add descriptive alt text: <img src=\\"logo.png\\" alt=\\"Company logo\\">",\n',
            '    "severity": "high",\n',
            '    "wcag_criteria": "1.1.1"\n',
            "  }\n",
            "]\n",
            "```\n\n",
            f"Git Diff:\n```diff\n{diff}\n```\n\n",
            "Respond ONLY with the JSON array, no additional text.",
        ])

        return "".join(prompt_parts)

    @staticmethod
    def build_code_review_prompt(diff: str, pr_context: str | None = None) -> str:
        """Build prompt for general code review.

        Args:
            diff: Git diff content
            pr_context: Optional PR title and description

        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "You are a senior code reviewer focused on code quality and maintainability.\n\n",
            "Review the following code changes:\n",
            "- Identify potential bugs and logic errors\n",
            "- Check code quality and best practices\n",
            "- Suggest improvements for readability and maintainability\n",
            "- Note any anti-patterns or code smells\n",
            "- Check for proper error handling\n\n",
        ]

        if pr_context:
            prompt_parts.append(f"PR Context: {pr_context}\n\n")

        prompt_parts.extend([
            "Provide your review as a JSON array of comment objects. Each comment should have:\n",
            '- "file": filename where the issue was found\n',
            '- "line": line number (or null if file-level)\n',
            '- "issue": brief description of the issue\n',
            '- "suggestion": concrete improvement recommendation\n',
            '- "severity": "critical", "high", "medium", or "low"\n',
            '- "category": "bug", "quality", "maintainability", or "style"\n\n',
            "Example format:\n",
            "```json\n",
            "[\n",
            "  {\n",
            '    "file": "app.py",\n',
            '    "line": 15,\n',
            '    "issue": "Potential null pointer exception",\n',
            '    "suggestion": "Add null check before accessing property",\n',
            '    "severity": "high",\n',
            '    "category": "bug"\n',
            "  }\n",
            "]\n",
            "```\n\n",
            f"Git Diff:\n```diff\n{diff}\n```\n\n",
            "Respond ONLY with the JSON array, no additional text.",
        ])

        return "".join(prompt_parts)
