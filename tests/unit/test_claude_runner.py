"""
Unit tests for the Claude runner.
"""

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from claude_code_bot.claude_runner import ClaudeRunner
from claude_code_bot.config import Config
from claude_code_bot.models.messages import ClaudeMessage, MessageType
from claude_code_bot.session.models import Session, SessionState


@pytest.fixture
def config():
    """Create a test configuration."""
    return Config(
        cli=Config().cli,
        session=Config().session,
        mcp_servers={
            "test": Config().mcp_servers.get("test", {})
        },
    )


@pytest.fixture
def mock_process():
    """Create a mock subprocess."""
    process = AsyncMock()
    process.returncode = None
    process.pid = 12345
    process.stdin = AsyncMock()
    process.stdout = AsyncMock()
    process.stderr = AsyncMock()
    return process


@pytest.fixture
async def claude_runner(config, tmp_path):
    """Create a test Claude runner."""
    # Set session directory to a temporary path
    config.session.session_dir = tmp_path / "sessions"
    
    runner = ClaudeRunner(config)
    await runner.initialize()
    yield runner
    await runner.shutdown()


@pytest.mark.asyncio
async def test_start_session(claude_runner, mock_process, mocker: MockerFixture, tmp_path):
    """Test starting a session."""
    # Mock the CLI runner's start method
    mocker.patch.object(
        claude_runner.cli_runner, "start", return_value=mock_process
    )
    
    # Create a test workspace directory
    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    
    # Start a session
    session = await claude_runner.start_session(
        workspace_path=workspace_path,
        system_prompt="Test prompt",
        allowed_tools=["tool1", "tool2"],
    )
    
    # Check that the session was created correctly
    assert session.id is not None
    assert session.workspace_path == workspace_path
    assert session.system_prompt == "Test prompt"
    assert session.allowed_tools == {"tool1", "tool2"}
    assert session.state == SessionState.RUNNING
    
    # Check that the CLI runner's start method was called correctly
    claude_runner.cli_runner.start.assert_called_once_with(
        workspace_path=workspace_path,
        system_prompt="Test prompt",
        allowed_tools=["tool1", "tool2"],
    )


@pytest.mark.asyncio
async def test_stop_session(claude_runner, mock_process, mocker: MockerFixture, tmp_path):
    """Test stopping a session."""
    # Mock the CLI runner's start and stop methods
    mocker.patch.object(
        claude_runner.cli_runner, "start", return_value=mock_process
    )
    mocker.patch.object(
        claude_runner.cli_runner, "stop", return_value=None
    )
    
    # Create a test workspace directory
    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    
    # Start a session
    session = await claude_runner.start_session(
        workspace_path=workspace_path,
    )
    
    # Stop the session
    await claude_runner.stop_session(session.id)
    
    # Check that the session state was updated correctly
    updated_session = await claude_runner.get_session(session.id)
    assert updated_session.state == SessionState.TERMINATED
    
    # Check that the CLI runner's stop method was called
    claude_runner.cli_runner.stop.assert_called_once()


@pytest.mark.asyncio
async def test_send_message(claude_runner, mock_process, mocker: MockerFixture, tmp_path):
    """Test sending a message to a session."""
    # Mock the CLI runner's start and send_message methods
    mocker.patch.object(
        claude_runner.cli_runner, "start", return_value=mock_process
    )
    mocker.patch.object(
        claude_runner.cli_runner, "send_message", return_value=None
    )
    
    # Mock the stream processor's process_stream method
    mock_messages = [
        ClaudeMessage(
            type=MessageType.ASSISTANT,
            content="Hello, world!",
            session_id="test-session",
        )
    ]
    
    # Create a mock StreamProcessor that yields the mock messages
    mock_stream_processor = MagicMock()
    mock_stream_processor.process_stream.return_value = mock_messages
    
    # Patch the StreamProcessor class to return our mock
    mocker.patch(
        "claude_code_bot.claude_runner.StreamProcessor",
        return_value=mock_stream_processor,
    )
    
    # Create a test workspace directory
    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    
    # Start a session
    session = await claude_runner.start_session(
        workspace_path=workspace_path,
    )
    
    # Send a message to the session
    messages = []
    async for message in claude_runner.send_message(session.id, "Hello, Claude!"):
        messages.append(message)
    
    # Check that the CLI runner's send_message method was called correctly
    claude_runner.cli_runner.send_message.assert_called_once_with("Hello, Claude!")
    
    # Check that the stream processor's process_stream method was called
    mock_stream_processor.process_stream.assert_called_once()
    
    # Check that we received the expected messages
    assert len(messages) == 1
    assert messages[0].type == MessageType.ASSISTANT
    assert messages[0].content == "Hello, world!"
    assert messages[0].session_id == session.id


@pytest.mark.asyncio
async def test_list_sessions(claude_runner, mock_process, mocker: MockerFixture, tmp_path):
    """Test listing sessions."""
    # Mock the CLI runner's start method
    mocker.patch.object(
        claude_runner.cli_runner, "start", return_value=mock_process
    )
    
    # Create a test workspace directory
    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    
    # Start two sessions
    session1 = await claude_runner.start_session(
        workspace_path=workspace_path,
        system_prompt="Test prompt 1",
    )
    
    session2 = await claude_runner.start_session(
        workspace_path=workspace_path,
        system_prompt="Test prompt 2",
    )
    
    # List the sessions
    sessions = await claude_runner.list_sessions()
    
    # Check that both sessions are in the list
    assert len(sessions) == 2
    session_ids = {session.id for session in sessions}
    assert session1.id in session_ids
    assert session2.id in session_ids

