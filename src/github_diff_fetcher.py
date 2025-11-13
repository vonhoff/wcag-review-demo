"""Fetches git diffs from GitHub Pull Requests."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from github import Auth, Github

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from github.PullRequest import PullRequest


class GitHubDiffFetcher:
    """Fetches git diffs from GitHub PRs."""

    def __init__(self, token: str, repository_name: str) -> None:
        if not token:
            raise ValueError("GitHub token cannot be empty")
        if not repository_name:
            raise ValueError("Repository name cannot be empty")

        auth = Auth.Token(token)
        self.github_client = Github(auth=auth)
        self.repository_name = repository_name

    def fetch_pr_diff(self, pr_number: int) -> str:
        """Fetch unified diff for a PR.
        
        Returns only the files that are actually changed in the PR.
        """
        if pr_number <= 0:
            raise ValueError("PR number must be a positive integer")

        try:
            repo = self.github_client.get_repo(self.repository_name)
            pull_request = repo.get_pull(pr_number)
            
            # Log PR info for debugging
            logger.info(
                "PR #%d: %s -> %s (base: %s, head: %s)",
                pr_number,
                pull_request.base.ref,
                pull_request.head.ref,
                pull_request.base.sha[:7] if pull_request.base.sha else "unknown",
                pull_request.head.sha[:7] if pull_request.head.sha else "unknown",
            )
            
            # Get list of changed files for logging
            files = pull_request.get_files()
            changed_files = [f.filename for f in files if f.status in ("added", "modified", "removed")]
            if changed_files:
                logger.info("Changed files in PR: %s", ", ".join(changed_files))
            else:
                logger.warning("No changed files found in PR")
            
            # Use the PR's diff property which gives us the unified diff directly
            # This only includes files that are actually changed in the PR
            diff = pull_request.diff
            if not diff:
                raise Exception(f"PR #{pr_number} has no diff (might be empty or closed)")
            
            return diff
        except Exception as e:
            raise Exception(f"Failed to fetch PR #{pr_number} diff: {e!s}") from e

    def get_pr_info(self, pr_number: int) -> dict[str, str | None]:
        """Get PR metadata."""
        if pr_number <= 0:
            raise ValueError("PR number must be a positive integer")

        try:
            repo = self.github_client.get_repo(self.repository_name)
            pull_request = repo.get_pull(pr_number)

            return {
                "title": pull_request.title,
                "description": pull_request.body,
                "base_branch": pull_request.base.ref,
                "head_branch": pull_request.head.ref,
                "state": pull_request.state,
                "url": pull_request.html_url,
            }
        except Exception as e:
            raise Exception(f"Failed to fetch PR #{pr_number} info: {e!s}") from e

    def close(self) -> None:
        """Close GitHub client."""
        self.github_client.close()

    def __enter__(self) -> GitHubDiffFetcher:  # noqa: PYI034
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()
