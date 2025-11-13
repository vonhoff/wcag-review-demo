"""Main orchestrator for Anthropic-powered code review."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

    import anthropic

from src.anthropic_client_factory import AnthropicClientFactory, MockAnthropicClient
from src.anthropic_prompt_service import AnthropicPromptService
from src.anthropic_response_parser import AnthropicResponseParser, ReviewComment
from src.github_diff_fetcher import GitHubDiffFetcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AnthropicCodeReview:
    """Orchestrates accessibility and code review analysis using Claude API."""

    client: anthropic.Anthropic | MockAnthropicClient

    EXCLUDE_PATTERNS: ClassVar[list[str]] = [
        r"package-lock\.json$",
        r"yarn\.lock$",
        r"\.min\.js$",
        r"\.min\.css$",
        r"dist/",
        r"build/",
        r"node_modules/",
    ]

    MAX_DIFF_SIZE = 50000

    def __init__(
        self,
        github_token: str,
        repository_name: str,
        anthropic_api_key: str,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """Initialize the code review orchestrator.

        Args:
            github_token: GitHub API token
            repository_name: Full repository name (owner/repo)
            anthropic_api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens for responses
        """
        self.github_fetcher = GitHubDiffFetcher(github_token, repository_name)
        self.client = AnthropicClientFactory.create_client(anthropic_api_key)
        self.model = model or AnthropicClientFactory.get_default_model()
        self.max_tokens = max_tokens or AnthropicClientFactory.get_default_max_tokens()
        self.prompt_service = AnthropicPromptService()
        self.parser = AnthropicResponseParser()

    def review_pr(self, pr_number: int) -> tuple[list[ReviewComment], str]:
        """Conduct unified accessibility-focused code review of a PR.

        Args:
            pr_number: Pull request number

        Returns:
            Tuple of (comments list, HTML report)
        """
        logger.info("Starting accessibility-focused code review for PR #%d", pr_number)

        raw_diff = self.github_fetcher.fetch_pr_diff(pr_number)
        logger.info("Raw diff size: %d characters", len(raw_diff))
        filtered_diff = self._filter_diff(raw_diff)

        if not filtered_diff.strip():
            logger.warning("No relevant changes found after filtering")
            return [], self.parser.generate_html_report([], pr_number)

        logger.info("Filtered diff size: %d characters", len(filtered_diff))

        prompt = self.prompt_service.build_prompt(filtered_diff)

        # Save debug files
        self._save_debug_files(pr_number, raw_diff, filtered_diff, prompt)

        response_text = self._call_claude(prompt)
        comments = self.parser.parse_response(response_text)

        logger.info("Found %d issues", len(comments))

        html_report = self.parser.generate_html_report(comments, pr_number)

        return comments, html_report

    def _filter_diff(self, diff: str) -> str:
        """Filter diff to exclude large/non-essential files.

        Args:
            diff: Raw git diff

        Returns:
            Filtered diff content
        """
        lines = diff.split("\n")
        filtered_lines = []
        current_file_lines: list[str] = []
        current_filename: str | None = None
        skip_file = False
        included_files: list[str] = []
        excluded_files: list[str] = []

        for line in lines:
            if line.startswith(("--- a/", "+++ b/")):
                # Process previous file if any
                if current_filename is not None and not skip_file:
                    filtered_lines.extend(current_file_lines)
                    included_files.append(current_filename)
                elif current_filename is not None:
                    excluded_files.append(current_filename)

                # Start new file
                current_filename = line[6:]
                current_file_lines = [line]
                skip_file = any(re.search(pattern, current_filename) for pattern in self.EXCLUDE_PATTERNS)
            else:
                if current_file_lines:
                    current_file_lines.append(line)

        # Process last file
        if current_filename is not None and not skip_file:
            filtered_lines.extend(current_file_lines)
            included_files.append(current_filename)
        elif current_filename is not None:
            excluded_files.append(current_filename)

        filtered_diff = "\n".join(filtered_lines)

        # Log file information
        if included_files:
            logger.info("Included files: %s", ", ".join(included_files))
        if excluded_files:
            logger.info("Excluded files: %s", ", ".join(excluded_files))

        # Check size after filtering
        original_size = len(filtered_diff)
        if original_size > self.MAX_DIFF_SIZE:
            logger.warning(
                "Filtered diff size (%d) exceeds limit (%d), truncating",
                original_size,
                self.MAX_DIFF_SIZE,
            )
            filtered_diff = filtered_diff[: self.MAX_DIFF_SIZE]

        return filtered_diff

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API with the given prompt.

        Args:
            prompt: Prompt text

        Returns:
            Response text from Claude

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            # Handle both real API response (object with .content) and mock response (dict)
            if hasattr(response, "content"):
                # Real API response
                content_blocks = response.content
            else:
                # Mock response (dict)
                content_blocks = response.get("content", [])

            text_parts = []
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block["text"])
                elif hasattr(block, "type") and block.type == "text":
                    text_parts.append(block.text)

            return "".join(text_parts)

        except Exception:
            logger.exception("Claude API call failed")
            raise

    def _save_debug_files(
        self, pr_number: int, raw_diff: str, filtered_diff: str, prompt: str
    ) -> None:
        """Save debug files for troubleshooting.

        Args:
            pr_number: Pull request number
            raw_diff: Raw diff from GitHub
            filtered_diff: Filtered diff after processing
            prompt: Full prompt sent to Claude
        """
        debug_dir = Path("reports") / "debug" / f"pr_{pr_number}"
        debug_dir.mkdir(parents=True, exist_ok=True)

        # Save raw diff
        (debug_dir / "01_raw_diff.diff").write_text(raw_diff, encoding="utf-8")
        logger.info("Saved raw diff to %s", debug_dir / "01_raw_diff.diff")

        # Save filtered diff
        (debug_dir / "02_filtered_diff.diff").write_text(filtered_diff, encoding="utf-8")
        logger.info("Saved filtered diff to %s", debug_dir / "02_filtered_diff.diff")

        # Save full prompt
        (debug_dir / "03_prompt.txt").write_text(prompt, encoding="utf-8")
        logger.info("Saved prompt to %s", debug_dir / "03_prompt.txt")

    def save_report(self, html_report: str, output_path: Path) -> None:
        """Save HTML report to file.

        Args:
            html_report: HTML report content
            output_path: Path to save the report
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_report, encoding="utf-8")
        logger.info("Report saved to %s", output_path)

    def close(self) -> None:
        """Clean up resources."""
        self.github_fetcher.close()

    def __enter__(self) -> AnthropicCodeReview:  # noqa: PYI034
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()
