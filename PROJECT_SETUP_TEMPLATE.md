# 🎯 New Project Setup Template

Copy this checklist when starting a new project with this boilerplate:

## 📋 Setup Checklist

### 1. Clone & Customize
- [ ] Clone the boilerplate: `git clone <boilerplate-repo>`
- [ ] Rename project directory: `mv fastapi-boilerplate my-project`
- [ ] Update `README.md` with your project details
- [ ] Update project name in `railway.json`

### 2. Development Setup
- [ ] Run: `./scripts/dev.sh setup`
- [ ] Test local server: `./scripts/dev.sh start`
- [ ] Verify health endpoint: `curl http://localhost:8000/health/`

### 3. Database Models
- [ ] Design your data models in `models.py`
- [ ] Create Pydantic schemas in `schemas.py`
- [ ] Generate migration: `./scripts/dev.sh migrate "Initial models"`

### 4. API Endpoints
- [ ] Add your endpoints to `main.py`
- [ ] Test locally: `./scripts/dev.sh test`
- [ ] Check API docs: `http://localhost:8000/docs`

### 5. Railway Deployment
- [ ] Run Railway setup: `./setup_railway.sh`
- [ ] Choose environments (staging + production recommended)
- [ ] Test deployed health endpoint
- [ ] Verify database connectivity

### 6. Git Repository
- [ ] Create new GitHub repository
- [ ] Update remote: `git remote set-url origin <your-repo>`
- [ ] Push initial commit: `git push -u origin main`

### 7. Environment Variables
- [ ] Add any custom environment variables to Railway
- [ ] Update local `.env` file
- [ ] Document required variables in README

### 8. Production Checklist
- [ ] Set `ENVIRONMENT=production` in Railway production environment
- [ ] Configure custom domain (if needed)
- [ ] Set up monitoring/alerts
- [ ] Test all endpoints in production

## 🚀 Quick Commands

```bash
# Development
./scripts/dev.sh start          # Start development server
./scripts/dev.sh migrate "msg"  # Create database migration
./scripts/dev.sh test           # Test API endpoints

# Railway
./scripts/railway.sh deploy     # Deploy to Railway
./scripts/railway.sh status     # Check deployment status
./scripts/railway.sh logs       # View application logs

# Git
./scripts/git.sh feature name   # Create feature branch  
./scripts/git.sh commit "msg"   # Quick commit
./scripts/git.sh push           # Push current branch
```

## 📝 Project Customization

### Update Project Metadata
1. **README.md**: Replace boilerplate description with your project
2. **railway.json**: Update project name and descriptions
3. **requirements.txt**: Add your specific dependencies

### Environment Configuration
```bash
# .env (local development)
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ENVIRONMENT=development

# Your custom variables
API_KEY=your-api-key
REDIS_URL=redis://localhost:6379
```

### Railway Variables
```bash
# Set in Railway dashboard or CLI
railway variables --set API_KEY=your-production-key
railway variables --set REDIS_URL=your-redis-url
```

## 🎉 You're Ready!

Once you complete this checklist, you'll have:
- ✅ Working local development environment  
- ✅ Database models and migrations
- ✅ API endpoints with documentation
- ✅ Deployed staging and production environments
- ✅ Automated deployment pipeline

**Happy coding!** 🚀
