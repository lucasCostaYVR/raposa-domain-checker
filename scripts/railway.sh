#!/bin/bash

# Raposa Domain Checker - Railway Management Scripts
# Collection of useful commands for managing Railway deployments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for colored output
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        error "Railway CLI not found. Install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
}

# Show current Railway status
show_status() {
    log "Current Railway Status:"
    railway status
    echo ""
}

# Quick health check for both environments
health_check() {
    log "Checking API health..."
    echo ""
    
    info "Production Health Check:"
    curl -s https://api.domainchecker.raposa.tech/healthz/ | jq '.' 2>/dev/null || echo "Production API not responding"
    echo ""
    
    info "Development Health Check:"
    curl -s https://stage.domainchecker.raposa.tech/healthz/ | jq '.' 2>/dev/null || echo "Development API not responding"
    echo ""
}

# Deploy to development
deploy_dev() {
    log "Deploying to development environment..."
    
    # Ensure we're on develop branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "develop" ]; then
        warn "Current branch is $current_branch, switching to develop..."
        git checkout develop
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        error "You have uncommitted changes. Please commit or stash them first."
        git status --short
        exit 1
    fi
    
    # Pull latest changes
    git pull origin develop
    
    # Push to trigger deployment
    log "Pushing to develop branch (triggers automatic deployment)..."
    git push origin develop
    
    log "Development deployment triggered! Check Railway dashboard for progress."
    info "URL: https://stage.domainchecker.raposa.tech"
}

# Deploy to production
deploy_prod() {
    log "Deploying to production environment..."
    
    # Ensure we're on main branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        warn "Current branch is $current_branch, switching to main..."
        git checkout main
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        error "You have uncommitted changes. Please commit or stash them first."
        git status --short
        exit 1
    fi
    
    # Merge develop into main
    log "Merging develop branch into main..."
    git merge develop
    
    # Push to trigger deployment
    log "Pushing to main branch (triggers automatic deployment)..."
    git push origin main
    
    log "Production deployment triggered! Check Railway dashboard for progress."
    info "URL: https://api.domainchecker.raposa.tech"
}

# View logs for current environment
view_logs() {
    log "Viewing logs for current environment..."
    railway logs
}

# View deployment logs specifically
view_deployment_logs() {
    log "Viewing deployment logs for current environment..."
    railway logs --deployment
}

# View build logs
view_build_logs() {
    log "Viewing build logs for current environment..."
    railway logs --build
}

# Monitor deployment in real-time
monitor_deployment() {
    log "Monitoring deployment logs in real-time..."
    info "Press Ctrl+C to stop monitoring"
    railway logs --deployment --follow 2>/dev/null || railway logs --deployment
}

# Switch between environments
switch_env() {
    if [ "$1" = "dev" ] || [ "$1" = "development" ]; then
        log "Switching to development environment..."
        railway environment development
        railway service raposa-stage
        git checkout develop 2>/dev/null || true
    elif [ "$1" = "prod" ] || [ "$1" = "production" ]; then
        log "Switching to production environment..."
        railway environment production
        railway service raposa-app-api
        git checkout main 2>/dev/null || true
    else
        error "Invalid environment. Use 'dev' or 'prod'"
        exit 1
    fi
    
    show_status
}

# Create a new database migration
create_migration() {
    if [ -z "$1" ]; then
        error "Please provide a migration description"
        echo "Usage: $0 migrate \"Add new column to users\""
        exit 1
    fi
    
    log "Creating new database migration: $1"
    
    # Ensure we're in the correct directory
    if [ ! -f "alembic.ini" ]; then
        error "alembic.ini not found. Run this from the project root."
        exit 1
    fi
    
    # Generate migration
    alembic revision --autogenerate -m "$1"
    
    log "Migration created successfully!"
    warn "Remember to review the generated migration file before deploying."
}

# Rollback deployment
rollback() {
    warn "Rolling back last deployment..."
    railway rollback
    log "Rollback completed!"
}

# Show environment variables
show_vars() {
    log "Environment variables for current service:"
    railway variables
}

# Set environment variable
set_var() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        error "Please provide variable name and value"
        echo "Usage: $0 setvar VARIABLE_NAME value"
        exit 1
    fi
    
    log "Setting environment variable: $1"
    railway variables set "$1=$2"
    log "Variable set successfully!"
}

# Quick project setup
setup_project() {
    log "Setting up Railway project links..."
    
    # Link to production environment
    info "Linking production environment..."
    railway link -e production -s raposa-app-api
    
    # Switch to development
    info "Linking development environment..."  
    railway link -e development -s raposa-stage
    
    log "Project setup completed!"
    show_status
}

# Show deployment history
show_deployments() {
    log "Recent deployments:"
    railway deployments
}

# Full development workflow
dev_workflow() {
    log "Starting development workflow..."
    
    # Switch to development environment
    switch_env dev
    
    # Check health
    health_check
    
    # Show logs
    info "Recent logs:"
    railway logs --tail 10
}

# Show help
show_help() {
    echo "Raposa Domain Checker - Railway Management Scripts"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  status              Show current Railway status"
    echo "  health              Check API health for both environments"
    echo "  deploy-dev          Deploy to development environment"
    echo "  deploy-prod         Deploy to production environment"
    echo "  logs                View logs for current environment"
    echo "  deploy-logs         View deployment logs specifically"
    echo "  build-logs          View build logs"
    echo "  monitor             Monitor deployment in real-time"
    echo "  switch <env>        Switch to dev/prod environment"
    echo "  migrate <message>   Create new database migration"
    echo "  rollback            Rollback last deployment"
    echo "  vars                Show environment variables"
    echo "  setvar <name> <val> Set environment variable"
    echo "  setup               Setup Railway project links"
    echo "  deployments         Show deployment history"
    echo "  dev                 Start development workflow"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy-dev"
    echo "  $0 switch prod"
    echo "  $0 monitor              # Watch deployment in real-time"
    echo "  $0 deploy-logs          # View deployment logs"
    echo "  $0 migrate \"Add email verification\""
    echo "  $0 setvar DEBUG true"
}

# Main script logic
main() {
    check_railway_cli
    
    case "${1:-help}" in
        "status")
            show_status
            ;;
        "health")
            health_check
            ;;
        "deploy-dev")
            deploy_dev
            ;;
        "deploy-prod")
            deploy_prod
            ;;
        "logs")
            view_logs
            ;;
        "deploy-logs")
            view_deployment_logs
            ;;
        "build-logs")
            view_build_logs
            ;;
        "monitor")
            monitor_deployment
            ;;
        "switch")
            switch_env "$2"
            ;;
        "migrate")
            create_migration "$2"
            ;;
        "rollback")
            rollback
            ;;
        "vars")
            show_vars
            ;;
        "setvar")
            set_var "$2" "$3"
            ;;
        "setup")
            setup_project
            ;;
        "deployments")
            show_deployments
            ;;
        "dev")
            dev_workflow
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
