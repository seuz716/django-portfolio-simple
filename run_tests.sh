#!/bin/bash
# =============================================================================
# Django Portfolio - Test Runner Script
# Lead SDET Implementation
# =============================================================================
# Usage: ./run_tests.sh [options]
# Options:
#   --coverage    Run with coverage report
#   --verbose     Show detailed output
#   --fail-fast   Stop on first failure
#   --help        Show this help message
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
COVERAGE=false
VERBOSE=false
FAIL_FAST=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        --help)
            echo "Django Portfolio Test Runner"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --coverage    Generate coverage report"
            echo "  --verbose     Show detailed test output"
            echo "  --fail-fast   Stop execution on first failure"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Change to project directory
cd "$(dirname "$0")"

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}  Django Portfolio - Test Suite Runner${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Set environment variables for testing
export DJANGO_SETTINGS_MODULE=django_portfolio.settings
export SECRET_KEY="test-secret-key-for-testing-only-min-50-chars-random-string"
export DEBUG=True
export ALLOWED_HOSTS="localhost,127.0.0.1,testserver"

# Build pytest command
PYTEST_CMD="pytest tests_new/"

# Add verbose flag if requested
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add fail-fast flag if requested
if [ "$FAIL_FAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=blog --cov=portfolio --cov=django_portfolio --cov-report=term-missing --cov-report=html:htmlcov"
fi

echo -e "${YELLOW}Running tests...${NC}"
echo -e "${BLUE}Command:${NC} $PYTEST_CMD"
echo ""

# Run tests
if eval $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}=================================================${NC}"
    echo -e "${GREEN}  ✓ All tests passed!${NC}"
    echo -e "${GREEN}=================================================${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${BLUE}Coverage report generated at: htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}=================================================${NC}"
    echo -e "${RED}  ✗ Some tests failed${NC}"
    echo -e "${RED}=================================================${NC}"
    exit 1
fi
