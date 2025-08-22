#!/bin/bash

# Linear Claude Agent - Development Setup Script
# This script sets up the development environment for the Linear Claude Agent

set -e  # Exit on any error

echo "🚀 Setting up Linear Claude Agent development environment..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.12"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
    echo "❌ Python $required_version or higher is required. Found: Python $python_version"
    echo "Please install Python $required_version+ and try again."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"

# Check if uv is installed
echo "📋 Checking uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    pip install uv
else
    echo "✅ uv is already installed: $(uv --version)"
fi

# Install dependencies
echo "📦 Installing project dependencies..."
uv sync

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
uv run pre-commit install

# Create environment file
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your actual configuration values"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p /tmp/linear-agent/worktrees

# Check Docker
echo "📋 Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is available: $(docker --version)"
    
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose is available: $(docker-compose --version)"
    elif docker compose version &> /dev/null; then
        echo "✅ Docker Compose plugin is available"
    else
        echo "⚠️  Docker Compose not found. Please install Docker Compose for local development."
    fi
else
    echo "⚠️  Docker not found. Please install Docker for containerized development."
fi

# Check Claude Code CLI
echo "📋 Checking Claude Code CLI..."
if command -v claude &> /dev/null; then
    echo "✅ Claude Code CLI is available: $(claude --version 2>&1 || echo 'version unknown')"
else
    echo "⚠️  Claude Code CLI not found. Please install Claude Code CLI:"
    echo "    Visit: https://claude.ai/code"
fi

# Check Git
echo "📋 Checking Git..."
if command -v git &> /dev/null; then
    echo "✅ Git is available: $(git --version)"
else
    echo "❌ Git is required but not found. Please install Git."
    exit 1
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration values"
echo "2. Start the development server:"
echo "   uv run python -m linear_agent.main"
echo ""
echo "🐳 For Docker development:"
echo "   docker-compose up --build"
echo ""
echo "🧪 Run tests:"
echo "   uv run pytest"
echo ""
echo "🔧 Code quality checks:"
echo "   uv run ruff check"
echo "   uv run mypy src/"
echo ""
echo "📚 View API documentation:"
echo "   http://localhost:8000/api/v1/docs (when server is running)"
echo ""