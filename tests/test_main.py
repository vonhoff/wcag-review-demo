"""Tests for main module."""

import os
from unittest.mock import patch

import pytest

from src.main import load_config


class TestLoadConfig:
    """Test suite for configuration loading."""

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPOSITORY": "owner/repo",
            "ANTHROPIC_API_KEY": "test_key",
            "CLAUDE_MODEL": "test-model",
            "MAX_TOKENS": "4096",
        },
    )
    def test_load_config_success(self) -> None:
        """Test successful config loading."""
        config = load_config()

        assert config["github_token"] == "test_token"
        assert config["repository_name"] == "owner/repo"
        assert config["anthropic_api_key"] == "test_key"
        assert config["model"] == "test-model"
        assert config["max_tokens"] == 4096

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPOSITORY": "owner/repo",
            "ANTHROPIC_API_KEY": "test_key",
        },
    )
    def test_load_config_with_defaults(self) -> None:
        """Test config loading with default values."""
        config = load_config()

        assert config["model"] is None
        assert config["max_tokens"] == 8192

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPOSITORY": "owner/repo",
        },
        clear=True,
    )
    def test_load_config_missing_required(self) -> None:
        """Test config loading with missing required variables."""
        with pytest.raises(ValueError, match="Missing required environment variables"):
            load_config()
