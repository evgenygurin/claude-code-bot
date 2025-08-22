# Claude Code CLI Python Wrapper

A Python wrapper for Claude Code CLI with support for async execution, NDJSON stream processing, and MCP server integration.

## Features

- **Async Subprocess Execution**: Run Claude Code CLI asynchronously
- **NDJSON Stream Processing**: Parse and process NDJSON output in real-time
- **Session Management**: Persist sessions between invocations
- **MCP Server Integration**: Configure and manage MCP servers
- **Tool Permission Management**: Control tool access and permissions

## Installation

```bash
# Clone the repository
git clone https://github.com/evgenygurin/claude-code-bot.git
cd claude-code-bot

# Install the package
pip install -e .
```

## Requirements

- Python 3.12+
- Claude Code CLI installed and configured
- Optional: Linear API key for Linear MCP integration
- Optional: GitHub token for GitHub MCP integration

## Usage

### Basic Usage

```python
import asyncio
from pathlib import Path
from claude_code_bot import ClaudeRunner, MessageType

async def main():
    # Create a Claude runner
    runner = ClaudeRunner()
    await runner.initialize()

    try:
        # Start a session
        session = await runner.start_session(
            workspace_path=Path("./workspace"),
            system_prompt="You are a helpful AI assistant.",
            allowed_tools=["run_command", "file_write"],
        )

        # Send a message
        async for message in runner.send_message(session.id, "Hello, Claude!"):
            if message.type == MessageType.ASSISTANT:
                print(f"Claude: {message.content}")

        # Stop the session
        await runner.stop_session(session.id)

    finally:
        # Shut down the runner
        await runner.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Session Management

```python
# Start a session
session = await runner.start_session(
    workspace_path=Path("./workspace"),
    system_prompt="You are a helpful AI assistant.",
    allowed_tools=["run_command", "file_write"],
)

# Pause a session (stops the process but keeps the session state)
await runner.pause_session(session.id)

# Continue a session
async for message in runner.continue_session(session.id):
    print(message.content)

# List all sessions
sessions = await runner.list_sessions()
for session in sessions:
    print(f"Session {session.id}: {session.state}")

# Delete a session
await runner.delete_session(session.id)
```

### Tool Usage

```python
# Send a message that might trigger tool use
async for message in runner.send_message(session.id, "Can you create a Python script that prints 'Hello, world!'?"):
    if message.type == MessageType.TOOL_USE:
        print(f"Claude is using tool: {message.tool_name}")
        print(f"Tool input: {message.tool_input}")
    elif message.type == MessageType.TOOL_RESULT:
        print(f"Tool result: {message.result}")
        print(f"Is error: {message.is_error}")
```

## Configuration

The wrapper can be configured using environment variables or a configuration file:

### Environment Variables

- `CLAUDE_CODE_EXECUTABLE`: Path to the Claude Code CLI executable (default: `claude-code`)
- `CLAUDE_CODE_TIMEOUT`: Default timeout for CLI operations in seconds (default: `60`)
- `CLAUDE_CODE_MAX_RETRIES`: Maximum number of retries for CLI operations (default: `3`)
- `CLAUDE_CODE_RETRY_DELAY`: Delay between retries in seconds (default: `1`)
- `CLAUDE_CODE_MAX_SESSIONS`: Maximum number of concurrent sessions (default: `10`)
- `CLAUDE_CODE_SESSION_TIMEOUT`: Session timeout in seconds (default: `3600`)
- `CLAUDE_CODE_SESSION_DIR`: Directory for storing session data (default: `~/.claude_code_bot/sessions`)
- `CLAUDE_CODE_CLEANUP_INTERVAL`: Interval for cleaning up expired sessions in seconds (default: `300`)
- `CLAUDE_CODE_LOG_LEVEL`: Log level (default: `INFO`)
- `CLAUDE_CODE_LOG_FILE`: Log file path (default: `None`)
- `CLAUDE_CODE_ALLOWED_TOOLS`: Comma-separated list of allowed tools (default: `None`)
- `LINEAR_API_KEY`: Linear API key for Linear MCP integration
- `GITHUB_TOKEN`: GitHub token for GitHub MCP integration

### Custom Configuration

```python
from claude_code_bot import ClaudeRunner, Config, ToolPermission

# Create a custom configuration
config = Config()
config.cli.executable = "/path/to/claude-code"
config.cli.timeout = 120
config.session.max_sessions = 5
config.session.session_timeout = 7200
config.mcp_servers = {
    "custom": {
        "name": "custom",
        "url": "http://localhost:8000",
        "api_key": "your-api-key",
        "enabled": True,
        "tools": {
            "run_command": ToolPermission.EXECUTE,
            "file_write": ToolPermission.WRITE,
            "text_editor": ToolPermission.WRITE,
            "ripgrep_search": ToolPermission.READ,
        },
    }
}

# Create a Claude runner with the custom configuration
runner = ClaudeRunner(config)
```

## Development

### Setup

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run unit tests
pytest tests/unit

# Run integration tests (requires Claude Code CLI)
CLAUDE_CODE_TEST_INTEGRATION=1 pytest tests/integration
```

## License

MIT

