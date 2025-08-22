"""
MCP server configuration and integration.

This module provides MCP server configuration and integration for the Claude Code CLI,
including Linear MCP server auto-configuration and custom MCP server support.
"""

import json
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from ..config import Config, McpServerConfig, ToolPermission
from ..utils.errors import McpServerError

logger = logging.getLogger(__name__)


class McpServerType(str, Enum):
    """Enum for MCP server types."""

    LINEAR = "linear"
    GITHUB = "github"
    DESKTOP = "desktop"
    CUSTOM = "custom"


class McpToolConfig(BaseModel):
    """Configuration for an MCP tool."""

    name: str = Field(..., description="Name of the tool")
    permission: ToolPermission = Field(..., description="Permission level for the tool")
    config: Dict[str, Any] = Field(default_factory=dict, description="Tool configuration")


class McpServer:
    """
    Model Context Protocol server configuration.

    This class represents a Model Context Protocol server configuration,
    including server URL, API key, and tool permissions.
    """

    def __init__(
        self,
        name: str,
        url: str,
        server_type: McpServerType = McpServerType.CUSTOM,
        api_key: Optional[str] = None,
        tools: Optional[Dict[str, ToolPermission]] = None,
        enabled: bool = True,
    ):
        """
        Initialize the MCP server.

        Args:
            name: Name of the MCP server.
            url: URL of the MCP server.
            server_type: Type of the MCP server.
            api_key: Optional API key for the MCP server.
            tools: Optional tool permissions for the MCP server.
            enabled: Whether the MCP server is enabled.
        """
        self.name = name
        self.url = url
        self.server_type = server_type
        self.api_key = api_key
        self.tools = tools or {}
        self.enabled = enabled

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the MCP server to a dictionary.

        Returns:
            The MCP server as a dictionary.
        """
        return {
            "name": self.name,
            "url": self.url,
            "server_type": self.server_type.value,
            "api_key": self.api_key,
            "tools": self.tools,
            "enabled": self.enabled,
        }

    def to_config(self) -> McpServerConfig:
        """
        Convert the MCP server to a configuration object.

        Returns:
            The MCP server as a configuration object.
        """
        return McpServerConfig(
            name=self.name,
            url=self.url,
            api_key=self.api_key,
            enabled=self.enabled,
            tools=self.tools,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "McpServer":
        """
        Create an MCP server from a dictionary.

        Args:
            data: The dictionary to create the MCP server from.

        Returns:
            The created MCP server.
        """
        server_type = data.get("server_type", McpServerType.CUSTOM.value)
        if isinstance(server_type, str):
            server_type = McpServerType(server_type)

        return cls(
            name=data["name"],
            url=data["url"],
            server_type=server_type,
            api_key=data.get("api_key"),
            tools=data.get("tools", {}),
            enabled=data.get("enabled", True),
        )

    @classmethod
    def from_config(cls, config: McpServerConfig) -> "McpServer":
        """
        Create an MCP server from a configuration object.

        Args:
            config: The configuration object to create the MCP server from.

        Returns:
            The created MCP server.
        """
        return cls(
            name=config.name,
            url=config.url,
            server_type=McpServerType.CUSTOM,
            api_key=config.api_key,
            tools=config.tools,
            enabled=config.enabled,
        )


class McpServerManager:
    """
    Manager for MCP servers.

    This class handles configuring and managing MCP servers,
    including Linear MCP server auto-configuration and custom MCP server support.
    """

    def __init__(self, config: Config):
        """
        Initialize the MCP server manager.

        Args:
            config: Configuration for the MCP server manager.
        """
        self.config = config
        self.servers: Dict[str, McpServer] = {}

    def initialize(self) -> None:
        """
        Initialize the MCP server manager.

        This method loads MCP server configurations from the configuration.
        """
        # Load MCP servers from configuration
        for name, server_config in self.config.mcp_servers.items():
            self.servers[name] = McpServer.from_config(server_config)

        # Auto-configure Linear MCP server if available
        self._auto_configure_linear_mcp()

        # Auto-configure GitHub MCP server if available
        self._auto_configure_github_mcp()

        # Auto-configure Desktop Commander MCP server if available
        self._auto_configure_desktop_mcp()

        logger.info(f"Initialized MCP server manager with {len(self.servers)} servers")

    def get_server(self, name: str) -> McpServer:
        """
        Get an MCP server by name.

        Args:
            name: The name of the MCP server to get.

        Returns:
            The MCP server.

        Raises:
            McpServerError: If the MCP server does not exist.
        """
        if name not in self.servers:
            raise McpServerError(f"MCP server not found: {name}", server_name=name)

        return self.servers[name]

    def add_server(self, server: McpServer) -> None:
        """
        Add an MCP server.

        Args:
            server: The MCP server to add.

        Raises:
            McpServerError: If an MCP server with the same name already exists.
        """
        if server.name in self.servers:
            raise McpServerError(
                f"MCP server already exists: {server.name}", server_name=server.name
            )

        self.servers[server.name] = server
        logger.info(f"Added MCP server: {server.name}")

    def update_server(self, server: McpServer) -> None:
        """
        Update an MCP server.

        Args:
            server: The MCP server to update.

        Raises:
            McpServerError: If the MCP server does not exist.
        """
        if server.name not in self.servers:
            raise McpServerError(
                f"MCP server not found: {server.name}", server_name=server.name
            )

        self.servers[server.name] = server
        logger.info(f"Updated MCP server: {server.name}")

    def remove_server(self, name: str) -> None:
        """
        Remove an MCP server.

        Args:
            name: The name of the MCP server to remove.

        Raises:
            McpServerError: If the MCP server does not exist.
        """
        if name not in self.servers:
            raise McpServerError(f"MCP server not found: {name}", server_name=name)

        del self.servers[name]
        logger.info(f"Removed MCP server: {name}")

    def list_servers(self) -> List[McpServer]:
        """
        List all MCP servers.

        Returns:
            A list of all MCP servers.
        """
        return list(self.servers.values())

    def get_enabled_servers(self) -> List[McpServer]:
        """
        Get all enabled MCP servers.

        Returns:
            A list of all enabled MCP servers.
        """
        return [server for server in self.servers.values() if server.enabled]

    def _auto_configure_linear_mcp(self) -> None:
        """
        Auto-configure Linear MCP server if available.

        This method checks for Linear API key in environment variables
        and configures a Linear MCP server if available.
        """
        linear_api_key = os.environ.get("LINEAR_API_KEY")
        if not linear_api_key:
            logger.debug("Linear API key not found in environment variables")
            return

        linear_server = McpServer(
            name="linear",
            url="https://api.linear.app/graphql",
            server_type=McpServerType.LINEAR,
            api_key=linear_api_key,
            tools={
                "linear_comment_on_issue": ToolPermission.WRITE,
                "linear_get_issue": ToolPermission.READ,
                "linear_get_issue_comments": ToolPermission.READ,
                "linear_search_issues": ToolPermission.READ,
                "linear_create_issue": ToolPermission.WRITE,
                "linear_update_issue": ToolPermission.WRITE,
                "linear_get_teams": ToolPermission.READ,
                "linear_search_teams": ToolPermission.READ,
                "linear_search_projects": ToolPermission.READ,
                "linear_get_issue_states": ToolPermission.READ,
                "linear_search_users": ToolPermission.READ,
                "linear_get_issue_priority_values": ToolPermission.READ,
                "linear_get_issue_labels": ToolPermission.READ,
            },
        )

        self.servers[linear_server.name] = linear_server
        logger.info("Auto-configured Linear MCP server")

    def _auto_configure_github_mcp(self) -> None:
        """
        Auto-configure GitHub MCP server if available.

        This method checks for GitHub token in environment variables
        and configures a GitHub MCP server if available.
        """
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            logger.debug("GitHub token not found in environment variables")
            return

        github_server = McpServer(
            name="github",
            url="https://api.github.com",
            server_type=McpServerType.GITHUB,
            api_key=github_token,
            tools={
                "github_create_issue": ToolPermission.WRITE,
                "github_list_users": ToolPermission.READ,
                "search_issues": ToolPermission.READ,
                "view_issue": ToolPermission.READ,
                "view_pr": ToolPermission.READ,
                "create_pr": ToolPermission.WRITE,
                "edit_pr_meta": ToolPermission.WRITE,
                "create_pr_comment": ToolPermission.WRITE,
                "create_issue_comment": ToolPermission.WRITE,
                "create_pr_review_comment": ToolPermission.WRITE,
                "github_assign_pr_reviewers": ToolPermission.WRITE,
            },
        )

        self.servers[github_server.name] = github_server
        logger.info("Auto-configured GitHub MCP server")

    def _auto_configure_desktop_mcp(self) -> None:
        """
        Auto-configure Desktop Commander MCP server if available.

        This method configures a Desktop Commander MCP server for file operations.
        """
        desktop_server = McpServer(
            name="desktop",
            url="http://localhost:8000",
            server_type=McpServerType.DESKTOP,
            tools={
                "file_write": ToolPermission.WRITE,
                "text_editor": ToolPermission.WRITE,
                "run_command": ToolPermission.EXECUTE,
            },
        )

        self.servers[desktop_server.name] = desktop_server
        logger.info("Auto-configured Desktop Commander MCP server")

