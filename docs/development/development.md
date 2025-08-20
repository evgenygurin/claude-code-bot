# 💻 Development Guide

## Обзор

Этот документ содержит подробную информацию для разработчиков Claude Code Bot, включая настройку среды разработки, архитектурные решения, инструменты и best practices.

## Быстрый старт

### ⚡ Quick Setup

```bash
# 1. Клонирование репозитория
git clone https://github.com/your-org/claude-code-bot.git
cd claude-code-bot

# 2. Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Установка зависимостей
uv pip install -e ".[dev,test]"

# 4. Копирование конфигурации
cp .env.example .env

# 5. Настройка базы данных
make db-setup

# 6. Установка pre-commit hooks
pre-commit install

# 7. Проверка настройки
make check
```

### 📋 Системные требования

**Основные:**
- **Python 3.12+** (рекомендуется 3.12)
- **PostgreSQL 15+** для основной БД
- **Redis 7+** для кеширования и очередей
- **Docker & Docker Compose** для контейнеризации
- **Git 2.30+** для version control

**Рекомендуемые инструменты:**
- **uv** (быстрый package manager)
- **make** (automation commands)
- **pre-commit** (git hooks)
- **act** (local GitHub Actions testing)

### 🔧 Установка инструментов

**macOS (Homebrew):**
```bash
# Основные инструменты
brew install python@3.12 postgresql@15 redis
brew install --cask docker

# Дополнительные инструменты
pip install uv pre-commit
brew install act
```

**Ubuntu/Debian:**
```bash
# Python и зависимости
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
sudo apt install postgresql-15 redis-server
sudo apt install docker.io docker-compose

# uv и дополнительные инструменты
pip install uv pre-commit
```

**Windows:**
```powershell
# Через Chocolatey
choco install python312 postgresql redis docker-desktop

# Через pip
pip install uv pre-commit
```

## Архитектура разработки

### 🏗️ Структура проекта

```text
claude-code-bot/
├── .github/                    # GitHub workflows и templates
│   ├── workflows/             # GitHub Actions
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── .vscode/                   # VS Code настройки
├── alembic/                   # Database migrations
├── app/                       # Main application code
│   ├── api/                   # FastAPI routes
│   ├── core/                  # Core business logic
│   ├── integrations/          # Integration implementations
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business services
│   ├── utils/                 # Utility functions
│   └── workers/               # Background workers
├── docs/                      # Documentation
├── scripts/                   # Development и deployment scripts
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docker/                    # Docker configurations
├── k8s/                       # Kubernetes manifests
├── .env.example              # Environment variables template
├── docker-compose.yml        # Local development setup
├── Makefile                  # Development commands
├── pyproject.toml            # Python project configuration
└── README.md
```

### 🔄 Development Workflow

**Daily Workflow:**
```bash
# 1. Обновление кода
git pull origin develop

# 2. Проверка статуса
make status

# 3. Запуск в dev режиме
make dev

# 4. Разработка новой функции
git checkout -b feature/your-feature

# 5. Тестирование изменений
make test
make lint

# 6. Commit и push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature

# 7. Создание Pull Request через GitHub CLI
gh pr create --title "Your Feature" --body "Description"
```

### 🐍 Python Environment Setup

**pyproject.toml конфигурация:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "claude-code-bot"
version = "0.1.0"
description = "AI-powered integration creation platform"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "pydantic>=2.5.0",
    "redis>=5.0.0",
    "anthropic>=0.8.0",
    "httpx>=0.25.0",
    "structlog>=23.2.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.1.6",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.25.0",
    "faker>=20.1.0",
]
test = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "factory-boy>=3.3.0",
    "testcontainers>=3.7.0",
]

[tool.ruff]
line-length = 88
target-version = "py312"
src = ["app", "tests"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "UP",  # pyupgrade
    "RUF", # ruff-specific rules
]
ignore = [
    "E501", # line too long (handled by formatter)
    "B008", # do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*" = ["S101", "ARG", "FBT"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
]
asyncio_mode = "auto"
```

## Database Development

### 🗄️ PostgreSQL Setup

**Local Development Database:**
```bash
# Создание пользователя и базы данных
createuser -s claude_code_bot
createdb -O claude_code_bot claude_code_bot_dev

# Настройка тестовой БД
createdb -O claude_code_bot claude_code_bot_test

# Применение миграций
alembic upgrade head
```

**Database Configuration:**
```python
# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 🔄 Database Migrations

**Создание миграции:**
```bash
# Автоматическая генерация миграции
alembic revision --autogenerate -m "Add integration table"

# Ручная миграция
alembic revision -m "Custom migration"

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1

# Просмотр текущей версии
alembic current

# История миграций
alembic history
```

**Пример миграции:**
```python
"""Add integration table

Revision ID: 001_add_integration_table
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_add_integration_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    
    op.create_index('idx_integrations_name', 'integrations', ['name'])
    op.create_index('idx_integrations_type', 'integrations', ['type'])
    op.create_index('idx_integrations_status', 'integrations', ['status'])

def downgrade() -> None:
    op.drop_table('integrations')
```

### 📊 Database Models

**Base Model Pattern:**
```python
# app/models/base.py
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class UUIDMixin:
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
```

**Integration Model:**
```python
# app/models/integration.py
from enum import Enum
from typing import Dict, Any, Optional
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDMixin

class IntegrationStatus(str, Enum):
    REQUESTED = "requested"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    TESTING = "testing"
    REVIEWING = "reviewing"
    ACTIVE = "active"
    FAILED = "failed"
    DEPRECATED = "deprecated"

class Integration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integrations"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[IntegrationStatus] = mapped_column(
        SQLEnum(IntegrationStatus),
        nullable=False,
        default=IntegrationStatus.REQUESTED
    )
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    events: Mapped[list["IntegrationEvent"]] = relationship(
        back_populates="integration",
        cascade="all, delete-orphan"
    )
```

## Testing Strategy

### 🧪 Test Structure

**Test Categories:**
- **Unit Tests** — тестирование отдельных функций и классов
- **Integration Tests** — тестирование взаимодействия компонентов
- **End-to-End Tests** — тестирование полных пользовательских сценариев
- **Contract Tests** — тестирование API контрактов
- **Load Tests** — тестирование производительности

### 🔬 Unit Testing

**Test Configuration:**
```python
# tests/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from app.database import Base
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def postgres_container():
    """Start PostgreSQL container for tests."""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture(scope="session")
async def test_engine(postgres_container):
    """Create test database engine."""
    database_url = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(database_url)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
```

**Service Testing Example:**
```python
# tests/unit/test_integration_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from app.services.integration_service import IntegrationService
from app.schemas.integration import IntegrationCreateSchema
from app.models.integration import Integration, IntegrationStatus

class TestIntegrationService:
    @pytest.fixture
    def mock_db_session(self):
        return AsyncMock()
    
    @pytest.fixture
    def integration_service(self, mock_db_session):
        return IntegrationService(db=mock_db_session)
    
    async def test_create_integration_success(self, integration_service, mock_db_session):
        # Arrange
        create_data = IntegrationCreateSchema(
            name="test-integration",
            type="webhook",
            config={"url": "https://example.com"}
        )
        
        mock_db_session.add = Mock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Act
        result = await integration_service.create(create_data)
        
        # Assert
        assert isinstance(result, Integration)
        assert result.name == "test-integration"
        assert result.type == "webhook"
        assert result.status == IntegrationStatus.REQUESTED
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    async def test_create_integration_duplicate_name(
        self, integration_service, mock_db_session
    ):
        # Arrange
        create_data = IntegrationCreateSchema(
            name="existing-integration",
            type="webhook",
            config={"url": "https://example.com"}
        )
        
        # Mock existing integration
        existing_integration = Mock()
        mock_db_session.scalar = AsyncMock(return_value=existing_integration)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Integration with name .* already exists"):
            await integration_service.create(create_data)

    @pytest.mark.parametrize("integration_type,expected_validator", [
        ("webhook", "WebhookIntegration"),
        ("github", "GitHubIntegration"),
        ("slack", "SlackIntegration"),
    ])
    async def test_get_integration_validator(
        self, integration_service, integration_type, expected_validator
    ):
        # Act
        validator = integration_service.get_validator(integration_type)
        
        # Assert
        assert validator.__class__.__name__ == expected_validator
```

### 🔗 Integration Testing

**API Testing:**
```python
# tests/integration/test_integration_api.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestIntegrationAPI:
    @pytest.fixture
    async def client(self) -> AsyncClient:
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client
    
    async def test_create_integration_endpoint(self, client):
        # Arrange
        payload = {
            "name": "test-integration",
            "type": "webhook",
            "config": {"url": "https://example.com"}
        }
        
        # Act
        response = await client.post("/api/v1/integrations", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-integration"
        assert data["type"] == "webhook"
        assert data["status"] == "requested"
        assert "id" in data
        assert "created_at" in data

    async def test_list_integrations_pagination(self, client):
        # Arrange - create test integrations
        for i in range(15):
            await client.post("/api/v1/integrations", json={
                "name": f"integration-{i}",
                "type": "webhook",
                "config": {"url": f"https://example-{i}.com"}
            })
        
        # Act
        response = await client.get("/api/v1/integrations?limit=10&offset=0")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["limit"] == 10
        assert data["offset"] == 0

    async def test_get_integration_by_id(self, client):
        # Arrange
        create_response = await client.post("/api/v1/integrations", json={
            "name": "test-integration",
            "type": "webhook",
            "config": {"url": "https://example.com"}
        })
        integration_id = create_response.json()["id"]
        
        # Act
        response = await client.get(f"/api/v1/integrations/{integration_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == integration_id
        assert data["name"] == "test-integration"

    async def test_update_integration_status(self, client):
        # Arrange
        create_response = await client.post("/api/v1/integrations", json={
            "name": "test-integration",
            "type": "webhook",
            "config": {"url": "https://example.com"}
        })
        integration_id = create_response.json()["id"]
        
        # Act
        response = await client.patch(
            f"/api/v1/integrations/{integration_id}/status",
            json={"status": "active"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
```

### 🎭 End-to-End Testing

**E2E Test Example:**
```python
# tests/e2e/test_integration_workflow.py
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from tests.helpers import (
    create_github_issue,
    wait_for_integration_creation,
    wait_for_pr_creation
)

@pytest.mark.e2e
class TestIntegrationWorkflow:
    async def test_full_integration_creation_workflow(self):
        """Test complete workflow from GitHub issue to deployed integration."""
        
        # Arrange
        issue_data = {
            "title": "Add Jira integration for project management",
            "body": """
            ## Integration Request
            
            **Service:** Jira
            **Type:** webhook
            **Description:** Integration for receiving Jira issue updates
            
            ### Configuration
            - API endpoint: https://company.atlassian.net
            - Webhook events: issue_created, issue_updated, issue_resolved
            
            ### Expected Behavior
            - Receive webhook notifications from Jira
            - Parse issue data and store in database  
            - Send notifications to configured channels
            """,
            "labels": ["integration-request"]
        }
        
        with patch('app.services.github_service.GitHubService') as mock_github:
            with patch('app.services.ai_service.AIService') as mock_ai:
                # Mock GitHub service
                mock_github.return_value.create_comment = AsyncMock()
                mock_github.return_value.create_pr = AsyncMock(
                    return_value={"number": 123, "html_url": "https://github.com/repo/pull/123"}
                )
                
                # Mock AI service
                mock_ai.return_value.generate_integration = AsyncMock(
                    return_value={
                        "code": "integration_code_here",
                        "tests": "test_code_here",
                        "docs": "documentation_here"
                    }
                )
                
                # Act
                issue = await create_github_issue(issue_data)
                
                # Wait for automatic processing
                integration = await wait_for_integration_creation(
                    issue_id=issue["id"],
                    timeout=60
                )
                
                # Assert integration creation
                assert integration is not None
                assert integration["name"] == "jira-integration"
                assert integration["type"] == "webhook"
                assert integration["status"] == "generating"
                
                # Wait for PR creation
                pr = await wait_for_pr_creation(
                    integration_id=integration["id"],
                    timeout=120
                )
                
                # Assert PR creation
                assert pr is not None
                assert "jira" in pr["title"].lower()
                assert pr["files_changed"] > 0
                
                # Verify AI service was called
                mock_ai.return_value.generate_integration.assert_called_once()
                
                # Verify GitHub service was called
                mock_github.return_value.create_pr.assert_called_once()

    async def test_error_handling_workflow(self):
        """Test error handling in integration creation workflow."""
        
        # Arrange - invalid issue format
        issue_data = {
            "title": "Invalid request",
            "body": "No proper template used",
            "labels": ["integration-request"]
        }
        
        with patch('app.services.github_service.GitHubService') as mock_github:
            mock_github.return_value.create_comment = AsyncMock()
            
            # Act
            issue = await create_github_issue(issue_data)
            
            # Wait for error handling
            await asyncio.sleep(5)  # Allow processing time
            
            # Assert error comment was added
            mock_github.return_value.create_comment.assert_called()
            call_args = mock_github.return_value.create_comment.call_args[1]
            assert "invalid format" in call_args["body"].lower()
```

### 📊 Test Coverage

**Coverage Configuration:**
```ini
# .coveragerc
[run]
source = app
omit = 
    app/main.py
    app/config.py
    */tests/*
    */venv/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

**Coverage Commands:**
```bash
# Запуск тестов с покрытием
pytest --cov=app --cov-report=html --cov-report=term

# Только покрытие без тестов
coverage run -m pytest
coverage report
coverage html

# Проверка минимального покрытия
coverage report --fail-under=80
```

## Development Tools

### 🛠️ Makefile Commands

```makefile
# Makefile
.PHONY: help setup dev test lint format clean

# Python and dependencies
PYTHON := python3.12
UV := uv
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(UV) pip install -e ".[dev,test]"
	$(ACTIVATE) && pre-commit install
	cp .env.example .env
	@echo "✅ Development environment setup complete!"

dev: ## Start development server
	$(ACTIVATE) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests
	$(ACTIVATE) && pytest -v

test-unit: ## Run unit tests only
	$(ACTIVATE) && pytest tests/unit/ -v

test-integration: ## Run integration tests only
	$(ACTIVATE) && pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	$(ACTIVATE) && pytest tests/e2e/ -v -s

test-cov: ## Run tests with coverage
	$(ACTIVATE) && pytest --cov=app --cov-report=html --cov-report=term

lint: ## Run all linting tools
	$(ACTIVATE) && ruff check . --fix
	$(ACTIVATE) && ruff format .
	$(ACTIVATE) && mypy app/
	$(ACTIVATE) && bandit -r app/

format: ## Format code
	$(ACTIVATE) && ruff format .
	$(ACTIVATE) && ruff check . --fix

check: ## Run all checks (lint + test)
	make lint
	make test

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ dist/ build/

# Database commands
db-upgrade: ## Apply database migrations
	$(ACTIVATE) && alembic upgrade head

db-downgrade: ## Rollback last migration
	$(ACTIVATE) && alembic downgrade -1

db-revision: ## Create new migration
	$(ACTIVATE) && alembic revision --autogenerate -m "$(MESSAGE)"

db-reset: ## Reset database (WARNING: destructive)
	$(ACTIVATE) && alembic downgrade base
	$(ACTIVATE) && alembic upgrade head

# Docker commands
docker-build: ## Build Docker image
	docker build -t claude-code-bot:latest .

docker-up: ## Start services with docker-compose
	docker-compose up -d

docker-down: ## Stop docker-compose services
	docker-compose down

docker-logs: ## Show docker-compose logs
	docker-compose logs -f

docker-test: ## Run tests in Docker
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Deployment commands
deploy-staging: ## Deploy to staging
	./scripts/deploy.sh staging

deploy-prod: ## Deploy to production
	./scripts/deploy.sh production

# Documentation
docs: ## Build documentation
	$(ACTIVATE) && mkdocs serve

docs-build: ## Build documentation for deployment
	$(ACTIVATE) && mkdocs build
```

### 🔧 Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, app/]
        exclude: tests/

  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest unit tests
        entry: pytest tests/unit/
        language: system
        pass_filenames: false
        always_run: true
```

### 📝 VS Code Configuration

**.vscode/settings.json:**
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "none",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "files.associations": {
        "*.yml": "yaml",
        "*.yaml": "yaml"
    }
}
```

**.vscode/launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI Development Server",
            "type": "python",
            "request": "launch",
            "program": "-m",
            "args": ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Run Tests",
            "type": "python", 
            "request": "launch",
            "program": "-m",
            "args": ["pytest", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### 🐳 Docker Development

**Dockerfile for Development:**
```dockerfile
# docker/Dockerfile.dev
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Install application in development mode
RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml for Development:**
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://claude_bot:password@postgres:5432/claude_bot_dev
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
      - /app/.venv
    depends_on:
      - postgres
      - redis
    networks:
      - claude-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=claude_bot_dev
      - POSTGRES_USER=claude_bot
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - claude-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - claude-network

  test-postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=claude_bot_test
      - POSTGRES_USER=claude_bot
      - POSTGRES_PASSWORD=password
    tmpfs:
      - /var/lib/postgresql/data
    networks:
      - claude-network

volumes:
  postgres_data:

networks:
  claude-network:
    driver: bridge
```

## Performance Monitoring

### 📊 Application Monitoring

**Structured Logging:**
```python
# app/utils/logging.py
import structlog
import sys
from typing import Any, Dict

def configure_logging(debug: bool = False) -> None:
    """Configure structured logging."""
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer() if not debug else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(30 if not debug else 10),
        logger_factory=structlog.WriteLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )

# Usage in application
logger = structlog.get_logger(__name__)

async def create_integration(data: IntegrationCreateSchema) -> Integration:
    logger.info(
        "Creating integration",
        integration_name=data.name,
        integration_type=data.type,
        user_id="user-123"  # from context
    )
    
    try:
        integration = await service.create(data)
        logger.info(
            "Integration created successfully",
            integration_id=str(integration.id),
            integration_name=integration.name
        )
        return integration
    except Exception as e:
        logger.error(
            "Failed to create integration",
            integration_name=data.name,
            error=str(e),
            exc_info=True
        )
        raise
```

**Metrics Collection:**
```python
# app/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_INTEGRATIONS = Gauge(
    'active_integrations_total',
    'Number of active integrations',
    ['type']
)

INTEGRATION_CREATION_DURATION = Histogram(
    'integration_creation_duration_seconds',
    'Time to create integration',
    ['type', 'status']
)

def track_request_metrics(func):
    """Decorator to track request metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(
                method="POST", 
                endpoint="/integrations", 
                status="success"
            ).inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(
                method="POST", 
                endpoint="/integrations", 
                status="error"
            ).inc()
            raise
        finally:
            REQUEST_DURATION.labels(
                method="POST", 
                endpoint="/integrations"
            ).observe(time.time() - start_time)
    
    return wrapper

# Start metrics server
def start_metrics_server(port: int = 9090):
    start_http_server(port)
```

### 🚨 Health Checks

```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.core.redis import get_redis
from app.services.claude_service import get_claude_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
    claude_service = Depends(get_claude_service)
):
    """Detailed health check with dependencies."""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database health
    try:
        result = await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": 0  # measure actual time
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Redis health  
    try:
        await redis.ping()
        health_status["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Claude API health
    try:
        await claude_service.health_check()
        health_status["checks"]["claude_api"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["claude_api"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    if health_status["status"] == "degraded":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
```

## Security Guidelines

### 🔐 Environment Configuration

**.env.example:**
```bash
# Application
APP_NAME="Claude Code Bot"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT="development"

# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/claude_bot"
DATABASE_TEST_URL="postgresql+asyncpg://user:password@localhost:5432/claude_bot_test"

# Redis
REDIS_URL="redis://localhost:6379/0"

# External APIs
CLAUDE_API_KEY="your-claude-api-key"
CLAUDE_API_BASE_URL="https://api.anthropic.com"

# GitHub
GITHUB_TOKEN="your-github-token"
GITHUB_WEBHOOK_SECRET="your-webhook-secret"
GITHUB_APP_ID="your-app-id"
GITHUB_APP_PRIVATE_KEY_PATH="/path/to/private-key.pem"

# Security
JWT_SECRET_KEY="your-jwt-secret-key"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"  # or "console"

# Monitoring
METRICS_PORT=9090
HEALTH_CHECK_TIMEOUT=5

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST=20
```

### 🛡️ Security Middleware

```python
# app/api/middleware.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import time
import hashlib
import hmac
from collections import defaultdict, deque

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        minute_ago = current_time - 60
        while (self.requests[client_ip] and 
               self.requests[client_ip][0] < minute_ago):
            self.requests[client_ip].popleft()
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response

class WebhookSignatureMiddleware(BaseHTTPMiddleware):
    """Validate webhook signatures."""
    
    def __init__(self, app, webhook_paths: list[str], secret: str):
        super().__init__(app)
        self.webhook_paths = webhook_paths
        self.secret = secret.encode()

    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(path) for path in self.webhook_paths):
            signature = request.headers.get("X-Hub-Signature-256")
            if not signature:
                raise HTTPException(status_code=401, detail="Missing signature")
            
            body = await request.body()
            expected_signature = hmac.new(
                self.secret, body, hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(f"sha256={expected_signature}", signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        response = await call_next(request)
        return response

# JWT Authentication
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Troubleshooting

### 🐛 Common Issues

**1. Import Errors**
```bash
# Problem: ModuleNotFoundError
# Solution: Install in editable mode
pip install -e .

# Or check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

**2. Database Connection Issues**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U claude_bot -d claude_bot_dev

# Reset database
make db-reset
```

**3. Redis Connection Issues**
```bash
# Check Redis is running
redis-cli ping

# Check configuration
redis-cli config get "*"
```

**4. Test Failures**
```bash
# Run with verbose output
pytest -v -s

# Run specific test
pytest tests/unit/test_integration_service.py::TestIntegrationService::test_create_integration_success -v

# Check coverage
pytest --cov=app --cov-report=term-missing
```

### 🔍 Debugging Tools

**Python Debugger:**
```python
import pdb; pdb.set_trace()  # Simple debugger

# Or use ipdb for better interface
import ipdb; ipdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

**Async Debugging:**
```python
import asyncio
import aiotools

# Debug async functions
async def debug_async():
    await aiotools.aio_sleep(1)
    print("Debug point reached")

# Run with asyncio debug mode
asyncio.run(main(), debug=True)
```

**SQL Query Debugging:**
```python
# Enable SQL logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or in configuration
DATABASE_URL += "?echo=true"
```

### 📱 Development Workflow Issues

**Git Issues:**
```bash
# Reset local changes
git checkout .
git clean -fd

# Rebase conflicts
git rebase --abort
git rebase --continue

# Fix commit messages
git commit --amend
git rebase -i HEAD~3
```

**Virtual Environment Issues:**
```bash
# Recreate venv
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Заключение

Этот development guide предоставляет все необходимые инструменты и знания для эффективной разработки Claude Code Bot. Регулярно обновляйте этот документ по мере развития проекта и добавления новых инструментов.

Ключевые принципы:
- **Test-Driven Development** для качества кода
- **Continuous Integration** для автоматизации
- **Security-First Approach** для безопасности
- **Performance Monitoring** для надежности
- **Documentation** для поддерживаемости

Happy coding! 🚀
