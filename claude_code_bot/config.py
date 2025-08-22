"""
Configuration management for Claude Code CLI.

This module provides configuration management for the Claude Code CLI wrapper,
including loading configuration from environment variables and files.
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, field_validator

from .utils.errors import ConfigurationError


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ToolPermission(str, Enum):
    """Tool permission levels."""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ALL = "all"


class McpServerConfig(BaseModel):
    """Configuration for an MCP server."""

    name: str = Field(..., description="Name of the MCP server")
    url: str = Field(..., description="URL of the MCP server")
    api_key: Optional[str] = Field(None, description="API key for the MCP server")
    enabled: bool = Field(True, description="Whether the MCP server is enabled")
    tools: Dict[str, ToolPermission] = Field(
        default_factory=dict, description="Tool permissions for the MCP server"
    )


class SessionConfig(BaseModel):
    """Configuration for session management."""

    max_sessions: int = Field(10, description="Maximum number of concurrent sessions")
    session_timeout: int = Field(
        3600, description="Session timeout in seconds (default: 1 hour)"
    )
    session_dir: Path = Field(
        Path.home() / ".claude_code_bot" / "sessions",
        description="Directory for storing session data",
    )
    cleanup_interval: int = Field(
        300, description="Interval for cleaning up expired sessions in seconds"
    )


class CliConfig(BaseModel):
    """Configuration for the Claude Code CLI."""

    executable: str = Field("claude-code", description="Path to the Claude Code CLI executable")
    timeout: int = Field(60, description="Default timeout for CLI operations in seconds")
    max_retries: int = Field(3, description="Maximum number of retries for CLI operations")
    retry_delay: int = Field(1, description="Delay between retries in seconds")
    env_vars: Dict[str, str] = Field(
        default_factory=dict, description="Environment variables for the CLI process"
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: LogLevel = Field(LogLevel.INFO, description="Log level")
    file: Optional[Path] = Field(None, description="Log file path")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )


class Config(BaseModel):
    """Configuration for the Claude Code CLI wrapper."""

    cli: CliConfig = Field(default_factory=CliConfig, description="CLI configuration")
    session: SessionConfig = Field(
        default_factory=SessionConfig, description="Session configuration"
    )
    mcp_servers: Dict[str, McpServerConfig] = Field(
        default_factory=dict, description="MCP server configurations"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig, description="Logging configuration"
    )
    allowed_tools: Set[str] = Field(
        default_factory=set, description="Set of allowed tools"
    )

    @field_validator("mcp_servers")
    @classmethod
    def validate_mcp_servers(cls, v: Dict[str, McpServerConfig]) -> Dict[str, McpServerConfig]:
        """Validate MCP server configurations."""
        if not v:
            raise ConfigurationError("At least one MCP server must be configured")
        return v

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.

        Returns:
            Config: The loaded configuration.
        """
        config_dict: Dict[str, Any] = {
            "cli": {
                "executable": os.environ.get("CLAUDE_CODE_EXECUTABLE", "claude-code"),
                "timeout": int(os.environ.get("CLAUDE_CODE_TIMEOUT", "60")),
                "max_retries": int(os.environ.get("CLAUDE_CODE_MAX_RETRIES", "3")),
                "retry_delay": int(os.environ.get("CLAUDE_CODE_RETRY_DELAY", "1")),
            },
            "session": {
                "max_sessions": int(os.environ.get("CLAUDE_CODE_MAX_SESSIONS", "10")),
                "session_timeout": int(os.environ.get("CLAUDE_CODE_SESSION_TIMEOUT", "3600")),
                "session_dir": os.environ.get(
                    "CLAUDE_CODE_SESSION_DIR",
                    str(Path.home() / ".claude_code_bot" / "sessions"),
                ),
                "cleanup_interval": int(
                    os.environ.get("CLAUDE_CODE_CLEANUP_INTERVAL", "300")
                ),
            },
            "logging": {
                "level": os.environ.get("CLAUDE_CODE_LOG_LEVEL", "INFO"),
                "file": os.environ.get("CLAUDE_CODE_LOG_FILE"),
                "format": os.environ.get(
                    "CLAUDE_CODE_LOG_FORMAT",
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                ),
            },
        }

        # Parse allowed tools
        allowed_tools_str = os.environ.get("CLAUDE_CODE_ALLOWED_TOOLS", "")
        if allowed_tools_str:
            config_dict["allowed_tools"] = set(allowed_tools_str.split(","))

        # Parse MCP servers
        mcp_servers_str = os.environ.get("CLAUDE_CODE_MCP_SERVERS")
        if mcp_servers_str:
            try:
                config_dict["mcp_servers"] = json.loads(mcp_servers_str)
            except json.JSONDecodeError as e:
                raise ConfigurationError(
                    f"Failed to parse MCP servers configuration: {e}"
                ) from e

        return cls(**config_dict)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Config":
        """
        Load configuration from a file.

        Args:
            path: Path to the configuration file.

        Returns:
            Config: The loaded configuration.

        Raises:
            ConfigurationError: If the file cannot be read or parsed.
        """
        path = Path(path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")

        try:
            with open(path, "r") as f:
                config_dict = json.load(f)
            return cls(**config_dict)
        except (json.JSONDecodeError, OSError) as e:
            raise ConfigurationError(f"Failed to load configuration from {path}: {e}") from e

    def to_file(self, path: Union[str, Path]) -> None:
        """
        Save configuration to a file.

        Args:
            path: Path to the configuration file.

        Raises:
            ConfigurationError: If the file cannot be written.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except OSError as e:
            raise ConfigurationError(f"Failed to save configuration to {path}: {e}") from e

