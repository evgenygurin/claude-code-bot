"""
Tool permission management for MCP servers.

This module provides tool permission management for MCP servers,
including tool configuration and permission checking.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..config import ToolPermission
from ..utils.errors import McpServerError
from .server import McpServer

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Enum for tool categories."""

    FILE = "file"
    COMMAND = "command"
    SEARCH = "search"
    ISSUE = "issue"
    PR = "pr"
    WEB = "web"
    DATABASE = "database"
    OTHER = "other"


class ToolManager:
    """
    Manager for MCP tools.

    This class handles tool permission management for MCP servers,
    including tool configuration and permission checking.
    """

    def __init__(self):
        """Initialize the tool manager."""
        self.tool_categories: Dict[str, ToolCategory] = {}
        self._initialize_tool_categories()

    def _initialize_tool_categories(self) -> None:
        """
        Initialize tool categories.

        This method maps tool names to categories.
        """
        # File operations
        file_tools = [
            "file_write",
            "text_editor",
            "ripgrep_search",
        ]
        for tool in file_tools:
            self.tool_categories[tool] = ToolCategory.FILE

        # Command execution
        command_tools = [
            "run_command",
        ]
        for tool in command_tools:
            self.tool_categories[tool] = ToolCategory.COMMAND

        # Search operations
        search_tools = [
            "ripgrep_search",
            "search_all_repos",
            "search_issues",
        ]
        for tool in search_tools:
            self.tool_categories[tool] = ToolCategory.SEARCH

        # Issue management
        issue_tools = [
            "create_issue_comment",
            "view_issue",
            "github_create_issue",
            "linear_comment_on_issue",
            "linear_get_issue",
            "linear_get_issue_comments",
            "linear_search_issues",
            "linear_create_issue",
            "linear_update_issue",
        ]
        for tool in issue_tools:
            self.tool_categories[tool] = ToolCategory.ISSUE

        # PR management
        pr_tools = [
            "create_pr",
            "edit_pr_meta",
            "view_pr",
            "create_pr_comment",
            "create_pr_review_comment",
            "github_assign_pr_reviewers",
        ]
        for tool in pr_tools:
            self.tool_categories[tool] = ToolCategory.PR

        # Web search
        web_tools = [
            "exa_web_search",
            "exa_web_view_page",
        ]
        for tool in web_tools:
            self.tool_categories[tool] = ToolCategory.WEB

        # Database operations
        db_tools = [
            "sql_query",
            "plotly_chart",
            "view_all_databases",
            "set_active_database",
        ]
        for tool in db_tools:
            self.tool_categories[tool] = ToolCategory.DATABASE

    def get_tool_category(self, tool_name: str) -> ToolCategory:
        """
        Get the category of a tool.

        Args:
            tool_name: The name of the tool.

        Returns:
            The category of the tool.
        """
        return self.tool_categories.get(tool_name, ToolCategory.OTHER)

    def check_tool_permission(
        self, server: McpServer, tool_name: str, required_permission: ToolPermission
    ) -> bool:
        """
        Check if a tool has the required permission on an MCP server.

        Args:
            server: The MCP server to check.
            tool_name: The name of the tool to check.
            required_permission: The required permission level.

        Returns:
            True if the tool has the required permission, False otherwise.
        """
        if not server.enabled:
            return False

        # Get the tool's permission on the server
        tool_permission = server.tools.get(tool_name, ToolPermission.NONE)

        # Check if the tool has the required permission
        if tool_permission == ToolPermission.ALL:
            return True
        elif tool_permission == ToolPermission.NONE:
            return False
        elif required_permission == ToolPermission.READ:
            return tool_permission in (
                ToolPermission.READ,
                ToolPermission.WRITE,
                ToolPermission.EXECUTE,
            )
        elif required_permission == ToolPermission.WRITE:
            return tool_permission in (ToolPermission.WRITE, ToolPermission.EXECUTE)
        elif required_permission == ToolPermission.EXECUTE:
            return tool_permission == ToolPermission.EXECUTE
        else:
            return False

    def get_allowed_tools(
        self, servers: List[McpServer], required_permission: ToolPermission
    ) -> Set[str]:
        """
        Get the set of tools that have the required permission on any of the servers.

        Args:
            servers: The list of MCP servers to check.
            required_permission: The required permission level.

        Returns:
            The set of tools that have the required permission.
        """
        allowed_tools: Set[str] = set()

        for server in servers:
            if not server.enabled:
                continue

            for tool_name, permission in server.tools.items():
                if self.check_tool_permission(server, tool_name, required_permission):
                    allowed_tools.add(tool_name)

        return allowed_tools

    def get_server_for_tool(
        self, servers: List[McpServer], tool_name: str, required_permission: ToolPermission
    ) -> Optional[McpServer]:
        """
        Get the first server that has the required permission for a tool.

        Args:
            servers: The list of MCP servers to check.
            tool_name: The name of the tool to check.
            required_permission: The required permission level.

        Returns:
            The first server that has the required permission for the tool, or None if no server has the permission.
        """
        for server in servers:
            if self.check_tool_permission(server, tool_name, required_permission):
                return server

        return None

