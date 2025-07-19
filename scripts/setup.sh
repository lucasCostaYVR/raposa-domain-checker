#!/bin/bash

# Raposa Domain Checker - Quick Setup Script
# One-command setup for new development environments

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[SETUP] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    python_version=$(python3 --version | cut -d' ' -f2)
    info "Python version: $python_version"
    
    # Check Node.js for Railway CLI
    if ! command -v node &> /dev/null; then
        warn "Node.js not found. You'll need it for Railway CLI"
        info "Install from: https://nodejs.org/"
    else
        node_version=$(node --version)
        info "Node.js version: $node_version"
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        error "Git is required but not installed"
        exit 1
    fi
    git_version=$(git --version)
    info "Git version: $git_version"
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        error "curl is required but not installed"
        exit 1
    fi
    
    log "✅ System requirements check complete"
}

# Install development tools
install_tools() {
    log "Installing development tools..."
    
    # Install Railway CLI if not present
    if ! command -v railway &> /dev/null; then
        if command -v npm &> /dev/null; then
            log "Installing Railway CLI..."
            npm install -g @railway/cli
        else
            warn "npm not available. Please install Railway CLI manually:"
            echo "npm install -g @railway/cli"
        fi
    else
        info "✅ Railway CLI already installed"
    fi
    
    # Install jq for JSON parsing if not present
    if ! command -v jq &> /dev/null; then
        warn "jq not found. Install it for better JSON handling:"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "brew install jq"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "sudo apt-get install jq  # or yum install jq"
        fi
    else
        info "✅ jq already installed"
    fi
    
    log "Development tools setup complete"
}

# Setup Python environment
setup_python() {
    log "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    else
        info "✅ Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    info "Virtual environment activated"
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        log "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        warn "requirements.txt not found"
    fi
    
    # Install development dependencies
    log "Installing development dependencies..."
    pip install black flake8 pytest pytest-asyncio httpx alembic
    
    log "✅ Python environment setup complete"
}

# Setup Railway connection
setup_railway() {
    log "Setting up Railway connection..."
    
    if ! command -v railway &> /dev/null; then
        error "Railway CLI not found. Please install it first."
        return 1
    fi
    
    # Check if already logged in
    if railway whoami &> /dev/null; then
        info "✅ Already logged into Railway"
    else
        log "Logging into Railway..."
        railway login
    fi
    
    # Link project environments
    log "Linking Railway project..."
    info "This will link to the raposa-domain-checker project"
    info "Make sure you have access to the project first"
    
    read -p "Link Railway environments now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./scripts/railway.sh setup
    else
        warn "Skipping Railway setup. Run './scripts/railway.sh setup' later"
    fi
}

# Setup Git hooks (optional)
setup_git_hooks() {
    log "Setting up Git hooks..."
    
    # Create pre-commit hook for code formatting
    hook_file=".git/hooks/pre-commit"
    if [ ! -f "$hook_file" ]; then
        cat > "$hook_file" << 'EOF'
#!/bin/bash
# Pre-commit hook for code formatting

echo "Running pre-commit checks..."

# Format Python code with black
if command -v black &> /dev/null; then
    black src/ --check --quiet || {
        echo "Code formatting issues found. Running black..."
        black src/
        echo "Code formatted. Please review and commit again."
        exit 1
    }
fi

# Run flake8 linting
if command -v flake8 &> /dev/null; then
    flake8 src/ --max-line-length=88 --ignore=E203,W503 || {
        echo "Linting issues found. Please fix them before committing."
        exit 1
    }
fi

echo "Pre-commit checks passed!"
EOF
        chmod +x "$hook_file"
        info "✅ Git pre-commit hook installed"
    else
        info "✅ Git hooks already configured"
    fi
}

# Create development configuration
create_dev_config() {
    log "Creating development configuration..."
    
    # Create .env.example if it doesn't exist
    if [ ! -f ".env.example" ]; then
        cat > ".env.example" << 'EOF'
# Raposa Domain Checker - Environment Configuration

# Application Environment
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/raposa_dev

# SendGrid Email Service
SENDGRID_API_KEY=SG.your_api_key_here
SENDGRID_FROM_EMAIL=dev@raposa.tech

# Optional: Development Settings
DEBUG=true
LOG_LEVEL=DEBUG
EOF
        info "✅ Created .env.example file"
    else
        info "✅ .env.example already exists"
    fi
    
    # Create development environment file
    if [ ! -f ".env" ]; then
        warn "No .env file found. Copy .env.example and update with your values:"
        echo "cp .env.example .env"
    else
        info "✅ .env file exists"
    fi
}

# Run quick verification
verify_setup() {
    log "Verifying setup..."
    
    # Check if virtual environment works
    if source venv/bin/activate && python -c "import fastapi" 2>/dev/null; then
        info "✅ Python environment working"
    else
        warn "❌ Python environment issues detected"
    fi
    
    # Check if scripts are executable
    if [ -x "scripts/dev.sh" ] && [ -x "scripts/railway.sh" ] && [ -x "scripts/git.sh" ]; then
        info "✅ Scripts are executable"
    else
        warn "❌ Some scripts are not executable"
    fi
    
    # Check Railway connection
    if command -v railway &> /dev/null && railway whoami &> /dev/null; then
        info "✅ Railway CLI connected"
    else
        warn "❌ Railway CLI not connected"
    fi
    
    log "Setup verification complete!"
}

# Show next steps
show_next_steps() {
    log "🎉 Setup complete! Here are your next steps:"
    echo ""
    info "1. Activate Python environment:"
    echo "   source venv/bin/activate"
    echo ""
    info "2. Configure environment variables:"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your actual values"
    echo ""
    info "3. Start development server:"
    echo "   ./scripts/dev.sh start"
    echo ""
    info "4. Useful commands:"
    echo "   ./scripts/dev.sh help      # Development tools"
    echo "   ./scripts/railway.sh help  # Railway management"
    echo "   ./scripts/git.sh help      # Git workflow"
    echo ""
    info "5. Test your setup:"
    echo "   ./scripts/dev.sh info"
    echo "   ./scripts/railway.sh status"
    echo ""
    log "Happy coding! 🚀"
}

# Main setup process
main() {
    echo "🚀 Raposa Domain Checker - Development Environment Setup"
    echo ""
    
    check_requirements
    echo ""
    
    install_tools
    echo ""
    
    setup_python
    echo ""
    
    setup_railway
    echo ""
    
    setup_git_hooks
    echo ""
    
    create_dev_config
    echo ""
    
    verify_setup
    echo ""
    
    show_next_steps
}

# Run main function
main "$@"
