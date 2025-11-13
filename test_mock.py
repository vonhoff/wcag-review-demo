from src.anthropic_code_review import AnthropicCodeReview
import tempfile
import os

# Test with mock API key
with tempfile.TemporaryDirectory() as temp_dir:
    reviewer = AnthropicCodeReview(
        github_token='dummy',
        repository_name='test/repo',
        anthropic_api_key='TEST'
    )

    # Mock the GitHub fetcher methods
    reviewer.github_fetcher.get_pr_info = lambda x: {'title': 'Test PR', 'description': 'Test description'}
    reviewer.github_fetcher.fetch_pr_diff = lambda x: '''--- a/test.js
+++ b/test.js
@@ -1 +1 @@
-old code
+new code'''

    comments, html_report = reviewer.review_pr(123)

    print(f'Found {len(comments)} comments')
    print(f'HTML report contains WCAG table: {"WCAG Compliance Check" in html_report}')
    print(f'First comment issue: {comments[0].issue if comments else "No comments"}')
    print('Mock API test successful!')
