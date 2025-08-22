"""
Async subprocess execution for Claude Code CLI.

This module provides async subprocess execution for the Claude Code CLI,
including starting, stopping, and communicating with the subprocess.
"""

import asyncio
import logging
import os
import shlex
import signal
from asyncio.subprocess import Process
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..config import Config
from ..utils.async_utils import terminate_process
from ..utils.errors import ClaudeCliError

logger = logging.getLogger(__name__)


class ClaudeCliRunner:
    """
    Runner for Claude Code CLI subprocess.

    This class handles the low-level interaction with the Claude Code CLI process,
    including starting, stopping, and communicating with the subprocess.
    """

    def __init__(self, config: Config):
        """
        Initialize the Claude CLI runner.

        Args:
            config: Configuration for the Claude CLI runner.
        """
        self.config = config
        self.process: Optional[Process] = None
        self._process_lock = asyncio.Lock()

    async def start(
        self,
        workspace_path: Union[str, Path],
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Process:
        """
        Start the Claude Code CLI subprocess.

        Args:
            workspace_path: Path to the workspace directory.
            system_prompt: Optional system prompt for Claude.
            allowed_tools: Optional list of allowed tools.
            env_vars: Optional environment variables for the subprocess.

        Returns:
            The started subprocess.

        Raises:
            ClaudeCliError: If the subprocess fails to start.
        """
        async with self._process_lock:
            if self.process is not None and self.process.returncode is None:
                logger.warning("Claude CLI process is already running, terminating it")
                await self.stop()

            workspace_path = Path(workspace_path).resolve()
            if not workspace_path.exists():
                raise ClaudeCliError(
                    f"Workspace path does not exist: {workspace_path}",
                    details={"workspace_path": str(workspace_path)},
                )

            cmd = [self.config.cli.executable]

            # Add workspace path
            cmd.extend(["--workspace", str(workspace_path)])

            # Add system prompt if provided
            if system_prompt:
                cmd.extend(["--system-prompt", system_prompt])

            # Add allowed tools if provided
            if allowed_tools:
                for tool in allowed_tools:
                    cmd.extend(["--allow-tool", tool])

            # Prepare environment variables
            process_env = os.environ.copy()
            if env_vars:
                process_env.update(env_vars)
            if self.config.cli.env_vars:
                process_env.update(self.config.cli.env_vars)

            logger.debug(f"Starting Claude CLI process: {shlex.join(cmd)}")

            try:
                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=process_env,
                    cwd=str(workspace_path),
                )
                logger.info(
                    f"Started Claude CLI process with PID {self.process.pid}"
                )
                return self.process
            except (OSError, FileNotFoundError) as e:
                raise ClaudeCliError(
                    f"Failed to start Claude CLI process: {e}",
                    details={"command": shlex.join(cmd)},
                ) from e

    async def stop(self, timeout: float = 5.0, force: bool = False) -> None:
        """
        Stop the Claude Code CLI subprocess.

        Args:
            timeout: Timeout in seconds for the subprocess to terminate.
            force: Whether to force kill the subprocess if it doesn't terminate within the timeout.

        Raises:
            ClaudeCliError: If the subprocess fails to stop.
        """
        async with self._process_lock:
            if self.process is None:
                logger.debug("No Claude CLI process to stop")
                return

            if self.process.returncode is not None:
                logger.debug(
                    f"Claude CLI process already terminated with exit code {self.process.returncode}"
                )
                return

            logger.debug(f"Stopping Claude CLI process with PID {self.process.pid}")

            try:
                await terminate_process(self.process, timeout, force)
                logger.info(
                    f"Stopped Claude CLI process with exit code {self.process.returncode}"
                )
            except Exception as e:
                raise ClaudeCliError(
                    f"Failed to stop Claude CLI process: {e}",
                    details={"pid": self.process.pid},
                ) from e

    async def send_message(self, message: str) -> None:
        """
        Send a message to the Claude Code CLI subprocess.

        Args:
            message: The message to send.

        Raises:
            ClaudeCliError: If the message cannot be sent.
        """
        if self.process is None or self.process.returncode is not None:
            raise ClaudeCliError(
                "Cannot send message: Claude CLI process is not running"
            )

        if self.process.stdin is None:
            raise ClaudeCliError(
                "Cannot send message: Claude CLI process stdin is not available"
            )

        try:
            message_bytes = (message + "\n").encode("utf-8")
            self.process.stdin.write(message_bytes)
            await self.process.stdin.drain()
            logger.debug(f"Sent message to Claude CLI process: {message[:50]}...")
        except (OSError, BrokenPipeError) as e:
            raise ClaudeCliError(f"Failed to send message to Claude CLI process: {e}") from e

    async def get_process_output(self) -> Tuple[str, str]:
        """
        Get the stdout and stderr output from the Claude Code CLI subprocess.

        Returns:
            A tuple of (stdout, stderr) as strings.

        Raises:
            ClaudeCliError: If the output cannot be retrieved.
        """
        if self.process is None:
            raise ClaudeCliError(
                "Cannot get output: Claude CLI process is not running"
            )

        if self.process.stdout is None or self.process.stderr is None:
            raise ClaudeCliError(
                "Cannot get output: Claude CLI process stdout/stderr is not available"
            )

        try:
            stdout_data, stderr_data = await asyncio.gather(
                self.process.stdout.read(), self.process.stderr.read()
            )
            return stdout_data.decode("utf-8"), stderr_data.decode("utf-8")
        except OSError as e:
            raise ClaudeCliError(f"Failed to get output from Claude CLI process: {e}") from e

    async def is_running(self) -> bool:
        """
        Check if the Claude Code CLI subprocess is running.

        Returns:
            True if the subprocess is running, False otherwise.
        """
        return self.process is not None and self.process.returncode is None

    async def get_exit_code(self) -> Optional[int]:
        """
        Get the exit code of the Claude Code CLI subprocess.

        Returns:
            The exit code if the subprocess has terminated, None otherwise.
        """
        if self.process is None:
            return None
        return self.process.returncode

