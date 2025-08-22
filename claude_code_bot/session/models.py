"""
Session models for Claude Code CLI.

This module defines the models for Claude Code CLI sessions,
including session state and history.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator

from ..models.messages import AnyClaudeMessage, ClaudeMessage


class SessionState(str, Enum):
    """Enum for session states."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATED = "terminated"
    ERROR = "error"


class Session(BaseModel):
    """Model for a Claude Code CLI session."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Session ID")
    workspace_path: Path = Field(..., description="Path to the workspace directory")
    system_prompt: Optional[str] = Field(None, description="System prompt for Claude")
    allowed_tools: Set[str] = Field(default_factory=set, description="Set of allowed tools")
    state: SessionState = Field(
        default=SessionState.CREATED, description="Current state of the session"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the session was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the session was last updated"
    )
    last_active_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the session was last active"
    )
    message_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="History of messages in the session"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the session"
    )
    error: Optional[str] = Field(None, description="Error message if the session is in error state")

    @field_validator("workspace_path")
    @classmethod
    def validate_workspace_path(cls, v: Path) -> Path:
        """Validate the workspace path."""
        return v.resolve()

    def add_message(self, message: AnyClaudeMessage) -> None:
        """
        Add a message to the session history.

        Args:
            message: The message to add.
        """
        self.message_history.append(message.model_dump())
        self.updated_at = datetime.now()
        self.last_active_at = datetime.now()

    def update_state(self, state: SessionState, error: Optional[str] = None) -> None:
        """
        Update the session state.

        Args:
            state: The new state.
            error: Optional error message if the state is ERROR.
        """
        self.state = state
        self.updated_at = datetime.now()
        if state == SessionState.ERROR and error:
            self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the session to a dictionary.

        Returns:
            The session as a dictionary.
        """
        return self.model_dump()

    def to_json(self) -> str:
        """
        Convert the session to a JSON string.

        Returns:
            The session as a JSON string.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """
        Create a session from a dictionary.

        Args:
            data: The dictionary to create the session from.

        Returns:
            The created session.
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Session":
        """
        Create a session from a JSON string.

        Args:
            json_str: The JSON string to create the session from.

        Returns:
            The created session.
        """
        return cls.from_dict(json.loads(json_str))

    def is_active(self) -> bool:
        """
        Check if the session is active.

        Returns:
            True if the session is active, False otherwise.
        """
        return self.state in (SessionState.RUNNING, SessionState.PAUSED)

    def is_terminated(self) -> bool:
        """
        Check if the session is terminated.

        Returns:
            True if the session is terminated, False otherwise.
        """
        return self.state in (SessionState.TERMINATED, SessionState.ERROR)

