# WCAG Review Demo

A clean, well-architected Python utility that fetches git diffs from GitHub Pull Requests, filters them based on configurable criteria, and sends them to the Anthropic Claude API for intelligent analysis. Built following DRY and SOLID principles for maintainability and extensibility.

## 🌟 Features

- **GitHub Integration**: Seamlessly fetch PR diffs using the GitHub API
- **Smart Filtering**: Filter diffs by file patterns, change size, and custom criteria
- **AI-Powered Analysis**: Leverage Claude's advanced AI for multiple analysis types:
  - Code reviews with quality feedback
  - Concise change summaries
  - Security vulnerability detection
  - WCAG accessibility compliance checks
- **Clean Architecture**: Built with SOLID principles for maintainability
- **Well Tested**: Comprehensive unit test coverage
- **Workflow Integration**: Manual GitHub Actions workflow for easy PR analysis

## 📁 Project Structure

```
wcag-review-demo/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main orchestrator
│   ├── github_diff_fetcher.py  # GitHub API integration
│   ├── diff_filter.py          # Diff filtering logic
│   └── claude_client.py        # Claude API client
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_github_diff_fetcher.py
│   ├── test_diff_filter.py
│   └── test_claude_client.py
├── site/
│   └── index.html              # Demo documentation page
├── .github/
│   └── workflows/
│       └── analyze-pr.yml      # GitHub Actions workflow
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- GitHub personal access token with repo read permissions
- Anthropic API key for Claude access

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vonhoff/wcag-review-demo.git
   cd wcag-review-demo
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

### Configuration

Create a `.env` file with the following required variables:

```env
# Required
GITHUB_TOKEN=your_github_token_here
GITHUB_REPOSITORY=owner/repo
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
ANALYSIS_TYPE=review
GITHUB_PR_NUMBER=1
```

## 💻 Usage

### Command Line

Analyze a specific PR:

```bash
python -m src.main <pr_number>
```

Or use environment variables:

```bash
export GITHUB_PR_NUMBER=123
export ANALYSIS_TYPE=security
python -m src.main
```

### GitHub Actions Workflow

1. Go to your repository's "Actions" tab
2. Select "Analyze PR with Claude" workflow
3. Click "Run workflow"
4. Enter the PR number and select analysis type
5. View the results in the workflow logs

### As a Python Module

```python
from src.main import PRDiffAnalyzer

# Create analyzer
with PRDiffAnalyzer(
    github_token="your_token",
    repository_name="owner/repo",
    anthropic_api_key="your_api_key",
) as analyzer:
    # Analyze a PR
    result = analyzer.analyze_pr(
        pr_number=123,
        analysis_type="review"
    )
    
    print(result["analysis"])
```

## 🎯 Analysis Types

The utility supports four types of analysis:

| Type | Description |
|------|-------------|
| `review` | Comprehensive code review focusing on quality, bugs, and best practices |
| `summary` | Concise summary of changes and their significance |
| `security` | Security vulnerability analysis with fix recommendations |
| `accessibility` | WCAG compliance check with accessibility improvements |

Set the analysis type via the `ANALYSIS_TYPE` environment variable or the `analysis_type` parameter.

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_github_diff_fetcher.py

# Run with verbose output
pytest -v
```

## 🏗️ Architecture

The project follows clean architecture principles with clear separation of concerns:

### Components

- **GitHubDiffFetcher**: Handles all GitHub API interactions using PyGithub
- **DiffFilter**: Filters diffs based on file patterns, change size, and criteria
- **ClaudeClient**: Manages communication with the Anthropic Claude API
- **PRDiffAnalyzer**: Orchestrates the complete workflow

### Design Principles

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Classes are open for extension, closed for modification
- **Dependency Inversion**: Depends on abstractions, not concrete implementations
- **DRY**: No code duplication, reusable components
- **Clean Code**: Well-documented, type-hinted, and tested

## 📊 Filtering Options

Configure diff filtering when creating the analyzer:

```python
analyzer = PRDiffAnalyzer(
    github_token="...",
    repository_name="...",
    anthropic_api_key="...",
    include_patterns=[r"\.py$", r"\.js$"],  # Only Python and JS files
    exclude_patterns=[r"test_", r"__pycache__"],  # Exclude test files
)
```

Available filter options:
- `include_patterns`: List of regex patterns for files to include
- `exclude_patterns`: List of regex patterns for files to exclude (takes precedence)
- `min_line_changes`: Minimum number of line changes to include a file
- `max_line_changes`: Maximum number of line changes to include a file

## 🔒 Security

- API keys are managed through environment variables
- No secrets are committed to the repository
- GitHub token requires only read permissions for public repos
- All API communications use HTTPS

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ using Python, GitHub API, and Claude AI