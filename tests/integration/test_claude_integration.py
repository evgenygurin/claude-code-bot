"""
Integration tests for Claude Code CLI integration.

These tests require the Claude Code CLI to be installed and configured.
They are skipped by default unless the CLAUDE_CODE_TEST_INTEGRATION environment variable is set.
"""

import asyncio
import os
from pathlib import Path

import pytest

from claude_code_bot.claude_runner import ClaudeRunner
from claude_code_bot.config import Config
from claude_code_bot.models.messages import MessageType, ToolUseMessage


# Skip these tests unless the CLAUDE_CODE_TEST_INTEGRATION environment variable is set
pytestmark = pytest.mark.skipif(
    os.environ.get("CLAUDE_CODE_TEST_INTEGRATION") != "1",
    reason="Integration tests are disabled. Set CLAUDE_CODE_TEST_INTEGRATION=1 to enable.",
)


@pytest.fixture
def workspace_path(tmp_path):
    """Create a test workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Create a simple Python file in the workspace
    with open(workspace / "hello.py", "w") as f:
        f.write('print("Hello, world!")\n')
    
    return workspace


@pytest.fixture
async def claude_runner(tmp_path):
    """Create a Claude runner for integration tests."""
    # Create a custom configuration for the tests
    config = Config()
    config.session.session_dir = tmp_path / "sessions"
    
    runner = ClaudeRunner(config)
    await runner.initialize()
    yield runner
    await runner.shutdown()


@pytest.mark.asyncio
async def test_start_session(claude_runner, workspace_path):
    """Test starting a session with the actual Claude Code CLI."""
    session = await claude_runner.start_session(
        workspace_path=workspace_path,
        system_prompt="You are a helpful AI assistant.",
    )
    
    assert session.id is not None
    assert session.workspace_path == workspace_path
    
    # Clean up
    await claude_runner.stop_session(session.id)


@pytest.mark.asyncio
async def test_send_message(claude_runner, workspace_path):
    """Test sending a message to the actual Claude Code CLI."""
    session = await claude_runner.start_session(
        workspace_path=workspace_path,
        system_prompt="You are a helpful AI assistant.",
    )
    
    # Send a message and collect the responses
    messages = []
    async for message in claude_runner.send_message(session.id, "Hello, Claude!"):
        messages.append(message)
        # Break after receiving a few messages to keep the test short
        if len(messages) >= 3:
            break
    
    # Check that we received at least one message
    assert len(messages) > 0
    
    # Clean up
    await claude_runner.stop_session(session.id)


@pytest.mark.asyncio
async def test_tool_use(claude_runner, workspace_path):
    """Test that Claude Code uses tools."""
    session = await claude_runner.start_session(
        workspace_path=workspace_path,
        system_prompt="You are a helpful AI assistant.",
        allowed_tools=["run_command"],
    )
    
    # Send a message that should trigger tool use
    tool_use_messages = []
    async for message in claude_runner.send_message(
        session.id, "Can you run the hello.py script in the workspace?"
    ):
        if isinstance(message, ToolUseMessage):
            tool_use_messages.append(message)
        
        # Break after receiving a tool use message to keep the test short
        if len(tool_use_messages) > 0:
            break
    
    # Check that we received at least one tool use message
    assert len(tool_use_messages) > 0
    assert tool_use_messages[0].tool_name == "run_command"
    
    # Clean up
    await claude_runner.stop_session(session.id)


@pytest.mark.asyncio
async def test_continue_session(claude_runner, workspace_path):
    """Test continuing a session with the actual Claude Code CLI."""
    session = await claude_runner.start_session(
        workspace_path=workspace_path,
        system_prompt="You are a helpful AI assistant.",
    )
    
    # Send a message
    messages = []
    async for message in claude_runner.send_message(session.id, "Hello, Claude!"):
        messages.append(message)
        # Break after receiving a few messages to keep the test short
        if len(messages) >= 3:
            break
    
    # Pause the session
    await claude_runner.pause_session(session.id)
    
    # Continue the session
    continue_messages = []
    async for message in claude_runner.continue_session(session.id):
        continue_messages.append(message)
        # Break after receiving a few messages to keep the test short
        if len(continue_messages) >= 3:
            break
    
    # Check that we received at least one message when continuing
    assert len(continue_messages) > 0
    
    # Clean up
    await claude_runner.stop_session(session.id)

