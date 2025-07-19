#!/bin/bash

# Raposa Domain Checker - Development Helper Scripts
# Quick commands for common development tasks

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[DEV] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

# Quick development server start
start_dev() {
    log "Starting development server..."
    
    # Check if we're in the right directory
    if [ ! -f "src/main.py" ]; then
        error "main.py not found in src/. Run this from project root."
        exit 1
    fi
    
    # Set development environment
    export ENVIRONMENT=development
    
    # Start server with hot reload
    info "Starting FastAPI server with hot reload..."
    cd src && uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# Test API endpoints
test_api() {
    log "Testing API endpoints..."
    
    base_url="http://localhost:8000"
    
    info "Health Check:"
    curl -s "$base_url/healthz/" | jq '.' 2>/dev/null || echo "Health check failed"
    echo ""
    
    info "API Root:"
    curl -s "$base_url/" | jq '.' 2>/dev/null || echo "Root endpoint failed"
    echo ""
    
    info "OpenAPI Docs available at: http://localhost:8000/docs"
}

# Setup local development environment
setup_dev() {
    log "Setting up local development environment..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    info "Python version: $python_version"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    log "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    log "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install development dependencies
    log "Installing development dependencies..."
    pip install black flake8 pytest pytest-asyncio httpx
    
    log "Development environment setup complete!"
    info "Activate with: source venv/bin/activate"
}

# Format code with Black
format_code() {
    log "Formatting code with Black..."
    
    if ! command -v black &> /dev/null; then
        warn "Black not installed. Installing..."
        pip install black
    fi
    
    black src/ --line-length 88
    log "Code formatting complete!"
}

# Lint code with flake8
lint_code() {
    log "Linting code with flake8..."
    
    if ! command -v flake8 &> /dev/null; then
        warn "Flake8 not installed. Installing..."
        pip install flake8
    fi
    
    flake8 src/ --max-line-length=88 --ignore=E203,W503
    log "Code linting complete!"
}

# Run tests
run_tests() {
    log "Running tests..."
    
    if ! command -v pytest &> /dev/null; then
        warn "Pytest not installed. Installing..."
        pip install pytest pytest-asyncio httpx
    fi
    
    # Run tests with coverage if available
    if command -v pytest-cov &> /dev/null; then
        pytest tests/ --cov=src/ --cov-report=html
        info "Coverage report generated in htmlcov/"
    else
        pytest tests/
    fi
}

# Database operations
db_reset() {
    log "Resetting development database..."
    
    # Remove existing database file if using SQLite
    if [ -f "dev.db" ]; then
        rm dev.db
        log "Removed existing database file"
    fi
    
    # Run migrations
    if [ -f "alembic.ini" ]; then
        log "Running Alembic migrations..."
        alembic upgrade head
    else
        warn "No alembic.ini found, database will be created on first run"
    fi
    
    log "Database reset complete!"
}

# Generate new migration
new_migration() {
    if [ -z "$1" ]; then
        error "Please provide a migration description"
        echo "Usage: $0 migration \"Add new column\""
        exit 1
    fi
    
    log "Creating new migration: $1"
    alembic revision --autogenerate -m "$1"
    log "Migration created! Review it before applying."
}

# Check dependencies for updates
check_deps() {
    log "Checking for dependency updates..."
    
    if ! command -v pip-check &> /dev/null; then
        info "Installing pip-check..."
        pip install pip-check
    fi
    
    pip-check
}

# Generate requirements.txt from current environment
freeze_deps() {
    log "Generating requirements.txt..."
    pip freeze > requirements.txt
    log "Requirements.txt updated!"
}

# Start fresh development session
dev_session() {
    log "Starting fresh development session..."
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
        info "Virtual environment activated"
    fi
    
    # Install/update dependencies
    pip install -r requirements.txt
    
    # Format and lint code
    format_code
    lint_code
    
    # Start development server
    start_dev
}

# Clean up development files
clean() {
    log "Cleaning up development files..."
    
    # Remove Python cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove coverage files
    rm -rf htmlcov/ .coverage 2>/dev/null || true
    
    log "Cleanup complete!"
}

# Show development environment info
dev_info() {
    log "Development Environment Info:"
    echo ""
    
    info "Python version: $(python3 --version 2>&1)"
    info "Current directory: $(pwd)"
    info "Git branch: $(git branch --show-current 2>/dev/null || echo 'Not a git repo')"
    
    if [ -d "venv" ]; then
        info "Virtual environment: ✅ Found"
    else
        warn "Virtual environment: ❌ Not found"
    fi
    
    if [ -f "requirements.txt" ]; then
        info "Dependencies: $(wc -l < requirements.txt) packages listed"
    fi
    
    echo ""
    info "Quick commands:"
    echo "  Start server: $0 start"
    echo "  Test API: $0 test"
    echo "  Format code: $0 format"
    echo "  Run tests: $0 tests"
}

# Show help
show_help() {
    echo "Raposa Domain Checker - Development Helper Scripts"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  start               Start development server with hot reload"
    echo "  test                Test API endpoints"
    echo "  setup               Setup local development environment"
    echo "  format              Format code with Black"
    echo "  lint                Lint code with flake8"
    echo "  tests               Run test suite"
    echo "  db-reset            Reset development database"
    echo "  migration <msg>     Generate new Alembic migration"
    echo "  check-deps          Check for dependency updates"
    echo "  freeze              Update requirements.txt"
    echo "  session             Start fresh development session"
    echo "  clean               Clean up development files"
    echo "  info                Show development environment info"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start            # Start development server"
    echo "  $0 session          # Full development startup"
    echo "  $0 migration \"Add user roles\""
}

# Main script logic
main() {
    case "${1:-help}" in
        "start")
            start_dev
            ;;
        "test")
            test_api
            ;;
        "setup")
            setup_dev
            ;;
        "format")
            format_code
            ;;
        "lint")
            lint_code
            ;;
        "tests")
            run_tests
            ;;
        "db-reset")
            db_reset
            ;;
        "migration")
            new_migration "$2"
            ;;
        "check-deps")
            check_deps
            ;;
        "freeze")
            freeze_deps
            ;;
        "session")
            dev_session
            ;;
        "clean")
            clean
            ;;
        "info")
            dev_info
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

main "$@"
