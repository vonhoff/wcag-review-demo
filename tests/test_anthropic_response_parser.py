"""Tests for AnthropicResponseParser."""

import pytest

from src.anthropic_response_parser import AnthropicResponseParser, ReviewComment


class TestAnthropicResponseParser:
    """Test suite for AnthropicResponseParser."""

    def test_parse_valid_response(self) -> None:
        """Test parsing valid JSON response."""
        response = """[
            {
                "file": "test.html",
                "line": 10,
                "issue": "Missing alt text",
                "suggestion": "Add alt attribute",
                "severity": "high",
                "wcag_criteria": "1.1.1"
            }
        ]"""

        comments = AnthropicResponseParser.parse_response(response)

        assert len(comments) == 1
        assert comments[0].file == "test.html"
        assert comments[0].line == 10
        assert comments[0].issue == "Missing alt text"
        assert comments[0].severity == "high"
        assert comments[0].wcag_criteria == "1.1.1"

    def test_parse_response_with_code_blocks(self) -> None:
        """Test parsing response wrapped in code blocks."""
        response = """```json
        [
            {
                "file": "app.py",
                "line": null,
                "issue": "Test issue",
                "suggestion": "Test suggestion",
                "severity": "low",
                "category": "style"
            }
        ]
        ```"""

        comments = AnthropicResponseParser.parse_response(response)

        assert len(comments) == 1
        assert comments[0].file == "app.py"
        assert comments[0].line is None

    def test_parse_invalid_json(self) -> None:
        """Test parsing invalid JSON raises error."""
        with pytest.raises(ValueError, match="Invalid JSON response"):
            AnthropicResponseParser.parse_response("not valid json")

    def test_parse_non_array_response(self) -> None:
        """Test parsing non-array JSON raises error."""
        with pytest.raises(TypeError, match="Response must be a JSON array"):
            AnthropicResponseParser.parse_response('{"error": "test"}')

    def test_parse_missing_required_field(self) -> None:
        """Test parsing response with missing required field."""
        response = """[
            {
                "file": "test.py",
                "issue": "Missing suggestion field",
                "severity": "medium"
            }
        ]"""

        with pytest.raises(ValueError, match="Missing required field"):
            AnthropicResponseParser.parse_response(response)

    def test_generate_html_report_with_comments(self) -> None:
        """Test HTML report generation with comments."""
        comments = [
            ReviewComment(
                file="test.html",
                line=10,
                issue="Missing alt text",
                suggestion="Add alt attribute",
                severity="high",
                wcag_criteria="1.1.1",
            )
        ]

        html = AnthropicResponseParser.generate_html_report(
            comments, pr_number=123, review_type="accessibility"
        )

        assert "<!DOCTYPE html>" in html
        assert "test.html" in html
        assert "Missing alt text" in html
        assert "Add alt attribute" in html
        assert "high" in html.lower()
        assert "WCAG 1.1.1" in html

    def test_generate_html_report_empty_comments(self) -> None:
        """Test HTML report generation with no comments."""
        html = AnthropicResponseParser.generate_html_report(
            [], pr_number=123, review_type="code_review"
        )

        assert "<!DOCTYPE html>" in html
        assert "No Issues Found" in html

    def test_generate_html_report_escapes_html(self) -> None:
        """Test that HTML report properly escapes HTML in comments."""
        comments = [
            ReviewComment(
                file="<script>test.js</script>",
                line=1,
                issue="Test <b>issue</b>",
                suggestion="Test <i>suggestion</i>",
                severity="medium",
            )
        ]

        html = AnthropicResponseParser.generate_html_report(
            comments, pr_number=1, review_type="code_review"
        )

        assert "&lt;script&gt;" in html
        assert "<script>" not in html or "<!DOCTYPE" in html

    def test_parse_multiple_comments(self) -> None:
        """Test parsing multiple comments."""
        response = """[
            {
                "file": "file1.py",
                "line": 1,
                "issue": "Issue 1",
                "suggestion": "Fix 1",
                "severity": "critical"
            },
            {
                "file": "file2.py",
                "line": 2,
                "issue": "Issue 2",
                "suggestion": "Fix 2",
                "severity": "low"
            }
        ]"""

        comments = AnthropicResponseParser.parse_response(response)

        assert len(comments) == 2
        assert comments[0].severity == "critical"
        assert comments[1].severity == "low"
