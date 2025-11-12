"""Diff Filter Module.

This module provides functionality to filter git diffs based on various criteria
such as file patterns, change types, and content patterns.
"""

import re


class DiffFilter:
    """Filters git diffs based on configurable criteria.

    This class follows the Single Responsibility Principle by focusing solely
    on filtering diffs. It uses the Strategy pattern to allow flexible filtering.

    Attributes:
        include_patterns: List of regex patterns for files to include.
        exclude_patterns: List of regex patterns for files to exclude.
        min_line_changes: Minimum number of line changes to include a file.
        max_line_changes: Maximum number of line changes to include a file.
    """

    def __init__(
        self,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        min_line_changes: int = 0,
        max_line_changes: int | None = None,
    ) -> None:
        """Initialize the diff filter.

        Args:
            include_patterns: List of regex patterns for files to include.
                If None, all files are included by default.
            exclude_patterns: List of regex patterns for files to exclude.
                These take precedence over include_patterns.
            min_line_changes: Minimum number of line changes to include a file.
            max_line_changes: Maximum number of line changes to include a file.
                If None, no maximum limit is applied.
        """
        self.include_patterns = [re.compile(p) for p in (include_patterns or [])]
        self.exclude_patterns = [re.compile(p) for p in (exclude_patterns or [])]
        self.min_line_changes = max(0, min_line_changes)
        self.max_line_changes = max_line_changes

    def filter_diff(self, diff: str) -> str:
        """Filter a unified diff based on configured criteria.

        Args:
            diff: The unified diff string to filter.

        Returns:
            The filtered diff string containing only matching files.
        """
        if not diff.strip():
            return ""

        # Parse the diff into individual file changes
        file_diffs = self._parse_diff_by_files(diff)

        # Filter each file diff
        filtered_diffs = []
        for file_diff in file_diffs:
            if self._should_include_file_diff(file_diff):
                filtered_diffs.append(file_diff["content"])

        return "\n\n".join(filtered_diffs)

    def _parse_diff_by_files(self, diff: str) -> list[dict[str, str | int]]:
        """Parse a unified diff into individual file changes.

        Args:
            diff: The unified diff string.

        Returns:
            List of dictionaries containing file diff information.
        """
        files = []
        current_file = None
        current_content = []

        for line in diff.split("\n"):
            # Detect start of a new file diff
            if line.startswith("--- a/"):
                if current_file and current_content:
                    files.append({
                        "filename": current_file,
                        "content": "\n".join(current_content),
                        "additions": self._count_additions(current_content),
                        "deletions": self._count_deletions(current_content),
                    })
                    current_content = []

                # Extract filename
                current_file = line[6:]  # Remove "--- a/"
                current_content.append(line)
            elif current_file:
                current_content.append(line)

        # Add the last file
        if current_file and current_content:
            files.append({
                "filename": current_file,
                "content": "\n".join(current_content),
                "additions": self._count_additions(current_content),
                "deletions": self._count_deletions(current_content),
            })

        return files

    def _should_include_file_diff(self, file_diff: dict[str, str | int]) -> bool:
        """Determine if a file diff should be included based on filters.

        Args:
            file_diff: Dictionary containing file diff information.

        Returns:
            True if the file should be included, False otherwise.
        """
        filename = str(file_diff["filename"])
        additions = int(file_diff["additions"])
        deletions = int(file_diff["deletions"])
        total_changes = additions + deletions

        # Check exclusion patterns first (they take precedence)
        if self.exclude_patterns:
            for pattern in self.exclude_patterns:
                if pattern.search(filename):
                    return False

        # Check inclusion patterns
        if self.include_patterns:
            included = False
            for pattern in self.include_patterns:
                if pattern.search(filename):
                    included = True
                    break
            if not included:
                return False

        # Check line change limits
        if total_changes < self.min_line_changes:
            return False

        return not (self.max_line_changes is not None and total_changes > self.max_line_changes)

    def _count_additions(self, lines: list[str]) -> int:
        """Count the number of added lines in a diff.

        Args:
            lines: List of diff lines.

        Returns:
            Number of lines starting with '+' (excluding +++).
        """
        return sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))

    def _count_deletions(self, lines: list[str]) -> int:
        """Count the number of deleted lines in a diff.

        Args:
            lines: List of diff lines.

        Returns:
            Number of lines starting with '-' (excluding ---).
        """
        return sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))

    def get_summary(self, diff: str) -> dict[str, int]:
        """Get a summary of changes in a diff.

        Args:
            diff: The unified diff string.

        Returns:
            Dictionary containing summary statistics.
        """
        file_diffs = self._parse_diff_by_files(diff)

        total_additions = sum(int(f["additions"]) for f in file_diffs)
        total_deletions = sum(int(f["deletions"]) for f in file_diffs)

        return {
            "files_changed": len(file_diffs),
            "additions": total_additions,
            "deletions": total_deletions,
            "total_changes": total_additions + total_deletions,
        }
