"""Configuration management using Pydantic Settings."""

from typing import List, Optional
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )
    
    # Application settings
    app_name: str = "Linear Claude Agent"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = False
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    allowed_origins: List[str] = ["*"]
    
    # Database settings
    database_url: Optional[PostgresDsn] = None
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis settings
    redis_url: Optional[RedisDsn] = None
    redis_ttl_seconds: int = 3600
    
    # Linear API settings
    linear_api_url: str = "https://api.linear.app/graphql"
    linear_client_id: Optional[str] = None
    linear_client_secret: Optional[str] = None
    linear_webhook_secret: Optional[str] = None
    
    # Claude Code settings
    claude_code_binary: str = "claude"
    claude_max_concurrent_sessions: int = 5
    claude_session_timeout_minutes: int = 60
    claude_default_model: str = "claude-3-sonnet-20240229"
    
    # Git settings
    git_worktree_base_path: str = "/tmp/linear-agent/worktrees"
    git_cleanup_hours: int = 24
    git_max_worktrees_per_repo: int = 10
    
    # Security settings
    secret_key: str = Field(min_length=32)
    encryption_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Logging settings
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_format: str = "json"
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_port: int = 9090
    sentry_dsn: Optional[str] = None
    
    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """Set default SQLite URL for development if not provided."""
        if v is None:
            return "sqlite+aiosqlite:///./linear_agent.db"
        return v
    
    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, v: Optional[str]) -> Optional[str]:
        """Set default Redis URL if not provided."""
        if v is None:
            return "redis://localhost:6379/0"
        return v
    
    @field_validator("secret_key", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Generate a default secret key for development."""
        if not v or len(v) < 32:
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        if self.database_url is None:
            return "sqlite:///./linear_agent.db"
        
        url_str = str(self.database_url)
        if url_str.startswith("sqlite+aiosqlite://"):
            return url_str.replace("sqlite+aiosqlite://", "sqlite://")
        elif url_str.startswith("postgresql+asyncpg://"):
            return url_str.replace("postgresql+asyncpg://", "postgresql://")
        return url_str


# Global settings instance
settings = Settings()