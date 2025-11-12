"""Main Module - Orchestrates the PR diff analysis workflow.

This module provides the main entry point and orchestrates the workflow of
fetching PR diffs, filtering them, and sending them to Claude for analysis.
"""

import os
import sys

from dotenv import load_dotenv

from src.claude_client import ClaudeClient
from src.diff_filter import DiffFilter
from src.github_diff_fetcher import GitHubDiffFetcher


class PRDiffAnalyzer:
    """Orchestrates the PR diff analysis workflow.

    This class follows the Dependency Inversion Principle by depending on
    abstractions (the client classes) rather than concrete implementations.
    It also follows the Single Responsibility Principle by focusing on
    orchestrating the workflow.

    Attributes:
        github_fetcher: GitHub diff fetcher instance.
        diff_filter: Diff filter instance.
        claude_client: Claude API client instance.
    """

    def __init__(
        self,
        github_token: str,
        repository_name: str,
        anthropic_api_key: str,
        claude_model: str | None = None,
        max_tokens: int | None = None,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> None:
        """Initialize the PR diff analyzer.

        Args:
            github_token: GitHub personal access token.
            repository_name: Full repository name (owner/repo).
            anthropic_api_key: Anthropic API key.
            claude_model: Claude model to use (optional).
            max_tokens: Maximum tokens for Claude responses (optional).
            include_patterns: File patterns to include in filtering (optional).
            exclude_patterns: File patterns to exclude in filtering (optional).
        """
        self.github_fetcher = GitHubDiffFetcher(github_token, repository_name)
        self.diff_filter = DiffFilter(
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
        self.claude_client = ClaudeClient(
            api_key=anthropic_api_key,
            model=claude_model,
            max_tokens=max_tokens,
        )

    def analyze_pr(
        self,
        pr_number: int,
        analysis_type: str = "review",
        include_pr_info: bool = True,
    ) -> dict[str, str]:
        """Analyze a pull request.

        Args:
            pr_number: The pull request number.
            analysis_type: Type of analysis ('review', 'summary', 'security', 'accessibility').
            include_pr_info: Whether to include PR information as context.

        Returns:
            Dictionary containing the analysis results.
        """
        print(f"Fetching PR #{pr_number} diff...")
        raw_diff = self.github_fetcher.fetch_pr_diff(pr_number)

        print("Filtering diff...")
        filtered_diff = self.diff_filter.filter_diff(raw_diff)

        if not filtered_diff.strip():
            return {
                "error": "No changes matched the filter criteria",
                "pr_number": str(pr_number),
            }

        # Get diff summary
        summary = self.diff_filter.get_summary(filtered_diff)
        print(f"Filtered diff contains {summary['files_changed']} files with "
              f"{summary['total_changes']} total changes")

        # Get PR context if requested
        context = None
        if include_pr_info:
            print("Fetching PR information...")
            pr_info = self.github_fetcher.get_pr_info(pr_number)
            context = f"PR Title: {pr_info['title']}\n"
            if pr_info["description"]:
                context += f"Description: {pr_info['description']}"

        print(f"Sending to Claude for {analysis_type} analysis...")
        analysis = self.claude_client.analyze_diff(
            diff=filtered_diff,
            context=context,
            analysis_type=analysis_type,
        )

        return {
            "pr_number": str(pr_number),
            "analysis_type": analysis_type,
            "summary": summary,
            "analysis": analysis,
        }

    def close(self) -> None:
        """Close all client connections."""
        self.github_fetcher.close()

    def __enter__(self) -> "PRDiffAnalyzer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()


def load_environment() -> dict[str, str]:
    """Load environment variables.

    Returns:
        Dictionary containing required environment variables.

    Raises:
        ValueError: If required environment variables are missing.
    """
    load_dotenv()

    required_vars = {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "GITHUB_REPOSITORY": os.getenv("GITHUB_REPOSITORY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    }

    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return {
        "github_token": required_vars["GITHUB_TOKEN"],
        "repository_name": required_vars["GITHUB_REPOSITORY"],
        "anthropic_api_key": required_vars["ANTHROPIC_API_KEY"],
        "claude_model": os.getenv("CLAUDE_MODEL"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "4096")),
    }


def main() -> None:
    """Main entry point for the PR diff analyzer."""
    try:
        # Load environment variables
        env_config = load_environment()

        # Get PR number from environment or command line
        pr_number_str = os.getenv("GITHUB_PR_NUMBER")
        if not pr_number_str and len(sys.argv) > 1:
            pr_number_str = sys.argv[1]

        if not pr_number_str:
            print("Error: PR number not provided")
            print("Usage: python -m src.main <pr_number>")
            print("Or set GITHUB_PR_NUMBER environment variable")
            sys.exit(1)

        try:
            pr_number = int(pr_number_str)
        except ValueError:
            print(f"Error: Invalid PR number '{pr_number_str}'")
            sys.exit(1)

        # Get analysis type from environment or default to 'review'
        analysis_type = os.getenv("ANALYSIS_TYPE", "review")

        # Create and run the analyzer
        with PRDiffAnalyzer(
            github_token=env_config["github_token"],
            repository_name=env_config["repository_name"],
            anthropic_api_key=env_config["anthropic_api_key"],
            claude_model=env_config["claude_model"],
            max_tokens=env_config["max_tokens"],
        ) as analyzer:
            result = analyzer.analyze_pr(pr_number, analysis_type=analysis_type)

            if "error" in result:
                print(f"\nError: {result['error']}")
                sys.exit(1)

            # Print results
            print("\n" + "=" * 80)
            print(f"PR #{result['pr_number']} Analysis ({result['analysis_type']})")
            print("=" * 80)
            print("\nSummary:")
            print(f"  Files changed: {result['summary']['files_changed']}")
            print(f"  Additions: {result['summary']['additions']}")
            print(f"  Deletions: {result['summary']['deletions']}")
            print(f"\nAnalysis:\n{result['analysis']}")
            print("=" * 80)

    except Exception as e:
        print(f"Error: {e!s}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
