"""
Integration tests for MCP server setup.

These tests verify that MCP servers are properly configured and integrated.
"""

import os
from pathlib import Path

import pytest

from claude_code_bot.config import Config, ToolPermission
from claude_code_bot.mcp.server import McpServer, McpServerManager, McpServerType
from claude_code_bot.mcp.tools import ToolManager


@pytest.fixture
def config():
    """Create a test configuration with MCP servers."""
    config = Config()
    config.mcp_servers = {
        "test": {
            "name": "test",
            "url": "http://localhost:8000",
            "api_key": "test-key",
            "enabled": True,
            "tools": {
                "run_command": ToolPermission.EXECUTE.value,
                "file_write": ToolPermission.WRITE.value,
                "text_editor": ToolPermission.WRITE.value,
                "ripgrep_search": ToolPermission.READ.value,
            },
        }
    }
    return config


@pytest.fixture
def mcp_manager(config):
    """Create a test MCP server manager."""
    manager = McpServerManager(config)
    manager.initialize()
    return manager


@pytest.fixture
def tool_manager():
    """Create a test tool manager."""
    return ToolManager()


def test_mcp_server_initialization(mcp_manager):
    """Test that MCP servers are properly initialized."""
    # Check that the test server was loaded
    assert "test" in mcp_manager.servers
    test_server = mcp_manager.servers["test"]
    assert test_server.name == "test"
    assert test_server.url == "http://localhost:8000"
    assert test_server.api_key == "test-key"
    assert test_server.enabled is True
    
    # Check that the tools were loaded
    assert "run_command" in test_server.tools
    assert test_server.tools["run_command"] == ToolPermission.EXECUTE
    assert "file_write" in test_server.tools
    assert test_server.tools["file_write"] == ToolPermission.WRITE
    assert "text_editor" in test_server.tools
    assert test_server.tools["text_editor"] == ToolPermission.WRITE
    assert "ripgrep_search" in test_server.tools
    assert test_server.tools["ripgrep_search"] == ToolPermission.READ


def test_auto_configure_linear_mcp(monkeypatch):
    """Test that Linear MCP server is auto-configured when the API key is available."""
    # Set the LINEAR_API_KEY environment variable
    monkeypatch.setenv("LINEAR_API_KEY", "test-linear-key")
    
    # Create a new MCP server manager
    config = Config()
    manager = McpServerManager(config)
    manager.initialize()
    
    # Check that the Linear MCP server was auto-configured
    assert "linear" in manager.servers
    linear_server = manager.servers["linear"]
    assert linear_server.name == "linear"
    assert linear_server.url == "https://api.linear.app/graphql"
    assert linear_server.api_key == "test-linear-key"
    assert linear_server.server_type == McpServerType.LINEAR
    assert linear_server.enabled is True
    
    # Check that the Linear tools were configured
    assert "linear_comment_on_issue" in linear_server.tools
    assert linear_server.tools["linear_comment_on_issue"] == ToolPermission.WRITE
    assert "linear_get_issue" in linear_server.tools
    assert linear_server.tools["linear_get_issue"] == ToolPermission.READ


def test_auto_configure_github_mcp(monkeypatch):
    """Test that GitHub MCP server is auto-configured when the token is available."""
    # Set the GITHUB_TOKEN environment variable
    monkeypatch.setenv("GITHUB_TOKEN", "test-github-token")
    
    # Create a new MCP server manager
    config = Config()
    manager = McpServerManager(config)
    manager.initialize()
    
    # Check that the GitHub MCP server was auto-configured
    assert "github" in manager.servers
    github_server = manager.servers["github"]
    assert github_server.name == "github"
    assert github_server.url == "https://api.github.com"
    assert github_server.api_key == "test-github-token"
    assert github_server.server_type == McpServerType.GITHUB
    assert github_server.enabled is True
    
    # Check that the GitHub tools were configured
    assert "github_create_issue" in github_server.tools
    assert github_server.tools["github_create_issue"] == ToolPermission.WRITE
    assert "view_issue" in github_server.tools
    assert github_server.tools["view_issue"] == ToolPermission.READ


def test_get_server(mcp_manager):
    """Test getting an MCP server by name."""
    # Get the test server
    server = mcp_manager.get_server("test")
    assert server.name == "test"
    assert server.url == "http://localhost:8000"
    
    # Try to get a non-existent server
    with pytest.raises(Exception):
        mcp_manager.get_server("non-existent")


def test_add_server(mcp_manager):
    """Test adding a new MCP server."""
    # Create a new server
    server = McpServer(
        name="new-server",
        url="http://localhost:8001",
        server_type=McpServerType.CUSTOM,
        api_key="new-key",
        tools={
            "run_command": ToolPermission.EXECUTE,
            "file_write": ToolPermission.WRITE,
        },
    )
    
    # Add the server
    mcp_manager.add_server(server)
    
    # Check that the server was added
    assert "new-server" in mcp_manager.servers
    new_server = mcp_manager.servers["new-server"]
    assert new_server.name == "new-server"
    assert new_server.url == "http://localhost:8001"
    assert new_server.api_key == "new-key"
    assert new_server.server_type == McpServerType.CUSTOM
    assert new_server.enabled is True
    
    # Check that the tools were added
    assert "run_command" in new_server.tools
    assert new_server.tools["run_command"] == ToolPermission.EXECUTE
    assert "file_write" in new_server.tools
    assert new_server.tools["file_write"] == ToolPermission.WRITE


def test_update_server(mcp_manager):
    """Test updating an existing MCP server."""
    # Get the test server
    server = mcp_manager.get_server("test")
    
    # Update the server
    server.url = "http://localhost:8002"
    server.api_key = "updated-key"
    server.tools["new_tool"] = ToolPermission.READ
    
    # Update the server in the manager
    mcp_manager.update_server(server)
    
    # Check that the server was updated
    updated_server = mcp_manager.get_server("test")
    assert updated_server.url == "http://localhost:8002"
    assert updated_server.api_key == "updated-key"
    assert "new_tool" in updated_server.tools
    assert updated_server.tools["new_tool"] == ToolPermission.READ


def test_remove_server(mcp_manager):
    """Test removing an MCP server."""
    # Remove the test server
    mcp_manager.remove_server("test")
    
    # Check that the server was removed
    assert "test" not in mcp_manager.servers
    
    # Try to remove a non-existent server
    with pytest.raises(Exception):
        mcp_manager.remove_server("non-existent")


def test_list_servers(mcp_manager):
    """Test listing all MCP servers."""
    # List all servers
    servers = mcp_manager.list_servers()
    
    # Check that the test server is in the list
    assert len(servers) == 1
    assert servers[0].name == "test"


def test_get_enabled_servers(mcp_manager):
    """Test getting all enabled MCP servers."""
    # Get all enabled servers
    enabled_servers = mcp_manager.get_enabled_servers()
    
    # Check that the test server is in the list
    assert len(enabled_servers) == 1
    assert enabled_servers[0].name == "test"
    
    # Disable the test server
    test_server = mcp_manager.get_server("test")
    test_server.enabled = False
    mcp_manager.update_server(test_server)
    
    # Check that there are no enabled servers
    enabled_servers = mcp_manager.get_enabled_servers()
    assert len(enabled_servers) == 0


def test_tool_manager_get_tool_category(tool_manager):
    """Test getting the category of a tool."""
    # Check the category of some tools
    assert tool_manager.get_tool_category("run_command").value == "command"
    assert tool_manager.get_tool_category("file_write").value == "file"
    assert tool_manager.get_tool_category("ripgrep_search").value == "search"
    assert tool_manager.get_tool_category("linear_get_issue").value == "issue"
    assert tool_manager.get_tool_category("create_pr").value == "pr"
    assert tool_manager.get_tool_category("exa_web_search").value == "web"
    assert tool_manager.get_tool_category("sql_query").value == "database"
    assert tool_manager.get_tool_category("unknown_tool").value == "other"


def test_tool_manager_check_tool_permission(tool_manager, mcp_manager):
    """Test checking if a tool has the required permission on an MCP server."""
    # Get the test server
    server = mcp_manager.get_server("test")
    
    # Check permissions for tools
    assert tool_manager.check_tool_permission(server, "run_command", ToolPermission.EXECUTE) is True
    assert tool_manager.check_tool_permission(server, "run_command", ToolPermission.WRITE) is True
    assert tool_manager.check_tool_permission(server, "run_command", ToolPermission.READ) is True
    
    assert tool_manager.check_tool_permission(server, "file_write", ToolPermission.EXECUTE) is False
    assert tool_manager.check_tool_permission(server, "file_write", ToolPermission.WRITE) is True
    assert tool_manager.check_tool_permission(server, "file_write", ToolPermission.READ) is True
    
    assert tool_manager.check_tool_permission(server, "ripgrep_search", ToolPermission.EXECUTE) is False
    assert tool_manager.check_tool_permission(server, "ripgrep_search", ToolPermission.WRITE) is False
    assert tool_manager.check_tool_permission(server, "ripgrep_search", ToolPermission.READ) is True
    
    assert tool_manager.check_tool_permission(server, "unknown_tool", ToolPermission.READ) is False


def test_tool_manager_get_allowed_tools(tool_manager, mcp_manager):
    """Test getting the set of tools that have the required permission on any of the servers."""
    # Get all servers
    servers = mcp_manager.list_servers()
    
    # Get allowed tools for different permission levels
    execute_tools = tool_manager.get_allowed_tools(servers, ToolPermission.EXECUTE)
    write_tools = tool_manager.get_allowed_tools(servers, ToolPermission.WRITE)
    read_tools = tool_manager.get_allowed_tools(servers, ToolPermission.READ)
    
    # Check the allowed tools
    assert "run_command" in execute_tools
    assert "file_write" not in execute_tools
    assert "ripgrep_search" not in execute_tools
    
    assert "run_command" in write_tools
    assert "file_write" in write_tools
    assert "text_editor" in write_tools
    assert "ripgrep_search" not in write_tools
    
    assert "run_command" in read_tools
    assert "file_write" in read_tools
    assert "text_editor" in read_tools
    assert "ripgrep_search" in read_tools


def test_tool_manager_get_server_for_tool(tool_manager, mcp_manager):
    """Test getting the first server that has the required permission for a tool."""
    # Get all servers
    servers = mcp_manager.list_servers()
    
    # Get server for different tools and permission levels
    run_command_server = tool_manager.get_server_for_tool(servers, "run_command", ToolPermission.EXECUTE)
    file_write_server = tool_manager.get_server_for_tool(servers, "file_write", ToolPermission.WRITE)
    ripgrep_search_server = tool_manager.get_server_for_tool(servers, "ripgrep_search", ToolPermission.READ)
    unknown_tool_server = tool_manager.get_server_for_tool(servers, "unknown_tool", ToolPermission.READ)
    
    # Check the servers
    assert run_command_server is not None
    assert run_command_server.name == "test"
    
    assert file_write_server is not None
    assert file_write_server.name == "test"
    
    assert ripgrep_search_server is not None
    assert ripgrep_search_server.name == "test"
    
    assert unknown_tool_server is None

