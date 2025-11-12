# WCAG Review Demo

Streamlined Python utility for AI-powered accessibility and code quality reviews using Anthropic Claude API. Focuses on WCAG compliance checks and code review analysis.

## Architecture

Clean, modular design with four core components:

- **`AnthropicClientFactory`** - Creates configured Claude API clients
- **`AnthropicPromptService`** - Builds accessibility and code review prompts
- **`AnthropicCodeReview`** - Main orchestrator for fetching diffs, filtering, and invoking Claude
- **`AnthropicResponseParser`** - Parses JSON responses and generates HTML reports

Supporting modules:
- **`GitHubDiffFetcher`** - Fetches PR diffs via GitHub API

## Features

- ✅ WCAG 2.1 AA accessibility compliance reviews
- ✅ Code quality and best practices analysis
- ✅ Automated diff filtering (excludes lock files, minified files)
- ✅ HTML report generation as workflow artifacts
- ✅ Python 3.11+ with full type hints
- ✅ Clean, testable, SOLID-compliant code

## Quick Start

### Installation

```bash
git clone https://github.com/vonhoff/wcag-review-demo.git
cd wcag-review-demo
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and configure:

```env
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=owner/repo
ANTHROPIC_API_KEY=your_anthropic_key
REVIEW_TYPE=accessibility  # or code_review
```

### Usage

**CLI:**
```bash
python -m src.main 123
```

**Programmatic:**
```python
from src.anthropic_code_review import AnthropicCodeReview

with AnthropicCodeReview(
    github_token=token,
    repository_name="owner/repo",
    anthropic_api_key=api_key
) as reviewer:
    comments, html = reviewer.review_pr_accessibility(123)
    reviewer.save_report(html, Path("report.html"))
```

**GitHub Actions:**
Trigger manually from Actions tab, select review type and PR number.

## Review Types

### Accessibility Review
Checks for WCAG 2.1 AA compliance:
- ARIA labels and roles
- Keyboard navigation
- Color contrast
- Semantic HTML
- Screen reader compatibility

### Code Review
Analyzes code quality:
- Potential bugs and logic errors
- Best practices violations
- Maintainability issues
- Error handling

## Output

Reviews generate:
- JSON array of structured comments with file/line/issue/suggestion/severity
- HTML report with categorized issues and severity counts
- Saved as workflow artifacts in `reports/` directory

## Testing

```bash
pytest                              # Run all tests
pytest --cov=src --cov-report=html  # With coverage
ruff check src/ tests/              # Lint code
```

39 tests, all passing.

## License

MIT License - see LICENSE file for details.
