"""
Error handling utilities for Claude Code CLI.

This module defines custom exception classes and error handling utilities
for the Claude Code CLI wrapper.
"""

from typing import Any, Dict, Optional


class ClaudeCodeError(Exception):
    """Base exception class for Claude Code CLI errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ClaudeCliError(ClaudeCodeError):
    """Exception raised for errors in the Claude Code CLI."""

    def __init__(
        self,
        message: str,
        exit_code: Optional[int] = None,
        stderr: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(message, details)


class StreamProcessingError(ClaudeCodeError):
    """Exception raised for errors in stream processing."""

    def __init__(
        self,
        message: str,
        line: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.line = line
        super().__init__(message, details)


class SessionError(ClaudeCodeError):
    """Exception raised for errors in session management."""

    def __init__(
        self,
        message: str,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        super().__init__(message, details)


class McpServerError(ClaudeCodeError):
    """Exception raised for errors in MCP server integration."""

    def __init__(
        self,
        message: str,
        server_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.server_name = server_name
        super().__init__(message, details)


class ToolExecutionError(ClaudeCodeError):
    """Exception raised for errors in tool execution."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.tool_name = tool_name
        self.tool_input = tool_input
        super().__init__(message, details)


class ConfigurationError(ClaudeCodeError):
    """Exception raised for errors in configuration."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.config_key = config_key
        super().__init__(message, details)


class TimeoutError(ClaudeCodeError):
    """Exception raised for timeout errors."""

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.timeout_seconds = timeout_seconds
        super().__init__(message, details)

