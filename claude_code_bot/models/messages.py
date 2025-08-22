"""
Message models for Claude Code CLI.

This module defines the Pydantic models for the different types of messages
that can be exchanged with the Claude Code CLI.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Literal, Optional, Union

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Enum for message types."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


class ClaudeMessage(BaseModel):
    """Base class for all Claude Code messages."""

    type: MessageType = Field(..., description="Type of the message")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp of the message"
    )
    session_id: str = Field(..., description="ID of the session")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata for the message"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClaudeMessage":
        """Create a message from a dictionary."""
        msg_type = data.get("type")
        if msg_type == MessageType.TOOL_USE:
            return ToolUseMessage(**data)
        elif msg_type == MessageType.TOOL_RESULT:
            return ToolResultMessage(**data)
        else:
            return cls(**data)


class ToolUseMessage(ClaudeMessage):
    """Message for tool use requests."""

    type: Literal[MessageType.TOOL_USE] = Field(
        MessageType.TOOL_USE, description="Type of the message"
    )
    tool_name: str = Field(..., description="Name of the tool to use")
    tool_input: Dict[str, Any] = Field(..., description="Input for the tool")
    tool_use_id: str = Field(..., description="ID of the tool use request")


class ToolResultMessage(ClaudeMessage):
    """Message for tool execution results."""

    type: Literal[MessageType.TOOL_RESULT] = Field(
        MessageType.TOOL_RESULT, description="Type of the message"
    )
    tool_use_id: str = Field(..., description="ID of the tool use request")
    is_error: bool = Field(False, description="Whether the tool execution resulted in an error")
    result: Any = Field(..., description="Result of the tool execution")


# Type alias for any type of Claude message
AnyClaudeMessage = Union[ClaudeMessage, ToolUseMessage, ToolResultMessage]

