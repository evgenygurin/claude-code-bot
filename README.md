# Linear Claude Agent 🤖

Modern Python Linear Agent with FastAPI and Claude Code integration.

A production-ready Linear Agent using Python 3.12, uv package manager, and FastAPI that integrates seamlessly with Linear issues and Claude Code for automated development workflows.

## 🌟 Features

- **🚀 Modern Python Stack**: Python 3.12, uv package manager, FastAPI
- **🔌 Linear Integration**: Full Linear API integration with Agent Sessions
- **🤖 Claude Code Integration**: Python wrapper for Claude Code CLI
- **🔄 Git Management**: Isolated worktrees for each issue
- **⚡ High Performance**: Async/await throughout, optimized for speed
- **🛡️ Security First**: Encrypted tokens, sandboxed execution
- **📊 Monitoring**: Comprehensive logging and metrics
- **🐳 Container Ready**: Docker and Kubernetes support

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- uv package manager
- Git
- Claude Code CLI
- Docker (optional)

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd claude-code-bot
   ```

2. **Run the setup script**:

   ```bash
   ./scripts/setup-dev.sh
   ```

3. **Configure environment**:

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start the development server**:

   ```bash
   uv run python -m linear_agent.main
   ```

### Using Docker

```bash
# Start all services
docker-compose up --build

# Start with monitoring
docker-compose --profile monitoring up --build
```

## 📋 Configuration

Key environment variables:

```bash
# Linear API
LINEAR_CLIENT_ID=your_linear_client_id
LINEAR_CLIENT_SECRET=your_linear_client_secret
LINEAR_WEBHOOK_SECRET=your_webhook_secret

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# Security
SECRET_KEY=your-secret-key-32-chars-minimum
```

See `env.example` for complete configuration options.

## 🧪 Testing

```bash
# Run all tests
./scripts/run-tests.sh

# Run with coverage
./scripts/run-tests.sh --coverage

# Run only unit tests
./scripts/run-tests.sh --unit

# Run only integration tests
./scripts/run-tests.sh --integration
```

## 🏗️ Architecture

### Core Components

- **FastAPI Backend**: High-performance async API server
- **Linear Integration**: OAuth, webhooks, Agent Sessions
- **Claude Code Integration**: CLI wrapper with NDJSON processing
- **Git Management**: Isolated worktrees for security
- **Session Management**: Persistent tracking and recovery

### Project Structure

```text
src/linear_agent/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── api/                 # API routes
│   ├── webhooks.py      # Linear webhooks
│   ├── agents.py        # Agent management
│   └── health.py        # Health checks
├── services/            # Business logic
│   ├── linear.py        # Linear API client
│   ├── claude.py        # Claude Code integration
│   ├── git.py           # Git worktree management
│   └── sessions.py      # Session management
├── models/              # Database models
└── schemas/             # Pydantic schemas
```

## 🔄 Workflow

1. **Issue Assignment**: Linear webhook triggers when issue assigned to agent
2. **Worktree Creation**: Isolated git worktree created for the issue
3. **Claude Processing**: Claude Code analyzes and processes the issue
4. **Result Posting**: Results posted back to Linear as comments
5. **Cleanup**: Automatic cleanup of resources

## 🛡️ Security

- **Isolated Execution**: Each issue processed in separate git worktree
- **Encrypted Storage**: Tokens encrypted at rest
- **Access Controls**: Configurable tool permissions
- **Audit Logging**: Comprehensive audit trail

## 📊 Monitoring

- **Prometheus Metrics**: Performance and usage metrics
- **Structured Logging**: JSON logging with correlation IDs
- **Health Checks**: Comprehensive health monitoring
- **Error Tracking**: Sentry integration for error tracking

## 🚀 Deployment

### Docker

```bash
# Build production image
docker build --target production -t linear-agent .

# Run with environment
docker run -p 8000:8000 --env-file .env linear-agent
```

### Kubernetes

Helm charts and Kubernetes manifests available in `deployment/` directory.

## 🔧 Development

### Code Quality

```bash
# Linting
uv run ruff check

# Type checking
uv run mypy src/

# Format code
uv run ruff format

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Database Migrations

```bash
# Create migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head
```

## 📚 API Documentation

When running in development mode, API documentation is available at:

- **Swagger UI**: <http://localhost:8000/api/v1/docs>
- **ReDoc**: <http://localhost:8000/api/v1/redoc>

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Linear**: For the excellent Linear API and Agent Sessions
- **Anthropic**: For Claude Code and AI capabilities
- **FastAPI**: For the amazing web framework
- **Python Community**: For the modern tooling ecosystem
