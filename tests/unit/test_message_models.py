"""
Unit tests for message models.
"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from claude_code_bot.models.messages import (
    AnyClaudeMessage,
    ClaudeMessage,
    MessageType,
    ToolResultMessage,
    ToolUseMessage,
)


def test_claude_message_creation():
    """Test creating a ClaudeMessage."""
    message = ClaudeMessage(
        type=MessageType.ASSISTANT,
        content="Hello, world!",
        session_id="test-session",
    )
    assert message.type == MessageType.ASSISTANT
    assert message.content == "Hello, world!"
    assert message.session_id == "test-session"
    assert message.metadata is None
    assert isinstance(message.timestamp, datetime)


def test_tool_use_message_creation():
    """Test creating a ToolUseMessage."""
    message = ToolUseMessage(
        content="Using tool",
        session_id="test-session",
        tool_name="test-tool",
        tool_input={"param": "value"},
        tool_use_id="test-tool-use",
    )
    assert message.type == MessageType.TOOL_USE
    assert message.content == "Using tool"
    assert message.session_id == "test-session"
    assert message.tool_name == "test-tool"
    assert message.tool_input == {"param": "value"}
    assert message.tool_use_id == "test-tool-use"
    assert isinstance(message.timestamp, datetime)


def test_tool_result_message_creation():
    """Test creating a ToolResultMessage."""
    message = ToolResultMessage(
        content="Tool result",
        session_id="test-session",
        tool_use_id="test-tool-use",
        result={"output": "value"},
    )
    assert message.type == MessageType.TOOL_RESULT
    assert message.content == "Tool result"
    assert message.session_id == "test-session"
    assert message.tool_use_id == "test-tool-use"
    assert message.result == {"output": "value"}
    assert message.is_error is False
    assert isinstance(message.timestamp, datetime)


def test_tool_result_message_with_error():
    """Test creating a ToolResultMessage with an error."""
    message = ToolResultMessage(
        content="Tool error",
        session_id="test-session",
        tool_use_id="test-tool-use",
        result={"error": "Something went wrong"},
        is_error=True,
    )
    assert message.type == MessageType.TOOL_RESULT
    assert message.content == "Tool error"
    assert message.session_id == "test-session"
    assert message.tool_use_id == "test-tool-use"
    assert message.result == {"error": "Something went wrong"}
    assert message.is_error is True


def test_message_to_dict():
    """Test converting a message to a dictionary."""
    message = ClaudeMessage(
        type=MessageType.ASSISTANT,
        content="Hello, world!",
        session_id="test-session",
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
    )
    message_dict = message.to_dict()
    assert message_dict["type"] == "assistant"
    assert message_dict["content"] == "Hello, world!"
    assert message_dict["session_id"] == "test-session"
    assert "timestamp" in message_dict


def test_message_from_dict():
    """Test creating a message from a dictionary."""
    message_dict = {
        "type": "assistant",
        "content": "Hello, world!",
        "session_id": "test-session",
        "timestamp": "2023-01-01T12:00:00",
    }
    message = ClaudeMessage.from_dict(message_dict)
    assert message.type == MessageType.ASSISTANT
    assert message.content == "Hello, world!"
    assert message.session_id == "test-session"


def test_tool_use_message_from_dict():
    """Test creating a ToolUseMessage from a dictionary."""
    message_dict = {
        "type": "tool_use",
        "content": "Using tool",
        "session_id": "test-session",
        "tool_name": "test-tool",
        "tool_input": {"param": "value"},
        "tool_use_id": "test-tool-use",
        "timestamp": "2023-01-01T12:00:00",
    }
    message = ClaudeMessage.from_dict(message_dict)
    assert isinstance(message, ToolUseMessage)
    assert message.type == MessageType.TOOL_USE
    assert message.content == "Using tool"
    assert message.session_id == "test-session"
    assert message.tool_name == "test-tool"
    assert message.tool_input == {"param": "value"}
    assert message.tool_use_id == "test-tool-use"


def test_tool_result_message_from_dict():
    """Test creating a ToolResultMessage from a dictionary."""
    message_dict = {
        "type": "tool_result",
        "content": "Tool result",
        "session_id": "test-session",
        "tool_use_id": "test-tool-use",
        "result": {"output": "value"},
        "timestamp": "2023-01-01T12:00:00",
    }
    message = ClaudeMessage.from_dict(message_dict)
    assert isinstance(message, ToolResultMessage)
    assert message.type == MessageType.TOOL_RESULT
    assert message.content == "Tool result"
    assert message.session_id == "test-session"
    assert message.tool_use_id == "test-tool-use"
    assert message.result == {"output": "value"}
    assert message.is_error is False


def test_invalid_message_type():
    """Test creating a message with an invalid type."""
    with pytest.raises(ValidationError):
        ClaudeMessage(
            type="invalid",
            content="Hello, world!",
            session_id="test-session",
        )


def test_missing_required_fields():
    """Test creating a message with missing required fields."""
    with pytest.raises(ValidationError):
        ClaudeMessage(
            type=MessageType.ASSISTANT,
            content="Hello, world!",
        )

    with pytest.raises(ValidationError):
        ToolUseMessage(
            content="Using tool",
            session_id="test-session",
            tool_input={"param": "value"},
            tool_use_id="test-tool-use",
        )

    with pytest.raises(ValidationError):
        ToolResultMessage(
            content="Tool result",
            session_id="test-session",
            result={"output": "value"},
        )

