#!/usr/bin/env python3
"""
Basic usage example for Claude Code CLI wrapper.

This example demonstrates how to use the Claude Code CLI wrapper to:
1. Start a session
2. Send a message
3. Process the response
4. Stop the session
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from claude_code_bot import ClaudeRunner, MessageType, ToolUseMessage


async def main():
    """Run the example."""
    # Create a Claude runner
    runner = ClaudeRunner()
    await runner.initialize()

    try:
        # Create a workspace directory
        workspace_path = Path.cwd() / "workspace"
        workspace_path.mkdir(exist_ok=True)

        # Create a simple Python file in the workspace
        with open(workspace_path / "hello.py", "w") as f:
            f.write('print("Hello, world!")\n')

        print(f"Created workspace at {workspace_path}")

        # Start a session
        print("Starting session...")
        session = await runner.start_session(
            workspace_path=workspace_path,
            system_prompt="You are a helpful AI assistant.",
            allowed_tools=["run_command"],
        )
        print(f"Started session {session.id}")

        # Send a message
        print("\nSending message...")
        message = "Can you run the hello.py script in the workspace?"
        print(f"User: {message}")

        async for response in runner.send_message(session.id, message):
            if response.type == MessageType.ASSISTANT:
                print(f"Claude: {response.content}")
            elif isinstance(response, ToolUseMessage):
                print(f"Claude is using tool: {response.tool_name}")
                print(f"Tool input: {response.tool_input}")

        # Stop the session
        print("\nStopping session...")
        await runner.stop_session(session.id)
        print(f"Stopped session {session.id}")

    finally:
        # Shut down the runner
        await runner.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

