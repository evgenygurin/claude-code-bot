"""
Async utilities for Claude Code CLI.

This module provides async utility functions for working with subprocesses,
streams, and other async operations.
"""

import asyncio
import json
import logging
from asyncio import Task
from asyncio.subprocess import Process
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, TypeVar

from ..utils.errors import StreamProcessingError, TimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def read_stream_lines(stream: asyncio.StreamReader) -> AsyncIterator[str]:
    """
    Read lines from a stream asynchronously.

    Args:
        stream: The stream to read from.

    Yields:
        Each line from the stream.
    """
    while not stream.at_eof():
        line = await stream.readline()
        if not line:
            break
        yield line.decode("utf-8").rstrip()


async def read_json_stream(stream: asyncio.StreamReader) -> AsyncIterator[Dict[str, Any]]:
    """
    Read JSON objects from a stream asynchronously.

    Args:
        stream: The stream to read from.

    Yields:
        Each JSON object from the stream.

    Raises:
        StreamProcessingError: If a line cannot be parsed as JSON.
    """
    async for line in read_stream_lines(stream):
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {line}")
            raise StreamProcessingError(
                f"Failed to parse JSON: {e}", line=line
            ) from e


async def wait_for_with_timeout(
    coro: Callable[..., T], timeout: float, *args: Any, **kwargs: Any
) -> T:
    """
    Wait for a coroutine to complete with a timeout.

    Args:
        coro: The coroutine to wait for.
        timeout: The timeout in seconds.
        *args: Arguments to pass to the coroutine.
        **kwargs: Keyword arguments to pass to the coroutine.

    Returns:
        The result of the coroutine.

    Raises:
        TimeoutError: If the coroutine does not complete within the timeout.
    """
    try:
        return await asyncio.wait_for(coro(*args, **kwargs), timeout)
    except asyncio.TimeoutError as e:
        raise TimeoutError(
            f"Operation timed out after {timeout} seconds",
            timeout_seconds=timeout,
        ) from e


async def cancel_tasks(tasks: List[Task]) -> None:
    """
    Cancel a list of tasks and wait for them to complete.

    Args:
        tasks: The tasks to cancel.
    """
    for task in tasks:
        if not task.done():
            task.cancel()

    # Wait for all tasks to be cancelled
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def terminate_process(
    process: Process, timeout: float = 5.0, force: bool = False
) -> None:
    """
    Terminate a subprocess with a timeout.

    Args:
        process: The process to terminate.
        timeout: The timeout in seconds.
        force: Whether to force kill the process if it doesn't terminate within the timeout.
    """
    if process.returncode is not None:
        return

    if force:
        process.kill()
    else:
        process.terminate()

    try:
        await asyncio.wait_for(process.wait(), timeout)
    except asyncio.TimeoutError:
        logger.warning(
            f"Process did not terminate within {timeout} seconds, killing it"
        )
        process.kill()
        await process.wait()

