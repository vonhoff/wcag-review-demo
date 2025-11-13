"""Parser for Anthropic API responses and HTML report generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path


@dataclass
class ReviewComment:
    """Represents a single review comment."""

    file: str
    line: int | None
    issue: str
    suggestion: str
    severity: str
    category: str | None = None
    wcag_criteria: str | None = None


class AnthropicResponseParser:
    """Parses Claude API responses and generates HTML reports."""

    @staticmethod
    def _load_template(template_name: str) -> str:
        """Load an HTML template from the data directory."""
        template_path = Path(__file__).parent.parent / "data" / f"{template_name}.html"
        with template_path.open(encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def parse_response(response_text: str) -> list[ReviewComment]:
        """Parse JSON response into ReviewComment objects.

        Args:
            response_text: Raw response text from Claude API

        Returns:
            List of ReviewComment objects

        Raises:
            ValueError: If response is not valid JSON or missing required fields
        """
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}") from e

        if not isinstance(data, list):
            raise TypeError("Response must be a JSON array")

        comments = []
        for item in data:
            if not isinstance(item, dict):
                continue

            try:
                comment = ReviewComment(
                    file=item["file"],
                    line=item.get("line"),
                    issue=item["issue"],
                    suggestion=item["suggestion"],
                    severity=item["severity"],
                    category=item.get("category"),
                    wcag_criteria=item.get("wcag_criteria"),
                )
                comments.append(comment)
            except KeyError as e:
                raise ValueError(f"Missing required field: {e}") from e

        return comments

    @staticmethod
    def generate_html_report(
        comments: list[ReviewComment],
        pr_number: int,
    ) -> str:
        """Generate HTML report from review comments.

        Args:
            comments: List of review comments
            pr_number: Pull request number

        Returns:
            HTML report as string
        """
        # Load the HTML template
        template = AnthropicResponseParser._load_template("report_template")

        # WCAG criteria to check
        wcag_criteria = [
            "1.3.1 Info and Relationships",
            "1.3.2 Meaningful Sequence",
            "1.3.5 Identify Input Purpose",
            "2.4.4 Link Purpose (In Context)",
            "2.4.6 Headings and Labels",
            "4.1.2 Name, Role, and Value",
            "2.5.3 Label in Name",
            "3.3.2 Labels or Instructions",
        ]

        # Generate WCAG table rows (placeholder implementation)
        wcag_table_rows = []
        for criterion in wcag_criteria:
            # For now, mark all as "Not Checked" - in a real implementation,
            # this would be populated based on Claude analysis results
            wcag_table_rows.append(f"""<tr>
    <td>{escape(criterion)}</td>
    <td>Not Checked</td>
    <td>No automated analysis performed</td>
</tr>""")
        wcag_table_html = "\n".join(wcag_table_rows)

        # Generate summary cards
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for comment in comments:
            if comment.severity in severity_counts:
                severity_counts[comment.severity] += 1

        summary_cards = []
        for severity, count in severity_counts.items():
            summary_cards.append(f"<div><strong>{severity.upper()}</strong>: {count}</div>")
        summary_cards_html = "\n".join(summary_cards)

        # Generate content
        if not comments:
            content_html = "<h2>No Issues Found</h2><p>The code review completed successfully.</p>"
        else:
            comment_items = []
            for comment in comments:
                line_display = f"Line {comment.line}" if comment.line else "File-level"

                comment_html = f"""
<div>
    <h3>{escape(comment.file)} - {line_display}</h3>
    <p><strong>Severity:</strong> {comment.severity}</p>
    <p><strong>Issue:</strong> {escape(comment.issue)}</p>
    <p><strong>Suggestion:</strong> {escape(comment.suggestion)}</p>
"""

                if comment.wcag_criteria or comment.category:
                    tags = []
                    if comment.wcag_criteria:
                        tags.append(f"WCAG {escape(comment.wcag_criteria)}")
                    if comment.category:
                        tags.append(escape(comment.category))
                    comment_html += f"    <p><strong>Tags:</strong> {', '.join(tags)}</p>"

                comment_html += "</div>"
                comment_items.append(comment_html)

            content_html = "\n".join(comment_items)

        # Fill in template placeholders
        return template.format(
            pr_number=pr_number,
            generated_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),  # noqa: UP017
            wcag_table_rows=wcag_table_html,
            summary_cards=summary_cards_html,
            content=content_html,
        )
