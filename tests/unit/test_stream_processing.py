"""
Unit tests for NDJSON stream processing.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from claude_code_bot.cli.stream import StreamProcessor
from claude_code_bot.models.messages import (
    ClaudeMessage,
    MessageType,
    ToolResultMessage,
    ToolUseMessage,
)
from claude_code_bot.utils.errors import StreamProcessingError


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
def stream_processor(mock_process):
    """Create a test stream processor."""
    return StreamProcessor(mock_process)


def create_message_json(
    message_type=MessageType.ASSISTANT, content="Test message", session_id="test-session"
):
    """Create a JSON string for a test message."""
    message = {
        "type": message_type.value,
        "content": content,
        "session_id": session_id,
        "timestamp": "2023-01-01T12:00:00",
    }
    return json.dumps(message)


def create_tool_use_json(
    content="Using tool",
    session_id="test-session",
    tool_name="test-tool",
    tool_input=None,
    tool_use_id="test-tool-use",
):
    """Create a JSON string for a test tool use message."""
    message = {
        "type": MessageType.TOOL_USE.value,
        "content": content,
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_input": tool_input or {"param": "value"},
        "tool_use_id": tool_use_id,
        "timestamp": "2023-01-01T12:00:00",
    }
    return json.dumps(message)


def create_tool_result_json(
    content="Tool result",
    session_id="test-session",
    tool_use_id="test-tool-use",
    result=None,
    is_error=False,
):
    """Create a JSON string for a test tool result message."""
    message = {
        "type": MessageType.TOOL_RESULT.value,
        "content": content,
        "session_id": session_id,
        "tool_use_id": tool_use_id,
        "result": result or {"output": "value"},
        "is_error": is_error,
        "timestamp": "2023-01-01T12:00:00",
    }
    return json.dumps(message)


class MockStreamReader:
    """Mock for asyncio.StreamReader that yields predefined lines."""

    def __init__(self, lines):
        self.lines = lines
        self.index = 0

    async def readline(self):
        """Return the next line or an empty bytes object if at the end."""
        if self.index < len(self.lines):
            line = self.lines[self.index]
            self.index += 1
            return line
        return b""

    def at_eof(self):
        """Return True if all lines have been read."""
        return self.index >= len(self.lines)


@pytest.mark.asyncio
async def test_process_stream_assistant_message(stream_processor, mock_process, mocker: MockerFixture):
    """Test processing an assistant message from the stream."""
    # Create a mock stream reader with a single assistant message
    message_json = create_message_json()
    mock_reader = MockStreamReader([message_json.encode() + b"\n"])
    mock_process.stdout = mock_reader

    # Process the stream
    messages = []
    async for message in stream_processor.process_stream():
        messages.append(message)

    # Check that we received the expected message
    assert len(messages) == 1
    assert messages[0].type == MessageType.ASSISTANT
    assert messages[0].content == "Test message"
    assert messages[0].session_id == "test-session"


@pytest.mark.asyncio
async def test_process_stream_tool_use_message(stream_processor, mock_process, mocker: MockerFixture):
    """Test processing a tool use message from the stream."""
    # Create a mock stream reader with a single tool use message
    message_json = create_tool_use_json()
    mock_reader = MockStreamReader([message_json.encode() + b"\n"])
    mock_process.stdout = mock_reader

    # Process the stream
    messages = []
    async for message in stream_processor.process_stream():
        messages.append(message)

    # Check that we received the expected message
    assert len(messages) == 1
    assert isinstance(messages[0], ToolUseMessage)
    assert messages[0].type == MessageType.TOOL_USE
    assert messages[0].content == "Using tool"
    assert messages[0].session_id == "test-session"
    assert messages[0].tool_name == "test-tool"
    assert messages[0].tool_input == {"param": "value"}
    assert messages[0].tool_use_id == "test-tool-use"


@pytest.mark.asyncio
async def test_process_stream_tool_result_message(stream_processor, mock_process, mocker: MockerFixture):
    """Test processing a tool result message from the stream."""
    # Create a mock stream reader with a single tool result message
    message_json = create_tool_result_json()
    mock_reader = MockStreamReader([message_json.encode() + b"\n"])
    mock_process.stdout = mock_reader

    # Process the stream
    messages = []
    async for message in stream_processor.process_stream():
        messages.append(message)

    # Check that we received the expected message
    assert len(messages) == 1
    assert isinstance(messages[0], ToolResultMessage)
    assert messages[0].type == MessageType.TOOL_RESULT
    assert messages[0].content == "Tool result"
    assert messages[0].session_id == "test-session"
    assert messages[0].tool_use_id == "test-tool-use"
    assert messages[0].result == {"output": "value"}
    assert messages[0].is_error is False


@pytest.mark.asyncio
async def test_process_stream_multiple_messages(stream_processor, mock_process, mocker: MockerFixture):
    """Test processing multiple messages from the stream."""
    # Create a mock stream reader with multiple messages
    message_jsons = [
        create_message_json(),
        create_tool_use_json(),
        create_tool_result_json(),
    ]
    mock_reader = MockStreamReader([json.encode() + b"\n" for json in message_jsons])
    mock_process.stdout = mock_reader

    # Process the stream
    messages = []
    async for message in stream_processor.process_stream():
        messages.append(message)

    # Check that we received the expected messages
    assert len(messages) == 3
    assert messages[0].type == MessageType.ASSISTANT
    assert isinstance(messages[1], ToolUseMessage)
    assert isinstance(messages[2], ToolResultMessage)


@pytest.mark.asyncio
async def test_process_stream_invalid_json(stream_processor, mock_process, mocker: MockerFixture):
    """Test processing an invalid JSON message from the stream."""
    # Create a mock stream reader with an invalid JSON message
    invalid_json = "This is not valid JSON"
    mock_reader = MockStreamReader([invalid_json.encode() + b"\n"])
    mock_process.stdout = mock_reader

    # Process the stream
    with pytest.raises(StreamProcessingError):
        async for message in stream_processor.process_stream():
            pass


@pytest.mark.asyncio
async def test_process_stream_invalid_message(stream_processor, mock_process, mocker: MockerFixture):
    """Test processing a valid JSON but invalid message from the stream."""
    # Create a mock stream reader with a valid JSON but invalid message
    invalid_message = json.dumps({"type": "invalid", "content": "Test message"})
    mock_reader = MockStreamReader([invalid_message.encode() + b"\n"])
    mock_process.stdout = mock_reader

    # Process the stream
    with pytest.raises(StreamProcessingError):
        async for message in stream_processor.process_stream():
            pass


@pytest.mark.asyncio
async def test_process_stream_with_type(stream_processor, mock_process, mocker: MockerFixture):
    """Test processing the stream and filtering by message type."""
    # Create a mock stream reader with multiple messages
    message_jsons = [
        create_message_json(),
        create_tool_use_json(),
        create_tool_result_json(),
    ]
    mock_reader = MockStreamReader([json.encode() + b"\n" for json in message_jsons])
    mock_process.stdout = mock_reader

    # Process the stream and filter for ToolUseMessage
    messages = []
    async for message in stream_processor.process_stream_with_type(ToolUseMessage):
        messages.append(message)

    # Check that we received only the tool use message
    assert len(messages) == 1
    assert isinstance(messages[0], ToolUseMessage)
    assert messages[0].type == MessageType.TOOL_USE

