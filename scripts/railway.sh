#!/bin/bash

# Railway Management Script for FastAPI Projects
# Manage Railway deployments and environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[RAILWAY]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_help() {
    echo "Railway Management for FastAPI"
    echo ""
    echo "Usage: ./scripts/railway.sh [command]"
    echo ""
    echo "Commands:"
    echo "  status             Show project status and deployments"
    echo "  deploy             Deploy current branch to Railway"
    echo "  logs               View application logs"
    echo "  shell              Open shell in production environment"
    echo "  env                Manage environment variables"
    echo "  db                 Database operations"
    echo "  health             Check API health"
    echo "  setup              Setup new Railway project"
    echo ""
}

check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Install with:"
        echo "curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
}

check_login() {
    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway. Run: railway login"
        exit 1
    fi
}

show_status() {
    print_step "Getting project status..."

    echo ""
    echo "Project Information:"
    railway status

    echo ""
    echo "Recent Deployments:"
    railway logs --lines 10
}

deploy_app() {
    print_step "Deploying to Railway..."

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes"
        read -p "Continue with deployment? (y/n): " continue_deploy
        if [ "$continue_deploy" != "y" ]; then
            exit 0
        fi
    fi

    # Deploy
    railway up

    if [ $? -eq 0 ]; then
        print_success "Deployment completed"

        # Show deployment URL
        PROJECT_URL=$(railway status --json 2>/dev/null | grep -o '"url":"[^"]*"' | cut -d'"' -f4 || echo "")
        if [ ! -z "$PROJECT_URL" ]; then
            echo ""
            echo "🌐 Your API: $PROJECT_URL"
            echo "📊 Health check: $PROJECT_URL/health/"
        fi
    else
        print_error "Deployment failed"
        exit 1
    fi
}

view_logs() {
    print_step "Viewing application logs..."
    railway logs --follow
}

open_shell() {
    print_step "Opening production shell..."
    railway shell
}

manage_env() {
    echo "Environment Variable Management"
    echo ""
    echo "1. List all variables"
    echo "2. Set a variable"
    echo "3. Delete a variable"
    echo ""
    read -p "Choose option (1-3): " option

    case $option in
        1)
            print_step "Listing environment variables..."
            railway variables
            ;;
        2)
            read -p "Variable name: " var_name
            read -p "Variable value: " var_value
            railway variables set "$var_name=$var_value"
            print_success "Variable set: $var_name"
            ;;
        3)
            read -p "Variable name to delete: " var_name
            railway variables delete "$var_name"
            print_success "Variable deleted: $var_name"
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

manage_db() {
    echo "Database Operations"
    echo ""
    echo "1. Connect to database"
    echo "2. Run migration"
    echo "3. Backup database"
    echo "4. Show database URL"
    echo ""
    read -p "Choose option (1-4): " option

    case $option in
        1)
            print_step "Connecting to database..."
            DATABASE_URL=$(railway variables get DATABASE_URL)
            if [ ! -z "$DATABASE_URL" ]; then
                railway run psql "$DATABASE_URL"
            else
                print_error "DATABASE_URL not found"
            fi
            ;;
        2)
            print_step "Running database migration..."
            railway run alembic upgrade head
            ;;
        3)
            print_step "Creating database backup..."
            BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
            DATABASE_URL=$(railway variables get DATABASE_URL)
            if [ ! -z "$DATABASE_URL" ]; then
                railway run pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
                print_success "Backup created: $BACKUP_FILE"
            else
                print_error "DATABASE_URL not found"
            fi
            ;;
        4)
            print_step "Database connection string:"
            railway variables get DATABASE_URL
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

check_health() {
    print_step "Checking API health..."

    PROJECT_URL=$(railway status --json 2>/dev/null | grep -o '"url":"[^"]*"' | cut -d'"' -f4 || echo "")

    if [ -z "$PROJECT_URL" ]; then
        print_error "Could not determine project URL"
        exit 1
    fi

    HEALTH_URL="$PROJECT_URL/health/"

    echo "Testing: $HEALTH_URL"

    if curl -s "$HEALTH_URL" > /dev/null; then
        print_success "API is healthy"
        echo ""
        echo "Health Response:"
        curl -s "$HEALTH_URL" | python -m json.tool
    else
        print_error "API health check failed"
        print_step "Check logs with: ./scripts/railway.sh logs"
    fi
}

setup_project() {
    print_step "Setting up new Railway project..."
    echo ""
    echo "This will run the automated setup script."
    echo "Make sure you have:"
    echo "1. Railway CLI installed and logged in"
    echo "2. Your code ready in this directory"
    echo ""
    read -p "Continue? (y/n): " continue_setup

    if [ "$continue_setup" = "y" ]; then
        if [ -f "./setup_railway.sh" ]; then
            ./setup_railway.sh
        else
            print_error "setup_railway.sh not found"
        fi
    fi
}

# Main command handling
check_railway_cli
check_login

case "${1:-}" in
    "status")
        show_status
        ;;
    "deploy")
        deploy_app
        ;;
    "logs")
        view_logs
        ;;
    "shell")
        open_shell
        ;;
    "env")
        manage_env
        ;;
    "db")
        manage_db
        ;;
    "health")
        check_health
        ;;
    "setup")
        setup_project
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
