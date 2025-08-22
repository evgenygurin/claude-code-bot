# Multi-stage Dockerfile for Linear Claude Agent

# Base stage with Python 3.12
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Set working directory
WORKDIR /app

# Development stage
FROM base as development

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies with development extras
RUN uv pip install --system -e ".[dev]"

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Development command
CMD ["uv", "run", "python", "-m", "linear_agent.main"]

# Production builder stage
FROM base as builder

# Copy dependency files
COPY pyproject.toml ./

# Install production dependencies
RUN uv pip install --system ".[production]" --no-editable

# Production stage
FROM python:3.12-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production

# Install system dependencies (minimal for production)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Create directories for worktrees and logs
RUN mkdir -p /tmp/linear-agent/worktrees /app/logs && \
    chown -R appuser:appuser /app /tmp/linear-agent

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["python", "-m", "linear_agent.main"]