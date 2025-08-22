"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from linear_agent.config import Settings


class TestSettings:
    """Test Settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings(secret_key="test-secret-key-32-chars-long")
        
        assert settings.app_name == "Linear Claude Agent"
        assert settings.environment == "development"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.debug is False
        
    def test_environment_validation(self):
        """Test environment field validation."""
        # Valid environments
        for env in ["development", "staging", "production"]:
            settings = Settings(
                environment=env,
                secret_key="test-secret-key-32-chars-long"
            )
            assert settings.environment == env
        
        # Invalid environment
        with pytest.raises(ValidationError):
            Settings(
                environment="invalid",
                secret_key="test-secret-key-32-chars-long"
            )
    
    def test_database_url_default(self):
        """Test database URL default value."""
        settings = Settings(secret_key="test-secret-key-32-chars-long")
        assert str(settings.database_url) == "sqlite+aiosqlite:///./linear_agent.db"
    
    def test_database_url_sync_property(self):
        """Test synchronous database URL conversion."""
        # SQLite conversion
        settings = Settings(
            database_url="sqlite+aiosqlite:///./test.db",
            secret_key="test-secret-key-32-chars-long"
        )
        assert settings.database_url_sync == "sqlite:///./test.db"
        
        # PostgreSQL conversion
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            secret_key="test-secret-key-32-chars-long"
        )
        assert settings.database_url_sync == "postgresql://user:pass@localhost/db"
    
    def test_redis_url_default(self):
        """Test Redis URL default value."""
        settings = Settings(secret_key="test-secret-key-32-chars-long")
        assert str(settings.redis_url) == "redis://localhost:6379/0"
    
    def test_secret_key_validation(self):
        """Test secret key validation and generation."""
        # Valid secret key
        secret_key = "this-is-a-valid-secret-key-32-chars"
        settings = Settings(secret_key=secret_key)
        assert settings.secret_key == secret_key
        
        # Auto-generated secret key for short input
        settings = Settings(secret_key="short")
        assert len(settings.secret_key) >= 32
        
        # Auto-generated secret key for empty input
        settings = Settings(secret_key="")
        assert len(settings.secret_key) >= 32
    
    def test_environment_properties(self):
        """Test environment check properties."""
        dev_settings = Settings(
            environment="development",
            secret_key="test-secret-key-32-chars-long"
        )
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False
        
        prod_settings = Settings(
            environment="production",
            secret_key="test-secret-key-32-chars-long"
        )
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True
    
    def test_log_level_validation(self):
        """Test log level validation."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            settings = Settings(
                log_level=level,
                secret_key="test-secret-key-32-chars-long"
            )
            assert settings.log_level == level
        
        # Invalid log level
        with pytest.raises(ValidationError):
            Settings(
                log_level="INVALID",
                secret_key="test-secret-key-32-chars-long"
            )
    
    def test_settings_from_env_file(self):
        """Test loading settings from .env file."""
        env_content = """
ENVIRONMENT=staging
DEBUG=true
API_PORT=9000
SECRET_KEY=test-secret-key-from-env-file-32
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file_path = f.name
        
        try:
            settings = Settings(_env_file=env_file_path)
            assert settings.environment == "staging"
            assert settings.debug is True
            assert settings.api_port == 9000
            assert settings.secret_key == "test-secret-key-from-env-file-32"
        finally:
            os.unlink(env_file_path)
    
    def test_settings_from_environment_variables(self, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("API_PORT", "8080")
        monkeypatch.setenv("SECRET_KEY", "env-var-secret-key-32-chars-long")
        
        settings = Settings()
        assert settings.environment == "production"
        assert settings.debug is False
        assert settings.api_port == 8080
        assert settings.secret_key == "env-var-secret-key-32-chars-long"
    
    def test_claude_settings(self):
        """Test Claude Code specific settings."""
        settings = Settings(secret_key="test-secret-key-32-chars-long")
        
        assert settings.claude_code_binary == "claude"
        assert settings.claude_max_concurrent_sessions == 5
        assert settings.claude_session_timeout_minutes == 60
        assert settings.claude_default_model == "claude-3-sonnet-20240229"
    
    def test_git_settings(self):
        """Test Git worktree settings."""
        settings = Settings(secret_key="test-secret-key-32-chars-long")
        
        assert settings.git_worktree_base_path == "/tmp/linear-agent/worktrees"
        assert settings.git_cleanup_hours == 24
        assert settings.git_max_worktrees_per_repo == 10