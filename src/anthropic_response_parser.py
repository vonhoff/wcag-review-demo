"""Parser for Anthropic API responses and HTML report generation."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape


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
        review_type: str,
    ) -> str:
        """Generate HTML report from review comments.

        Args:
            comments: List of review comments
            pr_number: Pull request number
            review_type: Type of review ("accessibility" or "code_review")

        Returns:
            HTML report as string
        """
        severity_colors = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#17a2b8",
        }

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for comment in comments:
            if comment.severity in severity_counts:
                severity_counts[comment.severity] += 1

        html_parts = [
            "<!DOCTYPE html>\n<html lang='en'>\n<head>\n",
            "  <meta charset='UTF-8'>\n",
            "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n",
            f"  <title>PR #{pr_number} - {review_type.replace('_', ' ').title()} Report</title>\n",
            "  <style>\n",
            "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; ",
            "line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; ",
            "background: #f5f5f5; }\n",
            "    .header { background: white; padding: 30px; border-radius: 8px; ",
            "margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }\n",
            "    .header h1 { margin: 0 0 10px 0; color: #2c3e50; }\n",
            "    .header .meta { color: #7f8c8d; font-size: 14px; }\n",
            "    .summary { display: flex; gap: 15px; margin-bottom: 20px; }\n",
            "    .summary-card { background: white; padding: 20px; border-radius: 8px; ",
            "flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }\n",
            "    .summary-card .count { font-size: 32px; font-weight: bold; margin: 10px 0; }\n",
            "    .summary-card .label { color: #7f8c8d; font-size: 14px; }\n",
            "    .comment { background: white; padding: 20px; border-radius: 8px; ",
            "margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); ",
            "border-left: 4px solid #3498db; }\n",
            "    .comment.critical { border-left-color: #dc3545; }\n",
            "    .comment.high { border-left-color: #fd7e14; }\n",
            "    .comment.medium { border-left-color: #ffc107; }\n",
            "    .comment.low { border-left-color: #17a2b8; }\n",
            "    .comment-header { display: flex; justify-content: space-between; ",
            "align-items: start; margin-bottom: 10px; }\n",
            "    .file-info { font-family: monospace; font-size: 14px; color: #2c3e50; }\n",
            "    .severity-badge { display: inline-block; padding: 4px 12px; ",
            "border-radius: 12px; font-size: 12px; font-weight: bold; ",
            "color: white; text-transform: uppercase; }\n",
            "    .issue { font-weight: 600; color: #2c3e50; margin-bottom: 8px; }\n",
            "    .suggestion { color: #34495e; background: #ecf0f1; padding: 12px; ",
            "border-radius: 4px; margin-top: 8px; }\n",
            "    .suggestion strong { display: block; margin-bottom: 4px; color: #27ae60; }\n",
            "    .meta-tag { display: inline-block; padding: 3px 8px; ",
            "background: #e8e8e8; border-radius: 3px; font-size: 11px; ",
            "margin-right: 5px; margin-top: 5px; }\n",
            "    .no-issues { background: white; padding: 40px; text-align: center; ",
            "border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }\n",
            "    .no-issues h2 { color: #27ae60; }\n",
            "  </style>\n</head>\n<body>\n",
            "  <div class='header'>\n",
            f"    <h1>PR #{pr_number} - {review_type.replace('_', ' ').title()} Report</h1>\n",
            f"    <div class='meta'>Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}</div>\n",
            "  </div>\n",
        ]

        html_parts.append("  <div class='summary'>\n")
        for sev, count in severity_counts.items():
            color = severity_colors.get(sev, "#6c757d")
            html_parts.append(
                f"    <div class='summary-card'>\n"
                f"      <div class='label'>{sev.upper()}</div>\n"
                f"      <div class='count' style='color: {color};'>{count}</div>\n"
                f"    </div>\n"
            )
        html_parts.append("  </div>\n")

        if not comments:
            html_parts.append(
                "  <div class='no-issues'>\n"
                "    <h2>✓ No Issues Found</h2>\n"
                "    <p>The code review completed successfully with no issues detected.</p>\n"
                "  </div>\n"
            )
        else:
            for comment in comments:
                severity_class = comment.severity.lower()
                severity_color = severity_colors.get(comment.severity, "#6c757d")

                line_display = f"Line {comment.line}" if comment.line else "File-level"

                html_parts.append(f"  <div class='comment {severity_class}'>\n")
                html_parts.append("    <div class='comment-header'>\n")
                html_parts.append(
                    f"      <div class='file-info'>{escape(comment.file)} - {line_display}</div>\n"
                )
                html_parts.append(
                    f"      <span class='severity-badge' style='background: {severity_color};'>"
                    f"{comment.severity}</span>\n"
                )
                html_parts.append("    </div>\n")
                html_parts.append(f"    <div class='issue'>{escape(comment.issue)}</div>\n")
                html_parts.append(
                    f"    <div class='suggestion'><strong>Suggestion:</strong> "
                    f"{escape(comment.suggestion)}</div>\n"
                )

                if comment.wcag_criteria or comment.category:
                    html_parts.append("    <div>\n")
                    if comment.wcag_criteria:
                        html_parts.append(
                            f"      <span class='meta-tag'>WCAG {escape(comment.wcag_criteria)}</span>\n"
                        )
                    if comment.category:
                        html_parts.append(
                            f"      <span class='meta-tag'>{escape(comment.category)}</span>\n"
                        )
                    html_parts.append("    </div>\n")

                html_parts.append("  </div>\n")

        html_parts.append("</body>\n</html>")

        return "".join(html_parts)
