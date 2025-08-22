#!/bin/bash

# Linear Claude Agent - Test Runner Script
# This script runs the test suite with different configurations

set -e

echo "🧪 Running Linear Claude Agent test suite..."

# Default test command
TEST_CMD="uv run pytest"

# Parse command line arguments
COVERAGE=false
INTEGRATION=false
UNIT_ONLY=false
VERBOSE=false
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --integration|-i)
            INTEGRATION=true
            shift
            ;;
        --unit|-u)
            UNIT_ONLY=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage      Run tests with coverage report"
            echo "  -i, --integration   Run integration tests only"
            echo "  -u, --unit          Run unit tests only"
            echo "  -v, --verbose       Run tests in verbose mode"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                   # Run all tests"
            echo "  $0 --coverage        # Run with coverage"
            echo "  $0 --unit           # Run unit tests only"
            echo "  $0 --integration     # Run integration tests only"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build test command based on options
if [ "$UNIT_ONLY" = true ]; then
    MARKERS="-m unit"
    echo "🔬 Running unit tests only..."
elif [ "$INTEGRATION" = true ]; then
    MARKERS="-m integration"
    echo "🔌 Running integration tests only..."
else
    echo "🧪 Running all tests..."
fi

if [ "$VERBOSE" = true ]; then
    TEST_CMD="$TEST_CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    echo "📊 Coverage reporting enabled"
    # Coverage is already configured in pyproject.toml
fi

# Add markers if specified
if [ -n "$MARKERS" ]; then
    TEST_CMD="$TEST_CMD $MARKERS"
fi

echo "Running: $TEST_CMD"
echo ""

# Check if test dependencies are installed
echo "📋 Checking test dependencies..."
if ! uv run python -c "import pytest, pytest_asyncio, httpx" 2>/dev/null; then
    echo "📦 Installing test dependencies..."
    uv sync --extra dev
fi

# Run the tests
eval $TEST_CMD

# Show coverage report if enabled
if [ "$COVERAGE" = true ]; then
    echo ""
    echo "📊 Coverage Summary:"
    uv run coverage report --show-missing
    
    echo ""
    echo "📊 HTML coverage report generated: htmlcov/index.html"
    
    # Open coverage report in browser (macOS/Linux)
    if command -v open &> /dev/null; then
        echo "🌐 Opening coverage report in browser..."
        open htmlcov/index.html
    elif command -v xdg-open &> /dev/null; then
        echo "🌐 Opening coverage report in browser..."
        xdg-open htmlcov/index.html
    fi
fi

echo ""
echo "✅ Test run complete!"