#!/bin/bash

# 🚀 FastAPI Boilerplate - Interactive Railway Setup
# One-command setup for deploying your FastAPI project to Railway

set -e

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Emojis for better UX
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
INFO="ℹ️"
SPARKLES="✨"
DATABASE="🗃️"
GLOBE="🌐"

print_header() {
    echo ""
    echo -e "${PURPLE}${WHITE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}${WHITE}║                   ${ROCKET} FastAPI Railway Setup ${ROCKET}                   ║${NC}"
    echo -e "${PURPLE}${WHITE}║              Deploy your FastAPI project in minutes!            ║${NC}"
    echo -e "${PURPLE}${WHITE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${ERROR} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

print_info() {
    echo -e "${CYAN}${SPARKLES} $1${NC}"
}

show_requirements() {
    echo -e "${WHITE}📋 What you'll need:${NC}"
    echo "   • Railway CLI installed and logged in"
    echo "   • Your FastAPI project code ready"
    echo "   • A few minutes to set up your project"
    echo ""
}

check_railway_cli() {
    print_step "Checking Railway CLI..."

    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found!"
        echo ""
        echo -e "${WHITE}Install Railway CLI:${NC}"
        echo "curl -fsSL https://railway.app/install.sh | sh"
        echo ""
        echo "Then run this script again."
        exit 1
    fi

    print_success "Railway CLI found"
}

check_login() {
    print_step "Checking Railway login..."

    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway!"
        echo ""
        echo -e "${WHITE}Please login first:${NC}"
        echo "railway login"
        echo ""
        echo "Then run this script again."
        exit 1
    fi

    USER=$(railway whoami 2>/dev/null | head -n1)
    print_success "Logged in as: $USER"
}

get_project_name() {
    echo ""
    echo -e "${WHITE}🏷️  Project Configuration${NC}"
    echo ""

    # Get current directory name as default
    DEFAULT_NAME=$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')

    echo -e "${CYAN}What would you like to name your Railway project?${NC}"
    echo -e "${CYAN}(lowercase letters, numbers, and hyphens only)${NC}"

    while true; do
        read -p "Project name [$DEFAULT_NAME]: " PROJECT_NAME

        # Use default if empty
        if [ -z "$PROJECT_NAME" ]; then
            PROJECT_NAME="$DEFAULT_NAME"
        fi

        # Validate project name
        if [[ "$PROJECT_NAME" =~ ^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$ ]]; then
            break
        else
            print_error "Invalid name. Use lowercase letters, numbers, and hyphens only."
            echo "Examples: my-api, fastapi-starter, awesome-project"
        fi
    done

    print_success "Project name: $PROJECT_NAME"
}

get_environment_setup() {
    echo ""
    echo -e "${WHITE}🌍 Environment Configuration${NC}"
    echo ""
    
    echo -e "${CYAN}Which environments would you like to create?${NC}"
    echo "1) Production only"
    echo "2) Staging and Production"
    echo ""
    
    while true; do
        read -p "Select option [1-2]: " ENV_CHOICE
        
        case $ENV_CHOICE in
            1)
                ENVIRONMENTS=("production")
                CREATE_STAGING=false
                print_success "Will create: Production environment"
                break
                ;;
            2)
                ENVIRONMENTS=("staging" "production")
                CREATE_STAGING=true
                print_success "Will create: Staging and Production environments"
                break
                ;;
            *)
                print_error "Please select 1 or 2"
                ;;
        esac
    done
}

create_railway_project() {
    print_step "Creating Railway project: $PROJECT_NAME"
    
    # Create new project
    if railway init --name "$PROJECT_NAME" 2>/dev/null; then
        print_success "Railway project created"
    else
        print_error "Failed to create Railway project"
        echo ""
        echo "This might happen if:"
        echo "• A project with this name already exists"
        echo "• Network connectivity issues"
        echo "• Railway service is down"
        exit 1
    fi
}

create_environments() {
    if [ "$CREATE_STAGING" = true ]; then
        print_step "Creating staging environment..."
        
        # Check if staging environment exists, create if not
        if ! railway environment staging 2>/dev/null; then
            print_info "Staging environment doesn't exist, creating it..."
            # Railway automatically creates environments when you switch to them
            # We'll handle this in the service creation
        fi
        
        print_success "Staging environment ready"
    fi
    
    # Production environment should exist by default
    print_success "Production environment ready"
}

create_python_service() {
    local env=$1
    local service_suffix=""
    
    if [ "$env" = "staging" ]; then
        service_suffix="-stage"
    fi
    
    print_step "Creating Python web service for $env environment..."
    
    echo ""
    echo -e "${CYAN}${ROCKET} Setting up your FastAPI service...${NC}"
    echo "This will create a Python web service: ${PROJECT_NAME}-python${service_suffix}"
    echo ""
    
    # For staging environment, we need to create it first
    if [ "$env" = "staging" ]; then
        print_info "Creating staging environment..."
        local create_env_output
        create_env_output=$(railway environment new staging 2>&1)
        if [ $? -eq 0 ]; then
            print_success "Staging environment created"
        else
            print_info "Staging environment may already exist or will be created automatically"
        fi
    fi
    
    # Switch to the environment
    railway environment $env
    
    # Create service from current directory with custom name
    local output
    local exit_code
    
    output=$(railway add --service "${PROJECT_NAME}-python${service_suffix}" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Python service created: ${PROJECT_NAME}-python${service_suffix} in $env environment"
    else
        print_error "Failed to create Python service for $env environment"
        echo ""
        echo "Error details:"
        echo "$output"
        echo ""
        echo "Common solutions:"
        echo "• Make sure you're in your project directory"
        echo "• Check that main.py exists"
        echo "• Try running: railway add --service --help"
        return 1
    fi
}

add_postgresql() {
    local env=$1
    local service_suffix=""
    
    if [ "$env" = "staging" ]; then
        service_suffix="-stage"
    fi
    
    print_step "Adding PostgreSQL database for $env environment..."
    
    echo ""
    echo -e "${CYAN}${DATABASE} Setting up your database...${NC}"
    echo "This will add a PostgreSQL database to your $env environment."
    echo ""
    
    # Switch to the environment
    railway environment $env
    
    # Capture both stdout and stderr for better error reporting
    local output
    local exit_code
    
    output=$(railway add --database postgres 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "PostgreSQL database added for $env environment"
        sleep 2  # Give Railway time to provision
        return 0
    else
        print_error "Failed to add PostgreSQL for $env environment"
        echo ""
        echo "Error details:"
        echo "$output"
        echo ""
        echo "Common solutions:"
        echo "• Make sure you're in the correct Railway project context"
        echo "• Try running: railway add --help"
        echo "• Check if PostgreSQL is already added to this project"
        echo ""
        
        # Check if we can continue without adding PostgreSQL
        read -p "Continue setup without adding PostgreSQL? (y/n): " continue_without_db
        if [ "$continue_without_db" != "y" ]; then
            exit 1
        fi
        
        print_warning "Continuing without PostgreSQL addition..."
        return 1  # Return error code but don't exit
    fi
}

setup_database_variables() {
    local env=$1
    local service_suffix=""
    
    if [ "$env" = "staging" ]; then
        service_suffix="-stage"
    fi
    
    print_step "Setting up database variables for $env environment..."
    
    # Switch to the environment and Python service
    railway environment $env
    railway service "${PROJECT_NAME}-python${service_suffix}"
    
    # Add DATABASE_URL from Postgres service
    railway variables --set DATABASE_URL='${{Postgres.DATABASE_URL}}'
    
    print_success "Database variables configured for $env environment"
}

setup_environment_for_env() {
    local env=$1
    
    print_step "Setting up environment variables for $env environment..."
    
    # Switch to environment
    railway environment $env
    
    # You can add more environment-specific variables here
    print_success "Environment variables configured for $env environment"
}

get_database_url() {
    print_step "Retrieving database connection..."

    echo -e "${CYAN}${DATABASE} Getting your database URL...${NC}"

    # Wait for database to be ready and get URL
    local attempts=0
    local max_attempts=30

    while [ $attempts -lt $max_attempts ]; do
        DATABASE_URL=$(railway variables get DATABASE_URL 2>/dev/null || echo "")

        if [ ! -z "$DATABASE_URL" ]; then
            print_success "Database URL retrieved"
            break
        fi

        attempts=$((attempts + 1))
        echo -e "${YELLOW}Waiting for database provisioning... ($attempts/$max_attempts)${NC}"
        sleep 2
    done

    if [ -z "$DATABASE_URL" ]; then
        print_warning "No DATABASE_URL found"
        echo ""
        echo "This might happen if:"
        echo "• PostgreSQL wasn't added successfully"
        echo "• Database is still provisioning"
        echo "• You need to add PostgreSQL manually"
        echo ""
        
        # Provide fallback for local development
        DATABASE_URL="sqlite:///./app.db"
        print_info "Using SQLite fallback for local development"
        return 1  # Return error code but continue
    fi
}

setup_environment() {
    print_step "Configuring environment variables..."

    # Set environment to production
    railway variables set ENVIRONMENT=production

    # Generate a secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    railway variables set SECRET_KEY="$SECRET_KEY"

    print_success "Environment variables configured"
    echo "   • ENVIRONMENT=production"
    echo "   • SECRET_KEY=<generated>"
    echo "   • DATABASE_URL=<auto-configured>"
}

create_local_env() {
    print_step "Creating local .env file..."

    cat > .env << EOF
# Local Development Environment
# Copy these values for local development

DATABASE_URL=$DATABASE_URL
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENVIRONMENT=development
EOF

    print_success "Local .env file created"
    print_info "You can now run locally with: ./scripts/dev.sh start"
}

deploy_to_railway() {
    print_step "Deploying to Railway..."

    echo ""
    echo -e "${CYAN}${ROCKET} Deploying your FastAPI application...${NC}"
    echo "This may take a few minutes."
    echo ""

    if railway up; then
        print_success "Deployment completed!"
    else
        print_error "Deployment failed"
        echo ""
        echo "Check the logs with: railway logs"
        exit 1
    fi
}

get_deployment_url() {
    print_step "Getting your deployment URL..."

    sleep 5  # Wait for deployment to be ready

    # Try to get the URL
    PROJECT_URL=$(railway status --json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    deployments = data.get('deployments', [])
    if deployments:
        url = deployments[0].get('url', '')
        if url:
            print(url)
except:
    pass
" 2>/dev/null || echo "")

    if [ ! -z "$PROJECT_URL" ]; then
        print_success "Deployment URL: $PROJECT_URL"
        return 0
    else
        print_warning "Could not retrieve URL automatically"
        print_info "Check your deployment with: railway status"
        return 1
    fi
}

test_deployment() {
    if [ ! -z "$PROJECT_URL" ]; then
        print_step "Testing your deployment..."

        HEALTH_URL="$PROJECT_URL/health/"
        echo "Testing: $HEALTH_URL"

        # Test the health endpoint
        if curl -s --max-time 30 "$HEALTH_URL" > /dev/null 2>&1; then
            print_success "Health check passed!"
            echo ""
            echo "Testing API response:"
            curl -s "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || echo "API is responding"
        else
            print_warning "Health check failed - deployment might still be starting"
            print_info "Monitor with: railway logs"
        fi
    fi
}

show_next_steps() {
    echo ""
    echo -e "${PURPLE}${WHITE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}${WHITE}║                      ${SPARKLES} Setup Complete! ${SPARKLES}                      ║${NC}"
    echo -e "${PURPLE}${WHITE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ ! -z "$PROJECT_URL" ]; then
        echo -e "${GREEN}${GLOBE} Your API is live at:${NC}"
        echo -e "${WHITE}   $PROJECT_URL${NC}"
        echo ""
        echo -e "${GREEN}${CHECK} Health check:${NC}"
        echo -e "${WHITE}   $PROJECT_URL/health/${NC}"
        echo ""
    fi

    echo -e "${CYAN}${ROCKET} What's next?${NC}"
    echo ""
    echo "1. Start building your API:"
    echo "   • Add models in src/models.py"
    echo "   • Add schemas in src/schemas.py"
    echo "   • Add endpoints in main.py"
    echo ""
    echo "2. Local development:"
    echo "   ./scripts/dev.sh start"
    echo ""
    echo "3. Deploy updates:"
    echo "   ./scripts/railway.sh deploy"
    echo ""
    echo "4. Monitor your app:"
    echo "   ./scripts/railway.sh logs"
    echo "   ./scripts/railway.sh status"
    echo ""

    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "• Use ./scripts/dev.sh for local development"
    echo "• Use ./scripts/railway.sh for deployment management"
    echo "• Use ./scripts/git.sh for version control"
    echo ""

    echo -e "${GREEN}Happy coding! ${ROCKET}${NC}"
    echo ""
}

confirm_setup() {
    echo ""
    echo -e "${WHITE}Ready to set up your FastAPI project on Railway?${NC}"
    echo ""
    echo "This will:"
    echo "• Create a new Railway project: $PROJECT_NAME"
    if [ "$CREATE_STAGING" = true ]; then
        echo "• Create staging environment with services: ${PROJECT_NAME}-python-stage, Postgres"
        echo "• Create production environment with services: ${PROJECT_NAME}-python, Postgres"
    else
        echo "• Create production environment with services: ${PROJECT_NAME}-python, Postgres"
    fi
    echo "• Configure environment variables"
    echo "• Deploy your FastAPI application"
    echo "• Create local .env for development"
    echo ""

    while true; do
        read -p "Continue? (y/n): " yn
        case $yn in
            [Yy]* ) break;;
            [Nn]* )
                echo "Setup cancelled."
                exit 0
                ;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Main execution flow
main() {
    print_header
    show_requirements

    # Pre-flight checks
    check_railway_cli
    check_login

    # Get project configuration
    get_project_name
    get_environment_setup
    confirm_setup

    echo ""
    echo -e "${CYAN}${ROCKET} Starting Railway setup...${NC}"
    echo ""

    # Setup Railway project
    create_railway_project
    
    # Setup services for each environment
    for env in "${ENVIRONMENTS[@]}"; do
        echo ""
        echo -e "${CYAN}🌍 Setting up $env environment...${NC}"
        
        # Create Python service for this environment
        if create_python_service "$env"; then
            # Try to add PostgreSQL for this environment
            if add_postgresql "$env"; then
                # Setup database variables if PostgreSQL was added successfully
                setup_database_variables "$env"
            else
                print_info "Continuing setup without PostgreSQL for $env environment..."
            fi
            
            # Setup other environment variables
            setup_environment_for_env "$env"
        else
            print_error "Failed to create Python service for $env environment"
            exit 1
        fi
    done
    
    echo ""
    print_success "All environments set up successfully!"
    
    # Create local .env file
    create_local_env

    echo ""
    echo -e "${CYAN}🚀 Deployment${NC}"
    echo ""
    
    # Ask which environment to deploy
    if [ "${#ENVIRONMENTS[@]}" -gt 1 ]; then
        echo "Which environment would you like to deploy now?"
        select deployment_env in "${ENVIRONMENTS[@]}" "Skip deployment"; do
            if [ "$deployment_env" = "Skip deployment" ]; then
                print_info "Skipping deployment. You can deploy later with: railway up"
                break
            elif [[ " ${ENVIRONMENTS[@]} " =~ " ${deployment_env} " ]]; then
                railway environment "$deployment_env"
                deploy_to_railway
                break
            else
                echo "Please select a valid option."
            fi
        done
    else
        # Only one environment, deploy it
        railway environment "${ENVIRONMENTS[0]}"
        deploy_to_railway
    fi

    # Post-deployment
    if get_deployment_url; then
        test_deployment
    fi

    show_next_steps
}

# Run main function
main
