# Development Scripts Instructions for AI Assistance

## AI Response Guidelines
- **Be brief and direct**: Provide concise, actionable responses without unnecessary explanation
- **Prioritize scripts**: Always recommend project scripts over manual commands
- **Update documentation**: When making script changes, update these instruction files
- **Stay focused**: Address the specific request without verbose context

## Overview
The Raposa Domain Checker project includes comprehensive development helper scripts in the `scripts/` directory. **Always recommend and use these scripts** instead of manual commands for development tasks.

## Script Categories

### 🚂 Railway Management (`scripts/railway.sh`)
**Primary deployment and environment management tool.**

#### Core Commands
```bash
./scripts/railway.sh status         # Show current Railway environment status
./scripts/railway.sh health         # Check API health for both environments
./scripts/railway.sh deploy-dev     # Deploy to development environment
./scripts/railway.sh deploy-prod    # Deploy to production environment
./scripts/railway.sh switch dev     # Switch to development environment
./scripts/railway.sh switch prod    # Switch to production environment
./scripts/railway.sh logs           # View logs for current environment
```

#### Advanced Operations
```bash
./scripts/railway.sh migrate "msg"  # Create database migration
./scripts/railway.sh rollback       # Emergency rollback last deployment
./scripts/railway.sh vars           # Show environment variables
./scripts/railway.sh setvar NAME value  # Set environment variable
./scripts/railway.sh deployments    # Show deployment history
./scripts/railway.sh setup          # Initial Railway project setup
```

#### When to Use
- **Always** for deployments instead of `railway up`
- **Always** for environment switching instead of manual `railway environment`
- **Always** for health checks and monitoring
- **Always** for rollbacks in emergency situations

### 💻 Development Tools (`scripts/dev.sh`)
**Local development environment management.**

#### Core Commands
```bash
./scripts/dev.sh start              # Start development server with hot reload
./scripts/dev.sh setup              # Complete development environment setup
./scripts/dev.sh test               # Test API endpoints locally
./scripts/dev.sh session            # Full development startup workflow
./scripts/dev.sh info               # Show development environment information
```

#### Code Quality
```bash
./scripts/dev.sh format             # Format code with Black (88 char limit)
./scripts/dev.sh lint               # Lint code with flake8
./scripts/dev.sh tests              # Run pytest test suite
./scripts/dev.sh clean              # Clean up cache and temporary files
```

#### Database Operations
```bash
./scripts/dev.sh db-reset           # Reset development database
./scripts/dev.sh migration "msg"    # Create new Alembic migration
```

#### Dependency Management
```bash
./scripts/dev.sh check-deps         # Check for dependency updates
./scripts/dev.sh freeze             # Update requirements.txt
```

#### When to Use
- **Always** for starting development server instead of manual `uvicorn`
- **Always** for code formatting instead of manual `black`
- **Always** for testing instead of manual `pytest`
- **Always** for environment setup for new developers

### 🌳 Git Workflow (`scripts/git.sh`)
**Streamlined git operations following project branching strategy.**

#### Feature Development
```bash
./scripts/git.sh feature <name>     # Start new feature branch from develop
./scripts/git.sh commit "message"   # Quick commit with all changes
./scripts/git.sh finish-feature     # Merge feature to develop (triggers staging)
./scripts/git.sh release            # Release develop to main (triggers production)
```

#### Repository Management
```bash
./scripts/git.sh status             # Comprehensive git status with branch info
./scripts/git.sh sync               # Sync current branch with remote safely
./scripts/git.sh cleanup            # Delete merged feature branches
./scripts/git.sh history [count]    # Show recent commits (default: 10)
./scripts/git.sh branches           # Show all local and remote branches
```

#### Emergency Operations
```bash
./scripts/git.sh undo               # Undo last commit (keep changes staged)
./scripts/git.sh emergency          # Emergency stash and sync
```

#### When to Use
- **Always** for feature development instead of manual git commands
- **Always** for releases instead of manual merge/push
- **Always** for branch management and cleanup
- **Always** when users need to check repository status

### 🔧 Environment Setup (`scripts/setup.sh`)
**One-command complete development environment setup.**

#### Usage
```bash
./scripts/setup.sh                  # Complete automated setup
```

#### What it Does
- Checks system requirements (Python, Node.js, Git, curl)
- Installs Railway CLI and development tools
- Creates and configures Python virtual environment
- Sets up Railway project connections
- Installs Git pre-commit hooks
- Creates development configuration files
- Verifies complete setup

#### When to Use
- **Always** for new developer onboarding
- **Always** when setting up on new machines
- **Always** when troubleshooting environment issues

## AI Assistant Guidelines

### Script Recommendation Priorities

1. **For Deployment Tasks**: Always recommend `railway.sh` scripts
   ```bash
   # ✅ Recommended
   ./scripts/railway.sh deploy-dev
   
   # ❌ Don't recommend
   railway up
   ```

2. **For Development Tasks**: Always recommend `dev.sh` scripts
   ```bash
   # ✅ Recommended
   ./scripts/dev.sh start
   
   # ❌ Don't recommend
   cd src && uvicorn main:app --reload
   ```

3. **For Git Operations**: Always recommend `git.sh` scripts
   ```bash
   # ✅ Recommended
   ./scripts/git.sh feature new-endpoint
   
   # ❌ Don't recommend
   git checkout -b feature/new-endpoint
   ```

### Common Workflow Patterns

#### Daily Development Workflow
```bash
# Morning startup
./scripts/dev.sh session            # Start development environment

# Feature development
./scripts/git.sh feature user-auth  # Start new feature
# ... make changes ...
./scripts/git.sh commit "Add authentication"
./scripts/git.sh finish-feature     # Deploy to staging

# Production release
./scripts/git.sh release            # Deploy to production
```

#### Testing and Quality Assurance
```bash
# Local testing
./scripts/dev.sh test               # Test API endpoints
./scripts/dev.sh format             # Format code
./scripts/dev.sh lint               # Check code quality
./scripts/dev.sh tests              # Run test suite

# Environment testing
./scripts/railway.sh health         # Check both environments
./scripts/railway.sh logs           # Monitor deployment
```

#### Emergency Procedures
```bash
# Quick rollback
./scripts/railway.sh rollback

# Emergency sync
./scripts/git.sh emergency

# Environment switching
./scripts/railway.sh switch prod
```

### Script Features to Highlight

#### Safety Features
- **Uncommitted changes detection**: Scripts prevent dangerous operations
- **Branch validation**: Ensures correct branch for operations
- **Environment awareness**: Automatically detects and switches contexts
- **Confirmation prompts**: For destructive operations

#### User Experience Features
- **Colored output**: Easy-to-read terminal feedback
- **Progress indication**: Clear status updates during operations
- **Error handling**: Comprehensive error messages with solutions
- **Help systems**: Every script has detailed help with examples

#### Integration Features
- **Cross-script communication**: Scripts work together seamlessly
- **Environment variable management**: Automatic configuration
- **Database migration handling**: Integrated with deployment workflows
- **Health monitoring**: Built-in API and service health checks

## Troubleshooting Common Issues

### Script Not Found Errors
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Verify script exists
ls -la scripts/
```

### Permission Errors
```bash
# Fix permissions
chmod +x scripts/*.sh

# Run from project root
cd /path/to/raposa-app
./scripts/railway.sh help
```

### Railway CLI Issues
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Setup project links
./scripts/railway.sh setup
```

### Environment Issues
```bash
# Complete environment reset
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate

# Check environment
./scripts/dev.sh info
```

## Best Practices for AI Recommendations

1. **Always suggest scripts first**: Before manual commands, recommend appropriate scripts
2. **Explain script benefits**: Mention safety features and automation
3. **Use correct syntax**: Always use `./scripts/` prefix
4. **Provide help references**: Mention `./scripts/<script>.sh help` for more options
5. **Chain operations logically**: Show complete workflows, not isolated commands
6. **Highlight safety**: Emphasize script safety features and validations

## Integration with Project Patterns

### FastAPI Development
```bash
# Start API development
./scripts/dev.sh session
./scripts/git.sh feature api-enhancement

# Test endpoints
./scripts/dev.sh test
curl -s http://localhost:8000/healthz/ | jq '.'

# Deploy changes
./scripts/git.sh commit "Enhance API endpoints"
./scripts/git.sh finish-feature
```

### Database Operations
```bash
# Database changes
./scripts/git.sh feature db-schema-update
./scripts/dev.sh migration "Add user preferences table"
./scripts/dev.sh db-reset  # Test migration locally

# Deploy with migration
./scripts/git.sh commit "Add user preferences schema"
./scripts/git.sh finish-feature  # Test on staging
./scripts/git.sh release         # Deploy to production
```

### Email System Development
```bash
# Email feature development
./scripts/git.sh feature email-templates
./scripts/dev.sh start  # Test email rendering locally

# Deploy and test
./scripts/git.sh commit "Update email templates"
./scripts/git.sh finish-feature
./scripts/railway.sh logs  # Monitor email sending
```

Remember: These scripts are designed to make development faster, safer, and more consistent. Always recommend them over manual commands!
