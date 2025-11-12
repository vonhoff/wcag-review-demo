"""Fetches git diffs from GitHub Pull Requests."""

from github import Auth, Github
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
        """Fetch unified diff for a PR."""
        if pr_number <= 0:
            raise ValueError("PR number must be a positive integer")

        try:
            repo = self.github_client.get_repo(self.repository_name)
            pull_request = repo.get_pull(pr_number)
            return self._get_pr_diff(pull_request)
        except Exception as e:
            raise Exception(f"Failed to fetch PR #{pr_number} diff: {e!s}") from e

    def _get_pr_diff(self, pull_request: PullRequest) -> str:
        """Convert PR files to unified diff format."""
        files = pull_request.get_files()
        diff_parts = []

        for file in files:
            if file.patch:
                diff_parts.append(f"--- a/{file.filename}")
                diff_parts.append(f"+++ b/{file.filename}")
                diff_parts.append(file.patch)
                diff_parts.append("")

        return "\n".join(diff_parts)

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

    def __enter__(self) -> "GitHubDiffFetcher":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()
