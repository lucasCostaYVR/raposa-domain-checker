#!/bin/bash

# FastAPI Development Helper Script
# Common development tasks for FastAPI projects

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[DEV]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "FastAPI Development Helper"
    echo ""
    echo "Usage: ./scripts/dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start              Start development server with hot reload"
    echo "  setup              Setup development environment"
    echo "  test               Test API endpoints"
    echo "  migrate            Create and apply database migration"
    echo "  shell              Start Python shell with app context"
    echo "  format             Format code with black"
    echo "  lint               Lint code with flake8"
    echo "  install            Install/update dependencies"
    echo "  clean              Clean cache and temp files"
    echo ""
}

start_server() {
    print_step "Starting development server..."
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Creating template..."
        cat > .env << EOF
ENVIRONMENT=development
DATABASE_URL=postgresql://username:password@localhost:5432/your_local_db
EOF
        print_step "Please update .env with your local database credentials"
    fi
    
    python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0
}

setup_environment() {
    print_step "Setting up development environment..."
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    fi
    
    # Create .env if not exists
    if [ ! -f ".env" ]; then
        cat > .env << EOF
ENVIRONMENT=development
DATABASE_URL=postgresql://username:password@localhost:5432/your_local_db

# Add your environment variables here
# SECRET_KEY=your-secret-key
# API_KEY=your-api-key
EOF
        print_success ".env template created"
        print_step "Please update .env with your configuration"
    fi
    
    print_success "Development environment ready!"
    echo "Next steps:"
    echo "1. Update .env with your database URL"
    echo "2. Run: ./scripts/dev.sh start"
}

test_api() {
    print_step "Testing API endpoints..."
    
    # Check if server is running
    if curl -s http://localhost:8000/health/ > /dev/null; then
        print_success "Health check passed"
        
        # Test health endpoint
        echo ""
        echo "Health Check Response:"
        curl -s http://localhost:8000/health/ | python -m json.tool
        
    else
        print_error "API server not responding on http://localhost:8000"
        print_step "Start the server first: ./scripts/dev.sh start"
    fi
}

create_migration() {
    print_step "Creating database migration..."
    
    read -p "Enter migration message: " message
    if [ -z "$message" ]; then
        message="Auto migration"
    fi
    
    alembic revision --autogenerate -m "$message"
    print_success "Migration created"
    
    read -p "Apply migration now? (y/n): " apply
    if [ "$apply" = "y" ]; then
        alembic upgrade head
        print_success "Migration applied"
    fi
}

python_shell() {
    print_step "Starting Python shell..."
    python -c "
import sys
sys.path.append('.')
from main import app
from src.database import get_db, engine
from src.models import Base
print('FastAPI app available as: app')
print('Database engine available as: engine')
print('Database models available as: Base')
print('Database session: next(get_db())')
"
    python
}

format_code() {
    print_step "Formatting code with black..."
    
    if command -v black &> /dev/null; then
        black .
        print_success "Code formatted"
    else
        print_error "Black not installed. Install with: pip install black"
    fi
}

lint_code() {
    print_step "Linting code with flake8..."
    
    if command -v flake8 &> /dev/null; then
        flake8 --max-line-length=88 --exclude=.venv,alembic .
        print_success "Linting complete"
    else
        print_error "Flake8 not installed. Install with: pip install flake8"
    fi
}

install_deps() {
    print_step "Installing/updating dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies updated"
}

clean_cache() {
    print_step "Cleaning cache and temporary files..."
    
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Cache cleaned"
}

# Main command handling
case "${1:-}" in
    "start")
        start_server
        ;;
    "setup")
        setup_environment
        ;;
    "test")
        test_api
        ;;
    "migrate")
        create_migration
        ;;
    "shell")
        python_shell
        ;;
    "format")
        format_code
        ;;
    "lint")
        lint_code
        ;;
    "install")
        install_deps
        ;;
    "clean")
        clean_cache
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
