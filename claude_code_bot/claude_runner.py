"""
Main API for Claude Code CLI.

This module provides the main API for the Claude Code CLI wrapper,
including session management, message sending, and tool execution.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Set, Union

from .cli.runner import ClaudeCliRunner
from .cli.stream import StreamProcessor
from .config import Config
from .mcp.server import McpServer, McpServerManager
from .mcp.tools import ToolManager, ToolPermission
from .models.messages import AnyClaudeMessage, ClaudeMessage, MessageType, ToolUseMessage
from .session.manager import SessionManager
from .session.models import Session, SessionState
from .utils.errors import (
    ClaudeCliError,
    ClaudeCodeError,
    McpServerError,
    SessionError,
    StreamProcessingError,
)

logger = logging.getLogger(__name__)


class ClaudeRunner:
    """
    Main API for Claude Code CLI.

    This class provides the main API for the Claude Code CLI wrapper,
    including session management, message sending, and tool execution.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Claude runner.

        Args:
            config: Optional configuration for the Claude runner.
                If not provided, configuration will be loaded from environment variables.
        """
        self.config = config or Config.from_env()
        self.cli_runner = ClaudeCliRunner(self.config)
        self.session_manager = SessionManager(self.config)
        self.mcp_manager = McpServerManager(self.config)
        self.tool_manager = ToolManager()
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Initialize the Claude runner.

        This method initializes the session manager and MCP server manager.
        """
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            await self.session_manager.initialize()
            self.mcp_manager.initialize()
            self._initialized = True
            logger.info("Initialized Claude runner")

    async def shutdown(self) -> None:
        """
        Shut down the Claude runner.

        This method shuts down the session manager and stops any running sessions.
        """
        if not self._initialized:
            return

        async with self._lock:
            if not self._initialized:
                return

            # Stop all running sessions
            sessions = await self.session_manager.list_sessions()
            for session in sessions:
                if session.state == SessionState.RUNNING:
                    try:
                        await self.stop_session(session.id)
                    except Exception as e:
                        logger.warning(f"Failed to stop session {session.id}: {e}")

            # Shut down the session manager
            await self.session_manager.shutdown()
            self._initialized = False
            logger.info("Shut down Claude runner")

    async def start_session(
        self,
        workspace_path: Union[str, Path],
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Start a new Claude Code session.

        Args:
            workspace_path: Path to the workspace directory.
            system_prompt: Optional system prompt for Claude.
            allowed_tools: Optional list of allowed tools.
            metadata: Optional metadata for the session.

        Returns:
            The created session.

        Raises:
            ClaudeCodeError: If the session cannot be created or started.
        """
        if not self._initialized:
            await self.initialize()

        workspace_path = Path(workspace_path).resolve()
        if not workspace_path.exists():
            raise ClaudeCodeError(
                f"Workspace path does not exist: {workspace_path}",
                details={"workspace_path": str(workspace_path)},
            )

        # Create a new session
        try:
            session = await self.session_manager.create_session(
                workspace_path=workspace_path,
                system_prompt=system_prompt,
                allowed_tools=set(allowed_tools) if allowed_tools else None,
                metadata=metadata,
            )
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to create session: {e}", details=e.details) from e

        # Start the Claude CLI process
        try:
            process = await self.cli_runner.start(
                workspace_path=workspace_path,
                system_prompt=system_prompt,
                allowed_tools=allowed_tools,
            )
        except ClaudeCliError as e:
            # Update session state to error
            session.update_state(SessionState.ERROR, str(e))
            await self.session_manager.update_session(session)
            raise ClaudeCodeError(f"Failed to start Claude CLI process: {e}", details=e.details) from e

        # Update session state to running
        session.update_state(SessionState.RUNNING)
        await self.session_manager.update_session(session)

        logger.info(f"Started session {session.id}")
        return session

    async def send_message(
        self, session_id: str, message: str
    ) -> AsyncIterator[AnyClaudeMessage]:
        """
        Send a message to a Claude Code session.

        Args:
            session_id: The ID of the session to send the message to.
            message: The message to send.

        Yields:
            Messages from Claude Code.

        Raises:
            ClaudeCodeError: If the message cannot be sent or the session is not running.
        """
        if not self._initialized:
            await self.initialize()

        # Get the session
        try:
            session = await self.session_manager.get_session(session_id)
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to get session: {e}", details=e.details) from e

        # Check if the session is running
        if session.state != SessionState.RUNNING:
            raise ClaudeCodeError(
                f"Session is not running: {session_id}",
                details={"session_id": session_id, "state": session.state},
            )

        # Send the message to the Claude CLI process
        try:
            await self.cli_runner.send_message(message)
        except ClaudeCliError as e:
            # Update session state to error
            session.update_state(SessionState.ERROR, str(e))
            await self.session_manager.update_session(session)
            raise ClaudeCodeError(f"Failed to send message: {e}", details=e.details) from e

        # Create a user message and add it to the session history
        user_message = ClaudeMessage(
            type=MessageType.USER,
            content=message,
            session_id=session_id,
        )
        session.add_message(user_message)
        await self.session_manager.update_session(session)

        # Process the response stream
        stream_processor = StreamProcessor(self.cli_runner.process)
        try:
            async for claude_message in stream_processor.process_stream():
                # Set the session ID on the message
                claude_message.session_id = session_id

                # Add the message to the session history
                session.add_message(claude_message)
                await self.session_manager.update_session(session)

                # Handle tool use messages
                if claude_message.type == MessageType.TOOL_USE:
                    tool_message = claude_message
                    if isinstance(tool_message, ToolUseMessage):
                        # TODO: Implement tool execution
                        pass

                yield claude_message
        except StreamProcessingError as e:
            # Update session state to error
            session.update_state(SessionState.ERROR, str(e))
            await self.session_manager.update_session(session)
            raise ClaudeCodeError(f"Failed to process response stream: {e}", details=e.details) from e

    async def continue_session(self, session_id: str) -> AsyncIterator[AnyClaudeMessage]:
        """
        Continue a Claude Code session.

        Args:
            session_id: The ID of the session to continue.

        Yields:
            Messages from Claude Code.

        Raises:
            ClaudeCodeError: If the session cannot be continued or is not in a pausable state.
        """
        if not self._initialized:
            await self.initialize()

        # Get the session
        try:
            session = await self.session_manager.get_session(session_id)
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to get session: {e}", details=e.details) from e

        # Check if the session is in a pausable state
        if session.state not in (SessionState.RUNNING, SessionState.PAUSED):
            raise ClaudeCodeError(
                f"Session is not in a pausable state: {session_id}",
                details={"session_id": session_id, "state": session.state},
            )

        # If the session is paused, restart the Claude CLI process
        if session.state == SessionState.PAUSED:
            try:
                process = await self.cli_runner.start(
                    workspace_path=session.workspace_path,
                    system_prompt=session.system_prompt,
                    allowed_tools=list(session.allowed_tools) if session.allowed_tools else None,
                )
            except ClaudeCliError as e:
                # Update session state to error
                session.update_state(SessionState.ERROR, str(e))
                await self.session_manager.update_session(session)
                raise ClaudeCodeError(
                    f"Failed to restart Claude CLI process: {e}", details=e.details
                ) from e

            # Update session state to running
            session.update_state(SessionState.RUNNING)
            await self.session_manager.update_session(session)

        # Process the response stream
        stream_processor = StreamProcessor(self.cli_runner.process)
        try:
            async for claude_message in stream_processor.process_stream():
                # Set the session ID on the message
                claude_message.session_id = session_id

                # Add the message to the session history
                session.add_message(claude_message)
                await self.session_manager.update_session(session)

                # Handle tool use messages
                if claude_message.type == MessageType.TOOL_USE:
                    tool_message = claude_message
                    if isinstance(tool_message, ToolUseMessage):
                        # TODO: Implement tool execution
                        pass

                yield claude_message
        except StreamProcessingError as e:
            # Update session state to error
            session.update_state(SessionState.ERROR, str(e))
            await self.session_manager.update_session(session)
            raise ClaudeCodeError(f"Failed to process response stream: {e}", details=e.details) from e

    async def stop_session(self, session_id: str) -> None:
        """
        Stop a Claude Code session.

        Args:
            session_id: The ID of the session to stop.

        Raises:
            ClaudeCodeError: If the session cannot be stopped.
        """
        if not self._initialized:
            await self.initialize()

        # Get the session
        try:
            session = await self.session_manager.get_session(session_id)
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to get session: {e}", details=e.details) from e

        # Check if the session is running
        if session.state != SessionState.RUNNING:
            logger.debug(f"Session is not running: {session_id}")
            return

        # Stop the Claude CLI process
        try:
            await self.cli_runner.stop()
        except ClaudeCliError as e:
            # Update session state to error
            session.update_state(SessionState.ERROR, str(e))
            await self.session_manager.update_session(session)
            raise ClaudeCodeError(f"Failed to stop Claude CLI process: {e}", details=e.details) from e

        # Update session state to terminated
        session.update_state(SessionState.TERMINATED)
        await self.session_manager.update_session(session)

        logger.info(f"Stopped session {session_id}")

    async def pause_session(self, session_id: str) -> None:
        """
        Pause a Claude Code session.

        This method stops the Claude CLI process but keeps the session in a pausable state.

        Args:
            session_id: The ID of the session to pause.

        Raises:
            ClaudeCodeError: If the session cannot be paused.
        """
        if not self._initialized:
            await self.initialize()

        # Get the session
        try:
            session = await self.session_manager.get_session(session_id)
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to get session: {e}", details=e.details) from e

        # Check if the session is running
        if session.state != SessionState.RUNNING:
            logger.debug(f"Session is not running: {session_id}")
            return

        # Stop the Claude CLI process
        try:
            await self.cli_runner.stop()
        except ClaudeCliError as e:
            # Update session state to error
            session.update_state(SessionState.ERROR, str(e))
            await self.session_manager.update_session(session)
            raise ClaudeCodeError(f"Failed to stop Claude CLI process: {e}", details=e.details) from e

        # Update session state to paused
        session.update_state(SessionState.PAUSED)
        await self.session_manager.update_session(session)

        logger.info(f"Paused session {session_id}")

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a Claude Code session.

        Args:
            session_id: The ID of the session to delete.

        Raises:
            ClaudeCodeError: If the session cannot be deleted.
        """
        if not self._initialized:
            await self.initialize()

        # Get the session
        try:
            session = await self.session_manager.get_session(session_id)
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to get session: {e}", details=e.details) from e

        # Stop the session if it's running
        if session.state == SessionState.RUNNING:
            try:
                await self.stop_session(session_id)
            except ClaudeCodeError as e:
                logger.warning(f"Failed to stop session {session_id}: {e}")

        # Delete the session
        try:
            await self.session_manager.delete_session(session_id)
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to delete session: {e}", details=e.details) from e

        logger.info(f"Deleted session {session_id}")

    async def list_sessions(self) -> List[Session]:
        """
        List all Claude Code sessions.

        Returns:
            A list of all sessions.

        Raises:
            ClaudeCodeError: If the sessions cannot be listed.
        """
        if not self._initialized:
            await self.initialize()

        try:
            return await self.session_manager.list_sessions()
        except Exception as e:
            raise ClaudeCodeError(f"Failed to list sessions: {e}") from e

    async def get_session(self, session_id: str) -> Session:
        """
        Get a Claude Code session by ID.

        Args:
            session_id: The ID of the session to get.

        Returns:
            The session.

        Raises:
            ClaudeCodeError: If the session cannot be found.
        """
        if not self._initialized:
            await self.initialize()

        try:
            return await self.session_manager.get_session(session_id)
        except SessionError as e:
            raise ClaudeCodeError(f"Failed to get session: {e}", details=e.details) from e

