"""
NDJSON stream processing for Claude Code CLI.

This module provides NDJSON stream processing for the Claude Code CLI,
including parsing and converting JSON objects to message models.
"""

import asyncio
import json
import logging
from asyncio.subprocess import Process
from typing import Any, AsyncIterator, Dict, Optional, Type, TypeVar, Union, cast

from pydantic import ValidationError

from ..models.messages import AnyClaudeMessage, ClaudeMessage, MessageType
from ..utils.async_utils import read_stream_lines
from ..utils.errors import StreamProcessingError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=ClaudeMessage)


class StreamProcessor:
    """
    Processor for NDJSON streams from Claude Code CLI.

    This class handles parsing NDJSON output from the Claude Code CLI
    and converting it to message models.
    """

    def __init__(self, process: Process, buffer_size: int = 64 * 1024):
        """
        Initialize the stream processor.

        Args:
            process: The subprocess to read from.
            buffer_size: The size of the circular buffer for stream processing.
        """
        self.process = process
        self.buffer_size = buffer_size
        self._buffer: list[str] = []
        self._buffer_index = 0
        self._message_count = 0

    def _add_to_buffer(self, line: str) -> None:
        """
        Add a line to the circular buffer.

        Args:
            line: The line to add.
        """
        if len(self._buffer) < self.buffer_size:
            self._buffer.append(line)
        else:
            self._buffer[self._buffer_index] = line
            self._buffer_index = (self._buffer_index + 1) % self.buffer_size

    async def process_stream(self) -> AsyncIterator[AnyClaudeMessage]:
        """
        Process the NDJSON stream from the subprocess.

        Yields:
            Message models parsed from the stream.

        Raises:
            StreamProcessingError: If the stream cannot be processed.
        """
        if self.process.stdout is None:
            raise StreamProcessingError(
                "Cannot process stream: subprocess stdout is not available"
            )

        async for line in read_stream_lines(self.process.stdout):
            if not line.strip():
                continue

            self._add_to_buffer(line)

            try:
                data = json.loads(line)
                message = self._parse_message(data)
                self._message_count += 1
                yield message
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {line}")
                raise StreamProcessingError(
                    f"Failed to parse JSON: {e}", line=line
                ) from e
            except ValidationError as e:
                logger.warning(f"Failed to validate message: {line}")
                raise StreamProcessingError(
                    f"Failed to validate message: {e}", line=line
                ) from e
            except Exception as e:
                logger.error(f"Unexpected error processing stream: {e}")
                raise StreamProcessingError(
                    f"Unexpected error processing stream: {e}", line=line
                ) from e

    def _parse_message(self, data: Dict[str, Any]) -> AnyClaudeMessage:
        """
        Parse a message from JSON data.

        Args:
            data: The JSON data to parse.

        Returns:
            The parsed message model.

        Raises:
            StreamProcessingError: If the message cannot be parsed.
        """
        try:
            return ClaudeMessage.from_dict(data)
        except ValidationError as e:
            logger.warning(f"Failed to validate message: {data}")
            raise StreamProcessingError(
                f"Failed to validate message: {e}", line=json.dumps(data)
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error parsing message: {e}")
            raise StreamProcessingError(
                f"Unexpected error parsing message: {e}", line=json.dumps(data)
            ) from e

    def get_buffer_contents(self) -> list[str]:
        """
        Get the contents of the buffer.

        Returns:
            The contents of the buffer.
        """
        if not self._buffer:
            return []

        if len(self._buffer) < self.buffer_size:
            return self._buffer.copy()

        # Reorder the buffer to get the oldest entries first
        return (
            self._buffer[self._buffer_index :] + self._buffer[: self._buffer_index]
        )

    def get_message_count(self) -> int:
        """
        Get the number of messages processed.

        Returns:
            The number of messages processed.
        """
        return self._message_count

    async def process_stream_with_type(
        self, message_type: Type[T]
    ) -> AsyncIterator[T]:
        """
        Process the NDJSON stream and filter by message type.

        Args:
            message_type: The message type to filter by.

        Yields:
            Message models of the specified type.
        """
        async for message in self.process_stream():
            if isinstance(message, message_type):
                yield cast(T, message)

