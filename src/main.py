"""Main entry point for Anthropic-powered code review."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.anthropic_code_review import AnthropicCodeReview


def load_config() -> dict[str, str]:
    """Load configuration from environment variables."""
    load_dotenv()

    required_vars = {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "GITHUB_REPOSITORY": os.getenv("GITHUB_REPOSITORY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    }

    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return {
        "github_token": required_vars["GITHUB_TOKEN"],
        "repository_name": required_vars["GITHUB_REPOSITORY"],
        "anthropic_api_key": required_vars["ANTHROPIC_API_KEY"],
        "model": os.getenv("CLAUDE_MODEL"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "8192")),
    }


def main() -> None:
    """Run accessibility and code review analysis."""
    try:
        config = load_config()

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

        review_type = os.getenv("REVIEW_TYPE", "accessibility")

        with AnthropicCodeReview(
            github_token=config["github_token"],
            repository_name=config["repository_name"],
            anthropic_api_key=config["anthropic_api_key"],
            model=config["model"],
            max_tokens=config["max_tokens"],
        ) as reviewer:
            if review_type == "accessibility":
                comments, html_report = reviewer.review_pr_accessibility(pr_number)
            else:
                comments, html_report = reviewer.review_pr_code_quality(pr_number)

            output_dir = Path("reports")
            output_file = output_dir / f"pr_{pr_number}_{review_type}_report.html"
            reviewer.save_report(html_report, output_file)

            print(f"\n{'=' * 80}")
            print(f"PR #{pr_number} - {review_type.title()} Review")
            print(f"{'=' * 80}")
            print(f"\nFound {len(comments)} issues")
            print(f"Report saved: {output_file}")
            print(f"{'=' * 80}\n")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
