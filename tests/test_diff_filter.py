"""Unit tests for the Diff Filter module."""


from src.diff_filter import DiffFilter


class TestDiffFilter:
    """Test suite for DiffFilter class."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default parameters."""
        filter = DiffFilter()
        assert filter.include_patterns == []
        assert filter.exclude_patterns == []
        assert filter.min_line_changes == 0
        assert filter.max_line_changes is None

    def test_init_with_patterns(self) -> None:
        """Test initialization with patterns."""
        filter = DiffFilter(
            include_patterns=[r"\.py$", r"\.js$"],
            exclude_patterns=[r"test_", r"__pycache__"],
            min_line_changes=5,
            max_line_changes=100,
        )
        assert len(filter.include_patterns) == 2
        assert len(filter.exclude_patterns) == 2
        assert filter.min_line_changes == 5
        assert filter.max_line_changes == 100

    def test_filter_diff_empty_input(self) -> None:
        """Test filtering with empty input."""
        filter = DiffFilter()
        result = filter.filter_diff("")
        assert result == ""

    def test_filter_diff_with_no_filters(self) -> None:
        """Test filtering with no filters applied."""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
-old line
+new line
 context line"""

        filter = DiffFilter()
        result = filter.filter_diff(diff)
        assert "test.py" in result
        assert "-old line" in result
        assert "+new line" in result

    def test_filter_diff_with_include_pattern(self) -> None:
        """Test filtering with include pattern."""
        diff = """--- a/main.py
+++ b/main.py
@@ -1,1 +1,1 @@
-old
+new

--- a/test.txt
+++ b/test.txt
@@ -1,1 +1,1 @@
-old
+new"""

        filter = DiffFilter(include_patterns=[r"\.py$"])
        result = filter.filter_diff(diff)

        assert "main.py" in result
        assert "test.txt" not in result

    def test_filter_diff_with_exclude_pattern(self) -> None:
        """Test filtering with exclude pattern."""
        diff = """--- a/main.py
+++ b/main.py
@@ -1,1 +1,1 @@
-old
+new

--- a/test_main.py
+++ b/test_main.py
@@ -1,1 +1,1 @@
-old
+new"""

        filter = DiffFilter(exclude_patterns=[r"^test_"])
        result = filter.filter_diff(diff)

        assert "main.py" in result
        assert "test_main.py" not in result

    def test_filter_diff_exclude_takes_precedence(self) -> None:
        """Test that exclude patterns take precedence over include patterns."""
        diff = """--- a/main.py
+++ b/main.py
@@ -1,1 +1,1 @@
-old
+new

--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
-old
+new"""

        filter = DiffFilter(
            include_patterns=[r"\.py$"],
            exclude_patterns=[r"^test"],
        )
        result = filter.filter_diff(diff)

        assert "main.py" in result
        assert "test.py" not in result

    def test_filter_diff_with_min_line_changes(self) -> None:
        """Test filtering with minimum line changes."""
        diff = """--- a/small.py
+++ b/small.py
@@ -1,1 +1,1 @@
-old
+new

--- a/large.py
+++ b/large.py
@@ -1,5 +1,5 @@
-line1
-line2
-line3
+new1
+new2
+new3"""

        filter = DiffFilter(min_line_changes=4)
        result = filter.filter_diff(diff)

        assert "small.py" not in result
        assert "large.py" in result

    def test_filter_diff_with_max_line_changes(self) -> None:
        """Test filtering with maximum line changes."""
        diff = """--- a/small.py
+++ b/small.py
@@ -1,1 +1,1 @@
-old
+new

--- a/large.py
+++ b/large.py
@@ -1,10 +1,10 @@
-line1
-line2
-line3
-line4
-line5
+new1
+new2
+new3
+new4
+new5"""

        filter = DiffFilter(max_line_changes=3)
        result = filter.filter_diff(diff)

        assert "small.py" in result
        assert "large.py" not in result

    def test_count_additions(self) -> None:
        """Test counting additions in diff lines."""
        lines = [
            "--- a/test.py",
            "+++ b/test.py",
            "@@ -1,3 +1,4 @@",
            " context",
            "-removed",
            "+added1",
            "+added2",
        ]

        filter = DiffFilter()
        count = filter._count_additions(lines)
        assert count == 2

    def test_count_deletions(self) -> None:
        """Test counting deletions in diff lines."""
        lines = [
            "--- a/test.py",
            "+++ b/test.py",
            "@@ -1,4 +1,2 @@",
            " context",
            "-removed1",
            "-removed2",
            "-removed3",
            "+added",
        ]

        filter = DiffFilter()
        count = filter._count_deletions(lines)
        assert count == 3

    def test_get_summary_empty_diff(self) -> None:
        """Test getting summary of empty diff."""
        filter = DiffFilter()
        summary = filter.get_summary("")

        assert summary["files_changed"] == 0
        assert summary["additions"] == 0
        assert summary["deletions"] == 0
        assert summary["total_changes"] == 0

    def test_get_summary_with_changes(self) -> None:
        """Test getting summary with changes."""
        diff = """--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,2 @@
-old1
+new1

--- a/file2.py
+++ b/file2.py
@@ -1,3 +1,2 @@
-old2
-old3
+new2"""

        filter = DiffFilter()
        summary = filter.get_summary(diff)

        assert summary["files_changed"] == 2
        assert summary["additions"] == 2
        assert summary["deletions"] == 3
        assert summary["total_changes"] == 5

    def test_parse_diff_by_files(self) -> None:
        """Test parsing diff into individual files."""
        diff = """--- a/file1.py
+++ b/file1.py
@@ -1,1 +1,1 @@
-old
+new

--- a/file2.py
+++ b/file2.py
@@ -1,1 +1,2 @@
 context
+added"""

        filter = DiffFilter()
        files = filter._parse_diff_by_files(diff)

        assert len(files) == 2
        assert files[0]["filename"] == "file1.py"
        assert files[1]["filename"] == "file2.py"
        assert files[0]["additions"] == 1
        assert files[0]["deletions"] == 1
        assert files[1]["additions"] == 1
        assert files[1]["deletions"] == 0

    def test_filter_diff_with_complex_pattern(self) -> None:
        """Test filtering with complex regex patterns."""
        diff = """--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,1 @@
-old
+new

--- a/tests/test_main.py
+++ b/tests/test_main.py
@@ -1,1 +1,1 @@
-old
+new

--- a/docs/readme.md
+++ b/docs/readme.md
@@ -1,1 +1,1 @@
-old
+new"""

        filter = DiffFilter(
            include_patterns=[r"^src/", r"^tests/"],
            exclude_patterns=[r"\.md$"],
        )
        result = filter.filter_diff(diff)

        assert "src/main.py" in result
        assert "tests/test_main.py" in result
        assert "docs/readme.md" not in result
