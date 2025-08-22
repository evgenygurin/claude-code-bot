"""Pytest configuration and fixtures."""

import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from linear_agent.main import create_app
from linear_agent.config import Settings


# Test settings
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        environment="test",
        database_url=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/15",  # Test Redis DB
        secret_key="test-secret-key-for-testing-only",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def app(test_settings: Settings):
    """Create test FastAPI application."""
    # Monkey patch settings for testing
    import linear_agent.config
    original_settings = linear_agent.config.settings
    linear_agent.config.settings = test_settings
    
    app = create_app()
    
    yield app
    
    # Restore original settings
    linear_agent.config.settings = original_settings


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# Database fixtures
@pytest_asyncio.fixture
async def async_engine(test_settings: Settings):
    """Create async database engine for testing."""
    engine = create_async_engine(
        str(test_settings.database_url),
        echo=test_settings.database_echo,
    )
    
    # Create tables
    # TODO: Import and create database models
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for testing."""
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


# Mock fixtures
@pytest.fixture
def mock_linear_webhook():
    """Mock Linear webhook payload."""
    return {
        "action": "create",
        "type": "Issue",
        "data": {
            "id": "test-issue-id",
            "identifier": "CCB-123",
            "title": "Test issue for agent",
            "description": "This is a test issue",
            "assignee": {
                "id": "agent-user-id",
                "name": "Test Agent"
            },
            "team": {
                "id": "team-id",
                "name": "Test Team"
            },
            "state": {
                "id": "state-id",
                "name": "Todo",
                "type": "unstarted"
            }
        },
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z"
    }


@pytest.fixture
def mock_claude_messages():
    """Mock Claude Code messages."""
    return [
        {
            "type": "user",
            "content": "Please help with this task",
            "timestamp": "2024-01-01T00:00:00.000Z"
        },
        {
            "type": "assistant", 
            "content": "I'll help you with this task. Let me analyze the requirements.",
            "timestamp": "2024-01-01T00:00:01.000Z"
        },
        {
            "type": "tool_use",
            "content": "",
            "tool_name": "Read",
            "tool_input": {"file_path": "README.md"},
            "tool_use_id": "tool-use-1",
            "timestamp": "2024-01-01T00:00:02.000Z"
        },
        {
            "type": "tool_result",
            "content": "File contents...",
            "tool_use_id": "tool-use-1",
            "is_error": False,
            "timestamp": "2024-01-01T00:00:03.000Z"
        }
    ]


# Marks for test categorization
pytest_plugins = []