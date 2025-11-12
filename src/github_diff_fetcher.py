"""GitHub Diff Fetcher Module.

This module provides functionality to fetch git diffs from GitHub Pull Requests
using the GitHub API.
"""


from github import Auth, Github
from github.PullRequest import PullRequest


class GitHubDiffFetcher:
    """Fetches git diffs from GitHub Pull Requests.

    This class follows the Single Responsibility Principle by focusing solely
    on fetching diffs from GitHub PRs.

    Attributes:
        github_client: Authenticated GitHub client instance.
        repository_name: Full repository name (owner/repo).
    """

    def __init__(self, token: str, repository_name: str) -> None:
        """Initialize the GitHub diff fetcher.

        Args:
            token: GitHub personal access token for authentication.
            repository_name: Full repository name in format 'owner/repo'.

        Raises:
            ValueError: If token or repository_name is empty.
        """
        if not token:
            raise ValueError("GitHub token cannot be empty")
        if not repository_name:
            raise ValueError("Repository name cannot be empty")

        auth = Auth.Token(token)
        self.github_client = Github(auth=auth)
        self.repository_name = repository_name

    def fetch_pr_diff(self, pr_number: int) -> str:
        """Fetch the unified diff for a specific pull request.

        Args:
            pr_number: The pull request number.

        Returns:
            The unified diff as a string.

        Raises:
            ValueError: If pr_number is invalid.
            Exception: If the PR cannot be fetched or diff cannot be retrieved.
        """
        if pr_number <= 0:
            raise ValueError("PR number must be a positive integer")

        try:
            repo = self.github_client.get_repo(self.repository_name)
            pull_request = repo.get_pull(pr_number)

            # Get the diff using the GitHub API
            return self._get_pr_diff(pull_request)


        except Exception as e:
            raise Exception(f"Failed to fetch PR #{pr_number} diff: {e!s}") from e

    def _get_pr_diff(self, pull_request: PullRequest) -> str:
        """Get the unified diff from a pull request object.

        Args:
            pull_request: The GitHub PullRequest object.

        Returns:
            The unified diff as a string.
        """
        # Get files changed in the PR
        files = pull_request.get_files()

        diff_parts = []
        for file in files:
            if file.patch:  # Only include files with patches (excludes binary files)
                diff_parts.append(f"--- a/{file.filename}")
                diff_parts.append(f"+++ b/{file.filename}")
                diff_parts.append(file.patch)
                diff_parts.append("")  # Empty line between files

        return "\n".join(diff_parts)

    def get_pr_info(self, pr_number: int) -> dict[str, str | None]:
        """Get basic information about a pull request.

        Args:
            pr_number: The pull request number.

        Returns:
            Dictionary containing PR title, description, and base branch.

        Raises:
            ValueError: If pr_number is invalid.
            Exception: If the PR cannot be fetched.
        """
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
        """Close the GitHub client connection."""
        self.github_client.close()

    def __enter__(self) -> "GitHubDiffFetcher":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()
