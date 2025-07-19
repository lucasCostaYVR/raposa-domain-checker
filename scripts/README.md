# Raposa Domain Checker - Development Scripts

This directory contains helper scripts to streamline development and deployment workflows.

## Scripts Overview

### 🚂 Railway Management (`railway.sh`)
Manage Railway deployments and environments effortlessly.

**Quick Commands:**
```bash
# Check current status
./scripts/railway.sh status

# Deploy to development
./scripts/railway.sh deploy-dev

# Deploy to production  
./scripts/railway.sh deploy-prod

# Check API health
./scripts/railway.sh health

# Switch environments
./scripts/railway.sh switch dev
./scripts/railway.sh switch prod

# View logs
./scripts/railway.sh logs

# Create database migration
./scripts/railway.sh migrate "Add new table"

# Rollback deployment
./scripts/railway.sh rollback
```

**Setup:**
```bash
# First time setup
./scripts/railway.sh setup
```

### 💻 Development Tools (`dev.sh`)
Local development environment management and utilities.

**Quick Commands:**
```bash
# Start development server
./scripts/dev.sh start

# Setup development environment
./scripts/dev.sh setup

# Test API endpoints
./scripts/dev.sh test

# Format code
./scripts/dev.sh format

# Lint code
./scripts/dev.sh lint

# Run tests
./scripts/dev.sh tests

# Full development session
./scripts/dev.sh session
```

**Database Operations:**
```bash
# Reset development database
./scripts/dev.sh db-reset

# Create new migration
./scripts/dev.sh migration "Add user roles"
```

### 🌳 Git Workflow (`git.sh`)
Streamlined git operations following our branching strategy.

**Feature Development:**
```bash
# Start new feature
./scripts/git.sh feature user-authentication

# Quick commit
./scripts/git.sh commit "Implement login endpoint"

# Finish feature (merge to develop)
./scripts/git.sh finish-feature

# Release to production
./scripts/git.sh release
```

**Utility Commands:**
```bash
# Check status
./scripts/git.sh status

# Sync with remote
./scripts/git.sh sync

# Clean up branches
./scripts/git.sh cleanup

# View history
./scripts/git.sh history 20

# Emergency sync
./scripts/git.sh emergency
```

## Installation

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

## Prerequisites

### Required Tools
- **Railway CLI**: `npm install -g @railway/cli`
- **jq**: `brew install jq` (for JSON parsing)
- **curl**: Usually pre-installed
- **git**: Version control

### Optional Tools (for development)
- **black**: Code formatting (`pip install black`)
- **flake8**: Code linting (`pip install flake8`)
- **pytest**: Testing (`pip install pytest`)

## Workflow Integration

### Daily Development Workflow
```bash
# 1. Start development session
./scripts/dev.sh session

# 2. Create feature branch
./scripts/git.sh feature new-feature

# 3. Develop and commit changes
./scripts/git.sh commit "Add awesome feature"

# 4. Test locally
./scripts/dev.sh test

# 5. Finish feature (auto-deploys to staging)
./scripts/git.sh finish-feature

# 6. Deploy to production when ready
./scripts/git.sh release
```

### Environment Management
```bash
# Development environment
./scripts/railway.sh switch dev
./scripts/railway.sh health
./scripts/railway.sh logs

# Production environment  
./scripts/railway.sh switch prod
./scripts/railway.sh health
./scripts/railway.sh deployments
```

## Branch Strategy Integration

The scripts are designed around our branch strategy:

- **`develop`** → Development environment (`stage.domainchecker.raposa.tech`)
- **`main`** → Production environment (`api.domainchecker.raposa.tech`)

### Automatic Deployments
- Push to `develop` → Triggers staging deployment
- Push to `main` → Triggers production deployment

## Troubleshooting

### Common Issues

**Railway CLI not found:**
```bash
npm install -g @railway/cli
railway login
```

**Permission denied:**
```bash
chmod +x scripts/*.sh
```

**Python environment issues:**
```bash
./scripts/dev.sh setup
source venv/bin/activate
```

**Git conflicts:**
```bash
./scripts/git.sh emergency
# Resolve conflicts manually
./scripts/git.sh sync
```

### Health Check Failures
```bash
# Check logs for errors
./scripts/railway.sh logs

# Check environment variables
./scripts/railway.sh vars

# Rollback if needed
./scripts/railway.sh rollback
```

## Script Customization

Each script is designed to be easily customizable. Common modifications:

### Adding New Commands
Add new functions to the respective script and update the `main()` function's case statement.

### Environment-Specific Settings
Modify environment variables or add new environment checks in the scripts.

### Integration with CI/CD
These scripts can be integrated into GitHub Actions or other CI/CD pipelines.

## Tips and Best Practices

1. **Always check status before deploying:**
   ```bash
   ./scripts/git.sh status
   ./scripts/railway.sh health
   ```

2. **Use feature branches for all changes:**
   ```bash
   ./scripts/git.sh feature descriptive-name
   ```

3. **Test locally before deploying:**
   ```bash
   ./scripts/dev.sh test
   ```

4. **Monitor deployments:**
   ```bash
   ./scripts/railway.sh logs
   ```

5. **Clean up regularly:**
   ```bash
   ./scripts/git.sh cleanup
   ./scripts/dev.sh clean
   ```

## Support

For issues with these scripts:
1. Check the help messages: `./scripts/<script>.sh help`
2. Verify prerequisites are installed
3. Check Railway and GitHub connectivity
4. Review error messages and logs

Happy coding! 🚀
