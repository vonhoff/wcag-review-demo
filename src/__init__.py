"""WCAG Review Demo - GitHub PR Diff Analyzer.

A Python utility to fetch git diffs from GitHub PRs, filter them,
and send them to the Anthropic Claude API for analysis.
"""

__version__ = "0.1.0"

from src.claude_client import ClaudeClient
from src.diff_filter import DiffFilter
from src.github_diff_fetcher import GitHubDiffFetcher
from src.main import PRDiffAnalyzer

__all__ = [
    "ClaudeClient",
    "DiffFilter",
    "GitHubDiffFetcher",
    "PRDiffAnalyzer",
]
