"""
Session management for Claude Code CLI.

This module provides session management for the Claude Code CLI,
including creating, retrieving, and managing sessions.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import aiofiles

from ..config import Config
from ..utils.errors import SessionError
from .models import Session, SessionState

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manager for Claude Code CLI sessions.

    This class handles creating, retrieving, and managing sessions,
    including persistence and cleanup.
    """

    def __init__(self, config: Config):
        """
        Initialize the session manager.

        Args:
            config: Configuration for the session manager.
        """
        self.config = config
        self.sessions: Dict[str, Session] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Initialize the session manager.

        This method loads existing sessions from disk and starts the cleanup task.
        """
        await self._load_sessions()
        self._start_cleanup_task()

    async def shutdown(self) -> None:
        """
        Shut down the session manager.

        This method stops the cleanup task and saves all sessions to disk.
        """
        self._stop_cleanup_task()
        await self._save_all_sessions()

    async def create_session(
        self,
        workspace_path: Path,
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Create a new session.

        Args:
            workspace_path: Path to the workspace directory.
            system_prompt: Optional system prompt for Claude.
            allowed_tools: Optional set of allowed tools.
            metadata: Optional metadata for the session.

        Returns:
            The created session.

        Raises:
            SessionError: If the session cannot be created.
        """
        async with self._lock:
            if len(self.sessions) >= self.config.session.max_sessions:
                # Try to clean up expired sessions
                await self._cleanup_expired_sessions()

                # Check again if we have room for a new session
                if len(self.sessions) >= self.config.session.max_sessions:
                    raise SessionError(
                        f"Maximum number of sessions reached: {self.config.session.max_sessions}"
                    )

            session = Session(
                workspace_path=workspace_path,
                system_prompt=system_prompt,
                allowed_tools=allowed_tools or set(),
                metadata=metadata or {},
            )

            self.sessions[session.id] = session
            await self._save_session(session)

            logger.info(f"Created session {session.id}")
            return session

    async def get_session(self, session_id: str) -> Session:
        """
        Get a session by ID.

        Args:
            session_id: The ID of the session to get.

        Returns:
            The session.

        Raises:
            SessionError: If the session does not exist.
        """
        async with self._lock:
            if session_id not in self.sessions:
                # Try to load the session from disk
                try:
                    session = await self._load_session(session_id)
                    self.sessions[session_id] = session
                    return session
                except Exception as e:
                    raise SessionError(
                        f"Session not found: {session_id}", session_id=session_id
                    ) from e

            return self.sessions[session_id]

    async def update_session(self, session: Session) -> None:
        """
        Update a session.

        Args:
            session: The session to update.

        Raises:
            SessionError: If the session does not exist.
        """
        async with self._lock:
            if session.id not in self.sessions:
                raise SessionError(
                    f"Session not found: {session.id}", session_id=session.id
                )

            self.sessions[session.id] = session
            session.updated_at = datetime.now()
            await self._save_session(session)

            logger.debug(f"Updated session {session.id}")

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: The ID of the session to delete.

        Raises:
            SessionError: If the session does not exist.
        """
        async with self._lock:
            if session_id not in self.sessions:
                raise SessionError(
                    f"Session not found: {session_id}", session_id=session_id
                )

            # Remove the session from memory
            session = self.sessions.pop(session_id)

            # Delete the session file
            session_file = self._get_session_file_path(session_id)
            try:
                if os.path.exists(session_file):
                    os.remove(session_file)
            except OSError as e:
                logger.warning(f"Failed to delete session file {session_file}: {e}")

            logger.info(f"Deleted session {session_id}")

    async def list_sessions(self) -> List[Session]:
        """
        List all sessions.

        Returns:
            A list of all sessions.
        """
        async with self._lock:
            return list(self.sessions.values())

    async def _save_session(self, session: Session) -> None:
        """
        Save a session to disk.

        Args:
            session: The session to save.

        Raises:
            SessionError: If the session cannot be saved.
        """
        session_file = self._get_session_file_path(session.id)
        session_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiofiles.open(session_file, "w") as f:
                await f.write(session.to_json())
        except OSError as e:
            raise SessionError(
                f"Failed to save session {session.id}: {e}", session_id=session.id
            ) from e

    async def _load_session(self, session_id: str) -> Session:
        """
        Load a session from disk.

        Args:
            session_id: The ID of the session to load.

        Returns:
            The loaded session.

        Raises:
            SessionError: If the session cannot be loaded.
        """
        session_file = self._get_session_file_path(session_id)
        if not session_file.exists():
            raise SessionError(
                f"Session file not found: {session_file}", session_id=session_id
            )

        try:
            async with aiofiles.open(session_file, "r") as f:
                session_json = await f.read()
            return Session.from_json(session_json)
        except (OSError, json.JSONDecodeError) as e:
            raise SessionError(
                f"Failed to load session {session_id}: {e}", session_id=session_id
            ) from e

    async def _load_sessions(self) -> None:
        """
        Load all sessions from disk.

        This method loads all session files from the session directory.
        """
        session_dir = Path(self.config.session.session_dir)
        if not session_dir.exists():
            session_dir.mkdir(parents=True, exist_ok=True)
            return

        for session_file in session_dir.glob("*.json"):
            try:
                session_id = session_file.stem
                session = await self._load_session(session_id)
                self.sessions[session_id] = session
                logger.debug(f"Loaded session {session_id}")
            except Exception as e:
                logger.warning(f"Failed to load session from {session_file}: {e}")

    async def _save_all_sessions(self) -> None:
        """
        Save all sessions to disk.

        This method saves all sessions in memory to disk.
        """
        for session in self.sessions.values():
            try:
                await self._save_session(session)
            except Exception as e:
                logger.warning(f"Failed to save session {session.id}: {e}")

    async def _cleanup_expired_sessions(self) -> None:
        """
        Clean up expired sessions.

        This method removes sessions that have been inactive for longer than the session timeout.
        """
        now = datetime.now()
        timeout = timedelta(seconds=self.config.session.session_timeout)
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if now - session.last_active_at > timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            try:
                await self.delete_session(session_id)
                logger.info(f"Cleaned up expired session {session_id}")
            except Exception as e:
                logger.warning(f"Failed to clean up expired session {session_id}: {e}")

    def _get_session_file_path(self, session_id: str) -> Path:
        """
        Get the file path for a session.

        Args:
            session_id: The ID of the session.

        Returns:
            The file path for the session.
        """
        return Path(self.config.session.session_dir) / f"{session_id}.json"

    def _start_cleanup_task(self) -> None:
        """
        Start the cleanup task.

        This method starts a background task that periodically cleans up expired sessions.
        """
        if self._cleanup_task is not None and not self._cleanup_task.done():
            return

        async def cleanup_loop() -> None:
            while True:
                try:
                    await asyncio.sleep(self.config.session.cleanup_interval)
                    await self._cleanup_expired_sessions()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in session cleanup task: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    def _stop_cleanup_task(self) -> None:
        """
        Stop the cleanup task.

        This method stops the background cleanup task.
        """
        if self._cleanup_task is not None and not self._cleanup_task.done():
            self._cleanup_task.cancel()

